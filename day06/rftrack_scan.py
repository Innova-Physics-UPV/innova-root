"""Orquestación RF-Track con adaptador a los originales de Javier incluidos.

No incluye sustituciones físicas ni un modo simulado.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
from innova.io import save_results, rows_to_columns

PHASE_SPACE = '%x %xp %y %yp %t %Pc'
METRICS = ('mean_kinetic_energy_MeV', 'peak_kinetic_energy_MeV',
           'min_kinetic_energy_MeV', 'energy_spread_rms_MeV',
           'energy_spread_fwhm_MeV', 'phase_spread_rms_deg',
           'real_particles_remaining', 'transmission_fraction')
INTEGER_FIELDS = ('run_id', 'n_macroparticles_injected', 'number_of_cells', 'seed',
                  'n_macroparticles_output')

def configuration(A):
    # Fuente: PDF §9.3. El adaptador real actualiza esta energía con el conversor
    # y la masa RF-Track del original de Javier.
    beta_inj = .4
    return dict(frequency=2856e6, beta_inj=beta_inj,
                kinetic_energy_inj_MeV=.51099895*(1/np.sqrt(1-beta_inj**2)-1),
                current_A=.150, n_macroparticles_injected=20000,
                beta_ph=.5, A=float(A), phase_advance=2*np.pi/3,
                number_of_cells=5, seed=42)

def load_adapter(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError('Falta adaptador verificado: consulta day06/ADAPTER.md')
    spec = importlib.util.spec_from_file_location('javier_adapter', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ('build_dc_beam', 'StandingWaveCavity', 'safe_tracking_options',
                 'beam_properties', 'track_volume'):
        if not callable(getattr(module, name, None)):
            raise TypeError('El adaptador debe exponer: ' + name)
    return module

def run_simulation(adapter, config):
    beam_in = adapter.build_dc_beam(dict(config))
    cavity = adapter.StandingWaveCavity(dict(config))
    options = adapter.safe_tracking_options(dict(config))
    beam_out = adapter.track_volume(beam_in, cavity, options, dict(config))
    data = np.asarray(beam_out.get_phase_space(PHASE_SPACE), dtype=np.float64)
    if data.ndim != 2 or data.shape[1] != 6 or not np.all(np.isfinite(data)):
        raise ValueError('RF-Track debe devolver matriz finita N x 6')
    props = adapter.beam_properties(beam_out, beam_in, dict(config))
    missing = set(METRICS)-set(props)
    if missing:
        raise ValueError('Falta mapear propiedades originales: ' + str(sorted(missing)))
    if not 0 <= float(props['transmission_fraction']) <= 1:
        raise ValueError('Transmisión fuera de [0,1]')
    return data, {k: float(props[k]) for k in METRICS}

def scan(adapter):
    rows, parts = [], []
    for run_id, A in enumerate((.08, .10, .12)):
        config = configuration(A)
        if callable(getattr(adapter, 'configure', None)):
            config = adapter.configure(config)
        data, props = run_simulation(adapter, config)
        rows.append(dict(run_id=run_id, **config, **props,
                         n_macroparticles_output=len(data)))
        part = {name: data[:, i] for i, name in enumerate(('x', 'xp', 'y', 'yp', 't', 'Pc'))}
        part['run_id'] = np.full(len(data), run_id, dtype=np.int64)
        parts.append(part)
    return rows_to_columns(rows, INTEGER_FIELDS), {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter', default=str(Path(__file__).with_name('javier_adapter.py')))
    parser.add_argument('--output', default='data/rftrack_amplitude_scan.root')
    args = parser.parse_args()
    adapter = load_adapter(args.adapter)
    # Importación explícita: esta entrada exige RF-Track real.
    import RF_Track
    sim, particles = scan(adapter)
    save_results(args.output, sim, particles)
    manifest = dict(source='RF-Track real mediante adaptador explícito a Javier',
                    adapter_sha256=hashlib.sha256(Path(args.adapter).read_bytes()).hexdigest(),
                    rftrack_version=str(getattr(RF_Track, '__version__', 'no disponible')),
                    simulations=len(sim['run_id']), particles=len(particles['run_id']),
                    phase_space=PHASE_SPACE)
    if callable(getattr(adapter, 'provenance', None)):
        manifest.update(adapter.provenance())
    Path(args.output).with_suffix('.provenance.json').write_text(json.dumps(manifest, indent=2))
    print(manifest)

if __name__ == '__main__':
    main()
