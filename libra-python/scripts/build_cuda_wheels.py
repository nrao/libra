#!/usr/bin/env python3
"""
Build LibRA Python wheels for multiple CUDA architectures.

Produces one wheel per GPU arch, tagged with the arch name so they can
coexist in a distribution directory, e.g.:
  wheels/volta70/libra_volta70-0.1.0-cp311-cp311-linux_x86_64.whl

Usage:
  python scripts/build_cuda_wheels.py [--arch VOLTA70 AMPERE80 ...] [--output-dir DIR]
  python scripts/build_cuda_wheels.py --list
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path
import time

# Kokkos arch name -> (tag used in wheel filename, CUDA compute capability)
CUDA_ARCHITECTURES = {
    'PASCAL60':  ('pascal60',  '6.0'),
    'PASCAL61':  ('pascal61',  '6.1'),
    'VOLTA70':   ('volta70',   '7.0'),
    'VOLTA72':   ('volta72',   '7.2'),
    'TURING75':  ('turing75',  '7.5'),
    'AMPERE80':  ('ampere80',  '8.0'),
    'AMPERE86':  ('ampere86',  '8.6'),
    'ADA89':     ('ada89',     '8.9'),
    'HOPPER90':  ('hopper90',  '9.0'),
}

# Default set built by CI (covers VLA/ALMA hardware at NRAO)
DEFAULT_ARCHES = ['VOLTA70', 'AMPERE80', 'HOPPER90']


def clean_build_dirs(source_dir: Path):
    for name in ['build', 'dist', '_skbuild']:
        d = source_dir / name
        if d.exists():
            print(f"  cleaning {d}")
            shutil.rmtree(d)


def build_wheel_for_arch(arch: str, source_dir: Path, output_dir: Path) -> Path | None:
    tag, cc = CUDA_ARCHITECTURES[arch]
    arch_out = output_dir / tag
    arch_out.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Building {arch}  (sm_{cc.replace('.', '')})  -> {arch_out}")
    print(f"{'='*60}")

    clean_build_dirs(source_dir)

    env = os.environ.copy()
    env['LIBRA_CUDA_ARCH'] = arch
    env['LIBRA_ENABLE_CUDA'] = 'ON'

    cmd = [sys.executable, "-m", "build", "--wheel", str(source_dir),
           "--outdir", str(source_dir / "dist")]

    t0 = time.time()
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FAILED for {arch} after {time.time()-t0:.1f}s: {e}")
        return None

    wheels = list((source_dir / "dist").glob("*.whl"))
    if not wheels:
        print(f"ERROR: no wheel produced for {arch}")
        return None

    wheel = wheels[0]

    # Rename to embed the arch tag in the wheel name, e.g.
    # libra-0.1.0-... -> libra_volta70-0.1.0-...
    stem = wheel.stem   # e.g. libra-0.1.0-cp311-cp311-linux_x86_64
    parts = stem.split("-", 1)  # ['libra', '0.1.0-cp311-...']
    tagged_name = f"{parts[0]}_{tag}-{parts[1]}{wheel.suffix}"
    dest = arch_out / tagged_name
    shutil.move(str(wheel), str(dest))

    print(f"  built in {time.time()-t0:.1f}s -> {dest}")
    return dest


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--arch', '-a', nargs='+',
                        choices=list(CUDA_ARCHITECTURES.keys()),
                        metavar='ARCH',
                        help=f"Architectures to build (default: {DEFAULT_ARCHES})")
    parser.add_argument('--output-dir', '-o', default='wheels',
                        help="Root output directory (default: wheels/)")
    parser.add_argument('--source-dir', '-s', default=None,
                        help="Path to libra-python/ (default: directory of this script's parent)")
    parser.add_argument('--list', action='store_true',
                        help="List available architectures and exit")
    args = parser.parse_args()

    if args.list:
        print(f"{'Arch':<12} {'Tag':<12} {'sm'}")
        for arch, (tag, cc) in CUDA_ARCHITECTURES.items():
            marker = " *" if arch in DEFAULT_ARCHES else ""
            print(f"  {arch:<12} {tag:<12} sm_{cc.replace('.','')}{marker}")
        print(f"\n* = default CI set")
        return

    source_dir = Path(args.source_dir) if args.source_dir else Path(__file__).parent.parent
    output_dir = Path(args.output_dir)
    arches = args.arch or DEFAULT_ARCHES

    if not (source_dir / "pyproject.toml").exists():
        print(f"ERROR: pyproject.toml not found in {source_dir}")
        sys.exit(1)

    print(f"LibRA Multi-CUDA Wheel Builder")
    print(f"  source : {source_dir}")
    print(f"  output : {output_dir}")
    print(f"  arches : {arches}")

    built, failed = [], []
    for arch in arches:
        w = build_wheel_for_arch(arch, source_dir, output_dir)
        (built if w else failed).append(arch)

    print(f"\n{'='*60}")
    print(f"SUMMARY  built={len(built)}  failed={len(failed)}")
    for arch in built:
        print(f"  OK  {arch}")
    for arch in failed:
        print(f"  FAIL {arch}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
