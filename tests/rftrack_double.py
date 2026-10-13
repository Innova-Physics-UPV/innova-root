"""Doble de API para tests: NO simulación física."""
from types import ModuleType, SimpleNamespace
import numpy as np

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


