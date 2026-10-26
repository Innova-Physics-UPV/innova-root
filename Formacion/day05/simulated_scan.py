"""Día 5: barrido ficticio para entender simulations, particles y run_id.

La fórmula y los parámetros son ejemplos nuevos, NO un modelo de RF-Track.
"""
from pathlib import Path
import numpy as np
import uproot

Path('data').mkdir(exist_ok=True)
gradients = [10., 11., 12.]
phases = [0., 20.]
n_particles = 100
rng = np.random.default_rng(42)

# Una lista de filas globales y otra de bloques de partículas.
simulation_rows = []
particle_blocks = []
run_id = 0

for gradient in gradients:
    for phase in phases:
        # Datos inventados para practicar. Sus unidades no representan una cavidad.
        x = rng.normal(0., 1., n_particles)
        y = rng.normal(0., 1., n_particles)
        energy = rng.normal(gradient*np.cos(np.deg2rad(phase)), .1, n_particles)

        simulation_rows.append({
            'run_id': run_id, 'gradient': gradient, 'phase': phase,
            'mean_energy': energy.mean(), 'sigma_energy': energy.std(),
        })
        particle_blocks.append({
            'run_id': np.full(n_particles, run_id, dtype=np.int64),
            'x': x, 'y': y, 'energy': energy,
        })
        run_id += 1

# uproot necesita columnas. Pasamos las seis filas de resumen a arrays.
simulations = {}
for name in simulation_rows[0]:
    values = [row[name] for row in simulation_rows]
    dtype = np.int64 if name == 'run_id' else np.float64
    simulations[name] = np.array(values, dtype=dtype)

# Reunimos los seis bloques de 100 partículas: 600 filas en total.
particles = {}
for name in particle_blocks[0]:
    particles[name] = np.concatenate([block[name] for block in particle_blocks])

with uproot.recreate('data/simulated_scan.root') as file:
    for name, columns in [('simulations', simulations), ('particles', particles)]:
        types = {column: values.dtype for column, values in columns.items()}
        tree = file.mktree(name, types)
        tree.extend(columns)

# Buscar una simulación por sus parámetros y luego sus partículas por run_id.
with uproot.open('data/simulated_scan.root') as file:
    sim = file['simulations'].arrays(library='np')
    part = file['particles'].arrays(library='np')
selected = (sim['gradient'] == 11.) & (sim['phase'] == 20.)
selected_id = sim['run_id'][selected][0]
energies = part['energy'][part['run_id'] == selected_id]
print('Simulaciones:', len(sim['run_id']))
print('Partículas:', len(part['run_id']))
print('run_id seleccionado:', selected_id, 'partículas asociadas:', len(energies))
