# Procedencia y fidelidad

Reconstruido el 13/10/2026 para Luiscarlos. Los dos originales de Javier fueron suministrados
posteriormente y se incluyen intactos. Para los demás archivos, «fiel» significa
fiel al comportamiento documentado, no identidad textual.

Fuente prioritaria: conversación «Formación en ROOT», ID
6a6b9708-6e54-83eb-b7ed-50ef86ee36de. La lectura devuelve cinco turnos recientes,
sin cursor anterior. Varias respuestas solo contienen referencias internas sin
texto. Confirma prototipo RF-Track y Geant4 conceptual; no recupera el código.

Fuente técnica consultada íntegramente como texto mediante Google Drive:
https://drive.google.com/file/d/1ey-xmP4LPcnGDvEYhGffHSfoZNva6Ios/view
ROOT_Data_Analysis_Workflow_for_RF_Track_and_Geant4.pdf, Luiscarlos Hernández,
septiembre 2026. No se incluye copia binaria en el proyecto. La extracción puede
tener artefactos tipográficos. No se ha inspeccionado visualmente el PDF.

| Archivos | Base | Clasificación |
|---|---|---|
| day02/trees.C, trees.py | §6.1–6.4 | Comportamiento fiel; datos y código nuevos |
| day03/numpy_root.py, chain.C | §6.5, §6.7–6.10 | Flujo fiel; matriz de ejemplo nueva |
| day04/uproot_io.py | §7.2–7.7 | Flujo fiel; mkrntuple explícito sustituye asignación dependiente de versión |
| day05/simulated_scan.py | §8 | Esquema y 6x100 fieles; gradientes/fases, semilla y fórmula son aproximaciones |
| day06/rftrack_scan.py | §9 | Parámetros, matriz y esquema del PDF; adaptador implementado contra originales |
| day06/javier_adapter.py, ADAPTER.md | Firmas y selftest de Funciones.py | Wrapper nuevo; sin modificar originales |
| external/javier/Funciones.py y notebook | Archivos suministrados | Copias exactas verificadas por SHA-256 |
| day07/analyze.py, analyze.C | §10.3–10.5 | Operaciones fieles; histograma r2 y exportación JSON nuevos |
| innova/io.py, tests/* | Necesidades del proyecto | Infraestructura nueva |
| docs/reference_results.csv | Tabla §10.5 | Transcripción documental; no ejecución nueva |

La correspondencia day02–day07 sigue la petición actual y el orden de secciones
del PDF; no se han recuperado nombres originales de archivos ni directorios.
Campos añadidos en día 6: beta_inj y n_macroparticles_output para hacer explícitos
supuestos y pérdidas. En escritura se elige TTree por compatibilidad de análisis;
el formato definitivo sigue pendiente en el documento. No hay implementación
Geant4 porque la fuente solo propone un flujo conceptual.

Búsquedas exactas en Drive y por nombres en Documents no localizaron fuentes
Javier inicialmente. Posteriormente el usuario suministró ambos desde Downloads;
las copias están incluidas y registradas en docs/ORIGINALS.json.

Documentación oficial contrastada:
https://uproot.readthedocs.io/en/stable/basic.html
https://uproot.readthedocs.io/en/stable/uproot.writing.writable.WritableDirectory.html
https://root.cern.ch/doc/master/classROOT_1_1RDataFrame.html

El notebook tiene cuatro celdas de código, kernel Python (RF-Track), Python 3.12.3.
Se inspeccionaron las fuentes sin ejecutar celdas; sus salidas guardadas no son
pruebas realizadas en este entorno. El notebook cambia beta/A/celdas respecto
a Funciones._selftest y al PDF, conservándose intacto. El barrido solicitado se
mantiene conforme al PDF y usa las firmas y el Volume del selftest de Funciones.
La población física inicial es el denominador de transmisión; no las 20000
macropartículas. No se identificó una versión exacta de RF-Track en la metadata.
