"""Mismas pruebas con lector local de uproot, sin su bucle de sockets fsspec."""
import sys
from pathlib import Path
import unittest
import uproot
import uproot.source.file

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
uproot.open.defaults['handler'] = uproot.source.file.MultithreadedFileSource
suite = unittest.defaultTestLoader.discover(str(root/'tests'))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
