"""Día 7: leer el resultado del día 6 y analizarlo con RDataFrame."""
import ROOT

file_path = 'data/rftrack_amplitude_scan.root'

# Cada RDataFrame lee uno de los dos árboles del archivo.
simulations = ROOT.RDataFrame('simulations', file_path)
particles = ROOT.RDataFrame('particles', file_path)
print('Simulaciones:', simulations.Count().GetValue())
print('Partículas:', particles.Count().GetValue())

# AsNumpy entrega las columnas como arrays para mostrarlas desde Python.
columns = simulations.AsNumpy([
    'run_id', 'A', 'mean_kinetic_energy_MeV', 'energy_spread_rms_MeV',
    'phase_spread_rms_deg', 'transmission_fraction',
])
for i in range(len(columns['run_id'])):
    print('run_id:', columns['run_id'][i], 'A:', columns['A'][i],
          'energía media:', columns['mean_kinetic_energy_MeV'][i],
          'sigma energía:', columns['energy_spread_rms_MeV'][i],
          'sigma fase:', columns['phase_spread_rms_deg'][i],
          'transmisión:', columns['transmission_fraction'][i])

# Filter selecciona simulaciones; Mean calcula la media de la columna seleccionada.
selected = simulations.Filter('A >= 0.10')
print('Simulaciones con A >= 0.10:', selected.Count().GetValue())
print('Su energía media:', selected.Mean('mean_kinetic_energy_MeV').GetValue())

# Relacionar los árboles por run_id, no por su número de fila.
for i in range(len(columns['run_id'])):
    run_id = int(columns['run_id'][i])
    run_particles = particles.Filter(f'run_id == {run_id}')
    print('Partículas de run_id', run_id, ':', run_particles.Count().GetValue())

# Define crea una columna; Histo1D calcula su distribución.
# Pc es momento, NO energía cinética. Evitamos confundir esas magnitudes.
with_radius = particles.Define('r2', 'x*x + y*y')
histogram = with_radius.Histo1D(('r2', 'x^2 + y^2;mm^2;Entradas', 100, 0., 100.), 'r2')
output = ROOT.TFile('data/day07_analysis.root', 'RECREATE')
histogram.GetValue().Write()
output.Close()
print('Histograma guardado: data/day07_analysis.root')
