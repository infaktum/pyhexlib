#  MIT License
#
#  Copyright (c) 2026 Heiko Sippel
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
#


"""Test-package shim: when pytest imports the test package named `pyhex`
it would shadow the real `pyhex` package in `src/`. To make the tests
work without renaming directories, load the real modules from `src/pyhex`
and inject them into sys.modules under the names `pyhex.*`.

This keeps the test package present but delegates module imports to the
implementation in `src/pyhex`.
"""
import importlib.util
import os
import sys

# Determine project root and src/pyhex path relative to this file
HERE = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC_PKG_DIR = os.path.join(PROJECT_ROOT, 'src', 'pyhex')

_modules = ['book', 'epub', 'markdown', '__init__']
for mod in _modules:
    path = os.path.join(SRC_PKG_DIR, f"{mod}.py")
    if not os.path.isfile(path):
        continue
    fullname = f"pyhex.{mod}" if mod != '__init__' else 'pyhex'
    if fullname in sys.modules:
        # already loaded
        continue
    spec = importlib.util.spec_from_file_location(fullname, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[fullname] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        # if loading fails, remove partial module to avoid confusing state
        sys.modules.pop(fullname, None)
        raise
    # Also make the submodule available as attribute of this package
    if fullname != 'pyhex':
        setattr(sys.modules.setdefault('pyhex', sys.modules.get(fullname)), mod, module)
