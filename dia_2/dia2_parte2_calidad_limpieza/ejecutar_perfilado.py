"""Perfila la calidad de las fuentes ya extraídas (data/interim/),
incluida la integridad referencial entre fuentes, y genera
reports/hallazgos_calidad.md.
"""

from datetime import datetime

import pandas as pd

import config
from quality import (
    formatear_integridad_markdown,
    formatear_perfil_markdown,
    perfilar,
    verificar_integridad_referencial,
)

FUENTES = [
    ("Ventas", "ventas", "venta_id"),
    ("Productos", "productos", "producto_id"),
    ("Clientes", "clientes", "cliente_id"),
    ("Inventario actual", "inventario_actual", ["producto_id", "bodega"]),
    ("Movimientos de inventario", "movimientos_inventario", "id"),
    ("Campañas (marketing)", "campanas", "campaña_id"),
]

# (tabla_hijo, columna_hijo, tabla_padre, columna_padre, etiqueta)
RELACIONES = [
    ("ventas", "producto_id", "productos", "producto_id", "ventas.producto_id -> productos"),
    ("ventas", "cliente_id", "clientes", "cliente_id", "ventas.cliente_id -> clientes"),
    ("inventario_actual", "producto_id", "productos", "producto_id", "inventario_actual.producto_id -> productos"),
    (
        "movimientos_inventario",
        "producto_id",
        "productos",
        "producto_id",
        "movimientos_inventario.producto_id -> productos",
    ),
]


def _cargar_interim(nombre_archivo: str) -> pd.DataFrame:
    ruta = config.INTERIM_DIR / f"{nombre_archivo}.parquet"
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró {ruta}. Ejecuta primero `python ejecutar_extraccion.py`.")
    return pd.read_parquet(ruta)


def main():
    tablas = {nombre_archivo: _cargar_interim(nombre_archivo) for _, nombre_archivo, _ in FUENTES}

    secciones = [
        "# Hallazgos de calidad de datos — Día 2",
        "",
        f"_Generado automáticamente el {datetime.now():%Y-%m-%d %H:%M}._",
        "",
        "Este reporte se regenera cada vez que se ejecuta este script. "
        "No editar a mano: los hallazgos deben salir siempre del perfilado "
        "real sobre los datos en `data/interim/`.",
        "",
    ]

    for nombre_fuente, nombre_archivo, llave in FUENTES:
        perfil = perfilar(tablas[nombre_archivo], nombre_fuente, llave)
        secciones.append(formatear_perfil_markdown(perfil))

    secciones.append("## Integridad referencial\n")
    for tabla_hijo, col_hijo, tabla_padre, col_padre, etiqueta in RELACIONES:
        resultado = verificar_integridad_referencial(
            tablas[tabla_hijo], col_hijo, tablas[tabla_padre][col_padre], etiqueta
        )
        secciones.append(formatear_integridad_markdown(resultado))

    ruta_reporte = config.REPORTS_DIR / "hallazgos_calidad.md"
    ruta_reporte.write_text("\n".join(secciones), encoding="utf-8")
    print(f"Reporte generado en {ruta_reporte}")


if __name__ == "__main__":
    main()
