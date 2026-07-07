# Limpieza y estandarización de las fuentes.

import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)

_PATRON_ANIO_PRIMERO = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$")
_PATRON_ANIO_AL_FINAL = re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$")


def _parsear_fecha(valor) -> pd.Timestamp:

    if pd.isna(valor):
        return pd.NaT

    texto = str(valor).strip().replace("/", "-")

    if _PATRON_ANIO_PRIMERO.match(texto):
        return pd.to_datetime(texto, format="%Y-%m-%d", errors="coerce")
    if _PATRON_ANIO_AL_FINAL.match(texto):
        return pd.to_datetime(texto, format="%d-%m-%Y", errors="coerce")
    return pd.to_datetime(texto, errors="coerce")


def _normalizar_fecha(serie: pd.Series) -> pd.Series:
    return serie.apply(_parsear_fecha)


def limpiar_ventas(df: pd.DataFrame) -> pd.DataFrame:

    df = df.drop_duplicates(subset="venta_id").copy()

    df["fecha_venta"] = _normalizar_fecha(df["fecha_venta"])
    df["canal_venta"] = df["canal_venta"].str.strip()
    df["metodo_pago"] = df["metodo_pago"].str.strip()

    # CORRECCIÓN: Convertir a numérico antes de aplicar operaciones matemáticas (.abs)
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
    df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce")
    df["descuento"] = pd.to_numeric(df["descuento"], errors="coerce")

    df["cantidad"] = df["cantidad"].abs()
    df["descuento"] = df["descuento"].abs()
    df["total_venta"] = (
        df["cantidad"] * df["precio_unitario"] - df["descuento"]
    ).round(2)

    return df.reset_index(drop=True)


def limpiar_productos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset="producto_id").copy()

    for col in ("nombre_producto", "categoria", "subcategoria", "marca"):
        df[col] = df[col].str.strip()

    df["categoria"] = df["categoria"].fillna("Sin Categoría")
    df["subcategoria"] = df["subcategoria"].fillna("Sin Subcategoría")

    df["precio_lista"] = pd.to_numeric(df["precio_lista"], errors="coerce")
    df["costo_unitario"] = pd.to_numeric(df["costo_unitario"], errors="coerce")

    filas_antes = len(df)
    df = df[(df["precio_lista"].isna()) | (df["precio_lista"] >= 0)]
    df = df.dropna(subset=["precio_lista"])

    if len(df) < filas_antes:
        logger.warning(
            "%s producto(s) descartado(s) por precio_lista inválido o negativo",
            filas_antes - len(df),
        )

    return df.reset_index(drop=True)


def limpiar_clientes(df: pd.DataFrame) -> pd.DataFrame:

    df = df.drop_duplicates(subset="cliente_id").copy()

    df["departamento"] = df["departamento"].str.strip()
    df["municipio"] = df["municipio"].str.strip().replace("", pd.NA)
    df["fecha_registro"] = _normalizar_fecha(df["fecha_registro"])

    # CORRECCIÓN: Convertir 'edad' de vuelta a tipo entero con soporte nativo de nulos (Int64)
    if "edad" in df.columns:
        df["edad"] = pd.to_numeric(df["edad"], errors="coerce").astype("Int64")

    return df.reset_index(drop=True)


def limpiar_inventario_actual(df: pd.DataFrame) -> pd.DataFrame:

    df = df.drop_duplicates(subset=["producto_id", "bodega"]).copy()

    df["bodega"] = df["bodega"].str.strip()

    # CORRECCIÓN: Convertir a numérico antes de truncar con .clip()
    df["existencia"] = pd.to_numeric(df["existencia"], errors="coerce")
    df["existencia"] = df["existencia"].clip(lower=0)

    return df.reset_index(drop=True)


def limpiar_movimientos_inventario(df: pd.DataFrame) -> pd.DataFrame:

    df = df.drop_duplicates(subset="id").copy()

    df["tipo"] = df["tipo"].str.strip()

    # CORRECCIÓN: Convertir a numérico antes de aplicar .abs()
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
    df["cantidad"] = df["cantidad"].abs()
    df["fecha"] = _normalizar_fecha(df["fecha"])

    return df.reset_index(drop=True)


def limpiar_campanas(df: pd.DataFrame) -> pd.DataFrame:

    df = df.drop_duplicates(subset="campaña_id").copy()

    df["plataforma"] = df["plataforma"].str.strip()
    df["fecha"] = _normalizar_fecha(df["fecha"])

    for col in ("impresiones", "clics", "costo", "leads", "conversiones"):
        df[col] = pd.to_numeric(df[col], errors="coerce").clip(lower=0)

    return df.reset_index(drop=True)
