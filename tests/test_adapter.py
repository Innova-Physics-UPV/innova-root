"""Pruebas del Python ORIGINAL con un doble de la API RF-Track.

No son simulaciones físicas ni validan RF-Track binario.
"""
import hashlib
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys
import unittest
from unittest.mock import patch
import numpy as np
from day06 import javier_adapter as adapter
from day06.rftrack_scan import scan, configuration
from innova.io import validate

ROOT = Path(__file__).resolve().parents[1]


def fake_rftrack():
    module = ModuleType('RF_Track')
    module.electronmass = .51099895
    module.clight = 299792458.
    module.ns = 299.792458
    module.C = 6.241509074e18
    module.UserField = type('UserField', (), {})
    class FieldMap:
        def __init__(self, *args): self.args = args
        def set_t0(self, value): self.t0 = value
        def set_phid(self, value): self.phid = value
    module.RF_FieldMap_1d_CINT = FieldMap
    module.TrackingOptions = type('TrackingOptions', (), {})
    class Bunch:
        def __init__(self, mass, population, charge, data):
            self.mass, self.population, self.charge = mass, population, charge
            self.data = np.asarray(data).copy()
        def __len__(self): return len(self.data)
        def __getitem__(self, index): return SimpleNamespace(mass=self.mass, Q=self.charge)
        def get_info(self):
            energy = np.sqrt(self.data[:, 5]**2+self.mass**2)-self.mass
            return SimpleNamespace(transmission=self.population, mean_K=energy.mean(), sigma_E=energy.std())
        def get_phase_space(self, fmt):
            names = ['%x', '%xp', '%y', '%yp', '%t', '%Pc']
            return self.data[:, [names.index(name) for name in fmt.split()]]
    module.Bunch6d = Bunch
    module.volumes = []
    class Volume:
        def __init__(self):
            self.calls = []
            module.volumes.append(self)
        def add(self, *args): self.calls.append(('add', args))
        def set_s0(self, value): self.calls.append(('s0', value))
        def set_s1(self, value): self.calls.append(('s1', value))
        def track(self, bunch, options):
            self.calls.append(('track', options))
            # Perder la mitad y mutar la población de entrada deliberadamente:
            # detecta si el adaptador usa el denominador después del tracking.
            initial = bunch.population
            bunch.population = initial/2
            return Bunch(bunch.mass, initial/2, bunch.charge, bunch.data[:len(bunch)//2])
    module.Volume = Volume
    return module


class JavierAdapterTests(unittest.TestCase):
    def setUp(self):
        adapter._functions = None
        adapter._injected_populations.clear()
        self.api = fake_rftrack()
        self.patcher = patch.dict(sys.modules, {'RF_Track': self.api})
        self.patcher.start()
    def tearDown(self):
        self.patcher.stop()
        adapter._functions = None
        adapter._injected_populations.clear()

    def test_originals_byte_hashes_and_notebook_syntax(self):
        records = json.loads((ROOT/'docs/ORIGINALS.json').read_text(encoding='utf-8'))
        for name, expected in records['files'].items():
            path = ROOT/'external/javier'/name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected['sha256'])
        notebook = json.loads((ROOT/'external/javier/Sweeps y Operaciones.ipynb').read_text(encoding='utf-8'))
        for i, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code':
                compile(''.join(cell['source']), f'original_notebook_cell_{i}', 'exec')

    def test_original_helpers_units_and_safe_margins(self):
        functions = adapter.original_functions()
        for A in (.08, .10, .12):
            config = adapter.configure(configuration(A))
            self.assertAlmostEqual(functions.beta_from_kinetic_energy(config['kinetic_energy_inj_MeV']), .4)
            cavity = adapter.StandingWaveCavity(config)
            self.assertTrue(functions.check_capture_margin(cavity, config['kinetic_energy_inj_MeV'])[0])
            self.assertAlmostEqual(functions.field_to_normalized_amplitude(cavity.E0, config['frequency']), A)
            options = adapter.safe_tracking_options(config)
            self.assertAlmostEqual(options.dt_mm, (1e9/config['frequency'])*self.api.ns/40)
            beam = adapter.build_dc_beam(config)
            self.assertEqual(len(beam), 20000)
            self.assertAlmostEqual(beam.get_info().transmission, .150/2856e6*self.api.C)
            data = beam.get_phase_space('%x %xp %y %yp %t %Pc')
            self.assertTrue(np.all(data[:, :4] == 0))
            self.assertTrue(np.all((data[:, 4] >= 0) & (data[:, 4] < (1e9/2856e6)*self.api.ns)))
            np.testing.assert_array_equal(data, adapter.build_dc_beam(config).data)

    def test_actual_adapter_original_functions_with_losses(self):
        sim, particles = scan(adapter)
        validate(sim, particles)
        np.testing.assert_allclose(sim['A'], [.08, .10, .12])
        np.testing.assert_array_equal(sim['n_macroparticles_injected'], [20000]*3)
        np.testing.assert_array_equal(sim['n_macroparticles_output'], [10000]*3)
        np.testing.assert_allclose(sim['transmission_fraction'], [.5]*3)
        self.assertEqual(len(particles['run_id']), 30000)
        self.assertEqual(adapter._injected_populations, {})
        for volume in self.api.volumes:
            self.assertEqual([call[0] for call in volume.calls], ['add', 's0', 's1', 'track'])
            self.assertEqual(volume.calls[0][1][1:], (0., 0., 0.))
            cavity = volume.calls[0][1][0]
            self.assertEqual(volume.calls[2][1], cavity.length_m)

    def test_notebook_configuration_rejected_by_margin(self):
        config = configuration(1.2)
        config.update(beta_inj=.3, number_of_cells=8)
        config = adapter.configure(config)
        beam = adapter.build_dc_beam(config)
        cavity = adapter.StandingWaveCavity(config)
        with self.assertRaisesRegex(RuntimeError, 'Margen de captura'):
            adapter.track_volume(beam, cavity, adapter.safe_tracking_options(config), config)
        self.assertEqual(self.api.volumes, [])
        self.assertEqual(adapter._injected_populations, {})


if __name__ == '__main__': unittest.main()
