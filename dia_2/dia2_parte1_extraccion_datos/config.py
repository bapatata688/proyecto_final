"""Configuración central: rutas, variables de entorno y logging.

Dejamos todo en un solo lugar para que el resto del código no dependa de
rutas absolutas ni de credenciales hardcodeadas.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "data" / "raw"
INTERIM_DIR = BASE_DIR / "data" / "interim"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"

for _dir in (RAW_DIR, INTERIM_DIR, PROCESSED_DIR, REPORTS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)


VENTAS_CSV = RAW_DIR / "ventas.csv"
PRODUCTOS_XLSX = RAW_DIR / "productos.xlsx"
CLIENTES_JSON = RAW_DIR / "clientes.json"
INVENTARIO_DB = RAW_DIR / "inventario.db"
API_MOCK_JSON = RAW_DIR / "api_marketing_response.json"

# API real de campañas de marketing
API_CAMPANAS_URL = os.environ.get("API_CAMPANAS_URL", "")
API_CAMPANAS_KEY = os.environ.get("API_CAMPANAS_KEY", "")
API_TIMEOUT_SEGUNDOS = int(os.environ.get("API_TIMEOUT_SEGUNDOS", "10"))
