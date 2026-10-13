"""PDF §6.5 y §6.7-6.10: NumPy -> RDF -> Snapshot -> TChain."""
from pathlib import Path
import numpy as np
import ROOT

def save_phase_space(data, output):
    data = np.asarray(data, dtype=np.float64)
    if data.ndim != 2 or data.shape[1] != 3:
        raise ValueError('Se espera una matriz N x 3: x, y, energy')
    columns = {name: np.ascontiguousarray(data[:, i])
               for i, name in enumerate(('x', 'y', 'energy'))}
    df = ROOT.RDF.FromNumpy(columns)
    print('Entradas:', df.Count().GetValue(), 'Media:', df.Mean('energy').GetValue())
    df.Snapshot('particles', str(output))

def main():
    Path('data').mkdir(exist_ok=True)
    for i in range(2):
        save_phase_space(np.array([[1, 2, 10+i], [3, 4, 12+i]]), f'data/day03_{i}.root')
    chain = ROOT.TChain('particles')
    for i in range(2):
        if chain.Add(f'data/day03_{i}.root') != 1:
            raise OSError('No se añadió el archivo')
    df = ROOT.RDataFrame(chain)
    assert df.Count().GetValue() == 4
    print(df.Define('r2', 'x*x+y*y').Filter('energy >= 11').AsNumpy())

if __name__ == '__main__':
    main()
