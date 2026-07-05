"""
Día 3 - Paso 1: Modelado dimensional.

Lee los datos limpios de calidad/data/processed (día 2) y construye
las tablas de dimensiones y de hechos del modelo estrella, con llaves
sustitutas (surrogate keys), listas para cargar a BigQuery.

es  reproducible: se puede volver a correr las veces que
sea necesario y siempre genera el mismo resultado a partir de los datos
de entrada
"""

import pandas as pd
from config import DATA_PROCESSED_DIR, DATA_DW_DIR


def cargar_processed():
    """Lee los parquet limpios que dejó el compañero en data/processed."""
    return {
        "ventas": pd.read_parquet(DATA_PROCESSED_DIR / "ventas.parquet"),
        "productos": pd.read_parquet(DATA_PROCESSED_DIR / "productos.parquet"),
        "clientes": pd.read_parquet(DATA_PROCESSED_DIR / "clientes.parquet"),
        "inventario_actual": pd.read_parquet(DATA_PROCESSED_DIR / "inventario_actual.parquet"),
        "movimientos_inventario": pd.read_parquet(DATA_PROCESSED_DIR / "movimientos_inventario.parquet"),
        "campanas": pd.read_parquet(DATA_PROCESSED_DIR / "campanas.parquet"),
    }


def construir_dim_producto(productos):
    dim = productos.copy()
    dim = dim.rename(columns={"producto_id": "producto_key"})
    return dim[[
        "producto_key", "nombre_producto", "categoria", "subcategoria",
        "marca", "costo_unitario", "precio_lista", "proveedor_id",
    ]]


def construir_dim_cliente(clientes):
    dim = clientes.copy()
    dim = dim.rename(columns={"cliente_id": "cliente_key"})
    # Fila "Desconocido" para clientes huérfanos (ver hallazgos_calidad.md:
    # ventas.cliente_id -> clientes: 1 huérfano -> 504). Sin esta fila,
    # el JOIN con fact_ventas perdería esa venta.
    desconocido = pd.DataFrame([{
        "cliente_key": -1, "nombre": "Cliente desconocido", "genero": "N/A",
        "edad": None, "departamento": "N/A", "municipio": "N/A",
        "fecha_registro": None, "segmento_cliente": "N/A",
    }])
    dim = pd.concat([dim, desconocido], ignore_index=True)
    return dim[[
        "cliente_key", "nombre", "genero", "edad", "departamento",
        "municipio", "fecha_registro", "segmento_cliente",
    ]]


def construir_dim_lookup(valores, nombre_columna_key, nombre_columna_valor):
    """Dimensión genérica tipo catálogo (canal, método de pago, plataforma, bodega)."""
    unicos = sorted(pd.unique(valores.dropna()))
    dim = pd.DataFrame({
        nombre_columna_key: range(1, len(unicos) + 1),
        nombre_columna_valor: unicos,
    })
    return dim


def construir_dim_sucursal(ventas):
    # No llegó un archivo fuente con nombres de sucursal, solo el ID.
    # Se arma con lo disponible; si tu compañero consigue un catálogo real
    # de sucursales, reemplaza esta función para leerlo en vez de inventar nombres.
    ids = sorted(ventas["sucursal_id"].dropna().unique())
    dim = pd.DataFrame({
        "sucursal_key": ids,
        "nombre_sucursal": [f"Sucursal {i}" for i in ids],
    })
    return dim


def construir_fact_ventas(ventas, dim_canal, dim_metodo_pago):
    f = ventas.copy()
    f = f.merge(dim_canal, left_on="canal_venta", right_on="canal_venta", how="left")
    f = f.merge(dim_metodo_pago, left_on="metodo_pago", right_on="metodo_pago", how="left")

    # Clientes huérfanos (no existen en dim_cliente) -> apuntan al registro -1 "Desconocido"
    clientes_validos = set(pd.read_parquet(DATA_PROCESSED_DIR / "clientes.parquet")["cliente_id"])
    f["cliente_key"] = f["cliente_id"].apply(lambda c: c if c in clientes_validos else -1)

    f = f.rename(columns={
        "producto_id": "producto_key",
        "sucursal_id": "sucursal_key",
    })

    return f[[
        "venta_id", "fecha_venta", "cliente_key", "producto_key", "sucursal_key",
        "canal_key", "metodo_pago_key", "cantidad", "precio_unitario",
        "descuento", "total_venta",
    ]]


def construir_fact_movimiento_inventario(movimientos):
    f = movimientos.copy()
    f = f.rename(columns={"producto_id": "producto_key"})
    return f[["id", "producto_key", "fecha", "tipo", "cantidad"]]


def construir_fact_inventario_existencia(inventario_actual, dim_bodega):
    f = inventario_actual.copy()
    f = f.merge(dim_bodega, left_on="bodega", right_on="bodega", how="left")
    f = f.rename(columns={"producto_id": "producto_key"})
    return f[["producto_key", "bodega_key", "existencia"]]


def construir_fact_marketing(campanas, dim_plataforma):
    f = campanas.copy()
    f = f.merge(dim_plataforma, left_on="plataforma", right_on="plataforma", how="left")
    f = f.rename(columns={"campaña_id": "campana_id"})
    return f[[
        "campana_id", "fecha", "plataforma_key", "impresiones", "clics",
        "costo", "leads", "conversiones",
    ]]


def main():
    datos = cargar_processed()

    # --- Dimensiones ---
    dim_producto = construir_dim_producto(datos["productos"])
    dim_cliente = construir_dim_cliente(datos["clientes"])
    dim_sucursal = construir_dim_sucursal(datos["ventas"])
    dim_canal = construir_dim_lookup(datos["ventas"]["canal_venta"], "canal_key", "canal_venta")
    dim_metodo_pago = construir_dim_lookup(datos["ventas"]["metodo_pago"], "metodo_pago_key", "metodo_pago")
    dim_plataforma = construir_dim_lookup(datos["campanas"]["plataforma"], "plataforma_key", "plataforma")
    dim_bodega = construir_dim_lookup(datos["inventario_actual"]["bodega"], "bodega_key", "bodega")

    # --- Hechos ---
    fact_ventas = construir_fact_ventas(datos["ventas"], dim_canal, dim_metodo_pago)
    fact_movimiento_inventario = construir_fact_movimiento_inventario(datos["movimientos_inventario"])
    fact_inventario_existencia = construir_fact_inventario_existencia(datos["inventario_actual"], dim_bodega)
    fact_marketing = construir_fact_marketing(datos["campanas"], dim_plataforma)

    tablas = {
        "dim_producto": dim_producto,
        "dim_cliente": dim_cliente,
        "dim_sucursal": dim_sucursal,
        "dim_canal": dim_canal,
        "dim_metodo_pago": dim_metodo_pago,
        "dim_plataforma": dim_plataforma,
        "dim_bodega": dim_bodega,
        "fact_ventas": fact_ventas,
        "fact_movimiento_inventario": fact_movimiento_inventario,
        "fact_inventario_existencia": fact_inventario_existencia,
        "fact_marketing": fact_marketing,
    }

    for nombre, df in tablas.items():
        salida = DATA_DW_DIR / f"{nombre}.parquet"
        df.to_parquet(salida, index=False)
        print(f"{nombre}: {df.shape[0]} filas -> {salida}")

    return tablas


if __name__ == "__main__":
    main()
