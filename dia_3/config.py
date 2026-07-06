"""
Configuración central del Día 3 - Modelado dimensional y carga al DW.
Ajusta PROJECT_ID y DATASET con los valores reales de tu proyecto en BigQuery.
"""

from pathlib import Path

# --- BigQuery ---
PROJECT_ID = "proyecto-final-501300"
DATASET = "dw_datacommerce"

# --- Rutas ---
BASE_DIR = Path(__file__).parent

# Carpeta con los datos procesados generados en el Día 2
DATA_PROCESSED_DIR = BASE_DIR.parent / "dia_2" / "data" / "processed"

# Carpeta donde se guardarán las tablas del Data Warehouse generadas en el Día 3
DATA_DW_DIR = BASE_DIR / "data" / "dw"

# Verificar que existan los datos procesados
if not DATA_PROCESSED_DIR.exists():
    raise FileNotFoundError(
        f"No encontré la carpeta: {DATA_PROCESSED_DIR}\n"
        "Ejecuta primero el Día 2 para generar los archivos en data/processed."
    )

# Crear la carpeta del DW si no existe
DATA_DW_DIR.mkdir(parents=True, exist_ok=True)

# --- Credenciales ---
CREDENTIALS_PATH = BASE_DIR / "credenciales_bigquery.json"