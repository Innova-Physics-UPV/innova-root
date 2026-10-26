"""Día 4: reunir archivos o leerlos por bloques."""
import numpy as np
import uproot

# Creamos otro archivo con el mismo nombre de árbol y las mismas ramas.
with uproot.recreate('data/day04_second.root') as file:
    tree = file.mktree('particles', {'x': 'float64', 'y': 'float64', 'energy': 'float64'})
    tree.extend({'x': np.array([5., 6.]), 'y': np.array([-5., -6.]),
                 'energy': np.array([15., 16.])})

# La parte después de ':' identifica el árbol dentro de cada archivo.
files = ['data/day04_tree.root:particles', 'data/day04_second.root:particles']

# concatenate carga todos los datos juntos en memoria: 5 + 2 = 7 filas.
columns = uproot.concatenate(files, library='np')
print('Todas las energías:', columns['energy'])

# iterate entrega un bloque cada vez. step_size=2 significa dos filas por bloque.
for block in uproot.iterate(files, library='np', step_size=2):
    print('Bloque:', block['energy'])
