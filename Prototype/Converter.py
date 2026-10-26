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
        data = file["phase_space"]

        simulations = {
            key: np.array([file[key].item()])
            for key in file.files
            if key != "phase_space"
        }

        run_id = int(file["run_id"].item())

        particles = {
            "run_id": np.full(len(data), run_id),
            "x": data[:, 0],
            "xp": data[:, 1],
            "y": data[:, 2],
            "yp": data[:, 3],
            "t": data[:, 4],
            "Pc": data[:, 5]
        }

    return simulations, particles

#Convierte el Numpy a un TTree
def converter(datasets, file_name):
    with uproot.recreate(file_name) as file:
        for name, columns in datasets.items():
            types = {
                column: values.dtype
                for column, values in columns.items()
            }

            tree = file.mktree(name, types)
            tree.extend(columns)

    print("Guardado:", file_name)

def approve(datasets, file_name):
    with uproot.open(file_name) as file:
        for name, columns in datasets.items():
            recovered = file[name].arrays(library="np")

            for column, original in columns.items():
                assert np.array_equal(
                    original,
                    recovered[column],
                    equal_nan=True
                ), f"Error en {name}/{column}"

            print(f"{name}: {len(next(iter(columns.values())))} entradas verificadas")