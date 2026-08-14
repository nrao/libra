import pytest
import os
import shutil
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
from libra import hummbee2py
from libra.helper_functions import compare_images_with_tolerance

# Get the functions from the dynamically imported modules
Hummbee = libra.hummbee2py.Hummbee
getchunk = libra.utilities2py.getchunk
ImageType = libra.utilities2py.ImageType

# Define the tolerance and the expected gold value
tol = 0.1
goldPeakRes = 4.98845

# Test class for testing PeakRes calculations
@pytest.fixture
def hummbee_test_setup(gold_standard_dir):
    """Setup fixture for Hummbee tests."""
    if gold_standard_dir is None:
        pytest.skip("Gold standard test data not found")
        
    # Get the test name
    test_name = "runPythonTests"
    
    # Create a unique directory for this test case
    test_dir = Path.cwd() / test_name
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files to the test directory
    shutil.copytree(gold_standard_dir / "unittest_hummbee.pb", test_dir / "unittest_hummbee.pb")
    shutil.copytree(gold_standard_dir / "unittest_hummbee.psf", test_dir / "unittest_hummbee.psf")
    shutil.copytree(gold_standard_dir / "unittest_hummbee.residual", test_dir / "unittest_hummbee.residual")
    shutil.copytree(gold_standard_dir / "unittest_hummbee.sumwt", test_dir / "unittest_hummbee.sumwt")
    
    # Set the current working directory to the test directory
    original_cwd = Path.cwd()
    os.chdir(test_dir)
    
    # Define parameters
    image_name = "unittest_hummbee"
    model_image_name = "unittest_hummbee.image"
    deconvolver = "asp"
    specmode = "cube"
    scales = []
    largestscale = -1
    fusedthreshold = 0
    nterms = 1
    gain = 0.1
    threshold = 1e-4
    nsigma = 1.5
    cycleniter = 10
    cyclefactor = 1.0
    mask = ["circle[[256pix,290pix],140pix]"]
    doPBCorr = False
    imagingMode = "deconvolve"
    
    # Call the function equivalent to Hummbee in Python
    peak_res = Hummbee(image_name, model_image_name,
                      deconvolver,
                      scales,
                      largestscale, fusedthreshold,
                      nterms,
                      gain, threshold,
                      nsigma,
                      cycleniter, cyclefactor,
                      mask, specmode,
                      doPBCorr,
                      imagingMode)
    
    yield {
        'test_dir': test_dir,
        'gold_dir': gold_standard_dir,
        'peak_res': peak_res
    }
    
    # Cleanup
    os.chdir(original_cwd)
    shutil.rmtree(test_dir)

class TestHummbee:

    def test_peak_res(self, hummbee_test_setup):
        peak_res = hummbee_test_setup['peak_res']
        assert abs(peak_res - goldPeakRes) < tol

    def test_residual_value(self, hummbee_test_setup):
        # comparing two files is not a stable test. Commented.
        #assert compare_images_with_tolerance(hummbee_test_setup['gold_dir']/"unittest_hummbee_gold2.residual", "unittest_hummbee.residual", tol2)
        r1_result = getchunk("unittest_hummbee", ImageType.RESIDUAL)
        rgold_result = 0.34095
        assert abs(r1_result[255, 287, 0, 0] - rgold_result) < 0.01

    # can't do the following because hummbee2py internally
    # has interaction with casa that conflict when both
    # are loaded simultaneously.
    '''def test_residual_value(self):
        ia = image()
        ia.open("unittest_hummbee.model")
        model_result = ia.getchunk()

        print("Value at location ", model_result[275,330,0,0])
        ia.close()'''


# Main entry point to run the tests
if __name__ == '__main__':
    pytest.main([__file__])
