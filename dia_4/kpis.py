"""
Día 4 - Cálculo de KPIs con Pandas.

Estas funciones reciben DataFrames ya combinados (joins hechos con las
dimensiones) y devuelven los indicadores de negocio. Se separan de la
conexión a BigQuery para poder probarlas con datos
locales sin necesitar credenciales.
"""

import pandas as pd


def ventas_por_canal(fact_ventas, dim_canal):
    df = fact_ventas.merge(dim_canal, on="canal_key", how="left")
    resumen = df.groupby("canal_venta").agg(
        num_ventas=("venta_id", "count"),
        ventas_totales=("total_venta", "sum"),
    ).reset_index()
    resumen["ticket_promedio"] = (resumen["ventas_totales"] / resumen["num_ventas"]).round(2)
    return resumen.sort_values("ventas_totales", ascending=False).reset_index(drop=True)


def top_productos(fact_ventas, dim_producto):
    df = fact_ventas.merge(dim_producto, on="producto_key", how="left")
    resumen = df.groupby(["nombre_producto", "categoria"]).agg(
        unidades_vendidas=("cantidad", "sum"),
        monto_vendido=("total_venta", "sum"),
    ).reset_index()
    return resumen.sort_values("monto_vendido", ascending=False).reset_index(drop=True)


def ventas_por_sucursal(fact_ventas, dim_sucursal):
    df = fact_ventas.merge(dim_sucursal, on="sucursal_key", how="left")
    resumen = df.groupby("nombre_sucursal").agg(
        num_ventas=("venta_id", "count"),
        ventas_totales=("total_venta", "sum"),
    ).reset_index()
    return resumen.sort_values("ventas_totales", ascending=False).reset_index(drop=True)


def metodo_pago_mas_usado(fact_ventas, dim_metodo_pago):
    df = fact_ventas.merge(dim_metodo_pago, on="metodo_pago_key", how="left")
    resumen = df.groupby("metodo_pago").agg(
        num_ventas=("venta_id", "count"),
        monto_total=("total_venta", "sum"),
    ).reset_index()
    return resumen.sort_values("num_ventas", ascending=False).reset_index(drop=True)


def top_clientes(fact_ventas, dim_cliente):
    df = fact_ventas.merge(dim_cliente, on="cliente_key", how="left")
    resumen = df.groupby(["nombre", "segmento_cliente"]).agg(
        num_compras=("venta_id", "count"),
        monto_total=("total_venta", "sum"),
    ).reset_index()
    return resumen.sort_values("monto_total", ascending=False).reset_index(drop=True)


def existencia_inventario(fact_inventario_existencia, dim_producto, dim_bodega):
    df = fact_inventario_existencia.merge(dim_producto, on="producto_key", how="left")
    df = df.merge(dim_bodega, on="bodega_key", how="left")
    resumen = df[["nombre_producto", "bodega", "existencia"]]
    return resumen.sort_values("existencia").reset_index(drop=True)


def desempeno_marketing(fact_marketing, dim_plataforma):
    df = fact_marketing.merge(dim_plataforma, on="plataforma_key", how="left")
    resumen = df.groupby("plataforma").agg(
        impresiones=("impresiones", "sum"),
        clics=("clics", "sum"),
        costo_total=("costo", "sum"),
        leads=("leads", "sum"),
        conversiones=("conversiones", "sum"),
    ).reset_index()
    resumen["ctr_pct"] = (resumen["clics"] / resumen["impresiones"] * 100).round(2)
    resumen["costo_por_lead"] = (resumen["costo_total"] / resumen["leads"]).round(2)
    resumen["tasa_conversion_pct"] = (resumen["conversiones"] / resumen["clics"] * 100).round(2)
    return resumen.sort_values("costo_total", ascending=False).reset_index(drop=True)


def movimientos_inventario_por_tipo(fact_movimiento_inventario):
    resumen = fact_movimiento_inventario.groupby("tipo").agg(
        num_movimientos=("id", "count"),
        unidades_movidas=("cantidad", "sum"),
    ).reset_index()
    return resumen
