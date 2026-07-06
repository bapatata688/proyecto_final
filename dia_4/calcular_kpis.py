"""
Día 4 - Paso 1: Calcular KPIs desde BigQuery.

Lee las tablas de dw_datacommerce (cargadas en el Día 3), calcula los
indicadores de negocio con pandas y guarda cada uno como CSV en data/kpis/.

"""

from google.cloud import bigquery
import kpis
from config import PROJECT_ID, DATASET, CREDENTIALS_PATH, DATA_KPIS_DIR


def leer_tabla(client, nombre_tabla):
    table_id = f"{PROJECT_ID}.{DATASET}.{nombre_tabla}"
    return client.list_rows(table_id).to_dataframe()


def main():
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"No encontré {CREDENTIALS_PATH}. Usa la misma clave JSON del Día 3, "
            "o cópiala a esta carpeta."
        )

    client = bigquery.Client.from_service_account_json(str(CREDENTIALS_PATH), project=PROJECT_ID)

    print("Descargando tablas desde BigQuery...")
    fact_ventas = leer_tabla(client, "fact_ventas")
    dim_canal = leer_tabla(client, "dim_canal")
    dim_producto = leer_tabla(client, "dim_producto")
    dim_sucursal = leer_tabla(client, "dim_sucursal")
    dim_metodo_pago = leer_tabla(client, "dim_metodo_pago")
    dim_cliente = leer_tabla(client, "dim_cliente")
    fact_inventario_existencia = leer_tabla(client, "fact_inventario_existencia")
    dim_bodega = leer_tabla(client, "dim_bodega")
    fact_marketing = leer_tabla(client, "fact_marketing")
    dim_plataforma = leer_tabla(client, "dim_plataforma")
    fact_movimiento_inventario = leer_tabla(client, "fact_movimiento_inventario")

    resultados = {
        "ventas_por_canal": kpis.ventas_por_canal(fact_ventas, dim_canal),
        "top_productos": kpis.top_productos(fact_ventas, dim_producto),
        "ventas_por_sucursal": kpis.ventas_por_sucursal(fact_ventas, dim_sucursal),
        "metodo_pago_mas_usado": kpis.metodo_pago_mas_usado(fact_ventas, dim_metodo_pago),
        "top_clientes": kpis.top_clientes(fact_ventas, dim_cliente),
        "existencia_inventario": kpis.existencia_inventario(
            fact_inventario_existencia, dim_producto, dim_bodega
        ),
        "desempeno_marketing": kpis.desempeno_marketing(fact_marketing, dim_plataforma),
        "movimientos_inventario_por_tipo": kpis.movimientos_inventario_por_tipo(
            fact_movimiento_inventario
        ),
    }

    for nombre, df in resultados.items():
        salida = DATA_KPIS_DIR / f"{nombre}.csv"
        df.to_csv(salida, index=False)
        print(f"{nombre}: {df.shape[0]} filas -> {salida}")

    return resultados


if __name__ == "__main__":
    main()
