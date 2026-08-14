#!/usr/bin/env python3
"""
Multi-GPU Architecture Wheel Builder for LibRA

This script builds LibRA wheels for different GPU architectures.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Define GPU architectures to build for
GPU_ARCHITECTURES = {
    'pascal61': 'PASCAL61',     # GTX 1080, GTX 1070, etc.
    'volta70': 'VOLTA70',       # V100, Titan V
    'turing75': 'TURING75',     # RTX 2080, RTX 2070, etc.
    'ampere80': 'AMPERE80',     # A100, RTX 3090, RTX 3080, etc.
    'ampere86': 'AMPERE86',     # RTX 3060, RTX 3070, etc.
    'ada89': 'ADA89',           # RTX 4090, RTX 4080, etc.
    'hopper90': 'HOPPER90',     # H100
}

def clean_build_dir():
    """Clean the build directory to ensure fresh builds."""
    build_dir = Path("build")
    if build_dir.exists():
        print(f"Cleaning build directory: {build_dir}")
        shutil.rmtree(build_dir)

def build_wheel_for_arch(arch_name, arch_value):
    """Build a wheel for a specific GPU architecture."""
    print(f"\n{'='*60}")
    print(f"Building wheel for {arch_name} (Kokkos_CUDA_ARCH_NAME={arch_value})")
    print(f"{'='*60}")
    
    # Clean build directory
    clean_build_dir()
    
    # Set environment variable for the architecture
    env = os.environ.copy()
    env['Kokkos_CUDA_ARCH_NAME'] = arch_value
    
    # Build the wheel
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'wheel', '.',
            '--no-deps', '--wheel-dir', 'dist'
        ], env=env, capture_output=True, text=True, timeout=3600)  # 1 hour timeout
        
        if result.returncode == 0:
            print(f"✅ Successfully built wheel for {arch_name}")
            
            # Rename wheel to include architecture
            wheel_files = list(Path("dist").glob("libra-*.whl"))
            if wheel_files:
                original_wheel = wheel_files[-1]  # Get the most recent wheel
                arch_wheel = original_wheel.parent / f"libra-{arch_name}-{original_wheel.name.split('-', 1)[1]}"
                original_wheel.rename(arch_wheel)
                print(f"   Renamed to: {arch_wheel.name}")
                return arch_wheel
            else:
                print(f"❌ No wheel file found for {arch_name}")
                return None
        else:
            print(f"❌ Failed to build wheel for {arch_name}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return None
            
    except subprocess.TimeoutExpired:
        print(f"❌ Build timed out for {arch_name}")
        return None
    except Exception as e:
        print(f"❌ Error building wheel for {arch_name}: {e}")
        return None

def main():
    """Main function to build wheels for all architectures."""
    print("LibRA Multi-GPU Architecture Wheel Builder")
    print("==========================================")
    
    # Ensure we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Run this script from libra-python directory.")
        sys.exit(1)
    
    # Create dist directory
    Path("dist").mkdir(exist_ok=True)
    
    # Build wheels for each architecture
    successful_builds = []
    failed_builds = []
    
    for arch_name, arch_value in GPU_ARCHITECTURES.items():
        wheel_path = build_wheel_for_arch(arch_name, arch_value)
        if wheel_path:
            successful_builds.append((arch_name, wheel_path))
        else:
            failed_builds.append(arch_name)
    
    # Summary
    print(f"\n{'='*60}")
    print("BUILD SUMMARY")
    print(f"{'='*60}")
    
    if successful_builds:
        print(f"✅ Successfully built {len(successful_builds)} wheels:")
        for arch_name, wheel_path in successful_builds:
            wheel_size = wheel_path.stat().st_size / (1024**3)  # Size in GB
            print(f"   {arch_name:12} -> {wheel_path.name} ({wheel_size:.1f}GB)")
    
    if failed_builds:
        print(f"\n❌ Failed to build {len(failed_builds)} wheels:")
        for arch_name in failed_builds:
            print(f"   {arch_name}")
    
    print(f"\nTotal wheels in dist/: {len(list(Path('dist').glob('*.whl')))}")
    
    # Final instructions
    if successful_builds:
        print(f"\n{'='*60}")
        print("NEXT STEPS")
        print(f"{'='*60}")
        print("You can now distribute these wheels:")
        print("1. Upload to PyPI: twine upload dist/*.whl")
        print("2. Install specific architecture: pip install dist/libra-<arch>-*.whl")
        print("3. Test on target systems with the corresponding GPU architecture")

if __name__ == "__main__":
    main()