

import numpy as np
import RF_Track as rft

# ---------------------------------------------------------------------------
# Constantes fisicas y de conversion
# ---------------------------------------------------------------------------
e_mass = rft.electronmass #MeV/c^2
C = rft.C 

def kinetic_energy_to_pc(kinetic_energy_MeV, mass_MeV=e_mass):
    """Convierte energia cinetica (MeV) a momento total Pc (MeV/c)."""
    total_energy = mass_MeV + kinetic_energy_MeV
    return np.sqrt(total_energy**2 - mass_MeV**2)


def beta_from_kinetic_energy(kinetic_energy_MeV, mass_MeV=e_mass):
    """Beta = v/c a partir de la energia cinetica (MeV). Util para fijar
    la energia de inyeccion a partir de un beta_inj deseado, o viceversa."""
    gamma = 1.0 + kinetic_energy_MeV / mass_MeV
    return np.sqrt(1.0 - 1.0 / gamma**2)


def kinetic_energy_from_beta(beta, mass_MeV=e_mass):
    """Inversa de beta_from_kinetic_energy."""
    gamma = 1.0 / np.sqrt(1.0 - beta**2)
    return (gamma - 1.0) * mass_MeV


def rf_period_ns(frequency):
    """Periodo de RF en nanosegundos."""
    return 1e9 / frequency


def normalized_amplitude_to_field(A, frequency, mass_MeV=e_mass):
    """Convierte el campo normalizado A (adimensional, A = e*E*lambda/(m*c^2)
    tal y como lo define el paper) al campo fisico E0 en V/m.

    E0 = A * (m c^2 [eV]) / lambda [m]
    """
    wavelength_m = rft.clight / frequency
    mc2_eV = mass_MeV * 1e6
    return A * mc2_eV / wavelength_m


def field_to_normalized_amplitude(E0, frequency, mass_MeV=e_mass):
    """Inversa de normalized_amplitude_to_field."""
    wavelength_m = rft.clight / frequency
    mc2_eV = mass_MeV * 1e6
    return E0 * wavelength_m / mc2_eV


class ConstantBetaCavity(rft.UserField):
    def __init__(self,
        frequency,
        beta_ph,
        A=None,
        phase_advance=2 * np.pi / 3,
        number_of_cells=1,
        phi0=0.0,
        E0=None,
        mass_MeV=e_mass,
    ):
        if E0 is None:
            if A is None:
                raise ValueError("Hay que dar A o E0.")
            E0 = normalized_amplitude_to_field(A, frequency, mass_MeV)

        c = rft.clight
        wavelength_m = c / frequency

        self.frequency = frequency
        self.beta_ph = beta_ph
        self.A = A if A is not None else field_to_normalized_amplitude(E0, frequency, mass_MeV)
        self.E0 = E0
        self.phase_advance = phase_advance
        self.number_of_cells = number_of_cells
        self.phi0 = phi0

        self.omega = 2 * np.pi * frequency
        self.k = self.omega / (beta_ph * c)  # numero de onda, rad/m
        self.cell_length_m = beta_ph * wavelength_m * phase_advance / (2 * np.pi)
        self.length_m = number_of_cells * self.cell_length_m

        super().__init__(self.length_m)

    def get_field(self, x, y, z, t):
        z_m = z * 1e-3
        t_s = (t / rft.ns) * 1e-9
        Ez = self.E0 * np.cos(self.k * z_m - self.omega * t_s + self.phi0)
        return ([0.0, 0.0, Ez], [0.0, 0.0, 0.0])


class StandingWaveCavity(rft.RF_FieldMap_1d_CINT):
    def __init__(
        self,
        frequency,
        beta_ph,
        A=None,
        phase_advance=2 * np.pi / 3,
        number_of_cells=1,
        phi0=0.0,
        phi_z0=0.0,
        E0=None,
        mass_MeV=e_mass,
        points_per_cell=400,
    ):
        if E0 is None:
            if A is None:
                raise ValueError("Hay que dar A o E0.")
            E0 = normalized_amplitude_to_field(A, frequency, mass_MeV)

        c = rft.clight
        wavelength_m = c / frequency

        self.frequency = frequency
        self.beta_ph = beta_ph
        self.A = A if A is not None else field_to_normalized_amplitude(E0, frequency, mass_MeV)
        self.E0 = E0
        self.phase_advance = phase_advance
        self.number_of_cells = number_of_cells
        self.phi0 = phi0
        self.phi_z0 = phi_z0

        self.omega = 2 * np.pi * frequency
        self.k = self.omega / (beta_ph * c)
        self.cell_length_m = beta_ph * wavelength_m * phase_advance / (2 * np.pi)
        self.length_m = number_of_cells * self.cell_length_m

        nz = max(200, int(points_per_cell * number_of_cells))
        z = np.linspace(0.0, self.length_m, nz)
        hz = z[1] - z[0]
        Ez_real = (self.E0 * np.cos(self.k * z + self.phi_z0)).astype(complex)

        super().__init__(Ez_real, hz, self.length_m, frequency, 1.0)
        self.set_t0(0.0)
        self.set_phid(np.degrees(phi0))


def safe_tracking_options(frequency, steps_per_period=40):
    T = rft.TrackingOptions()
    period_ns = rf_period_ns(frequency)
    T.dt_mm = (period_ns * rft.ns) / steps_per_period
    return T


def check_capture_margin(cavity, kinetic_energy_inj_MeV, margin_factor=0.5):
    is_sw = isinstance(cavity, StandingWaveCavity)
    amplitude_factor = 0.5 if is_sw else 1.0  # SW: solo la componente co-viajera (E0/2) acelera/frena neto
    max_decel_MeV = amplitude_factor * cavity.E0 * cavity.length_m / 1e6

    margin_ratio = kinetic_energy_inj_MeV / max_decel_MeV if max_decel_MeV > 0 else np.inf
    ok = margin_ratio >= (1.0 + margin_factor)

    if not ok:
        print(
            f"  [AVISO] Margen de energia insuficiente: KE_inj={kinetic_energy_inj_MeV:.4f} MeV "
            f"vs. frenada maxima={max_decel_MeV:.4f} MeV (ratio={margin_ratio:.2f}). "
            f"Baja A, sube beta_inj, o reduce N antes de trackear esta configuracion: "
            f"riesgo de particulas casi paradas -> integrador numericamente inestable."
        )
    return ok, max_decel_MeV, margin_ratio


def track_in_batches(volume, bunch, tracking_options, batch_size=500):
    X_in = bunch.get_phase_space("%x %xp %y %yp %t %Pc")
    n_total = X_in.shape[0]
    mass = bunch[0].mass if n_total > 0 else None
    charge = bunch[0].Q if n_total > 0 else None  # Q: carga de la macroparticula (en e)

    total_population = bunch.get_info().transmission
    out_rows = []
    n_batches = int(np.ceil(n_total / batch_size))
    for i in range(n_batches):
        lo, hi = i * batch_size, min((i + 1) * batch_size, n_total)
        X_batch = X_in[lo:hi]
        pop_batch = total_population * (hi - lo) / n_total
        bunch_batch = rft.Bunch6d(mass, pop_batch, charge, X_batch)
        bunch_out_batch = volume.track(bunch_batch, tracking_options)
        out_rows.append(bunch_out_batch.get_phase_space("%x %xp %y %yp %t %Pc"))

    X_out = np.vstack(out_rows) if out_rows else X_in[:0]
    # Sin aperturas en nuestras cavidades, entran y salen el mismo numero
    # de particulas por lote, asi que la poblacion total no cambia.
    return rft.Bunch6d(mass, total_population, charge, X_out)


def bucket_hamiltonian(psi, gamma, beta_ph, frequency, E_field_Vm, mass_MeV=e_mass):
    wavelength_m = rft.clight / frequency
    k1 = 2 * np.pi * mass_MeV / wavelength_m
    return k1 * (gamma / beta_ph - np.sqrt(gamma**2 - 1)) + (E_field_Vm / 1e6) * np.sin(psi)


def bucket_separatrix(beta_ph, frequency, E_field_Vm, mass_MeV=e_mass, n_points=400):
    gamma_ph = 1.0 / np.sqrt(1.0 - beta_ph**2)
    H_sep = bucket_hamiltonian(np.pi / 2, gamma_ph, beta_ph, frequency, E_field_Vm, mass_MeV)

    wavelength_m = rft.clight / frequency
    k1 = 2 * np.pi * mass_MeV / wavelength_m
    A_ = k1 / beta_ph
    c2 = E_field_Vm / 1e6

    psi = np.linspace(-np.pi / 2, 3 * np.pi / 2, n_points)  # un periodo completo, centrado en el centro estable (-pi/2)
    RHS = H_sep - c2 * np.sin(psi)

    a = A_**2 - k1**2
    b = -2 * A_ * RHS
    c = RHS**2 + k1**2
    disc = np.clip(b**2 - 4 * a * c, 0, None)  # 0 fuera del rango valido (fuera del bucket)
    r1 = (-b + np.sqrt(disc)) / (2 * a)
    r2 = (-b - np.sqrt(disc)) / (2 * a)
    gamma_hi = np.maximum(r1, r2)
    gamma_lo = np.minimum(r1, r2)

    # filtrar la raiz espuria de elevar al cuadrado (exige A_*gamma-RHS y
    # k1*sqrt(gamma^2-1) con el mismo signo)
    for arr in (gamma_hi, gamma_lo):
        with np.errstate(invalid="ignore"):
            valid = (arr > 1) & (np.abs((A_ * arr - RHS) - k1 * np.sqrt(np.clip(arr**2 - 1, 0, None))) < 1e-4 * k1)
        arr[~valid] = np.nan

    return np.degrees(psi), gamma_hi, gamma_lo


def track_with_snapshots(frequency, beta_ph, A, phase_advance, number_of_cells, beam_in, batch_size=None):
    T = safe_tracking_options(frequency)
    snapshots = [{"z_m": 0.0, "label": "entrada", "bunch": beam_in}]

    bunch = beam_in
    z_accum = 0.0
    for i in range(number_of_cells):
        cell = StandingWaveCavity(
            frequency, beta_ph, A=A, phase_advance=phase_advance,
            number_of_cells=1, phi_z0=i * phase_advance,
        )
        V = rft.Volume()
        V.add(cell, 0.0, 0.0, 0.0)
        V.set_s0(0.0)
        V.set_s1(cell.length_m)
        # V.track() directo: StandingWaveCavity es ahora un elemento nativo
        # (RF_FieldMap_1d_CINT), no hace falta track_in_batches(). Se deja
        # el parametro batch_size (ignorado si es None) por compatibilidad.
        bunch = track_in_batches(V, bunch, T, batch_size=batch_size) if batch_size else V.track(bunch, T)
        z_accum += cell.length_m
        snapshots.append({"z_m": z_accum, "label": f"celda {i+1}/{number_of_cells}", "bunch": bunch})

    return snapshots


def plot_eye_diagrams(snapshots, frequency, beta_ph, A, phase_advance, output_path,
                       mass_MeV=e_mass, max_points=4000, is_standing_wave=True):
    import matplotlib.pyplot as plt

    n = len(snapshots)
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 4.2), sharey=True)
    if n == 1:
        axes = [axes]

    E0 = normalized_amplitude_to_field(A, frequency, mass_MeV)
    E_field_comoving = E0 / 2 if is_standing_wave else E0
    psi_deg_grid, gamma_hi, gamma_lo = bucket_separatrix(beta_ph, frequency, E_field_comoving, mass_MeV)
    K_hi = mass_MeV * (gamma_hi - 1)
    K_lo = mass_MeV * (gamma_lo - 1)

    for j, (ax, snap) in enumerate(zip(axes, snapshots)):
        bunch = snap["bunch"]
        X = bunch.get_phase_space("%t %Pc")
        if X.shape[0] > max_points:
            idx = np.random.default_rng(0).choice(X.shape[0], max_points, replace=False)
            X = X[idx]
        t_ns = X[:, 0] / rft.ns
        Pc = X[:, 1]
        kinetic_energy = np.sqrt(Pc**2 + mass_MeV**2) - mass_MeV

        phase_deg = np.degrees(2 * np.pi * frequency * (t_ns * 1e-9))
        phase_deg = ((phase_deg + 180) % 360) - 180  # envolver a [-180, 180]

        ax.scatter(phase_deg, kinetic_energy, s=3, alpha=0.35, color="tab:blue", label="macroparticulas (RF-Track)")

        # separatriz: psi = j*phase_advance - fase_RF (mod 360), trasladada
        # a la misma variable "fase RF" que el scatter (fase_RF = j*theta - psi)
        theta_deg = np.degrees(j * phase_advance)
        phase_rf_hi = ((theta_deg - psi_deg_grid + 180) % 360) - 180
        phase_rf_lo = phase_rf_hi
        order = np.argsort(phase_rf_hi)
        ax.plot(phase_rf_hi[order], K_hi[order], "r-", lw=1.5, label="separatriz (teoria)")
        ax.plot(phase_rf_lo[order], K_lo[order], "r-", lw=1.5)

        ax.set_title(f"{snap['label']}\nz = {snap['z_m']*100:.2f} cm")
        ax.set_xlabel("fase RF (deg)")
        ax.set_xlim(-180, 180)
        ax.grid(alpha=0.3)
        if j == 0:
            ax.legend(loc="upper right", fontsize=8)

    axes[0].set_ylabel("energia cinetica (MeV)")
    fig.suptitle("Grafica del ojo: espacio de fases + separatriz analitica")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


# ---------------------------------------------------------------------------
# Generador del haz DC de inyeccion
# ---------------------------------------------------------------------------

def build_dc_beam(
    frequency,
    kinetic_energy_MeV,
    current_A,
    n_macroparticles,
    mass_MeV=e_mass,
    charge=-1,
    x_size_mm=0.0,
    xp_size_mrad=0.0,
    y_size_mm=0.0,
    yp_size_mrad=0.0,
    seed=None,
):
    rng = np.random.default_rng(seed)

    pc_MeV = kinetic_energy_to_pc(kinetic_energy_MeV, mass_MeV)

    # Fase uniforme en un periodo de RF -> tiempo de llegada uniforme.
    phase = rng.uniform(0.0, 2 * np.pi, n_macroparticles)
    period_ns = rf_period_ns(frequency)
    t_ns = phase / (2 * np.pi) * period_ns
    t_mm_over_c = t_ns * rft.ns  # conversion a la unidad interna de RF-Track

    x = rng.normal(0.0, x_size_mm, n_macroparticles) if x_size_mm > 0 else np.zeros(n_macroparticles)
    xp = rng.normal(0.0, xp_size_mrad, n_macroparticles) if xp_size_mrad > 0 else np.zeros(n_macroparticles)
    y = rng.normal(0.0, y_size_mm, n_macroparticles) if y_size_mm > 0 else np.zeros(n_macroparticles)
    yp = rng.normal(0.0, yp_size_mrad, n_macroparticles) if yp_size_mrad > 0 else np.zeros(n_macroparticles)

    Pc = np.full(n_macroparticles, pc_MeV)

    X = np.column_stack([x, xp, y, yp, t_mm_over_c, Pc])

    # Poblacion real de electrones contenida en un periodo de RF.
    period_s = period_ns * 1e-9
    real_population = current_A * period_s * C

    bunch = rft.Bunch6d(mass_MeV, real_population, charge, X)
    return bunch


# ---------------------------------------------------------------------------
# Extraccion de propiedades del haz
# ---------------------------------------------------------------------------

def _circular_std(phase_rad):
    """Desviacion estandar circular (evita el problema de wrap en +/-180 deg)."""
    if len(phase_rad) == 0:
        return np.nan
    mean_cos = np.mean(np.cos(phase_rad))
    mean_sin = np.mean(np.sin(phase_rad))
    R = np.hypot(mean_cos, mean_sin)
    R = min(R, 1.0)
    return np.sqrt(-2 * np.log(R)) if R > 0 else np.inf


def beam_properties(bunch, n_injected=None, frequency=None):
    info = bunch.get_info()
    X = bunch.get_phase_space("%t %Pc")
    t_mm_over_c = X[:, 0]
    Pc = X[:, 1]

    mass = bunch[0].mass if len(bunch) > 0 else e_mass
    kinetic_energy = np.sqrt(Pc**2 + mass**2) - mass

    phase_spread_rms_deg = None
    if frequency is not None and len(bunch) > 0:
        t_ns = t_mm_over_c / rft.ns
        phase_rad = 2 * np.pi * frequency * (t_ns * 1e-9)
        phase_spread_rms_deg = float(np.degrees(_circular_std(phase_rad)))

    # OJO: `info.transmission` de RF-Track es el numero de particulas REALES
    # restantes (no una fraccion) -- ver changelog 2.3.3: "transport tables
    # now return transmission in number of particles". Para obtener la
    # fraccion hay que dividir por la poblacion real inyectada.
    real_particles_remaining = float(info.transmission)

    props = {
        "n_macroparticles": len(bunch),
        "mean_kinetic_energy_MeV": float(info.mean_K),
        "peak_kinetic_energy_MeV": float(np.max(kinetic_energy)) if len(kinetic_energy) else np.nan,
        "min_kinetic_energy_MeV": float(np.min(kinetic_energy)) if len(kinetic_energy) else np.nan,
        "energy_spread_rms_MeV": float(info.sigma_E),
        "energy_spread_fwhm_MeV": _fwhm(kinetic_energy),
        "phase_spread_rms_deg": phase_spread_rms_deg,
        "real_particles_remaining": real_particles_remaining,
    }
    if n_injected:
        props["transmission_fraction"] = real_particles_remaining / n_injected

    return props


def _fwhm(values, bins=100):
    """FWHM aproximado de una distribucion de valores mediante histograma."""
    values = np.asarray(values)
    if values.size == 0:
        return np.nan
    hist, edges = np.histogram(values, bins=bins)
    if hist.max() == 0:
        return 0.0
    half = hist.max() / 2.0
    above = np.where(hist >= half)[0]
    centers = 0.5 * (edges[:-1] + edges[1:])
    return float(centers[above[-1]] - centers[above[0]])


# ---------------------------------------------------------------------------
# Autotest de este tramo: Volume vacio (con un Drift de verificacion)
# ---------------------------------------------------------------------------

def _selftest_cavity_phase_scan():
    frequency = 2856e6
    A = 0.5
    theta = 2 * np.pi / 3
    N = 30
    mass = e_mass
    kinetic_energy_MeV = 50.0  # ultra-relativista, para minimizar el phase-slip
    Pc = kinetic_energy_to_pc(kinetic_energy_MeV, mass)
    period_ns = rf_period_ns(frequency)
    T = safe_tracking_options(frequency)

    for label, cavity_cls, amplitude_factor in [
        ("TW (ConstantBetaCavity)", ConstantBetaCavity, 1.0),
        ("SW (StandingWaveCavity)", StandingWaveCavity, 0.5),
    ]:
        cav = cavity_cls(frequency, beta_ph=1.0, A=A, phase_advance=theta, number_of_cells=N)
        print(f"=== Autotest de sincronismo: {label}, beta_ph=1 ===")
        print(f"  E0 = {cav.E0/1e6:.3f} MV/m   L = {cav.length_m:.4f} m")

        # amplitude_factor: en SW solo la mitad del campo (la componente
        # co-viajera) contribuye a la ganancia neta de energia.
        expected_peak_MeV = amplitude_factor * cav.E0 * cav.length_m / 1e6

        max_dev = 0.0
        for phase_deg in range(0, 360, 30):
            t_mm_over_c = (phase_deg / 360.0) * period_ns * rft.ns
            X = np.array([[0.0, 0.0, 0.0, 0.0, t_mm_over_c, Pc]])
            bunch_in = rft.Bunch6d(mass, 1.0, -1, X)

            V = rft.Volume()
            V.add(cav, 0.0, 0.0, 0.0)
            V.set_s0(0.0)
            V.set_s1(cav.length_m)
            bunch_out = V.track(bunch_in, T)

            Pc_out = bunch_out.get_phase_space("%Pc")[0, 0]
            dE = Pc_out - Pc
            expected = expected_peak_MeV * np.cos(np.radians(phase_deg) + np.pi)  # +pi: convencion de signo
            dev = abs(dE - expected)
            max_dev = max(max_dev, dev)

        print(f"  Maxima desviacion simulada vs. teorica: {max_dev:.5f} MeV (pico esperado: {expected_peak_MeV:.3f} MeV)")
        assert max_dev < 0.02 * expected_peak_MeV, f"{label}: no reproduce el coseno esperado."
        print("  OK\n")


def _selftest():
    frequency = 2856e6  # S-band, como en los ejemplos del paper
    kinetic_energy_MeV = kinetic_energy_from_beta(0.4)  # ~ beta_inj = 0.4

    beam_in = build_dc_beam(
        frequency=frequency,
        kinetic_energy_MeV=kinetic_energy_MeV,
        current_A=0.150,  # 150 mA, como en el ejemplo ARCIS del paper
        n_macroparticles=20000,
        seed=42,
    )

    print("=== Haz de entrada (DC, uniforme en fase) ===")
    for k, v in beam_properties(beam_in, frequency=frequency).items():
        print(f"  {k}: {v}")

    # Cavidad de bunching real: onda ESTACIONARIA, beta_ph < 1, tipica de
    # la seccion de bunching de baja energia del paper (Sec. 3.2-3.3).
    #
    # OJO: con A=0.3 (valor usado en versiones anteriores) la frenada
    # maxima de esta cavidad (~0.064 MeV) SUPERA la energia cinetica de
    # inyeccion (~0.047 MeV): algunas particulas caen hasta el 38% de su
    # energia dentro de la cavidad, un punto numericamente al limite que
    # puede colgar/matar el kernel sin traceback (visto en la practica).
    # Se baja A a 0.1 para dejar margen comodo; ver check_capture_margin().
    beta_ph = 0.5
    A = 0.1  # antes: 0.3 (demasiado fuerte para beta_inj=0.4, ver nota arriba)
    N_cells = 5
    theta = 2 * np.pi / 3
    cavity = StandingWaveCavity(
        frequency, beta_ph=beta_ph, A=A, phase_advance=theta, number_of_cells=N_cells
    )
    print(f"\nCavidad SW: beta_ph={beta_ph}, A={A}, N={N_cells} celdas, "
          f"L={cavity.length_m*100:.2f} cm, E0={cavity.E0/1e6:.2f} MV/m")

    ok, max_decel_MeV, margin_ratio = check_capture_margin(cavity, kinetic_energy_MeV)
    print(f"  Margen de captura: frenada_max={max_decel_MeV:.4f} MeV, "
          f"KE_inj={kinetic_energy_MeV:.4f} MeV, ratio={margin_ratio:.2f} "
          f"({'OK' if ok else 'INSUFICIENTE'})")
    if not ok:
        raise RuntimeError(
            "Margen de captura insuficiente: ajusta A, beta_inj o N antes de trackear "
            "(ver aviso de check_capture_margin() arriba)."
        )

    V = rft.Volume()
    V.add(cavity, 0.0, 0.0, 0.0)
    V.set_s0(0.0)
    V.set_s1(cavity.length_m)
    T = safe_tracking_options(frequency)

    n_injected = beam_in.get_info().transmission  # poblacion real inyectada (sin perdidas aun)

    # V.track() directo: StandingWaveCavity ahora es un elemento NATIVO
    # (RF_FieldMap_1d_CINT), no un UserField con callback Python por paso,
    # asi que ya no hace falta track_in_batches() para evitar el segfault
    # visto antes bajo carga alta. track_in_batches() se deja disponible
    # en el script por si se necesita para otros elementos UserField.
    beam_out = V.track(beam_in, T)

    print("\n=== Haz de salida (tras la cavidad de bunching SW) ===")
    for k, v in beam_properties(beam_out, n_injected=n_injected, frequency=frequency).items():
        print(f"  {k}: {v}")


def _demo_eye_diagram():
    """Genera un ejemplo real de 'grafica del ojo' con la configuracion
    segura ya validada (beta_inj=0.8, cavidad SW beta_ph=0.5, A=0.1, N=5),
    mostrando la evolucion del espacio de fases celda a celda, con la
    separatriz analitica superpuesta."""
    frequency = 2856e6
    beta_ph = 0.5
    A = 0.1
    N_cells = 5
    theta = 2 * np.pi / 3

    kinetic_energy_MeV = kinetic_energy_from_beta(0.45)  # beta_inj proximo a beta_ph=0.5: inyeccion fisicamente acorde
    beam_in = build_dc_beam(frequency, kinetic_energy_MeV, 0.150, 500, seed=42)

    cavity_probe = StandingWaveCavity(frequency, beta_ph, A=A, phase_advance=theta, number_of_cells=N_cells)
    ok, max_decel_MeV, margin_ratio = check_capture_margin(cavity_probe, kinetic_energy_MeV)
    print(f"Margen de captura: ratio={margin_ratio:.2f} ({'OK' if ok else 'INSUFICIENTE'})")

    print("Trackeando celda a celda...")
    snapshots = track_with_snapshots(frequency, beta_ph, A, theta, N_cells, beam_in)

    output_path = "/mnt/user-data/outputs/eye_diagram_demo.png"
    plot_eye_diagrams(snapshots, frequency, beta_ph, A, theta, output_path, is_standing_wave=True)
    print(f"Grafica guardada en: {output_path}")
    return output_path


if __name__ == "__main__":
    _selftest_cavity_phase_scan()
    _selftest()
