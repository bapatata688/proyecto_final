"""
Día 3 - Paso 2: Carga al Data Warehouse (BigQuery).

Toma los parquet generados por modelado.py (data/dw/*.parquet) y los
carga a las tablas del dataset dw_datacommerce en BigQuery.
"""

from google.cloud import bigquery
import pandas as pd
from config import PROJECT_ID, DATASET, DATA_DW_DIR, CREDENTIALS_PATH

TABLAS = [
    "dim_producto",
    "dim_cliente",
    "dim_sucursal",
    "dim_canal",
    "dim_metodo_pago",
    "dim_plataforma",
    "dim_bodega",
    "fact_ventas",
    "fact_movimiento_inventario",
    "fact_inventario_existencia",
    "fact_marketing",
]


def main():
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"No encontré {CREDENTIALS_PATH}. Descarga la clave JSON de tu "
            "cuenta de servicio en GCP y guárdala con ese nombre exacto en "
            "esta carpeta (dia3_modelado_carga/)."
        )

    client = bigquery.Client.from_service_account_json(str(CREDENTIALS_PATH), project=PROJECT_ID)

    for nombre_tabla in TABLAS:
        ruta = DATA_DW_DIR / f"{nombre_tabla}.parquet"
        if not ruta.exists():
            print(f"[SALTADO] {nombre_tabla}: no existe {ruta}. Corre modelado.py primero.")
            continue

        df = pd.read_parquet(ruta)
        table_id = f"{PROJECT_ID}.{DATASET}.{nombre_tabla}"

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",  # reproducible: cada corrida reemplaza el contenido
            autodetect=True,
        )

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # espera a que termine el job

        tabla = client.get_table(table_id)
        print(f"[OK] {nombre_tabla}: {tabla.num_rows} filas cargadas en {table_id}")


if __name__ == "__main__":
    main()
