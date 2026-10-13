import importlib.util
import tempfile
import unittest
from pathlib import Path
import numpy as np
from innova.io import validate, save_results
from day05.simulated_scan import scan
from day06.rftrack_scan import configuration, load_adapter, scan as real_scan, METRICS

HAS_UPROOT = importlib.util.find_spec('uproot') is not None
HAS_ROOT = importlib.util.find_spec('ROOT') is not None

class PipelineTests(unittest.TestCase):
    def test_simulated_schema_and_summary(self):
        sim, parts = scan()
        validate(sim, parts)
        self.assertEqual(len(sim['run_id']), 6)
        self.assertEqual(len(parts['run_id']), 600)
        for i in range(6):
            mask = parts['run_id'] == i
            self.assertEqual(mask.sum(), 100)
            self.assertAlmostEqual(parts['energy'][mask].mean(), sim['mean_energy'][i])
            self.assertAlmostEqual(parts['energy'][mask].std(), sim['sigma_energy'][i])
        again = scan()
        for key in parts:
            np.testing.assert_array_equal(parts[key], again[1][key])

    def test_invalid_relations(self):
        sim, parts = scan()
        bad = dict(parts, run_id=parts['run_id']+100)
        with self.assertRaises(ValueError): validate(sim, bad)
        bad_sim = dict(sim, run_id=np.zeros(6, dtype=np.int64))
        with self.assertRaises(ValueError): validate(bad_sim, parts)
        with self.assertRaises(ValueError): validate(sim, dict(parts, x=parts['x'][:-1]))
        with self.assertRaises(ValueError): validate(sim, dict(parts, x=np.full(600, np.nan)))

    def test_external_dependency_fails_explicitly(self):
        with self.assertRaises(FileNotFoundError): load_adapter('missing_javier_adapter.py')

    def test_rftrack_contract_with_test_double(self):
        # Doble deliberado de prueba: NO ejecuta RF-Track y NO afirma validar física.
        calls = []
        class Bunch:
            def get_phase_space(self, fmt):
                self.asserted_format = fmt
                return np.zeros((20000, 6))
        class Adapter:
            def build_dc_beam(self, config):
                calls.append(config)
                return Bunch()
            def StandingWaveCavity(self, config): return object()
            def safe_tracking_options(self, config): return object()
            def track_volume(self, beam, cavity, options, config): return Bunch()
            def beam_properties(self, out, initial, config):
                return {k: 1.0 for k in METRICS}
        sim, parts = real_scan(Adapter())
        validate(sim, parts)
        np.testing.assert_array_equal(sim['A'], [.08, .10, .12])
        self.assertEqual(len(parts['run_id']), 60000)
        self.assertEqual([c['n_macroparticles_injected'] for c in calls], [20000]*3)
        self.assertAlmostEqual(configuration(.1)['kinetic_energy_inj_MeV'], .04655, places=5)

    @unittest.skipUnless(HAS_UPROOT, 'uproot no instalado')
    def test_uproot_roundtrip_and_join(self):
        import uproot
        sim, parts = scan()
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp)/'scan.root'
            save_results(file, sim, parts)
            with uproot.open(file) as f:
                self.assertEqual(f['simulations'].classname, 'TTree')
                self.assertEqual(f['particles'].classname, 'TTree')
                s = f['simulations'].arrays(library='np')
                p = f['particles'].arrays(library='np')
                for table, recovered in [(sim, s), (parts, p)]:
                    for key in table: np.testing.assert_array_equal(table[key], recovered[key])
                ids = s['run_id'][(s['gradient']==11)&(s['phase']==20)]
                self.assertEqual(len(ids), 1)
                self.assertEqual((p['run_id']==ids[0]).sum(), 100)

    @unittest.skipUnless(HAS_UPROOT, 'uproot no instalado')
    def test_tree_ntuple_and_blocks(self):
        from day04.uproot_io import main
        with tempfile.TemporaryDirectory() as tmp: main(tmp)

    @unittest.skipUnless(HAS_ROOT and HAS_UPROOT, 'ROOT/PyROOT o uproot no instalado')
    def test_root_interoperability(self):
        import ROOT
        sim, parts = scan()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'test.root'
            save_results(path, sim, parts)
            self.assertEqual(ROOT.RDataFrame('particles', str(path)).Count().GetValue(), 600)

if __name__ == '__main__': unittest.main()
