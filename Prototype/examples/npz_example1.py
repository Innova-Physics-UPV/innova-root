from Prototype import Converter
from Prototype import Analyzer

simulations=Converter.npz_reader("external/results1.npz")

Converter.converter(simulations, "data/results_npz.root")

Converter.approve(simulations, "data/results_npz.root")
df = Analyzer.load_simulations("data/results_npz.root")
df = df.Alias(
"mean_kinetic_energy_MeV",
"mea_kinetic_energy_MeV"
)
Analyzer.summarize_simulations(df)
Analyzer.filter_simulations(df,"A_M >= 2")
Analyzer.plot_simulations(df,"A_M","mean_kinetic_energy_MeV")