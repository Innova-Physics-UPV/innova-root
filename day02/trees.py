"""Equivalente PyROOT; buffers vivos hasta terminar la lectura."""
from array import array
from pathlib import Path
import ROOT

def main():
    Path('data').mkdir(exist_ok=True)
    buffers = {k: array('d', [0.]) for k in ('x', 'y', 'energy')}
    f = ROOT.TFile('data/day02.root', 'RECREATE')
    if f.IsZombie():
        raise OSError('No se puede crear el archivo')
    tree = ROOT.TTree('particles', 'Ejemplo')
    for k, v in buffers.items():
        tree.Branch(k, v, k + '/D')
    for i in range(5):
        buffers['x'][0], buffers['y'][0], buffers['energy'][0] = i, -i, 10+i
        tree.Fill()
    tree.Write()
    f.Close()
    f = ROOT.TFile.Open('data/day02.root')
    if not f or f.IsZombie():
        raise OSError('No se puede leer el archivo')
    tree = f.Get('particles')
    if not tree:
        raise ValueError('Falta particles')
    for k, v in buffers.items():
        if tree.SetBranchAddress(k, v) < 0:
            raise ValueError('Rama incompatible: ' + k)
    assert tree.GetEntries() == 5
    for i in range(tree.GetEntries()):
        if tree.GetEntry(i) <= 0:
            raise OSError('Error de entrada')
        print({k: v[0] for k, v in buffers.items()})
    tree.ResetBranchAddresses()
    f.Close()

if __name__ == '__main__':
    main()
