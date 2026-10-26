import ROOT

from Prototype import Analyzer, Validator

from Prototype import Converter

from pathlib import Path

def test_rftrack_physics_validation(tmp_path):
    input_file = Path(__file__).parent / "fixtures" / "run_0000.npz"
    output_file = tmp_path / "results.root"

    simulations, particles = Converter.npz_reader(input_file)

    datasets = {
        "simulations": simulations,
        "particles": particles
    }

    Converter.converter(datasets, output_file)

    df_particles = ROOT.RDataFrame("particles", str(output_file))
    df_sim = ROOT.RDataFrame("simulations", str(output_file))

    frequency = df_sim.Take["double"]("frequency").GetValue()[0]

    df_phase = Analyzer.add_rf_phase(df_particles, frequency)
    df_energy = Analyzer.add_kinetic_energy(df_particles)

    phase_result = Validator.validate_phase_spread(df_phase, df_sim)
    energy_result = Validator.validate_mean_kinetic_energy(df_energy, df_sim)

    results = [phase_result, energy_result]
    report = Validator.build_validation_report(results)

    assert report["status"] == "PASS"
    assert report["passed"] == 2

    
