from Prototype import Converter
from Prototype import Analyzer

df=Converter.csv_reader("external/javier/results1.csv")
#Revisar los nombres de las columnas
df = df.rename(columns={
    "transmissión_fraction": "transmission_fraction",
    "mea_kinetic_energy_MeV": "mean_kinetic_energy_MeV"
})

simulations = {
    column: df[column].to_numpy()
    for column in df.columns
}
Converter.converter(simulations, "data/results_csv.root")

Converter.approve(simulations, "data/results_csv.root")
df = Analyzer.load_simulations("data/results_csv.root")
Analyzer.summarize_simulations(df)
Analyzer.filter_simulations(df,"A_M >= 2")
Analyzer.plot_simulations(df,"A_M","mean_kinetic_energy_MeV")
