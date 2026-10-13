# Verificación: versión simplificada

## Esta versión

8 pruebas ejecutadas: 6 aprobadas y 2 omitidas porque el entorno local de Codex
no tiene PyROOT. Sin fallos. Se usó MultithreadedFileSource de uproot para leer
archivos locales sin el socket interno de fsspec. Mismas aserciones y datos.
Python 3.12, NumPy 2.5.4, uproot 5.7.7; sintaxis Python comprobada con compileall.

Pruebas aprobadas:
- Día 4: formato TTree/RNTuple, columnas y cinco filas recuperadas.
- Día 4: concatenate de dos archivos, siete filas, iterate por bloques [2,2,1,2].
- Día 5: seis simulaciones, 600 partículas, resumen, selección por run_id,
  recuperación desde archivo y reproducibilidad de la semilla.
- Día 6: el script lineal importa y llama al Python ORIGINAL de Javier con un
  doble de RF-Track; verifica Volume, 20000 inyectadas por run y pérdidas
  artificiales del 50%. El denominador de transmisión permanece correcto aunque
  el doble modifique la población inicial. Esto NO valida simulación física.
- Originales: hashes intactos y sintaxis de cuatro celdas del notebook.
- Helpers originales con doble de API: conversión beta/energía, semilla,
  población física, campo/amplitud y margen de captura.

Pruebas omitidas: días 2–3 con PyROOT y análisis del día 7 con PyROOT.
Macros C++ no ejecutadas: falta ROOT. El tracking real de la NUEVA versión
lineal todavía no se ha ejecutado en este entorno; falta RF_Track.

## Verificación anterior por el usuario en WSL

El usuario ejecutó la versión anterior con adaptador usando RF-Track 2.7.3,
NumPy/uproot y PyROOT. Su salida confirmó tres runs, 60000 partículas, 20000
por run, transmisión 1 y métricas iguales al PDF tras redondeo. El filtro A>=.10
dio 0.05133478971009009 MeV. Esta evidencia se refiere al código ANTERIOR;
no se etiqueta como ejecución física del código simplificado.

La revisión conserva los parámetros y las llamadas físicas originales, pero
elimina las capas intermedias. Para completar la verificación de esta revisión,
ejecutar en tu WSL desde la raíz con el mismo entorno activo:
```
python tests/run_local.py
python -m day06.rftrack_scan
python -m day07.analyze
```
Esperar tres simulaciones, 60000 filas si no hay pérdidas y 20000/run. Comparar
con reference_results.csv y con la salida anterior; no exigir igualdad exacta
con cifras redondeadas del PDF. Las pruebas no ejecutan RF-Track real de forma
automática; los dos últimos comandos sí lo hacen y deben ejecutarse aparte.

El ZIP se comprueba mediante CRC y hashes del manifiesto. Contiene fuentes y
documentación; no distribuye datos ficticios como resultados físicos.
