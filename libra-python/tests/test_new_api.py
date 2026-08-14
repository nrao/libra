"""
Test the new API for LibRA package.

This test module verifies that the lazy loading and new API work correctly
for all LibRA modules.
"""
import pytest
import importlib
import sys
from pathlib import Path

# Ensure we import the installed package, not source
# Remove any paths that might point to source code
libra_source_paths = [
    str(Path(__file__).parent.parent),  # libra-python directory
    str(Path(__file__).parent.parent.parent)  # main libra directory
]

for path in libra_source_paths:
    if path in sys.path:
        sys.path.remove(path)

import libra


class TestNewAPI:
    """Test the new API functionality."""
    
    def test_new_api_imports(self):
        """Test that all new API functions can be imported."""
        new_functions = [
            'asp', 'hummbee', 'restore', 'coyote', 'dale', 
            'roadrunner', 'mssplit', 'subms', 'tableinfo', 
            'getchunk', 'acme'
        ]
        
        for func_name in new_functions:
            try:
                func = getattr(libra, func_name)
                assert callable(func), f"{func_name} should be callable"
                print(f"✅ {func_name} import succeeded: {type(func)}")
            except (ImportError, AttributeError) as e:
                pytest.fail(f"Failed to import {func_name}: {e}")
    
    def test_backwards_compatible_imports(self):
        """Test that backwards compatible module imports work.""" 
        module_names = [
            'asp2py', 'hummbee2py', 'restore2py', 'coyote2py', 
            'dale2py', 'roadrunner2py', 'mssplit2py', 'subms2py',
            'tableinfo2py', 'utilities2py', 'acme2py'
        ]
        
        for module_name in module_names:
            try:
                module = getattr(libra, module_name)
                assert hasattr(module, '__name__'), f"{module_name} should be a module"
                print(f"✅ {module_name} import succeeded: {type(module)}")
            except (ImportError, AttributeError) as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
    
    def test_utility_functions(self):
        """Test LibRA utility functions."""
        # Test version
        assert hasattr(libra, '__version__')
        assert isinstance(libra.__version__, str)
        
        # Test list function
        assert hasattr(libra, 'list_available_modules')
        assert callable(libra.list_available_modules)
        
        # Test path functions
        assert hasattr(libra, 'get_data_path')
        assert hasattr(libra, 'get_bin_path') 
        assert hasattr(libra, 'get_include_path')
        
        for func_name in ['get_data_path', 'get_bin_path', 'get_include_path']:
            func = getattr(libra, func_name)
            assert callable(func), f"{func_name} should be callable"
    
    def test_lazy_loading_caching(self):
        """Test that lazy loading properly caches modules."""
        # Import a module twice
        asp1 = libra.asp
        asp2 = libra.asp
        
        # Should be the same object (cached)
        assert asp1 is asp2, "Lazy loading should cache modules"
        
        # Check that the module is in the cache
        assert 'asp2py' in libra._loaded_modules
        
    def test_module_mapping(self):
        """Test that the module mapping is correct."""
        expected_mapping = {
            'asp': ('asp2py', 'asp'),
            'hummbee': ('hummbee2py', 'hummbee'),
            'restore': ('restore2py', 'restore'),
            'coyote': ('coyote2py', 'coyote'),
            'dale': ('dale2py', 'dale'),
            'roadrunner': ('roadrunner2py', 'roadrunner'),
            'mssplit': ('mssplit2py', 'mssplit'),
            'subms': ('subms2py', 'subms'),
            'tableinfo': ('tableinfo2py', 'tableinfo'),
            'getchunk': ('utilities2py', 'getchunk'),
            'acme': ('acme2py', 'acme'),
        }
        
        assert libra._CLASS_MAP == expected_mapping
    
    @pytest.mark.unit
    def test_error_handling(self):
        """Test error handling for invalid imports."""
        with pytest.raises(AttributeError):
            _ = libra.nonexistent_function
            
    def test_new_api_function_types(self):
        """Test that new API functions are the correct type."""
        # Test a few key functions
        asp_func = libra.asp
        assert callable(asp_func), "asp should be callable"
        
        roadrunner_func = libra.roadrunner  
        assert callable(roadrunner_func), "roadrunner should be callable"
        
        getchunk_func = libra.getchunk
        assert callable(getchunk_func), "getchunk should be callable"

    def test_both_apis_work_together(self):
        """Test that both new API and backwards compatible API work together."""
        # New API
        asp_new = libra.asp
        
        # Backwards compatible API  
        asp_module = libra.asp2py
        asp_old = asp_module.asp
        
        # Both should be the same function
        assert asp_new is asp_old, "New API and backwards compatible API should return the same function"