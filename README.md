# innova-root — reconstrucción documental, días 2–7

Proyecto de formación de Luiscarlos para el workflow ROOT/RF-Track.
Se reconstruyen ejemplos y esquemas a partir del PDF y del historial disponible.
Incluye los dos originales de Javier, conservados byte a byte; los ejemplos de formación son reconstrucciones. Ver docs/PROVENANCE.md para
fidelidad por archivo y docs/VERIFICATION.md para comprobaciones reales.

## Instalación

Python 3.10+ y entorno virtual recomendado:
```
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```
ROOT/PyROOT y RF-Track se instalan por separado usando distribuciones compatibles
con el Python elegido. No se sustituyen por paquetes homónimos de PyPI. Comprobar:
```
python -c "import ROOT; print(ROOT.gROOT.GetVersion())"
python -c "import RF_Track; print(RF_Track)"
```
Para C++ usar la consola de ROOT o un entorno con root-config. Los scripts
Python se ejecutan como módulos desde la raíz para resolver innova.

## Recorrido

| Día | Tema | Comando |
|---|---|---|
| 02 | TFile/TTree, Branch, Fill, lectura | `python -m day02.trees` |
| 03 | TChain, PyROOT, FromNumpy, Snapshot, AsNumpy | `python -m day03.numpy_root` |
| 04 | uproot, TTree/RNTuple, concatenate/iterate | `python -m day04.uproot_io` |
| 05 | Barrido simulado, 6 runs x 100 partículas | `python -m day05.simulated_scan` |
| 06 | Barrido RF-Track real, A=.08,.10,.12; 20000 inyectadas/run | `python -m day06.rftrack_scan` |
| 07 | RDataFrame: Count, Filter, Mean, Define, Histo1D, AsNumpy | `python -m day07.analyze` |

Macros C++ (crear data antes; día 3 requiere sus archivos Python):
```
root -l -b -q 'day02/trees.C("data/day02.root")'
root -l -b -q 'day03/chain.C()'
root -l -b -q 'day07/analyze.C("data/rftrack_amplitude_scan.root")'
```
El día 6 incluye Funciones.py, Sweeps y Operaciones.ipynb y un adaptador
implementado contra sus firmas reales; ejecutar `python -m day06.rftrack_scan`. No contiene una cavidad inventada ni resultados sintéticos
etiquetados como reales. Sus parámetros y resultados de referencia provienen
del PDF. El código permite pérdidas y registra filas de salida reales.

Los scripts recrean sus archivos de salida: usar rutas nuevas para conservar
resultados existentes. Los .root generados no se incluyen en el ZIP ni en Git.

## Datos

Día 5: simulations(run_id, gradient, phase, mean_energy, sigma_energy) y
particles(run_id, x, y, energy). Fórmula y parámetros de ejemplo aproximados;
unidades no físicas. Día 6: simulations(parámetros y propiedades del haz) y
particles(run_id, x, xp, y, yp, t, Pc). Ver columnas en rftrack_scan.py y unidades
documentadas desde el original en ADAPTER.md. run_id es único en simulations y clave
de relación en particles; no se unen tablas por el número de fila.

## Pruebas
```
python -m unittest discover -s tests -v
python -m compileall -q innova day02 day03 day04 day05 day06 day07 tests
```
Las pruebas de uproot requieren requirements.txt. Las pruebas PyROOT se omiten
con motivo explícito si falta ROOT. La prueba del adaptador con un doble de
prueba solo valida orquestación y esquema, no física RF-Track.
Si el entorno restringe sockets internos de fsspec, ejecutar
`python tests/run_local.py`: usa un lector de archivos local para las mismas pruebas.

Prueba real pendiente: instalar RF-Track y ROOT compatibles, ejecutar día 6 y día 7,
verificar tres runs, 20000 inyectadas/run, las filas realmente supervivientes y
la recuperación A=.10 por run_id. Comparar métricas con la tabla del PDF teniendo
en cuenta versión, semilla y redondeo. No existe publicación en GitHub.

## Originales incorporados

Los archivos de external/javier/ son los proporcionados por el usuario,
sin modificaciones, con hashes registrados en docs/ORIGINALS.json. Las copias
originales se incluyen en el ZIP local, aunque .gitignore evita añadirlas a Git
automáticamente. El adaptador nuevo es day06/javier_adapter.py.

El notebook tiene valores distintos del PDF y de Funciones._selftest:
beta_inj=.3, A=1.2 y ocho celdas. La reconstrucción mantiene el barrido del PDF
con beta_inj=.4 y cinco celdas. No se ejecuta el notebook automáticamente ni se
editan sus celdas. Notebook opcional: matplotlib y Jupyter, separados del pipeline;
la demo conserva su ruta original /mnt/user-data/outputs.
