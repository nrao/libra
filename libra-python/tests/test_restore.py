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
from libra import restore2py, utilities2py

# Get the functions from the modules
Restore2py = restore2py.restore  # Use clean API function name
getchunk = utilities2py.getchunk
ImageType = utilities2py.ImageType


@pytest.fixture
def restore_test_setup(gold_standard_dir):
    """Setup fixture for Restore tests."""
    if gold_standard_dir is None:
        pytest.skip("Gold standard test data not found")
        
    test_name = 'restore2py_testdir'
    test_dir = Path.cwd() / test_name
    test_dir.mkdir(parents=True, exist_ok=True) 
    
    # Copy files
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE_restore.psf', test_dir / 'unittest_hummbee_mfs_revE_restore.psf')
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE_restore.residual', test_dir / 'unittest_hummbee_mfs_revE_restore.residual')
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE_restore.sumwt', test_dir / 'unittest_hummbee_mfs_revE_restore.sumwt')
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE_restore.weight', test_dir / 'unittest_hummbee_mfs_revE_restore.weight')
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE_restore.model', test_dir / 'unittest_hummbee_mfs_revE_restore.model')
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE_restore_gold.image', test_dir / 'unittest_hummbee_mfs_revE_restore_gold.image')
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE_restore.pb', test_dir / 'unittest_hummbee_mfs_revE_restore.pb')
    shutil.copytree(gold_standard_dir / 'unittest_hummbee_mfs_revE_restore_gold.image.pbcor', test_dir / 'unittest_hummbee_mfs_revE_restore_gold.image.pbcor')
    
    # Change current working directory to the test directory
    original_cwd = Path.cwd()
    os.chdir(test_dir)
    
    yield {'test_dir': test_dir, 'gold_dir': gold_standard_dir}
    
    # Cleanup
    os.chdir(original_cwd)
    shutil.rmtree(test_dir)

class TestRestore:


    def test_restore2py_func_level(self, restore_test_setup):
        nx = 2
        ny = 5

        model = np.array([
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10]
            ], dtype=np.float32)

        residual = np.array([
            [1, -1, 1, -1, 1],
            [-1, 1, -1, 1, -1]
            ], dtype=np.float32)

        image = np.zeros((nx, ny), dtype=np.float32)
        pb = np.zeros((nx, ny), dtype=np.float32)
        image_pbcor = np.zeros((nx, ny), dtype=np.float32)

        refi = 1.0
        refj = 1.0
        inci = 0.5
        incj = 0.5
        majaxis = 2.0
        minaxis = 1.0
        pa = 0.0
        pbcor = False

        Restore2py(
            model,
            residual,
            image,
            size_x=nx,
            size_y=ny,
            refi=refi,
            refj=refj,
            inci=inci,
            incj=incj,
            majaxis=majaxis,
            minaxis=minaxis,
            pa=pa,
            pbcor=pbcor,
            pb=pb,
            image_pbcor=image_pbcor
        )

        # Define tolerance and expected values
        tol = 0.01
        gold_val_loc1 = 19.6208
        gold_val_loc2 = 28.8573

        # Assertions
        assert np.isclose(image[0][1], gold_val_loc1, atol=tol), f"Value at image[1][0] is {image[1][0]}, expected {gold_val_loc1}"
        assert np.isclose(image[0][2], gold_val_loc2, atol=tol), f"Value at image[0][1] is {image[0][1]}, expected {gold_val_loc2}"


    def test_restore2py_mfs_pbcor(self, restore_test_setup):        
        nx = 4000
        ny = 4000
        refi = 2000
        refj = 2000
        inci = 1.21203e-07
        incj = 1.21203e-07
        majaxis = 4.90554e-06
        minaxis = 4.67228e-06
        pa = 2.76764
        pbcor = True

        image_name = "unittest_hummbee_mfs_revE_restore"
        residual = getchunk(image_name, ImageType.RESIDUAL)
        model = getchunk(image_name, ImageType.MODEL)
        image = np.zeros((nx, ny), dtype=np.float32)
        pb = getchunk(image_name, ImageType.PB)
        image_pbcor = np.zeros((nx, ny), dtype=np.float32)


        Restore2py(
            model[:, :, 0, 0],
            residual[:, :, 0, 0],
            image,
            size_x=nx,
            size_y=ny,
            refi=refi,
            refj=refj,
            inci=inci,
            incj=incj,
            majaxis=majaxis,
            minaxis=minaxis,
            pa=pa,
            pbcor=pbcor,
            pb=pb,
            image_pbcor=image_pbcor
        )

        tol = 0.01
        im_gold_val_loc1 = 0.2126
        im_gold_val_loc2 = 0.07974
        assert abs(image[1072][1639] - im_gold_val_loc1) < tol
        assert abs(image[3072][2406] - im_gold_val_loc2) < tol
        
        impbcor_gold_val_loc1 = 0.580613
        impbcor_gold_val_loc2 = 0.30845
        assert abs(image_pbcor[1072][1639] - impbcor_gold_val_loc1) < tol
        assert abs(image_pbcor[3072][2406] - impbcor_gold_val_loc2) < tol
        
         
    # teardown_method removed - handled by fixture
    

        

if __name__ == '__main__':
    pytest.main([__file__])