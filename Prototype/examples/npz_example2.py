from Prototype import Converter
from Prototype import Analyzer
import ROOT

simulations, particles = Converter.npz_reader(
    "external/run_0000.npz"
)

Converter.converter(
    {
        "simulations": simulations,
        "particles": particles
    },
    "data/results_npz.root"
)

Converter.approve({"simulations": simulations, "particles": particles}, "data/results_npz.root")

df_particles = Analyzer.load_particles("data/results_npz.root")

Analyzer.summarize_particles(df_particles)

Analyzer.plot_histogram(df_particles, "Pc")

Analyzer.plot_phase_space(df_particles, "t", "Pc")

df_zoom = df_particles.Filter("t >= 0 && t < 1000")

Analyzer.plot_phase_space(df_zoom, "t", "Pc")

df_phase = Analyzer.add_rf_phase(df_particles, 2.856e9)

Analyzer.plot_histogram(df_phase, "phase_deg", bins=72, minimum=0, maximum=360)

Analyzer.plot_phase_space(df_phase, "phase_deg", "Pc")

df_energy = Analyzer.add_kinetic_energy(df_phase)

df_centered_phase = Analyzer.add_centered_rf_phase(df_energy)

Analyzer.plot_phase_space(df_centered_phase, "centered_phase_deg", "Ek_MeV")

spread_root = Analyzer.circular_phase_spread(df_phase)

df_sim = ROOT.RDataFrame("simulations", "data/results_npz.root")

spread_rftrack = df_sim.Take["double"](
    "phase_spread_rms_deg"
).GetValue()[0]

print("ROOT:", spread_root)
print("RF-Track:", spread_rftrack)
print("Diferencia:", abs(spread_root - spread_rftrack))