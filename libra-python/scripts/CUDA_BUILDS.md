# LibRA CUDA Multi-Architecture Wheel Builder

This directory contains tools to build LibRA Python wheels for multiple CUDA architectures.

## Available CUDA Architectures

| Architecture | Kokkos Name | GPU Examples |
|--------------|-------------|--------------|
| `pascal60`   | PASCAL60    | Tesla P100 |
| `pascal61`   | PASCAL61    | GTX 1080, GTX 1070 |
| `volta70`    | VOLTA70     | Tesla V100 |
| `volta72`    | VOLTA72     | Xavier |
| `turing75`   | TURING75    | RTX 2080, RTX 2070 |
| `ampere80`   | AMPERE80    | A100, RTX 3090 |
| `ampere86`   | AMPERE86    | RTX 3080, RTX 3070 |
| `ada89`      | ADA89       | RTX 4090, RTX 4080 |
| `hopper90`   | HOPPER90    | H100 |

## Quick Start

### Build All Architectures (Batch)
```bash
./build_cuda_batch.sh
```

### Build Specific Architectures
```bash
# Single architecture
python3 build_cuda_wheels.py -a pascal61

# Multiple architectures
python3 build_cuda_wheels.py -a pascal61 volta70 ampere80

# Custom output directory
python3 build_cuda_wheels.py -a ampere80 -o /path/to/wheels/
```

### List Available Architectures
```bash
python3 build_cuda_wheels.py --list
```

## Usage Examples

### Build for Common Modern GPUs
```bash
python3 build_cuda_wheels.py -a turing75 ampere80 ampere86 ada89
```

### Build for Data Center GPUs
```bash
python3 build_cuda_wheels.py -a volta70 ampere80 hopper90
```

### Build for Legacy GPUs
```bash
python3 build_cuda_wheels.py -a pascal60 pascal61
```

## Output

Wheels are generated with architecture-specific names:
```
libra-0.1.0-cp310-cp310-linux_x86_64_pascal61.whl
libra-0.1.0-cp310-cp310-linux_x86_64_volta70.whl
libra-0.1.0-cp310-cp310-linux_x86_64_ampere80.whl
```

## Installation

Users can install the appropriate wheel for their GPU:
```bash
# For RTX 3080/3070 (Ampere 86)
pip install libra-0.1.0-cp310-cp310-linux_x86_64_ampere86.whl

# For A100 (Ampere 80)  
pip install libra-0.1.0-cp310-cp310-linux_x86_64_ampere80.whl
```

## Build Requirements

- CMake >= 3.18
- CUDA Toolkit
- Python 3.8+
- scikit-build-core
- pybind11

## Troubleshooting

### Build Fails
1. Check CUDA installation: `nvcc --version`
2. Verify CMake version: `cmake --version`
3. Clean build: `rm -rf build dist _skbuild`

### Wrong Architecture Detection
The build system will auto-detect your GPU if no architecture is specified. To force a specific architecture:
```bash
export LIBRA_CUDA_ARCH=AMPERE80
python3 -m build --wheel
```

## Integration with CI/CD

The build scripts can be integrated into CI/CD pipelines:
```yaml
# GitHub Actions example
- name: Build CUDA wheels
  run: |
    python3 build_cuda_wheels.py -a pascal61 volta70 turing75 ampere80 ampere86 ada89 hopper90 -o dist/
```