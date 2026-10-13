"""Día 6: RF-Track real -> NumPy -> dos TTree con uproot.

Ejecutar desde la raíz: python -m day06.rftrack_scan
Las funciones físicas son las originales de Javier, sin adaptador intermedio.
"""
from pathlib import Path
import numpy as np
import uproot
import RF_Track as rft
from external.javier.Funciones import (
    kinetic_energy_from_beta, build_dc_beam, StandingWaveCavity,
    safe_tracking_options, check_capture_margin, beam_properties,
)

Path('data').mkdir(exist_ok=True)

# 1. Parámetros del PDF: en el notebook recibido hay otros valores.
frequency = 2856e6       # Hz.
beta_inj = 0.4
kinetic_energy = kinetic_energy_from_beta(beta_inj)  # Electrones, MeV.
current = 0.150         # A (150 mA).
n_macroparticles = 20000
beta_ph = 0.5
amplitudes = [0.08, 0.10, 0.12]  # A es amplitud adimensional, no corriente.
phase_advance = 2*np.pi/3       # Radianes.
number_of_cells = 5
seed = 42

simulation_rows = []
particle_blocks = []

# 2. Ejecutar una simulación por amplitud. enumerate da run_id 0, 1 y 2.
for run_id, A in enumerate(amplitudes):
    beam_in = build_dc_beam(
        frequency=frequency, kinetic_energy_MeV=kinetic_energy,
        current_A=current, n_macroparticles=n_macroparticles, seed=seed,
    )
    # Población FÍSICA inicial: no confundir con 20000 macropartículas.
    # Se captura antes del tracking por si este modifica el haz de entrada.
    n_injected = float(beam_in.get_info().transmission)

    cavity = StandingWaveCavity(
        frequency, beta_ph=beta_ph, A=A,
        phase_advance=phase_advance, number_of_cells=number_of_cells,
    )
    # Mismo control que el selftest original de Funciones.py.
    margin_ok, _, _ = check_capture_margin(cavity, kinetic_energy)
    if not margin_ok:
        raise RuntimeError('Margen de captura insuficiente: no se ejecuta el tracking')

    volume = rft.Volume()
    volume.add(cavity, 0., 0., 0.)
    volume.set_s0(0.)
    volume.set_s1(cavity.length_m)
    options = safe_tracking_options(frequency)
    beam_out = volume.track(beam_in, options)

    # 3. Extraer una matriz: una fila por macropartícula, seis columnas.
    data = np.asarray(beam_out.get_phase_space('%x %xp %y %yp %t %Pc'))
    # x/y: mm; xp/yp: mrad; t: unidad interna mm/c; Pc: MeV/c.
    properties = beam_properties(beam_out, n_injected=n_injected, frequency=frequency)
    simulation_rows.append({
        'run_id': run_id, 'frequency': frequency, 'beta_inj': beta_inj,
        'kinetic_energy_inj_MeV': kinetic_energy, 'current_A': current,
        'n_macroparticles_injected': n_macroparticles, 'beta_ph': beta_ph,
        'A': A, 'phase_advance': phase_advance,
        'number_of_cells': number_of_cells, 'seed': seed,
        'n_macroparticles_output': len(data),
        'mean_kinetic_energy_MeV': properties['mean_kinetic_energy_MeV'],
        'peak_kinetic_energy_MeV': properties['peak_kinetic_energy_MeV'],
        'min_kinetic_energy_MeV': properties['min_kinetic_energy_MeV'],
        'energy_spread_rms_MeV': properties['energy_spread_rms_MeV'],
        'energy_spread_fwhm_MeV': properties['energy_spread_fwhm_MeV'],
        'phase_spread_rms_deg': properties['phase_spread_rms_deg'],
        'real_particles_remaining': properties['real_particles_remaining'],
        'transmission_fraction': properties['transmission_fraction'],
    })
    particle_blocks.append({
        'run_id': np.full(len(data), run_id, dtype=np.int64),
        'x': data[:, 0], 'xp': data[:, 1], 'y': data[:, 2],
        'yp': data[:, 3], 't': data[:, 4], 'Pc': data[:, 5],
    })
    print('run_id:', run_id, 'A:', A, 'partículas:', len(data),
          'energía media (MeV):', properties['mean_kinetic_energy_MeV'])

# 4. Pasar los resúmenes a columnas y reunir los bloques de partículas.
integer_fields = ['run_id', 'n_macroparticles_injected',
                  'n_macroparticles_output', 'number_of_cells', 'seed']
simulations = {}
for name in simulation_rows[0]:
    values = [row[name] for row in simulation_rows]
    dtype = np.int64 if name in integer_fields else np.float64
    simulations[name] = np.array(values, dtype=dtype)
particles = {}
for name in particle_blocks[0]:
    particles[name] = np.concatenate([block[name] for block in particle_blocks])

# Un resultado indefinido necesita revisión antes de guardar el resumen.
for values in simulations.values():
    if not np.all(np.isfinite(values)):
        raise ValueError('Una métrica del haz no es finita; revisar la simulación')

# 5. Guardar los dos TTree. Este bloque es el mismo que aprendimos en día 5.
with uproot.recreate('data/rftrack_amplitude_scan.root') as file:
    for name, columns in [('simulations', simulations), ('particles', particles)]:
        types = {column: values.dtype for column, values in columns.items()}
        tree = file.mktree(name, types)
        tree.extend(columns)
print('Guardado: data/rftrack_amplitude_scan.root')

# Opcional: registro de versiones y hashes. No interviene en la simulación.
import hashlib
import json
from importlib.metadata import version, PackageNotFoundError
try:
    rftrack_version = version('RF-Track')
except PackageNotFoundError:
    rftrack_version = 'no disponible'
original_dir = Path(__file__).resolve().parents[1] / 'external' / 'javier'
hashes = {}
for name in ['Funciones.py', 'Sweeps y Operaciones.ipynb']:
    hashes[name] = hashlib.sha256((original_dir/name).read_bytes()).hexdigest()
record = {'source': 'RF-Track: llamadas directas a Javier',
          'rftrack_version': rftrack_version, 'originals_sha256': hashes,
          'simulations': len(simulations['run_id']), 'particles': len(particles['run_id'])}
Path('data/rftrack_amplitude_scan.provenance.json').write_text(json.dumps(record, indent=2))
