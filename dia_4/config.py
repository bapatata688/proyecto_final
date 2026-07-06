"""
Configuración central del Día 4 - Consultas SQL, KPIs y gráficos.
"""

from pathlib import Path

# --- BigQuery ---
PROJECT_ID = "proyecto-final-501300"   # <-- mismo valor que se uso en dia3
DATASET = "dw_datacommerce"

# --- Rutas locales ---
BASE_DIR = Path(__file__).parent
DATA_KPIS_DIR = BASE_DIR / "data" / "kpis"      # aquí se guardan los KPIs calculados (csv/json)
GRAFICOS_DIR = BASE_DIR / "graficos"            # aquí se guardan los .png de los gráficos

DATA_KPIS_DIR.mkdir(parents=True, exist_ok=True)
GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)

# --- Credenciales ---
# Misma clave de cuenta de servicio que usaste en el Día 3. Cópiala a esta
# carpeta (dia4_analisis_kpis/) o ajusta esta ruta para apuntar a la del día 3
# y así no la duplicas:
CREDENTIALS_PATH = BASE_DIR.parent / "dia_3" / "credenciales_bigquery.json"
