# Verificación realizada — 13/10/2026

Entorno: Windows, Python 3.12 (runtime disponible en Codex). Dependencias
instaladas en work, fuera del proyecto entregado: uproot 5.7.7, NumPy 2.5.4,
Awkward 2.14.0. requirements.txt admite otras versiones compatibles; no se
garantiza haberlas probado todas.

## Resultado

Tras incorporar los originales: 11 pruebas, 10 aprobadas y 1 omitida,
sin fallos en la ejecución final. Se utilizó el lector local de uproot
MultithreadedFileSource, sin cambiar los datos ni las aserciones de las pruebas.
Equivalente reproducible: `python tests/run_local.py`.

- Adaptador externo ausente: error explícito, sin fallback a datos simulados.
- Validación: detecta run_id huérfanos/duplicados, longitudes y datos no finitos.
- Barrido simulado: 6 simulaciones, 600 partículas; resumen y reproducibilidad.
- Contrato día 6 mediante doble de prueba: tres amplitudes, 20000 por run,
  esquema y 60000 filas. Esto NO ejecuta ni valida RF-Track.
- Escritura/lectura TTree y RNTuple: clase y columnas verificadas.
- concatenate: 10 entradas; iterate: bloques [2,2,1,2,2,1].
- Round-trip simulations/particles: arrays exactos y selección de un run por
  parámetros con 100 partículas asociadas.
- Interoperabilidad PyROOT: omitida porque ROOT no está instalado.

Pruebas añadidas tras recibir las fuentes:

- SHA-256 y comparación byte a byte de ambos originales; sintaxis de las cuatro
  celdas de código del notebook comprobada sin ejecutar el notebook.
- Helpers originales: energía/beta, campo/amplitud, tiempo interno, semilla,
  población física inicial y opciones de 40 pasos por periodo.
- Adaptador real llamando al Python original con un doble de RF-Track: Volume,
  tres runs, pérdidas de prueba del 50%, y denominador inicial correcto aunque
  el doble modifique la población de entrada. No valida física ni API binaria.
- Configuración beta=.3, A=1.2 y 8 celdas del notebook: el helper original señala
  margen insuficiente y el adaptador aborta antes del tracking.

También se ejecutó el CLI del día 5: 6 entradas en simulations y 600 en
particles. `compileall` pasó en todos los módulos Python. Esto solo comprueba
sintaxis, no imports ROOT ni firmas del código externo.

La primera ejecución de las pruebas de archivos encontró un bloqueo de permisos
en el TEMP del sandbox. Se repitió con autorización y temporales en work;
la ejecución inicial pasó. En esta actualización la lectura por defecto de
uproot quedó bloqueada en el socket interno del bucle asyncio/fsspec del sandbox.
La elevación fue rechazada por la política actual. Se completaron las mismas
pruebas con MultithreadedFileSource, que lee los archivos locales sin ese socket.
No se han cambiado las aserciones para ocultar fallos.

## Pendiente

- Macros C++: no compiladas ni ejecutadas; falta ROOT/root-config.
- Día 2 PyROOT y día 3 FromNumpy/TChain: no ejecutados; falta ROOT.
- Día 6 RF-Track real: no ejecutado; falta RF_Track. Originales y adaptador ya incluidos.
- Día 7 RDataFrame completo e histogramas: no ejecutados; falta ROOT y salida real.
- Unidades, firmas, especie, configuración de Volume, opciones y semilla:
  comprobadas en los originales. Compatibilidad binaria, pérdidas físicas y
  reproducción numérica pendientes de ejecutar RF-Track real.

Los números de docs/reference_results.csv son referencias del PDF, no resultados
obtenidos en estas pruebas. Ningún archivo .root de prueba se distribuye como
salida física de RF-Track. El ZIP solo contiene fuentes y documentación.

## Completar la verificación

1. Instalar ROOT/PyROOT compatibles con Python y ejecutar días 2–3 y las macros.
2. Identificar e instalar una versión RF-Track compatible; seguir day06/ADAPTER.md.
3. Ejecutar el día 6 con el adaptador real; comprobar esquema y procedencia JSON.
4. Ejecutar día 7; esperar 3 simulaciones, 2 con A>=.10 y, si no hay pérdidas,
   60000 partículas totales y 20000 para A=.10. Revisar pérdidas si difiere.
5. Comparar las métricas con el PDF usando tolerancias definidas por el equipo,
   no igualdad exacta con sus cifras redondeadas. Registrar versiones y hashes
   de los originales y del adaptador.
