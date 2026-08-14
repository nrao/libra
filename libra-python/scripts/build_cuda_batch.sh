#!/bin/bash
# Quick batch script to build multiple CUDA wheels

#set -e  # Exit on error

echo "LibRA CUDA Wheels Batch Builder"
echo "==============================="

# Create output directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="wheels_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "Output directory: $OUTPUT_DIR"

# Define architectures to build
ARCHITECTURES=(
#    "pascal61"
    "volta70" 
    "turing75"
    "ampere80"
    "ampere86"
    "ada89"
    "hopper90"
)

echo "Building wheels for: ${ARCHITECTURES[*]}"
echo ""

# Build each architecture
SUCCESSFUL=0
FAILED=0

for ARCH in "${ARCHITECTURES[@]}"; do
    echo "Building $ARCH..."

    # Clean build, dist, and ../build directories
    for DIR in build dist ../build; do
        if [ -d "$DIR" ]; then
            echo "Cleaning $DIR directory"
            rm -rf "$DIR"
        fi
    done

    # Create a unique output subdirectory for this arch
    ARCH_OUTPUT_DIR="${OUTPUT_DIR}/${ARCH}"
    mkdir -p "$ARCH_OUTPUT_DIR"

    if python3 "$(dirname "$0")/build_cuda_wheels.py" -a "$ARCH" -o "$ARCH_OUTPUT_DIR"; then
        echo "✅ $ARCH build successful"
        ((SUCCESSFUL++))
    else
        echo "❌ $ARCH build failed"
        ((FAILED++))
    fi
    echo ""
done

echo "==============================="
echo "FINAL SUMMARY"
echo "==============================="
echo "Successful builds: $SUCCESSFUL"
echo "Failed builds: $FAILED"
echo "Output directory: $OUTPUT_DIR"

if [ $FAILED -gt 0 ]; then
    echo "Some builds failed!"
    exit 1
else
    echo "All builds completed successfully!"
    echo ""
    echo "Generated wheels:"
    ls -la "$OUTPUT_DIR"/*.whl 2>/dev/null || echo "No wheels found"
fi
