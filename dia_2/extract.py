"""Extracción de las fuentes: leemos cada archivo/API tal cual viene,
sin transformar nada

"""

import json
import logging
import sqlite3

import pandas as pd
import requests
from requests.exceptions import RequestException

import config

logger = logging.getLogger(__name__)


def _requerir_archivo(ruta):
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta} " 
        )


def extraer_ventas(ruta=config.VENTAS_CSV) -> pd.DataFrame:
    _requerir_archivo(ruta)
    df = pd.read_csv(ruta)
    logger.info("Ventas extraídas: %s filas, %s columnas", *df.shape)
    return df


def extraer_productos(ruta=config.PRODUCTOS_XLSX) -> pd.DataFrame:
    _requerir_archivo(ruta)
    df = pd.read_excel(ruta, engine="openpyxl")
    logger.info("Productos extraídos: %s filas, %s columnas", *df.shape)
    return df


def extraer_clientes(ruta=config.CLIENTES_JSON) -> pd.DataFrame:
    _requerir_archivo(ruta)
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    # Acepta tanto una lista plana como { "clientes": [...] }.
    registros = datos.get("clientes", datos) if isinstance(datos, dict) else datos
    df = pd.DataFrame(registros)
    logger.info("Clientes extraídos: %s filas, %s columnas", *df.shape)
    return df


def _leer_tabla_sqlite(ruta, tabla: str) -> pd.DataFrame:
    _requerir_archivo(ruta)
    with sqlite3.connect(ruta) as conexion:
        return pd.read_sql_query(f"SELECT * FROM {tabla}", conexion)


def extraer_inventario_actual(ruta=config.INVENTARIO_DB) -> pd.DataFrame:
    df = _leer_tabla_sqlite(ruta, "inventario_actual")
    logger.info("Inventario actual extraído: %s filas, %s columnas", *df.shape)
    return df


def extraer_movimientos_inventario(ruta=config.INVENTARIO_DB) -> pd.DataFrame:
    df = _leer_tabla_sqlite(ruta, "movimientos_inventario")
    logger.info("Movimientos de inventario extraídos: %s filas, %s columnas", *df.shape)
    return df


def _campanas_desde_api(url: str) -> list:
    encabezados = {"Authorization": f"Bearer {config.API_CAMPANAS_KEY}"} if config.API_CAMPANAS_KEY else {}
    respuesta = requests.get(url, headers=encabezados, timeout=config.API_TIMEOUT_SEGUNDOS)
    respuesta.raise_for_status()
    datos = respuesta.json()
    return datos.get("campaigns", datos) if isinstance(datos, dict) else datos


def _campanas_desde_mock(ruta) -> list:
    _requerir_archivo(ruta)
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    return datos.get("campaigns", datos) if isinstance(datos, dict) else datos


def extraer_campanas() -> pd.DataFrame:
    """Usa la API real si config.API_CAMPANAS_URL está definida; si no
    está definida, o si falla, cae al mock entregado por el instructor
    (data/raw/api_marketing_response.json).
    """
    if config.API_CAMPANAS_URL:
        try:
            registros = _campanas_desde_api(config.API_CAMPANAS_URL)
            logger.info("Campañas extraídas desde la API real")
        except RequestException as error:
            logger.warning("Falló la API de campañas (%s); usando mock local", error)
            registros = _campanas_desde_mock(config.API_MOCK_JSON)
    else:
        logger.info("API_CAMPANAS_URL no configurada; usando mock local")
        registros = _campanas_desde_mock(config.API_MOCK_JSON)

    df = pd.DataFrame(registros)
    logger.info("Campañas extraídas: %s filas, %s columnas", *df.shape)
    return df
