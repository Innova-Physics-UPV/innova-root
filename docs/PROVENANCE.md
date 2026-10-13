# Procedencia de la versión simplificada

Los dos archivos de external/javier/ son copias exactas suministradas por el
usuario. SHA-256 en ORIGINALS.json. Ninguna función de Javier fue reescrita.
La conversación Formación en ROOT (6a6b9708-6e54-83eb-b7ed-50ef86ee36de) y el PDF
son fuentes para reconstruir los ejemplos, no para recuperar su texto original.
La lectura del historial devolvió cinco turnos, algunas respuestas incompletas.

Documento técnico de Luiscarlos, septiembre 2026, consultado como texto:
https://drive.google.com/file/d/1ey-xmP4LPcnGDvEYhGffHSfoZNva6Ios/view
No se incluye una copia binaria del PDF ni se ha realizado inspección visual.

| Archivos | Fuente / grado de fidelidad |
|---|---|
| day02/trees.py y trees.C | PDF §6.1–6.4: conceptos fieles; código y cinco filas nuevos |
| day03/numpy_root.py, chain.py, chain.C | §6.5, §6.7–6.10: flujo fiel; datos nuevos |
| day04/*.py | §7: operaciones fieles; ejemplos cortos nuevos y mkrntuple explícito |
| day05/simulated_scan.py | §8: esquema y 6x100 fieles; fórmula, gradientes, fases y RNG de ejemplo |
| day06/rftrack_scan.py | §9 y Funciones._selftest: llamadas originales directas; barrido del PDF |
| day07/analyze.py, analyze.C | §10: análisis fiel; histograma r2 nuevo |
| tests/*, README y guías | Material nuevo, separado de los ejemplos |
| docs/reference_results.csv | Tabla §10.5 transcrita; no salida generada aquí |

Esta revisión elimina el adaptador y el módulo innova/io.py; cada script muestra
sus operaciones en el propio archivo. En día 5 se usa ahora un RNG seed=42 para
todo el ejemplo ficticio, por lo que sus números no son idénticos al ZIP anterior.
El día 6 conserva semilla 42 por run y parámetros físicos del workflow anterior.
Los comandos --adapter/--output y la exportación JSON de día 7 se retiraron para
reducir la interfaz; el JSON de procedencia de día 6 se conserva como bloque final.

El notebook suministrado usa beta=.3, A=1.2 y ocho celdas en el selftest, mientras
Funciones._selftest y el PDF usan beta=.4, A=.1 y cinco celdas. Se conservan las
fuentes intactas; el barrido de la formación procede del PDF. Los comentarios
del notebook no siempre coinciden con sus valores. No se ejecuta automáticamente.

Unidades originales: x/y mm, xp/yp mrad, t mm/c (dividir por rft.ns da ns),
Pc MeV/c, energías MeV, fase grados y A adimensional. Transmisión es población
física restante dividida por población física inicial. FWHM es el estimador por
histograma original; fase RMS se calcula con dispersión circular original.
Geant4 sigue conceptual: no hay implementación física inventada.

Referencias oficiales contrastadas en la versión anterior:
https://uproot.readthedocs.io/en/stable/basic.html
https://root.cern.ch/doc/master/classROOT_1_1RDataFrame.html
