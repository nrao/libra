# LibRA Python Scripts

This directory contains build scripts and pipeline tools for the LibRA Python package.

## Build Scripts

- **`build_cuda_wheels.py`** - Main script to build wheels for multiple CUDA architectures
- **`build_cuda_batch.sh`** - Batch script to build all common CUDA architectures
- **`CUDA_BUILDS.md`** - Detailed documentation for CUDA wheel building

## Pipeline Scripts

- **`libra_slurm_clean_python.py`** - SLURM pipeline generator using libra-python bindings
- **`example_config.json`** - Example configuration file for the Python pipeline

## Build Usage

Run from the `libra-python/` root directory:

```bash
# Build specific architectures
python3 scripts/build_cuda_wheels.py -a pascal61 volta70

# Build all architectures (batch)
scripts/build_cuda_batch.sh

# List available architectures
python3 scripts/build_cuda_wheels.py --list
```

## Pipeline Usage

### Basic Usage
```bash
python scripts/libra_slurm_clean_python.py --config scripts/example_config.json --cycles 10 --gpu-arch v100 --dry-run
```

### With Custom Parameters
```bash
python scripts/libra_slurm_clean_python.py \
    --config '{"imagename": "my_image", "vis": "/data/vis.ms", "cfcache": "/cache/libra.cf"}' \
    --cycles 5 \
    --gpu-arch h200 \
    --account my_account \
    --email user@msu.edu \
    --work-dir /scratch/imaging \
    --dry-run
```

## Configuration Parameters

### Required Parameters
- `imagename` (str): Base name for output images
- `vis` (str): Path to visibility measurement set
- `cfcache` (str): Path to CF cache directory

### Optional Parameters
- `mode` (str): Processing mode
- `nchan` (int): Number of channels
- `nspw` (int): Number of spectral windows
- `cell` (list): Cell size in arcseconds [x, y]
- `imsize` (list): Image size in pixels [nx, ny]
- `stokes` (str): Stokes parameters
- `gridder` (str): Gridding algorithm
- `deconvolver` (str): Deconvolution algorithm
- `niter` (int): Number of iterations
- `threshold` (str): Cleaning threshold
- `cycleniter` (int): Iterations per cycle
- `cyclethreshold` (str): Threshold per cycle
- `weighting` (str): Weighting scheme
- `robust` (float): Robust parameter

## How the Pipeline Works

1. **Script Generation**: Creates individual Python scripts for each libra operation:
   - `roadrunner_*.py` - For gridding operations (weight, psf, residual)
   - `hummbee_*.py` - For deconvolution and restoration
   - `dale_*.py` - For PSF normalization and model processing
   - `coyote_*.py` - For CF filling

2. **SLURM Integration**: Generates SLURM batch scripts that:
   - Set up proper GPU constraints
   - Manage job dependencies
   - Execute Python scripts with libra-python bindings

3. **Pipeline Flow**:
   ```
   Gridding (parallel) → PSF Normalization → Cleaning Cycles → Final Images
   ```

## Advantages over CLI Version

- **Type Safety**: Full parameter validation with Python type checking
- **Memory Efficiency**: Direct memory management through Python bindings
- **Error Handling**: Better exception handling and debugging
- **Flexibility**: Easy parameter modification without .def file parsing
- **Integration**: Natural integration with Python-based workflows

## GPU Architecture Support

- `v100`: NVIDIA V100 (32GB) - MSU ICER intel18-v100 partition
- `l40s`: NVIDIA L40S (48GB) - MSU ICER nel partition  
- `h200`: NVIDIA H200 (141GB) - MSU ICER nfh/neh partitions

## Development

These scripts are development tools and are not installed with the package. The build scripts create distribution wheels for different CUDA architectures, while the pipeline scripts generate SLURM jobs for radio interferometry processing.