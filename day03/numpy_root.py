"""Día 3: pasar columnas NumPy a RDataFrame y guardarlas."""
from pathlib import Path
import numpy as np
import ROOT

Path('data').mkdir(exist_ok=True)

# Cada array contiene una columna; sus posiciones representan las mismas filas.
x = np.array([0., 1., 2.])
y = np.array([0., -1., -2.])
energy = np.array([10., 11., 12.])
columns = {'x': x, 'y': y, 'energy': energy}

# RDataFrame permite expresar el análisis sin leer cada entrada manualmente.
df = ROOT.RDF.FromNumpy(columns)
print('Filas:', df.Count().GetValue())
print('Energía media:', df.Mean('energy').GetValue())

# Filter selecciona filas. Define añade una columna calculada.
selected = df.Filter('energy >= 11')
with_radius = selected.Define('r2', 'x*x + y*y')
print(with_radius.AsNumpy(['energy', 'r2']))

# Snapshot escribe las columnas en un TTree dentro de un archivo ROOT.
df.Snapshot('particles', 'data/day03_0.root')

# Segundo archivo pequeño: se usará en el ejemplo separado de TChain.
energy2 = np.array([13., 14., 15.])
df2 = ROOT.RDF.FromNumpy({'x': x, 'y': y, 'energy': energy2})
df2.Snapshot('particles', 'data/day03_1.root')
