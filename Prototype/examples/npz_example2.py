from Prototype import Converter
from Prototype import Analyzer
import numpy as np

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