"""Análisis con RDataFrame de los TTree del día 6, PDF §10."""
import argparse
import json
from pathlib import Path
import numpy as np
import ROOT

def analyze(path, output='data/day07_analysis.root'):
    simulations = ROOT.RDataFrame('simulations', str(path))
    particles = ROOT.RDataFrame('particles', str(path))
    columns = ['run_id', 'A', 'mean_kinetic_energy_MeV', 'energy_spread_rms_MeV',
               'phase_spread_rms_deg', 'transmission_fraction', 'n_macroparticles_injected']
    values = simulations.AsNumpy(columns)
    if len(np.unique(values['run_id'])) != len(values['run_id']):
        raise ValueError('Identificadores duplicados')
    report = dict(simulations=int(simulations.Count().GetValue()),
                  particles=int(particles.Count().GetValue()))
    selected = simulations.Filter('A >= 0.10')
    report['selected_simulations'] = int(selected.Count().GetValue())
    if report['selected_simulations']:
        report['selected_mean_kinetic_energy_MeV'] = float(selected.Mean('mean_kinetic_energy_MeV').GetValue())
    rows = []
    for i in np.argsort(values['A']):
        run_id = int(values['run_id'][i])
        row = {k: v[i].item() for k, v in values.items()}
        row['particles_stored'] = int(particles.Filter(f'run_id == {run_id}').Count().GetValue())
        rows.append(row)
    report['runs'] = rows
    if sum(r['particles_stored'] for r in rows) != report['particles']:
        raise ValueError('Partículas huérfanas')
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    f = ROOT.TFile(str(output), 'RECREATE')
    if f.IsZombie():
        raise OSError('No se puede escribir histogramas')
    histogram = particles.Define('r2', 'x*x+y*y').Histo1D(('r2', 'x^2+y^2', 100, 0., 100.), 'r2')
    histogram.GetValue().Write()
    f.Close()
    print(json.dumps(report, indent=2))
    Path(output).with_suffix('.json').write_text(json.dumps(report, indent=2))
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs='?', default='data/rftrack_amplitude_scan.root')
    parser.add_argument('--output', default='data/day07_analysis.root')
    args = parser.parse_args()
    analyze(args.input, args.output)
