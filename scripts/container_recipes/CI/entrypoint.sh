#!/bin/sh
set -e

# $HOME may be a fresh per-user volume -- seed the demo notebook once.
[ -f "$HOME/demo.ipynb" ] || cp /opt/libra/demo.ipynb "$HOME/demo.ipynb"

# Subshell keeps the cd out of the notebook root; a failed download
# must not block the spawn.
DATA_DIR="$HOME/sample_data"
if [ ! -d "$DATA_DIR/SNR_G55_10s.calib.ms" ]; then
    (
        mkdir -p "$DATA_DIR" && cd "$DATA_DIR" \
        && wget -q -O SNR_G55_10s.calib.tar.gz \
           https://casa.nrao.edu/Data/EVLA/SNRG55/SNR_G55_10s.calib.tar.gz \
        && tar xzf SNR_G55_10s.calib.tar.gz \
        && rm -f SNR_G55_10s.calib.tar.gz
    ) || {
        rm -rf "$DATA_DIR/SNR_G55_10s.calib.tar.gz" "$DATA_DIR/SNR_G55_10s.calib.ms"
        echo "entrypoint: sample data download failed, continuing without it" >&2
    }
fi

exec "$@"
