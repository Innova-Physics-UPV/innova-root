"""Comprobar resultados de los ejemplos. No hace falta leer tests para aprender."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import uproot
from rftrack_double import fake_rftrack

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
HAS_ROOT = importlib.util.find_spec('ROOT') is not None

class ExampleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.previous = Path.cwd()
        os.chdir(self.tmp.name)
    def tearDown(self):
        os.chdir(self.previous)
        self.tmp.cleanup()
    def execute(self, path):
        with contextlib.redirect_stdout(io.StringIO()):
            return runpy.run_path(str(PROJECT/path))

    def test_day04_tree_and_ntuple(self):
        self.execute('day04/write_tree.py')
        self.execute('day04/write_ntuple.py')
        for path, classname in [('data/day04_tree.root', 'TTree'),
                                ('data/day04_ntuple.root', 'ROOT::RNTuple')]:
            with uproot.open(path) as f:
                tree = f['particles']
                self.assertEqual(tree.classname, classname)
                self.assertEqual(tree.num_entries, 5)
                np.testing.assert_array_equal(tree.arrays(library='np')['energy'], [10,11,12,13,14])
        self.execute('day04/read.py')

    def test_day04_concatenate_iterate(self):
        self.execute('day04/write_tree.py')
        result = self.execute('day04/multiple_files.py')
        np.testing.assert_array_equal(result['columns']['energy'], [10,11,12,13,14,15,16])
        blocks = list(uproot.iterate(result['files'], step_size=2, library='np'))
        self.assertEqual([len(b['energy']) for b in blocks], [2,2,1,2])

    def test_day05_summary_relation_and_roundtrip(self):
        result = self.execute('day05/simulated_scan.py')
        sim, part = result['sim'], result['part']
        self.assertEqual(len(sim['run_id']), 6)
        self.assertEqual(len(part['run_id']), 600)
        self.assertEqual(len(np.unique(sim['run_id'])), 6)
        self.assertTrue(np.all(np.isin(part['run_id'], sim['run_id'])))
        for i in range(6):
            energies = part['energy'][part['run_id'] == i]
            self.assertEqual(len(energies), 100)
            self.assertAlmostEqual(energies.mean(), sim['mean_energy'][i])
            self.assertAlmostEqual(energies.std(), sim['sigma_energy'][i])
        self.assertEqual(len(result['energies']), 100)
        again = self.execute('day05/simulated_scan.py')
        np.testing.assert_array_equal(part['energy'], again['part']['energy'])

    def test_day06_original_calls_population_and_losses(self):
        # Ejecuta el script nuevo con el Python ORIGINAL y un doble de RF-Track.
        # Las pérdidas del 50% son artificiales: NO verifican física.
        api = fake_rftrack()
        with patch.dict(sys.modules, {'RF_Track': api}):
            result = self.execute('day06/rftrack_scan.py')
        with uproot.open('data/rftrack_amplitude_scan.root') as file:
            sim = file['simulations'].arrays(library='np')
            part = file['particles'].arrays(library='np')
        np.testing.assert_array_equal(sim['A'], [.08, .10, .12])
        np.testing.assert_array_equal(sim['n_macroparticles_injected'], [20000]*3)
        np.testing.assert_array_equal(sim['n_macroparticles_output'], [10000]*3)
        np.testing.assert_allclose(sim['transmission_fraction'], [.5]*3)
        self.assertEqual(len(part['run_id']), 30000)
        self.assertAlmostEqual(result['kinetic_energy'], .04655, places=5)
        for i, volume in enumerate(api.volumes):
            self.assertEqual([c[0] for c in volume.calls], ['add','s0','s1','track'])
            cavity = volume.calls[0][1][0]
            self.assertEqual(cavity.A, [.08,.10,.12][i])
            self.assertEqual(cavity.number_of_cells, 5)
            self.assertEqual(volume.calls[2][1], cavity.length_m)
            self.assertAlmostEqual(volume.calls[3][1].dt_mm, (1e9/2856e6)*api.ns/40)
        for name, expected in json.loads((PROJECT/'docs/ORIGINALS.json').read_text())['files'].items():
            self.assertEqual(result['record']['originals_sha256'][name], expected['sha256'])

    def test_original_hashes_and_notebook_syntax(self):
        records = json.loads((PROJECT/'docs/ORIGINALS.json').read_text())
        for name, expected in records['files'].items():
            self.assertEqual(hashlib.sha256((PROJECT/'external/javier'/name).read_bytes()).hexdigest(), expected['sha256'])
        notebook = json.loads((PROJECT/'external/javier/Sweeps y Operaciones.ipynb').read_text(encoding='utf-8'))
        for i, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code': compile(''.join(cell['source']), str(i), 'exec')

    def test_original_units_seed_and_notebook_margin(self):
        api = fake_rftrack()
        with patch.dict(sys.modules, {'RF_Track': api}):
            from external.javier import Funciones as functions
            energy = functions.kinetic_energy_from_beta(.4)
            self.assertAlmostEqual(functions.beta_from_kinetic_energy(energy), .4)
            beam = functions.build_dc_beam(2856e6, energy, .150, 20000, seed=42)
            again = functions.build_dc_beam(2856e6, energy, .150, 20000, seed=42)
            np.testing.assert_array_equal(beam.data, again.data)
            self.assertAlmostEqual(beam.get_info().transmission, .150/2856e6*api.C)
            for A in (.08,.10,.12):
                cavity = functions.StandingWaveCavity(2856e6, .5, A=A, number_of_cells=5)
                self.assertTrue(functions.check_capture_margin(cavity, energy)[0])
                self.assertAlmostEqual(functions.field_to_normalized_amplitude(cavity.E0,2856e6), A)
            cavity = functions.StandingWaveCavity(2856e6, .5, A=1.2, number_of_cells=8)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertFalse(functions.check_capture_margin(cavity, functions.kinetic_energy_from_beta(.3))[0])

    @unittest.skipUnless(HAS_ROOT, 'PyROOT no instalado')
    def test_days02_03_root(self):
        self.execute('day02/trees.py')
        with uproot.open('data/day02.root') as file:
            np.testing.assert_array_equal(file['particles'].arrays(library='np')['energy'], [10,11,12,13,14])
        result = self.execute('day03/numpy_root.py')
        self.assertEqual(result['df'].Count().GetValue(), 3)
        self.assertEqual(result['selected'].Count().GetValue(), 2)
        chain = self.execute('day03/chain.py')['chain']
        self.assertEqual(chain.GetEntries(), 6)

    @unittest.skipUnless(HAS_ROOT, 'PyROOT no instalado')
    def test_day07_root_analysis_structure(self):
        with patch.dict(sys.modules, {'RF_Track': fake_rftrack()}):
            self.execute('day06/rftrack_scan.py')
        result = self.execute('day07/analyze.py')
        self.assertEqual(result['simulations'].Count().GetValue(), 3)
        self.assertEqual(result['selected'].Count().GetValue(), 2)
        self.assertEqual(result['particles'].Count().GetValue(), 30000)

if __name__ == '__main__': unittest.main()
