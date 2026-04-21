"""Test package placeholder that delegates imports to the implementation.

We keep a tiny __init__ that sets the package __path__ to the real
implementation directory in ``src/pyhexlib``. This avoids shadowing the
implementation while allowing tests to remain in ``tests/pyhexlib``.
"""
import os

# Compute project root relative to this file and point the package to the
# implementation directory so imports like `import pyhexlib.basic` resolve to
# files under src/pyhexlib.
HERE = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC_PKG_DIR = os.path.join(PROJECT_ROOT, 'src', 'pyhexlib')

__path__ = [SRC_PKG_DIR]
