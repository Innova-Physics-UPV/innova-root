"""Adaptación a Funciones.py original, conservado sin modificaciones.

No importa ni ejecuta el notebook. No contiene un modelo físico sustituto.
"""
import hashlib
import importlib.util
from pathlib import Path

ORIGINAL = Path(__file__).resolve().parents[1] / 'external' / 'javier' / 'Funciones.py'
_functions = None
_injected_populations = {}


def original_functions():
    global _functions
    if _functions is None:
        if not ORIGINAL.is_file():
            raise FileNotFoundError(f'Falta original de Javier: {ORIGINAL}')
        try:
            import RF_Track  # noqa: F401
        except ImportError as exc:
            raise ImportError('Instala RF-Track en este Python; no hay fallback simulado') from exc
        spec = importlib.util.spec_from_file_location('innova_javier_original', ORIGINAL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _functions = module  # __name__ != __main__: no ejecuta selftests.
    return _functions


def configure(config):
    config = dict(config)
    functions = original_functions()
    config['kinetic_energy_inj_MeV'] = float(functions.kinetic_energy_from_beta(config['beta_inj']))
    return config


def build_dc_beam(config):
    functions = original_functions()
    beam = functions.build_dc_beam(
        frequency=config['frequency'],
        kinetic_energy_MeV=config['kinetic_energy_inj_MeV'],
        current_A=config['current_A'],
        n_macroparticles=config['n_macroparticles_injected'], seed=config['seed'],
    )
    # Capturar antes del tracking, incluso si modifica el Bunch de entrada.
    population = float(beam.get_info().transmission)
    if population <= 0:
        raise ValueError('Población física inyectada no positiva')
    _injected_populations[id(beam)] = population
    return beam


def StandingWaveCavity(config):
    return original_functions().StandingWaveCavity(
        frequency=config['frequency'], beta_ph=config['beta_ph'], A=config['A'],
        phase_advance=config['phase_advance'], number_of_cells=config['number_of_cells'],
    )


def safe_tracking_options(config):
    return original_functions().safe_tracking_options(config['frequency'])


def track_volume(beam_in, cavity, options, config):
    functions = original_functions()
    ok, _, _ = functions.check_capture_margin(cavity, config['kinetic_energy_inj_MeV'])
    if not ok:
        _injected_populations.pop(id(beam_in), None)
        raise RuntimeError('Margen de captura insuficiente según el helper original')
    import RF_Track as rft
    volume = rft.Volume()
    volume.add(cavity, 0.0, 0.0, 0.0)
    volume.set_s0(0.0)
    volume.set_s1(cavity.length_m)
    try:
        return volume.track(beam_in, options)
    except BaseException:
        _injected_populations.pop(id(beam_in), None)
        raise


def beam_properties(beam_out, beam_in, config):
    population = _injected_populations.pop(id(beam_in))
    return original_functions().beam_properties(
        beam_out, n_injected=population, frequency=config['frequency'],
    )


def provenance():
    paths = [ORIGINAL, ORIGINAL.with_name('Sweeps y Operaciones.ipynb')]
    return {
        'originals_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in paths if path.is_file()},
        'configuration_source': 'PDF sección 9 y Funciones._selftest; barrido A del PDF',
        'notebook_executed': False,
        'units': {'x': 'mm', 'xp': 'mrad', 'y': 'mm', 'yp': 'mrad',
                  't': 'mm/c (unidad interna RF-Track)', 'Pc': 'MeV/c', 'A': 'adimensional'},
    }
