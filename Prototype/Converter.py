import pandas as pd
import numpy as np
import uproot

#Convierte el csv a Numpy
def csv_reader(input_file):
    df = pd.read_csv(
        input_file,
        sep=";",
        decimal=",",
        encoding="cp1252"
    )
        # Identificador para relacionar resultados posteriormente
    df.insert(0, "run_id", np.arange(len(df)))

    return df

def npz_reader(input_file):
    with np.load(input_file, allow_pickle=False) as file:
        simulations = {
            key: file[key].copy()
            for key in file.files
            if key != "phase_space"
        }
    return simulations

#Convierte el Numpy a un TTree
def converter(simulations,file_name):
    with uproot.recreate(file_name) as file:
        types = {
            column: values.dtype
            for column, values in simulations.items()
        }

        tree = file.mktree("simulations", types)
        tree.extend(simulations)
    print('Guardado:', file_name)

def approve(simulations,output_file):
    with uproot.open(output_file) as file:
        tree = file["simulations"]
        recovered = tree.arrays(library="np")
        for column in simulations:
            assert np.array_equal(
                simulations[column],
                recovered[column],
                equal_nan=True
            )
        print("Todos los datos coinciden")


 #EJEMPLO CON CSV
df=csv_reader("external/javier/results1.csv")
#Revisar los nombres de las columnas
df = df.rename(columns={
    "transmissión_fraction": "transmission_fraction",
    "mea_kinetic_energy_MeV": "mean_kinetic_energy_MeV"
})

simulations = {
    column: df[column].to_numpy()
    for column in df.columns
}

converter(simulations, "data/results_csv.root")

approve(simulations, "data/results_csv.root")


#EJEMPLO CON NPZ
simulations=npz_reader("external/results1.npz")

converter(simulations, "data/results_npz.root")

approve(simulations, "data/results_npz.root")