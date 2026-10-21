import ROOT
import numpy as np

def load_simulations(file_path):
    return ROOT.RDataFrame("simulations", file_path)

def load_particles(file_path):
    return ROOT.RDataFrame("particles", file_path)

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

def summarize_particles(df):
    print("Macropartículas:", df.Count().GetValue())

    for variable in ["x", "xp", "y", "yp", "t", "Pc"]:
        mean = df.Mean(variable).GetValue()
        std = df.StdDev(variable).GetValue()

        print(f"{variable}: media = {mean:.5f}, sigma = {std:.5f}")

def filter_simulations(df, cond):
    selected = df.Filter(cond)
    print("Simulaciones con", cond, ":", selected.Count().GetValue())
    print(
        "Su energía media:",
        selected.Mean("mean_kinetic_energy_MeV").GetValue()
    )
    return selected

def add_rf_phase(df, frequency):
    c = 2.99792458e11
    df_phase = df.Define("phase_deg",f"fmod(360.0 * t * {frequency} / {c}, 360.0)")
    return df_phase

def add_centered_rf_phase(df_phase):
    df_centered_phase = df_phase.Define("centered_phase_deg","phase_deg < 180.0 ? phase_deg : phase_deg - 360.0")
    return df_centered_phase

def add_kinetic_energy(df):
    m_e = 0.51099895
    df_energy = df.Define("Ek_MeV",f"sqrt(Pc * Pc + {m_e} * {m_e}) - {m_e}")
    return df_energy

def circular_phase_spread(df):
    df_circular = df.Define(
        "cos_phase",
        "cos(phase_deg * 3.141592653589793 / 180.0)"
    ).Define(
        "sin_phase",
        "sin(phase_deg * 3.141592653589793 / 180.0)"
    )

    mean_cos = df_circular.Mean("cos_phase").GetValue()
    mean_sin = df_circular.Mean("sin_phase").GetValue()

    mean_vector = min(np.sqrt(mean_cos**2+mean_sin**2),1)
    circular_phase_spread = np.sqrt(-2 * np.log(mean_vector)) if mean_vector > 0 else np.inf
    circular_phase_spread_deg = circular_phase_spread * 180/np.pi

    return circular_phase_spread_deg

def plot_simulations(df, prop1, prop2):
    graph = df.Graph(prop1, prop2).GetValue()
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(1.5)

    canvas = ROOT.TCanvas("c1",f"{prop1} vs {prop2}", 900, 600)
    graph.Draw("AP")
    canvas.SaveAs(f"data/{prop1}_vs_{prop2}.png")

def plot_histogram(df, variable, bins=100, minimum=None, maximum=None):
    if minimum is None:
        minimum = df.Min(variable).GetValue()
    if maximum is None:
        maximum = df.Max(variable).GetValue()

    hist = df.Histo1D(
        (f"h_{variable}", variable, bins, minimum, maximum),
        variable
    )

    canvas = ROOT.TCanvas(f"c_{variable}", variable, 900, 600)
    hist.Draw()
    canvas.SaveAs(f"data/hist_{variable}.png")

def plot_phase_space(df, x, y, bins=100, x_label=None, y_label=None):
    x_min = df.Min(x).GetValue()
    x_max = df.Max(x).GetValue()
    y_min = df.Min(y).GetValue()
    y_max = df.Max(y).GetValue()

    hist = df.Histo2D(
        (
            f"h2_{x}_{y}",
            f"Espacio de fases: {y} vs {x}",
            bins, x_min, x_max,
            bins, y_min, y_max
        ),
        x, y
    )

    canvas = ROOT.TCanvas("c_phase", "Phase Space", 900, 600)

    hist.GetXaxis().SetTitle(f"{x} ({x_label})")
    hist.GetYaxis().SetTitle(f"{y} ({y_label})")

    canvas.SetRightMargin(0.15)
    hist.Draw("COLZ")

    canvas.SaveAs(f"data/phase_space_{x}_{y}.png")