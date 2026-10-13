"""Día 3: leer dos TTree como uno. Ejecutar antes day03.numpy_root."""
import ROOT

chain = ROOT.TChain('particles')
chain.Add('data/day03_0.root')
chain.Add('data/day03_1.root')

# No fusionamos los archivos: TChain presenta una vista conjunta de sus entradas.
print('Entradas conjuntas:', chain.GetEntries())  # 3 + 3 = 6.
for particle in chain:
    print(particle.energy)
