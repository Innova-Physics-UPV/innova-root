from Prototype import Analyzer
import numpy as np

def compare_values(calculated, reference, rtol=1e-9, atol=1e-12):
    if np.isinf(calculated) or np.isinf(reference) or np.isnan(calculated) or np.isnan(reference):
        return False
    return abs(calculated-reference) <= atol + rtol * abs(reference)

def validate_property(name, calculated, reference, rtol=1e-9, atol=1e-12):
    calculated = float(calculated)
    reference = float(reference)

    result = {
    "name": name,
    "calculated":calculated,
    "reference": reference,
    "absolute_error": abs(calculated-reference),
    "passed": compare_values(calculated,reference,rtol,atol)
}
    return result

def validate_phase_spread(df_particles, df_sim):
    calculated = Analyzer.circular_phase_spread(df_particles)
    reference = df_sim.Take["double"]("phase_spread_rms_deg").GetValue()[0]

    return validate_property("phase_spread_rms_deg", calculated, reference)

def validate_mean_kinetic_energy(df_particles, df_sim):
    calculated = df_particles.Mean("Ek_MeV").GetValue()
    reference = df_sim.Take["double"]("mean_kinetic_energy_MeV").GetValue()[0]

    return validate_property("mean_kinetic_energy_MeV", calculated, reference)

def build_validation_report(results):
    total = len(results)
    passed = sum(result["passed"] for result in results)
    failed = total - passed

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "status": "PASS" if total > 0 and failed == 0 else "FAIL",
        "results": results
    }