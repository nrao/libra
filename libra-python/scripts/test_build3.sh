#!/bin/bash
# Quick test script for Build 3 wheel
# Run this when build completes

set -e  # Exit on error

echo "===== Build 3 Wheel Test ====="
echo ""

# Check wheel exists
if [ ! -f dist/libra-0.1.0-cp312-cp312-linux_x86_64.whl ]; then
    echo "ERROR: Wheel not found in dist/"
    exit 1
fi

# 1. Check size
echo "1. Wheel size:"
ls -lh dist/libra-0.1.0-cp312-cp312-linux_x86_64.whl | awk '{print "   " $5}'
echo ""

# 2. Check symlinks
echo "2. Checking for libkokkoscore symlinks:"
unzip -l dist/libra-0.1.0-cp312-cp312-linux_x86_64.whl | grep "libkokkoscore.so.4.7" | head -5
if [ $? -eq 0 ]; then
    echo "   OK: Found kokkos symlinks"
else
    echo "   FAIL: No kokkos symlinks found"
    exit 1
fi
echo ""

# 3. Install wheel
echo "3. Installing wheel..."
pip uninstall -y libra >/dev/null 2>&1 || true
pip install dist/libra-0.1.0-cp312-cp312-linux_x86_64.whl >/dev/null 2>&1
echo "   Installed"
echo ""

# 4. Test import (critical test)
echo "4. Testing roadrunner2py import:"
cd /tmp
python << 'EOF'
try:
    import libra.roadrunner2py
    print("   SUCCESS: roadrunner2py imported")
except ImportError as e:
    print(f"   FAIL: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "Import failed. Check RPATH and symlinks."
    exit 1
fi
echo ""

# 5. Run full test
echo "5. Running full test suite:"
python ~/Software/libra/libra-python/scripts/test_wheel.py

echo ""
echo "===== Test Complete ====="
