"""Día 4: guardar los mismos datos como RNTuple."""
from pathlib import Path
import numpy as np
import uproot

Path('data').mkdir(exist_ok=True)
columns = {
    'x': np.array([0., 1., 2., 3., 4.]),
    'y': np.array([0., -1., -2., -3., -4.]),
    'energy': np.array([10., 11., 12., 13., 14.]),
}
with uproot.recreate('data/day04_ntuple.root') as file:
    # RNTuple es otro formato columnar de ROOT. Lo elegimos explícitamente.
    # En el PDF se usó asignación directa; mkrntuple deja claro el formato.
    file.mkrntuple('particles', columns)
print('RNTuple guardado en data/day04_ntuple.root')
