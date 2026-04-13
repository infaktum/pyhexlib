"""Top-level pytest conftest to ensure `src/` is first on sys.path.

Pytest can modify sys.path during collection which may cause the
`tests/pyhex` package to shadow the real `pyhex` package in `src/pyhex`.
Putting `src` at the front as early as possible prevents that.
"""
import os
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')

if os.path.isdir(SRC):
    # Remove any existing occurrences and insert at position 0
    while SRC in sys.path:
        sys.path.remove(SRC)
    sys.path.insert(0, SRC)

    # Ensure project root is not before src on sys.path to avoid
    # tests/pyhex shadowing src/pyhex. Move root to the end if present.
    if ROOT in sys.path:
        try:
            sys.path.remove(ROOT)
        except ValueError:
            pass
    sys.path.append(ROOT)

    # Write a small debug file so we can inspect sys.path and detect
    # whether the tests package is accidentally shadowing the real package.
    try:
        with open(os.path.join(ROOT, 'conftest_sys_path.log'), 'w', encoding='utf-8') as f:
            f.write('sys.path[:8]\n')
            for p in sys.path[:8]:
                f.write(f"{p}\n")
            f.write('\nfilesystem check for tests/pyhex and src/pyhex:\n')
            f.write(str(os.path.isdir(os.path.join(ROOT, 'tests', 'pyhex'))) + '\n')
            f.write(str(os.path.isdir(os.path.join(ROOT, 'src', 'pyhex'))) + '\n')
            # Try to import the top-level package and log which package is found
            try:
                import importlib
                pkg = importlib.import_module('pyhex')
                f.write('\nimport pyhex -> ' + repr(getattr(pkg, '__file__', None)) + '\n')
                f.write('pyhex.__path__ = ' + repr(getattr(pkg, '__path__', None)) + '\n')
            except Exception as e:
                f.write('\nimport pyhex failed: ' + repr(e) + '\n')
    except Exception:
        pass

# If the tests are organized under `tests/pyhex` (which makes a package named
# `pyhex`), pytest will try to import test modules as `pyhex.test_*`. To make
# those imports resolve while still using the real package in `src/pyhex`, we
# append the `tests/pyhex` directory to the real package's __path__ so Python
# will search both locations for submodules named `pyhex.*`.
try:
    import importlib
    pkg = importlib.import_module('pyhex')
    tests_pkg = os.path.join(ROOT, 'tests', 'pyhex')
    if os.path.isdir(tests_pkg):
        # only append if not already present
        for p in pkg.__path__:
            if os.path.abspath(p) == os.path.abspath(tests_pkg):
                break
        else:
            pkg.__path__.append(tests_pkg)
except Exception:
    # don't fail test startup for this auxiliary action
    pass

