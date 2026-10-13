# innova-root: aprender ROOT paso a paso

Ejemplos de los días 2–7 de la formación de Luiscarlos. Cada script se lee de
arriba abajo. Los primeros días introducen un concepto cada vez; los últimos
repiten las mismas operaciones con datos de simulación reales.

Los originales de Javier están intactos en external/javier/. Los demás ejemplos
son reconstrucciones del documento técnico, no copias recuperadas del código
original de formación. Ver docs/PROVENANCE.md.

## Preparar el entorno

Desde la raíz del proyecto en WSL:
```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```
Para ejemplos PyROOT y RF-Track, instalar en el MISMO Python una distribución
compatible de ROOT (incluye PyROOT) y RF-Track. En tu WSL el workflow anterior
funcionó con RF-Track 2.7.3. Se proporciona requirements-rftrack.txt para fijarla:
```
python -m pip install -r requirements-rftrack.txt
```
ROOT se instala aparte; su distribución Linux por pip es `root` y está marcada
como alfa. También puede usarse ROOT desde conda u otra instalación compatible.
Comprobar: `python -c "import ROOT, uproot, RF_Track"`.

## Orden de estudio

Ejecutar los comandos desde la raíz, conservando la .venv activa.
`python -m day02.trees` significa «ejecutar el archivo day02/trees.py como módulo».
Es la forma que usaremos todos los días para que Python encuentre las carpetas.

| Día | Qué abrir y ejecutar | Concepto |
|---|---|---|
| 02 | `python -m day02.trees` | TFile, TTree, Branch, Fill, Write y lectura |
| 03 | `python -m day03.numpy_root` | NumPy, FromNumpy, Count, Mean, Filter, Define, Snapshot |
| 03 | `python -m day03.chain` | Dos archivos, un TChain; 6 entradas |
| 04 | `python -m day04.write_tree` | Escribir TTree con mktree y extend |
| 04 | `python -m day04.write_ntuple` | Elegir explícitamente RNTuple |
| 04 | `python -m day04.read` | Recuperar ramas como arrays |
| 04 | `python -m day04.multiple_files` | concatenate e iterate; ejecutar write_tree primero |
| 05 | `python -m day05.simulated_scan` | Barrido ficticio y relación por run_id |
| 06 | `python -m day06.rftrack_scan` | Llamadas directas a Javier y escritura ROOT |
| 07 | `python -m day07.analyze` | Leer el resultado real y analizarlo con RDataFrame |

No hace falta estudiar los tests o los originales completos para empezar día 2.
Cada archivo introduce sus conceptos con comentarios junto a las instrucciones.
Hay una breve explicación en el README de cada día.

## Qué hace el barrido real

day06/rftrack_scan.py contiene todo el recorrido: parámetros -> build_dc_beam
-> StandingWaveCavity -> Volume.track -> get_phase_space y beam_properties
-> NumPy -> uproot. Ya no hay un adaptador ni un módulo de escritura intermedio.
La conversión a columnas y la escritura repiten el código aprendido en día 5.

Se mantienen A=[.08,.10,.12], 20000 macropartículas/run, beta_inj=.4,
2856 MHz, .150 A, beta_ph=.5, cinco celdas, avance 2*pi/3 y seed=42.
El haz es de electrones. A es adimensional. Se usa la población FÍSICA inicial
para calcular transmisión, no el número de macropartículas.

Los resultados tienen dos tablas: simulations contiene una fila por run;
particles contiene una fila por macropartícula. run_id conecta ambas.
El JSON de procedencia es un bloque opcional al final; no interviene en el tracking.

El notebook de Javier usa otros parámetros en varias celdas: beta=.3, A=1.2 y
ocho celdas. Se conserva sin ejecutar ni corregir. El barrido reconstruido usa
los parámetros del PDF, coherentes con Funciones._selftest; mantiene su control
de margen. Un resultado con pérdida total puede producir métricas indefinidas
y requiere revisión, no sustituimos sus valores silenciosamente.

Las salidas se guardan en data/. RECREATE reemplaza archivos anteriores con el
mismo nombre: cambia el nombre en el script si deseas conservar otro resultado.
Los .root, .venv y cachés están excluidos de Git. Los originales de Javier también
se excluyen automáticamente, pero el ZIP los incluye; `git add -f` permite
versionarlos expresamente, como ya hiciste en tu repositorio.

## C++ opcional

Tras crear data/ (los ejemplos Python lo hacen):
```
root -l -b -q 'day02/trees.C("data/day02.root")'
root -l -b -q 'day03/chain.C()'
root -l -b -q 'day07/analyze.C("data/rftrack_amplitude_scan.root")'
```
La macro chain necesita ejecutar antes day03.numpy_root.

## Comprobaciones separadas del material de estudio

```
python tests/run_local.py
```
Este comando usa el lector local de uproot para las mismas comprobaciones que
`python -m unittest discover -s tests -v`, sin depender del socket interno fsspec.
Las pruebas RF-Track usan un doble de API: comprueban el código y los datos,
no la física. Las pruebas PyROOT se omiten si falta ROOT.
Ver docs/VERIFICATION.md para distinguir esta versión simplificada del barrido
anterior que sí ejecutaste en WSL. No se ha publicado nada en GitHub.

## Actualizar desde el ZIP anterior

Extraer esta versión en una carpeta nueva: no mezclar los ZIP, porque la versión
anterior tenía archivos que ahora se han eliminado. Copiar tus resultados propios
y tu entorno solo si los necesitas. Los nuevos ejemplos no admiten los antiguos
argumentos --adapter/--output; las rutas son variables explícitas en cada script.
