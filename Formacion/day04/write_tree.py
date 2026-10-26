"""Día 4: escribir un TTree con uproot, sin importar ROOT."""
from pathlib import Path
import numpy as np
import uproot

Path('data').mkdir(exist_ok=True)
x = np.array([0., 1., 2., 3., 4.])
y = np.array([0., -1., -2., -3., -4.])
energy = np.array([10., 11., 12., 13., 14.])
columns = {'x': x, 'y': y, 'energy': energy}

with uproot.recreate('data/day04_tree.root') as file:
    # mktree define las ramas y sus tipos; todavía no hay filas.
    tree = file.mktree('particles', {'x': 'float64', 'y': 'float64', 'energy': 'float64'})
    # extend añade las cinco filas de las columnas.
    tree.extend(columns)
print('TTree guardado en data/day04_tree.root')
