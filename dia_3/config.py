"""
Configuración central del Día 3 - Modelado dimensional y carga al DW.
Ajusta PROJECT_ID y DATASET con los valores reales de tu proyecto en BigQuery
(los ves arriba a la izquierda en la consola: "proyecto-final-501300").
"""

from pathlib import Path

# --- BigQuery ---
PROJECT_ID = "proyecto-final-501300"   
DATASET = "dw_datacommerce"

BASE_DIR = Path(__file__).parent
DATA_PROCESSED_DIR = BASE_DIR.parent / "dia_2" / "dia2_parte2_calidad_limpieza" / "data" / "processed"
DATA_DW_DIR = BASE_DIR / "data" / "dw" 

if not DATA_PROCESSED_DIR.exists():
    raise FileNotFoundError(
        f"No encontré {DATA_PROCESSED_DIR}. Verifica que dia3_modelado_carga esté "
        "al mismo nivel que dia2_parte2_calidad_limpieza en el repo, y que el "
        "nombre de esa carpeta coincida exactamente."
    )

DATA_DW_DIR.mkdir(parents=True, exist_ok=True)

# --- Credenciales ---
CREDENTIALS_PATH = BASE_DIR / "credenciales_bigquery.json"
