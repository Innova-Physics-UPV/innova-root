import ROOT

from Prototype import Analyzer, Validator

def test_rftrack_physics_validation():
    file_path = "data/results_npz.root"

    df_particles = ROOT.RDataFrame("particles", file_path)
    df_sim = ROOT.RDataFrame("simulations", file_path)

    frequency = df_sim.Take["double"]("frequency").GetValue()[0]

    df_phase = Analyzer.add_rf_phase(df_particles, frequency)
    df_energy = Analyzer.add_kinetic_energy(df_particles)

    phase_result = Validator.validate_phase_spread(df_phase, df_sim)
    energy_result = Validator.validate_mean_kinetic_energy(df_energy, df_sim)

    results = [phase_result, energy_result]
    report = Validator.build_validation_report(results)

    assert report["status"] == "PASS"
    assert report["passed"] == 2

    
