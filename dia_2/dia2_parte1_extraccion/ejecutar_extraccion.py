"""Ejecuta la extracción de las fuentes y guarda cada una en
data/interim/ tal cual viene, sin limpiar (evidencia del paso de
extracción del día 2, separada de la limpieza).

Uso: python ejecutar_extraccion.py
"""

import logging

import config
import extract

logger = logging.getLogger(__name__)

FUENTES = [
    ("ventas", extract.extraer_ventas),
    ("productos", extract.extraer_productos),
    ("clientes", extract.extraer_clientes),
    ("inventario_actual", extract.extraer_inventario_actual),
    ("movimientos_inventario", extract.extraer_movimientos_inventario),
    ("campanas", extract.extraer_campanas),
]


def main():
    for nombre, extraer in FUENTES:
        df = extraer()
        ruta_salida = config.INTERIM_DIR / f"{nombre}.parquet"
        df.to_parquet(ruta_salida, index=False)
        logger.info("%s: %s filas -> %s", nombre, len(df), ruta_salida.name)


if __name__ == "__main__":
    main()
