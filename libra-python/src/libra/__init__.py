"""
LibRA Python Package

Provides Python class interfaces for the LibRA radio astronomy toolkit.
Each app is exposed as a class with parameters set in __init__ and execution
triggered by calling .run(), which returns self for chaining.
"""

import sys
import os
from pathlib import Path

__version__ = "0.1.0"

_package_dir = Path(__file__).parent
sys.path.insert(0, str(_package_dir))

from .roadrunner import RoadRunner
from .hummbee import Hummbee
from .asp import Asp
from .dale import Dale
from .restore import Restore
from .coyote import Coyote
from .mssplit import MSSplit
from .subms import SubMS
from .tableinfo import TableInfo
from .utilities import GetChunk
from .acme import Acme

__all__ = [
    "RoadRunner",
    "Hummbee",
    "Asp",
    "Dale",
    "Restore",
    "Coyote",
    "MSSplit",
    "SubMS",
    "TableInfo",
    "GetChunk",
    "Acme",
    "get_data_path",
    "get_bin_path",
    "get_include_path",
    "__version__",
]


def get_data_path():
    data_dir = _package_dir / "_data"
    return data_dir if data_dir.exists() else None


def get_bin_path():
    bin_dir = _package_dir / "_bin"
    return bin_dir if bin_dir.exists() else None


def get_include_path():
    include_dir = _package_dir / "_include"
    return include_dir if include_dir.exists() else None
