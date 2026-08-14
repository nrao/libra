import pytest
import os
import shutil
import numpy as np
import sys
from pathlib import Path

# Ensure we import the installed package, not source
libra_source_paths = [
    str(Path(__file__).parent.parent),  # libra-python directory
    str(Path(__file__).parent.parent.parent)  # main libra directory
]

for path in libra_source_paths:
    if path in sys.path:
        sys.path.remove(path)

# Import from installed package
import libra
from libra import asp2py, utilities2py

# Get the functions from the modules
Asp2py = asp2py.asp  # Use clean API function name
getchunk = utilities2py.getchunk
ImageType = utilities2py.ImageType


@pytest.fixture
def asp_test_setup(gold_standard_dir):
    """Setup fixture for ASP tests."""
    if gold_standard_dir is None:
        pytest.skip("Gold standard test data not found")
        
    test_name = 'casacore_asp_mfs'
    test_dir = Path.cwd() / test_name
    test_dir.mkdir(parents=True, exist_ok=True) 
    
    # Copy files
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE.psf', test_dir / 'unittest_hummbee_mfs_revE.psf')
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE.mask', test_dir / 'unittest_hummbee_mfs_revE.mask')
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE.residual', test_dir / 'unittest_hummbee_mfs_revE.residual')
    
    # Change current working directory to the test directory
    original_cwd = Path.cwd()
    os.chdir(test_dir)
    
    yield {'test_dir': test_dir, 'gold_dir': gold_standard_dir}
    
    # Cleanup: Move to the parent directory and clean up
    os.chdir(original_cwd)
    shutil.rmtree(test_dir)

class TestAsp:
        

    def test_asp_func_level(self, asp_test_setup):
        specmode = "cube"
        largestscale = -1
        fusedthreshold = 0
        nterms = 2
        gain = 0.1
        threshold = 1e-4
        nsigma = 1.5
        cycleniter = 10
        cyclefactor = 1.0
        psfwidth = 5.0
        nsigmathreshold = 1

        nx = 2
        ny = 5

        psfb = np.array([
            [1, 8, 12, 20, 25],
            [5, 9, 13, 24, 26]
        ])

        modelb = np.zeros((nx, ny))
        residualb = np.array([
            [1, 8, 12, -20, -25],
            [5, 9, -13, 24, 26]
        ])
        maskb = np.array([
            [1, 8, 0, 20, 25],
            [5, 9, 13, 24, 0]
        ])

        # Call the Asp function
        Asp2py(modelb, psfb, residualb, maskb,
            nx, ny,
            psfwidth,
            largestscale, fusedthreshold,
            nterms,
            gain, 
            threshold, nsigmathreshold,
            nsigma,
            cycleniter, cyclefactor,
            specmode
            )

        assert psfb[1, 0] == 5.0
        assert residualb[0, 3] == -20.0

    def test_getchunk(self, asp_test_setup):
        r1_result = getchunk("unittest_hummbee_mfs_revE", ImageType.RESIDUAL)
        assert abs(r1_result[1072,1639,0,0] - 12.110947) < 0.01


    def test_asp2py_mfs(self, asp_test_setup):
        specmode = "mfs"
        largestscale = -1
        fusedthreshold = 0.007
        nterms = 2
        gain = 0.2
        threshold = 2.6e-07
        nsigma = 0.0
        cycleniter = 3
        cyclefactor = 1.0

        psfwidth = 40.0 
        nsigmathreshold = 0
        nx = 4000
        ny = 4000
        
        # retrieve the input images
        image_name = "unittest_hummbee_mfs_revE"
        residual = getchunk(image_name, ImageType.RESIDUAL)
        psf = getchunk(image_name, ImageType.PSF)
        mask = getchunk(image_name, ImageType.MASK)
        model = np.zeros((nx, ny))


        Asp2py(model, psf[:, :, 0, 0], residual[:, :, 0, 0], mask[:, :, 0, 0],
            nx, ny,
            psfwidth,
            largestscale, fusedthreshold,
            nterms,
            gain, 
            threshold, nsigmathreshold,
            nsigma,
            cycleniter, cyclefactor,
            specmode
            )

        tol = 0.1
        res_gold_val_loc = 9.44497
        assert abs(residual[1072, 1639, 0, 0] - res_gold_val_loc) < tol


    # teardown_method removed - handled by fixture
    

        

if __name__ == '__main__':
    pytest.main([__file__])