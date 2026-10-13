"""Aproximación didáctica; NO RF-Track ni modelo físico de cavidad."""
import argparse
import itertools
import numpy as np
from innova.io import save_results, rows_to_columns

def run_simulation(gradient, phase, n, seed):
    rng = np.random.default_rng(seed)
    # Fórmula inventada y etiquetada únicamente para ensayar el pipeline.
    return np.column_stack((rng.normal(0, 1, n), rng.normal(0, 1, n),
                            rng.normal(gradient*np.cos(np.deg2rad(phase)), .1, n)))

def calculate_summary(data):
    return {'mean_energy': float(data[:, 2].mean()),
            'sigma_energy': float(data[:, 2].std(ddof=0))}

def scan(gradients=(10., 11., 12.), phases=(0., 20.), n=100, seed=42):
    if n <= 0:
        raise ValueError('n debe ser positivo')
    summaries, parts = [], []
    for run_id, (gradient, phase) in enumerate(itertools.product(gradients, phases)):
        data = run_simulation(gradient, phase, n, seed+run_id)
        summaries.append(dict(run_id=run_id, gradient=gradient, phase=phase,
                              **calculate_summary(data)))
        parts.append(dict(run_id=np.full(n, run_id, dtype=np.int64),
                          x=data[:, 0], y=data[:, 1], energy=data[:, 2]))
    return rows_to_columns(summaries), {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='data/simulated_scan.root')
    args = parser.parse_args()
    sim, particles = scan()
    save_results(args.output, sim, particles)
    print('simulations:', len(sim['run_id']), 'particles:', len(particles['run_id']))

if __name__ == '__main__':
    main()
