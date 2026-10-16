import ROOT

def load_simulations(file_path):
    return ROOT.RDataFrame("simulations", file_path)


def summarize_simulations(df):
    print("Simulaciones:", df.Count().GetValue())

    columns = df.AsNumpy([
        "run_id", "A_M", "N_cells", "length_cm",
        "transmission_fraction", "capture_fraction",
        "mean_kinetic_energy_MeV"
    ])

    for i in range(len(columns["run_id"])):
        print(
            "run_id:", columns["run_id"][i],
            "A:", columns["A_M"][i],
            "número de celdas:", columns["N_cells"][i],
            "longitud (cm):", columns["length_cm"][i],
            "energía media (MeV):", columns["mean_kinetic_energy_MeV"][i],
            "transmisión:", columns["transmission_fraction"][i],
            "captura:", columns["capture_fraction"][i]
        )

def filter_simulations(df, cond):
    selected = df.Filter(cond)
    print("Simulaciones con", cond, ":", selected.Count().GetValue())
    print(
        "Su energía media:",
        selected.Mean("mean_kinetic_energy_MeV").GetValue()
    )
    return selected


def plot_simulations(df, prop1, prop2):
    graph = df.Graph(prop1, prop2).GetValue()
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(1.5)

    canvas = ROOT.TCanvas("c1",f"{prop1} vs {prop2}", 900, 600)
    graph.Draw("AP")
    canvas.SaveAs(f"data/{prop1}_vs_{prop2}.png")


def main():
    df = load_simulations("data/results_csv.root")
    summarize_simulations(df)
    filter_simulations(df,"A_M >= 2")
    plot_simulations(df,"A_M","mean_kinetic_energy_MeV")

    df = load_simulations("data/results_npz.root")
    df = df.Alias(
    "mean_kinetic_energy_MeV",
    "mea_kinetic_energy_MeV"
)
    summarize_simulations(df)
    filter_simulations(df,"A_M >= 2")
    plot_simulations(df,"A_M","mean_kinetic_energy_MeV")


if __name__ == "__main__":
    main()