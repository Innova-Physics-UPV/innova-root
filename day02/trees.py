"""Día 2: guardar cinco filas y volver a leerlas con PyROOT."""
from pathlib import Path
from array import array
import ROOT

Path('data').mkdir(exist_ok=True)

# 1. TFile es el archivo. RECREATE crea uno nuevo o reemplaza el existente.
file = ROOT.TFile('data/day02.root', 'RECREATE')
if file.IsZombie():
    raise OSError('No se puede crear data/day02.root')

# 2. TTree es una tabla. Cada Branch es una columna.
tree = ROOT.TTree('particles', 'Cinco partículas de ejemplo')
# ROOT necesita variables cuya dirección de memoria pueda recordar.
# Un array de un elemento sirve como variable numérica modificable.
x = array('d', [0.0])
y = array('d', [0.0])
energy = array('d', [0.0])
tree.Branch('x', x, 'x/D')  # /D significa double (float de 64 bits).
tree.Branch('y', y, 'y/D')
tree.Branch('energy', energy, 'energy/D')

# 3. Cambiamos las variables; Fill copia sus valores en una nueva fila.
for i in range(5):
    x[0] = i
    y[0] = -i
    energy[0] = 10 + i
    tree.Fill()

# 4. Write guarda el árbol; Close cierra el archivo.
tree.Write()
file.Close()

# 5. READ abre el archivo existente sin reemplazarlo.
file = ROOT.TFile.Open('data/day02.root', 'READ')
tree = file.Get('particles')
print('Número de filas:', tree.GetEntries())

# PyROOT permite recorrer las entradas y acceder a las ramas por su nombre.
for particle in tree:
    print(particle.x, particle.y, particle.energy)
file.Close()
