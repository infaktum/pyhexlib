"""Top-level pytest conftest - ensure `src/` is first on sys.path.

This minimal top-level file ensures the project's `src` directory is inserted
at the front of ``sys.path`` early so imports performed during test collection
and package ``__init__`` execution find the implementation in ``src/pyhexlib``.
"""
import os
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')

if os.path.isdir(SRC) and SRC not in sys.path:
	# Insert at position 0 so imports prefer the source package over any
	# similarly named test packages.
	sys.path.insert(0, SRC)

# If tests live under `tests/pyhexlib`, make those test modules importable as
# submodules of the real `pyhexlib` package by appending the tests path to the
# implementation package's __path__. This reproduces the previous behavior but
# does so after ensuring the real package is importable from src/.
try:
	import importlib

	pkg = importlib.import_module('pyhexlib')
	tests_pkg = os.path.join(ROOT, 'tests', 'pyhexlib')
	if os.path.isdir(tests_pkg):
		existing = [os.path.abspath(p) for p in getattr(pkg, '__path__', [])]
		if os.path.abspath(tests_pkg) not in existing:
			pkg.__path__.append(tests_pkg)
except Exception:
	# don't fail test startup for this auxiliary action
	pass

