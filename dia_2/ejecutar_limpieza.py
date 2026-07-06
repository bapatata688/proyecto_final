"""Limpia las fuentes ya extraídas (data/interim/) y guarda el
resultado en data/processed/.
"""

import pandas as pd

import clean
import config

PIPELINE = [
    ("ventas", clean.limpiar_ventas),
    ("productos", clean.limpiar_productos),
    ("clientes", clean.limpiar_clientes),
    ("inventario_actual", clean.limpiar_inventario_actual),
    ("movimientos_inventario", clean.limpiar_movimientos_inventario),
    ("campanas", clean.limpiar_campanas),
]

# llave(s) de cada fuente + columnas que nunca deberían ser negativas
# después de limpiar
REGLAS_VALIDACION = {
    "ventas": (["venta_id"], ["cantidad", "descuento"]),
    "productos": (["producto_id"], ["precio_lista"]),
    "clientes": (["cliente_id"], []),
    "inventario_actual": (["producto_id", "bodega"], ["existencia"]),
    "movimientos_inventario": (["id"], ["cantidad"]),
    "campanas": (["campaña_id"], ["impresiones", "clics", "costo"]),
}


def _cargar_interim(nombre: str) -> pd.DataFrame:
    ruta = config.INTERIM_DIR / f"{nombre}.parquet"
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró {ruta}. Ejecuta primero `python ejecutar_extraccion.py`.")
    return pd.read_parquet(ruta)


def _validar(df: pd.DataFrame, nombre: str) -> None:
    llave, columnas_no_negativas = REGLAS_VALIDACION[nombre]
    assert df.duplicated(subset=llave).sum() == 0, f"{nombre}: quedaron duplicados por {llave}"
    for col in columnas_no_negativas:
        assert (df[col].dropna() >= 0).all(), f"{nombre}: {col} tiene valores negativos"


def main():
    for nombre, limpiar in PIPELINE:
        df_crudo = _cargar_interim(nombre)
        df_limpio = limpiar(df_crudo)
        _validar(df_limpio, nombre)

        ruta_salida = config.PROCESSED_DIR / f"{nombre}.parquet"
        df_limpio.to_parquet(ruta_salida, index=False)
        print(f"{nombre}: {len(df_crudo)} filas crudas -> {len(df_limpio)} filas limpias -> {ruta_salida.name}")


if __name__ == "__main__":
    main()
