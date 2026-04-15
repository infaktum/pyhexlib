"""Top-level pytest conftest to ensure `src/` is first on sys.path.

Pytest can modify sys.path during collection which may cause the
`tests/pyhexlib` package to shadow the real `pyhexlib` package in `src/pyhexlib`.
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
    # tests/pyhexlib shadowing src/pyhexlib. Move root to the end if present.
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
            f.write('\nfilesystem check for tests/pyhexlib and src/pyhexlib:\n')
            f.write(str(os.path.isdir(os.path.join(ROOT, 'tests', 'pyhexlib'))) + '\n')
            f.write(str(os.path.isdir(os.path.join(ROOT, 'src', 'pyhexlib'))) + '\n')
            # Try to import the top-level package and log which package is found
            try:
                import importlib

                pkg = importlib.import_module('pyhexlib')
                f.write('\nimport pyhexlib -> ' + repr(getattr(pkg, '__file__', None)) + '\n')
                f.write('pyhexlib.__path__ = ' + repr(getattr(pkg, '__path__', None)) + '\n')
            except Exception as e:
                f.write('\nimport pyhexlib failed: ' + repr(e) + '\n')
    except Exception:
        pass

# If the tests are organized under `tests/pyhexlib` (which makes a package named
# `pyhexlib`), pytest will try to import test modules as `pyhexlib.test_*`. To make
# those imports resolve while still using the real package in `src/pyhexlib`, we
# append the `tests/pyhexlib` directory to the real package's __path__ so Python
# will search both locations for submodules named `pyhexlib.*`.
try:
    import importlib

    pkg = importlib.import_module('pyhexlib')
    tests_pkg = os.path.join(ROOT, 'tests', 'pyhexlib')
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
