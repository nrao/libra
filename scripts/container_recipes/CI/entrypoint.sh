#!/bin/sh
set -e

DATA_DIR="$HOME/sample_data"
if [ ! -d "$DATA_DIR/SNR_G55_10s.calib" ]; then
    mkdir -p "$DATA_DIR"
    cd "$DATA_DIR"
    wget -q https://casa.nrao.edu/Data/EVLA/SNRG55/SNR_G55_10s.calib.tar.gz
    tar xzf SNR_G55_10s.calib.tar.gz
    rm SNR_G55_10s.calib.tar.gz
fi

exec "$@"
