# Adaptador a los originales de Javier

Los archivos suministrados por Luiscarlos están en external/javier/, copiados
byte a byte, sin editar. Sus hashes están en docs/ORIGINALS.json.
El adaptador nuevo day06/javier_adapter.py llama a las firmas comprobadas de
Funciones.py; el notebook se conserva como referencia y no se ejecuta.

| Función nueva del adaptador | Llamada al original |
|---|---|
| build_dc_beam(config) | build_dc_beam(frequency, kinetic_energy_MeV, current_A, n_macroparticles, seed=...) |
| StandingWaveCavity(config) | StandingWaveCavity(frequency, beta_ph, A, phase_advance, number_of_cells) |
| safe_tracking_options(config) | safe_tracking_options(frequency), por defecto 40 pasos por periodo |
| track_volume(...) | check_capture_margin; Volume.add, set_s0(0), set_s1(cavity.length_m), track |
| beam_properties(...) | beam_properties(beam_out, n_injected=población física inicial, frequency=...) |

Se captura la población inicial con beam_in.get_info().transmission ANTES del
tracking. El parámetro original n_injected NO significa macropartículas. El
adaptador conserva esa población aunque el tracking modifique el Bunch inicial.
El adaptador es para barrido secuencial; la paralelización requiere un proceso
independiente por trabajador.

La energía se calcula con kinetic_energy_from_beta(.4) del original. El haz es
de electrones: masa rft.electronmass, carga -1, tamaños transversales cero y fases
uniformes en un periodo RF; seed=42 en cada run. Se conservan 2856e6 Hz, .150 A,
20000 macropartículas, beta_ph=.5, cinco celdas, avance 2*pi/3 y A=[.08,.10,.12].
A es adimensional según normalized_amplitude_to_field: A=e*E*lambda/(m*c²).

Espacio de fases: x/y en mm, xp/yp en mrad, t en unidad interna mm/c,
Pc en MeV/c. t se conserva sin convertir a ns; el original usa t/rft.ns al
analizar. Energías en MeV y dispersión de fase circular en grados. FWHM conserva
la aproximación por histograma original, sin sustituirla por 2.355*sigma.

## Diferencias entre fuentes

Funciones._selftest usa beta_inj=.4, A=.1 y cinco celdas, coherente con el PDF.
La celda 1 del notebook recibido usa beta_inj=.3, A=1.2 y ocho celdas. Sus
comentarios todavía mencionan .4 y .1; tampoco aborta cuando el margen es
insuficiente. La demo usa A=1.2 y ocho celdas, pese al docstring de otra
configuración. El notebook no contiene el barrido [.08,.10,.12] de la formación;
ese barrido se reconstruye del PDF. No se corrigen estas diferencias en los
originales. La ruta /mnt/user-data/outputs de la demo se conserva en el notebook;
el pipeline reconstruido no la utiliza.

## Ejecutar

Desde la raíz con requirements.txt y RF-Track/PyROOT compatibles instalados:
```
python -m day06.rftrack_scan
python -m day07.analyze
```
No se necesita escribir otro adaptador. --adapter ruta.py sigue disponible para
versiones futuras. Se escribe TTree explícito y un JSON de procedencia con hashes
del adaptador y los originales. No se fuerzan 60000 filas si hay pérdidas.
El pipeline rechaza métricas no finitas: una pérdida total requiere definir una
política explícita para resúmenes indefinidos.

La integración está implementada contra las firmas originales. El tracking real
sigue sin ejecutar en este entorno, que carece de RF_Track y ROOT. Los dobles
de prueba verifican llamadas, población física y control de margen; no validan
la física, la API binaria ni la estabilidad del integrador.
