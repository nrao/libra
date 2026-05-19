#!/usr/bin/env bash
# k3s + NVIDIA GPU prep for the CI box.
#
# Run as root on the CI box (NOT on the workstation):
#   sudo bash scripts/k3s/setup-ci-box.sh
#
# This script is idempotent — re-running it is safe.
#
# What it does (and why):
#
#  1. Installs k3s with the default containerd runtime.
#     - k3s ships its own containerd (separate from any host docker).
#     - We do NOT install the k3s docker shim; we want containerd as the runtime
#       because the NVIDIA toolkit integrates more cleanly with containerd on
#       modern stacks.
#
#  2. Installs nvidia-container-toolkit and configures it for k3s's containerd.
#     - The toolkit ships a CDI generator + an OCI hook so containerd can
#       launch GPU-aware containers without nvidia-docker.
#     - `nvidia-ctk runtime configure --runtime=containerd` rewrites a
#       containerd config template so containerd registers an "nvidia" runtime
#       handler. We point it at k3s's config template path so k3s picks it up
#       on restart.
#
#  3. Generates the CDI spec.
#     - CDI (Container Device Interface) maps /dev/nvidia* device files into
#       a declarative spec that the device plugin and containerd can consume.
#     - Written to both /etc/cdi/ (persistent) and /var/run/cdi/ (runtime
#       mount path the device plugin pod reads).
#     - Must be regenerated if the driver version changes.
#
#  4. Applies the nvidia RuntimeClass.
#     - A RuntimeClass is a k8s object that selects which runtime handler
#       containerd uses for a given pod. Pods that opt in set
#       `spec.runtimeClassName: nvidia` and get the NVIDIA-enabled runtime.
#     - Without this, the default runc runtime is used and CUDA calls fail.
#
#  5. Installs the NVIDIA k8s device plugin via Helm.
#     - The plugin advertises `nvidia.com/gpu: <N>` as a schedulable resource.
#     - Installed via Helm (not the static manifest) so we can pass
#       runtimeClassName=nvidia. Without this, the device plugin pod runs under
#       runc, cannot open /dev/nvidiactl, and NVML initialisation fails.
#     - The Helm chart's nodeAffinity requires nvidia.com/gpu.present=true on
#       the node; this script labels the node automatically.
#
# After this script: a test pod with `runtimeClassName: nvidia` and a GPU
# request should run `nvidia-smi` successfully. The verify step at the end
# does exactly that.

set -euo pipefail

[[ $EUID -eq 0 ]] || { echo "Must run as root."; exit 1; }

# Pin versions explicitly. Bump deliberately; do not let `latest` drift in CI.
K3S_VERSION="${K3S_VERSION:-v1.31.4+k3s1}"             # TBC against k3s releases
NVIDIA_DEVICE_PLUGIN_CHART_VERSION="${NVIDIA_DEVICE_PLUGIN_CHART_VERSION:-0.19.1}"

# ------------------------------------------------------------------
# 1. Install k3s
# ------------------------------------------------------------------
if ! command -v k3s >/dev/null 2>&1; then
  echo "[k3s] Installing $K3S_VERSION ..."
  # --write-kubeconfig-mode 644: lets non-root users read the kubeconfig.
  # --disable traefik: we don't need the ingress controller for the demo.
  curl -sfL https://get.k3s.io | \
    INSTALL_K3S_VERSION="$K3S_VERSION" \
    INSTALL_K3S_EXEC="--write-kubeconfig-mode 644 --disable traefik" \
    sh -
else
  echo "[k3s] Already installed ($(k3s --version | head -1))."
fi

# Make kubectl / helm pick up the k3s kubeconfig automatically.
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# ------------------------------------------------------------------
# 2. NVIDIA container toolkit + containerd integration
# ------------------------------------------------------------------
if ! rpm -q nvidia-container-toolkit >/dev/null 2>&1; then
  echo "[nvidia] Installing nvidia-container-toolkit ..."
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo \
    | tee /etc/yum.repos.d/nvidia-container-toolkit.repo
  dnf -y install nvidia-container-toolkit
fi

# Configure the toolkit for k3s's containerd.
# k3s reads its containerd config from a template; we tell nvidia-ctk to
# patch THAT file so the change survives k3s restarts (containerd's own
# config.toml is regenerated from the template each boot).
K3S_CONTAINERD_TMPL=/var/lib/rancher/k3s/agent/etc/containerd/config.toml.tmpl
if [[ ! -f "$K3S_CONTAINERD_TMPL" ]]; then
  # First-boot quirk: the template only exists after k3s has run once.
  cp /var/lib/rancher/k3s/agent/etc/containerd/config.toml "$K3S_CONTAINERD_TMPL"
fi
nvidia-ctk runtime configure \
  --runtime=containerd \
  --config="$K3S_CONTAINERD_TMPL" \
  --set-as-default=false   # keep runc as default, opt into nvidia per-pod

systemctl restart k3s
echo "[nvidia] containerd configured with the nvidia runtime."

# ------------------------------------------------------------------
# 3. CDI spec
# ------------------------------------------------------------------
# The CDI spec maps physical GPU devices (/dev/nvidia0 etc.) into a format
# the device plugin and containerd can both consume. Must be regenerated
# whenever the driver is updated.
mkdir -p /etc/cdi /var/run/cdi
nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
cp /etc/cdi/nvidia.yaml /var/run/cdi/nvidia.yaml
echo "[nvidia] CDI spec written to /etc/cdi/nvidia.yaml and /var/run/cdi/nvidia.yaml"

# ------------------------------------------------------------------
# 4. RuntimeClass + 5. Device plugin (via Helm)
# ------------------------------------------------------------------
kubectl apply -f "$(dirname "$0")/nvidia-runtime-class.yaml"

# Label the node so the device plugin daemonset's nodeAffinity matches.
# The Helm chart requires one of several NFD labels; we set the simplest one.
NODE_NAME=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl label node "$NODE_NAME" nvidia.com/gpu.present=true --overwrite

# Install the device plugin via Helm so we can pass runtimeClassName.
# The static manifest approach lacks this flag and the pod falls back to runc,
# which cannot access /dev/nvidiactl and fails NVML initialisation.
if ! command -v helm >/dev/null 2>&1; then
  echo "[helm] Installing Helm ..."
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi

helm repo add nvdp https://nvidia.github.io/k8s-device-plugin --force-update
helm repo update nvdp

helm upgrade --install nvdp nvdp/nvidia-device-plugin \
  --namespace kube-system \
  --version "$NVIDIA_DEVICE_PLUGIN_CHART_VERSION" \
  --set deviceDiscoveryStrategy=nvml \
  --set nvidiaDriverRoot=/ \
  --set runtimeClassName=nvidia

echo "[k8s] Waiting for the device plugin DaemonSet to roll out ..."
kubectl -n kube-system rollout status daemonset/nvdp-nvidia-device-plugin --timeout=120s

# ------------------------------------------------------------------
# Verify
# ------------------------------------------------------------------
echo "[verify] Node should advertise nvidia.com/gpu:"
kubectl describe node | grep -E "nvidia\.com/gpu:\s+[1-9]" || {
  echo "ERROR: node is not advertising any GPUs."
  echo "Checklist:"
  echo "  1. nvidia-smi works on the host?"
  echo "  2. kubectl -n kube-system logs -l app.kubernetes.io/name=nvidia-device-plugin --tail=30"
  echo "  3. Does the pod have runtimeClassName=nvidia? (kubectl -n kube-system get pod -l app.kubernetes.io/name=nvidia-device-plugin -o yaml | grep runtimeClassName)"
  exit 1
}

echo "[verify] Launching a one-shot GPU pod ..."
kubectl run gpu-check \
  --rm -i --restart=Never \
  --image=nvidia/cuda:12.9.1-base-rockylinux8 \
  --overrides='{"spec":{"runtimeClassName":"nvidia","containers":[{"name":"gpu-check","image":"nvidia/cuda:12.9.1-base-rockylinux8","command":["nvidia-smi"],"resources":{"limits":{"nvidia.com/gpu":"1"}}}]}}' \
  -- nvidia-smi

echo "[done] k3s + NVIDIA prep complete. Move on to ARC install (scripts/runner/)."
