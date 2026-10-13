"""Escritura explícita de TTree y validación de la relación por run_id."""
from pathlib import Path
import numpy as np

def validate(simulations, particles):
    for table in (simulations, particles):
        if not table or 'run_id' not in table:
            raise ValueError('Cada tabla requiere run_id')
        lengths = {len(np.asarray(v)) for v in table.values()}
        if len(lengths) != 1:
            raise ValueError('Columnas de distinta longitud')
        for values in table.values():
            a = np.asarray(values)
            if a.ndim != 1 or a.dtype.kind not in 'iufb':
                raise ValueError('Solo columnas numéricas escalares')
            if not np.all(np.isfinite(a)):
                raise ValueError('Valores no finitos')
        if np.asarray(table['run_id']).dtype.kind not in 'iu':
            raise ValueError('run_id debe ser entero')
    ids = np.asarray(simulations['run_id'])
    if len(ids) != len(np.unique(ids)):
        raise ValueError('run_id duplicado en simulations')
    if not np.all(np.isin(particles['run_id'], ids)):
        raise ValueError('Partículas con run_id huérfano')

def save_results(path, simulations, particles):
    import uproot
    validate(simulations, particles)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with uproot.recreate(path) as f:
        for name, table in [('simulations', simulations), ('particles', particles)]:
            columns = {k: np.ascontiguousarray(v) for k, v in table.items()}
            tree = f.mktree(name, {k: v.dtype for k, v in columns.items()})
            tree.extend(columns)

def rows_to_columns(rows, integer_fields=('run_id',)):
    if not rows:
        raise ValueError('No hay simulaciones')
    return {key: np.asarray([row[key] for row in rows],
                           dtype=np.int64 if key in integer_fields else np.float64)
            for key in rows[0]}
