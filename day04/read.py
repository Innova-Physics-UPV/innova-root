"""Día 4: abrir un archivo, consultar sus objetos y recuperar columnas."""
import uproot

with uproot.open('data/day04_tree.root') as file:
    print('Objetos:', file.keys())
    tree = file['particles']
    print('Tipo:', tree.classname)
    print('Ramas:', tree.keys())
    columns = tree.arrays(library='np')
    print('Energías:', columns['energy'])
    print('Energía media:', columns['energy'].mean())

# El mismo acceso permite leer el RNTuple; verificar también su tipo.
with uproot.open('data/day04_ntuple.root') as file:
    ntuple = file['particles']
    print('Tipo:', ntuple.classname)
    print('Energías:', ntuple.arrays(library='np')['energy'])
