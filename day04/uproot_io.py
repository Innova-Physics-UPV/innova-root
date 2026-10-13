"""PDF §7: formatos explícitos y lectura por bloques."""
from pathlib import Path
import numpy as np
import uproot

def main(output_dir='data'):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    data = {'x': np.arange(5, dtype=np.float64),
            'y': -np.arange(5, dtype=np.float64),
            'energy': np.arange(10, 15, dtype=np.float64)}
    tree_file = output / 'day04_tree.root'
    ntuple_file = output / 'day04_ntuple.root'
    with uproot.recreate(tree_file) as f:
        tree = f.mktree('particles', {k: v.dtype for k, v in data.items()})
        tree.extend(data)
    with uproot.recreate(ntuple_file) as f:
        # Equivalente explícito a la asignación del PDF; evita defaults de versión.
        f.mkrntuple('particles', data)
    for path, expected in [(tree_file, 'TTree'), (ntuple_file, 'ROOT::RNTuple')]:
        with uproot.open(path) as f:
            obj = f['particles']
            assert obj.classname == expected, obj.classname
            arrays = obj.arrays(library='np')
            for name in data:
                np.testing.assert_array_equal(arrays[name], data[name])
            print(path.name, obj.classname, obj.num_entries)
    files = [str(tree_file)+':particles', str(tree_file)+':particles']
    all_data = uproot.concatenate(files, library='np')
    assert len(all_data['x']) == 10
    blocks = list(uproot.iterate(files, library='np', step_size=2))
    assert [len(b['x']) for b in blocks] == [2, 2, 1, 2, 2, 1]
    print('concatenate:', len(all_data['x']), 'iterate:', [len(b['x']) for b in blocks])

if __name__ == '__main__':
    main()
