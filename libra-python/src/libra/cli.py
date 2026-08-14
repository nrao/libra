"""
Command-line entry points for LibRA apps.
Each *_main function delegates to the underlying C++ binding via the class API,
passing all arguments through parafeed-style keyword args read from argv.
For interactive parameter sessions, invoke the underlying binary in _bin/.
"""

import sys


def _run_binary(name):
    """Exec the bundled LibRA binary, falling back to PATH."""
    import os
    from pathlib import Path
    bin_dir = Path(__file__).parent / "_bin"
    binary = bin_dir / name
    if not binary.exists():
        binary = name  # fall back to PATH
    os.execv(str(binary), [str(binary)] + sys.argv[1:])


def roadrunner_main():
    _run_binary("roadrunner")

def hummbee_main():
    _run_binary("hummbee")

def asp_main():
    _run_binary("asp")

def dale_main():
    _run_binary("dale")

def restore_main():
    _run_binary("restore")

def coyote_main():
    _run_binary("coyote")

def mssplit_main():
    _run_binary("mssplit")

def subms_main():
    _run_binary("subms")

def tableinfo_main():
    _run_binary("tableinfo")

def acme_main():
    _run_binary("acme")
