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
 
import unicodedata
 
 
def _normalizar_texto(valor: str) -> str:
    """Mayúsculas, sin espacios extra (incluidos los dobles espacios
    internos, ej. 'Pagina  Web') y sin acentos, para poder comparar
    contra el diccionario de alias sin importar cómo llegó escrito."""
    texto = str(valor).strip().upper()
    # OJO: el archivo real trae valores como "Pagina  Web" o
    # "Tienda  Física" con doble espacio interno. Si no se colapsa aquí,
    # "PAGINA  WEB" nunca hace match contra la clave "PAGINA WEB" del
    # diccionario y esas filas se pierden como "Sin Clasificar".
    texto = re.sub(r"\s+", " ", texto)
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
 
 
# Diccionario de alias -> categoría canónica. Cada entrada de la izquierda
# es una variante real encontrada en los datos oficiales (mayúsculas,
# minúsculas, abreviaturas, nombres de marca en vez de la categoría).
#
# Además del diccionario, _normalizar_categoria() aplica un segundo intento
# por PREFIJO (ver _resolver_por_prefijo) para capturar truncamientos que
# no se pueden listar uno por uno (ej. "Instagra", "Faceboo", "Mastercar",
# "Tienda Físic", "Onlin", "Credit", "Deposit", "Vis"): son la misma
# palabra con las últimas letras cortadas, típico de captura manual o de
# un campo de texto con límite de caracteres.
_ALIAS_CANAL = {
    "TIENDA": "Tienda Física", "TIENDA FISICA": "Tienda Física", "TIEND": "Tienda Física",
    "WEB": "Web", "SITIO WEB": "Web", "PAGINA WEB": "Web", "PAGINA WE": "Web",
    "ONLINE": "Web", "SITI": "Web", "WE": "Web",
    "SITIO": "Web",  # faltaba: "Sitio" solo (sin "Web") aparece miles de veces en los datos reales
    "WHATSAPP": "WhatsApp", "WA": "WhatsApp",
}
 
_ALIAS_METODO_PAGO = {
    "EFECTIVO": "Efectivo", "CASH": "Efectivo", "EFECTIV": "Efectivo",
    "TARJETA": "Tarjeta", "TARJET": "Tarjeta", "TC": "Tarjeta", "CREDITO": "Tarjeta",
    "VISA": "Tarjeta", "MASTERCARD": "Tarjeta", "TARJETA CREDITO": "Tarjeta",
    "TRANSFERENCIA": "Transferencia", "TRANSFERENCI": "Transferencia", "TRANSF": "Transferencia",
    "TRANSF.": "Transferencia", "DEPOSITO": "Transferencia",
}
 
_ALIAS_PLATAFORMA = {
    "FACEBOOK": "Facebook", "FB": "Facebook", "META": "Facebook", "FACEBOOK ADS": "Facebook",
    "INSTAGRAM": "Instagram", "IG": "Instagram", "INSTA": "Instagram",
    # unívocas: ninguna otra categoría de esta columna empieza con estas letras,
    # así que no hay ambigüedad al mapearlas directamente
    "F": "Facebook", "I": "Instagram",
}
 
# Longitud mínima para intentar resolver por prefijo. Con menos de 3
# caracteres el riesgo de ambigüedad sube mucho (ej. "W" podría ser "Web"
# o "WhatsApp"; "T" podría ser "Tarjeta" o "Transferencia"), así que esos
# casos cortos se dejan como "Sin Clasificar" en vez de adivinar.
_LONGITUD_MINIMA_PREFIJO = 3
 
 
def _resolver_por_prefijo(valor_normalizado: str, alias: dict):
    """Segundo intento de clasificación para valores truncados que no
    están en el diccionario de alias tal cual (ej. 'Instagra' en vez de
    'Instagram', 'Mastercar' en vez de 'Mastercard', 'Onlin' en vez de
    'Online'). Busca si el valor es el inicio de alguna clave conocida del
    diccionario; si todas las claves que empiezan así apuntan a la MISMA
    categoría canónica, se usa esa categoría. Si hay más de una categoría
    posible (ambigüedad real), se deja sin resolver."""
    if len(valor_normalizado) < _LONGITUD_MINIMA_PREFIJO:
        return None
 
    candidatos = {
        canonico
        for clave, canonico in alias.items()
        if clave.startswith(valor_normalizado)
    }
 
    if len(candidatos) == 1:
        return candidatos.pop()
    return None
 
 
def _normalizar_categoria(serie: pd.Series, alias: dict, nombre_columna: str) -> pd.Series:
    """Agrupa variantes (mayúsculas/minúsculas, abreviaturas, marcas,
    truncamientos) en una sola categoría canónica. Lo que no se reconoce
    se marca como 'Sin Clasificar' y se reporta -- mejor visibilizarlo que
    adivinar cuando el dato es realmente ambiguo (ej. 'T' o 'W' solos)."""
    es_nulo = serie.isna()
 
    normalizado = serie.apply(lambda v: _normalizar_texto(v) if pd.notna(v) else "")
    resultado = normalizado.map(alias)
 
    # Segundo intento (por prefijo) solo para lo que no fue nulo ni hizo
    # match directo en el diccionario.
    pendientes = resultado.isna() & ~es_nulo
    if pendientes.any():
        resultado.loc[pendientes] = normalizado[pendientes].apply(
            lambda v: _resolver_por_prefijo(v, alias)
        )
 
    no_reconocidos = normalizado[resultado.isna() & ~es_nulo].unique()
    if len(no_reconocidos):
        logger.warning(
            "%s: %s valor(es) no reconocido(s), marcados como 'Sin Clasificar': %s",
            nombre_columna, len(no_reconocidos), list(no_reconocidos),
        )
 
    return resultado.fillna("Sin Clasificar")
 
def limpiar_ventas(df: pd.DataFrame) -> pd.DataFrame:
    """- venta_id duplicado: se conserva el primero.
    - fecha_venta: se normaliza (el archivo real mezcla AAAA-MM-DD,
      DD/MM/AAAA y AAAA/MM/DD en la misma columna).
    - canal_venta/metodo_pago: se agrupan variantes de mayúsculas,
      abreviaturas, nombres de marca y truncamientos en una sola categoría
      canónica (ver _normalizar_categoria). Esto es lo que evita que
      "Tienda", "TIENDA", "Tiend" y "Tienda Física" aparezcan como 4 filas
      distintas en el dashboard.
    - cantidad/precio_unitario/descuento: se fuerzan a numérico. Con 255,000
      filas reales aparecieron valores no numéricos (texto) en estas
      columnas; lo que no se pueda convertir se marca como nulo real y la
      fila se descarta (una venta sin cantidad o precio válido no es
      utilizable para KPIs de ingresos).
    - cantidad/descuento negativos -> valor absoluto: no existen ventas
      ni descuentos negativos, se interpreta como error de captura.
    - total_venta: se recalcula como cantidad × precio_unitario − descuento,
      para no arrastrar errores de captura del archivo original.
    """
    df = df.drop_duplicates(subset="venta_id").copy()
 
    df["fecha_venta"] = _normalizar_fecha(df["fecha_venta"])
    df["canal_venta"] = _normalizar_categoria(df["canal_venta"], _ALIAS_CANAL, "canal_venta")
    df["metodo_pago"] = _normalizar_categoria(df["metodo_pago"], _ALIAS_METODO_PAGO, "metodo_pago")
 
    # CORRECCIÓN: Convertir a numérico antes de aplicar operaciones matemáticas (.abs)
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
    df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce")
    df["descuento"] = pd.to_numeric(df["descuento"], errors="coerce").fillna(0)
 
    filas_antes = len(df)
    df = df.dropna(subset=["cantidad", "precio_unitario"]).copy()
    descartadas = filas_antes - len(df)
    if descartadas:
        logger.warning(
            "limpiar_ventas: %s fila(s) descartada(s) por cantidad/precio_unitario no numérico",
            descartadas,
        )
 
    df["cantidad"] = df["cantidad"].abs()
    df["descuento"] = df["descuento"].abs()
    df["total_venta"] = (
        df["cantidad"] * df["precio_unitario"] - df["descuento"]
    ).round(2)
 
    return df.reset_index(drop=True)
 
 
def limpiar_productos(df: pd.DataFrame) -> pd.DataFrame:
    """- producto_id duplicado: se conserva el primero.
    - nombre_producto/categoria/subcategoria/marca: se recortan espacios extra.
    - categoria/subcategoria nulas -> "Sin Categoría"/"Sin Subcategoría"
    - precio_lista/costo_unitario: se convierten a número; un
      precio_lista no convertible se descarta (no se puede vender un
      producto sin precio). precio_lista/costo_unitario negativos -> valor
      absoluto: no existen precios ni costos negativos, se interpreta
      como error de captura (hallazgo real con datos oficiales).
    """
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
 
    df["precio_lista"] = df["precio_lista"].abs()
    df["costo_unitario"] = df["costo_unitario"].abs()
 
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
    """- (producto_id, bodega) duplicado: se conserva el primero.
    - existencia: se fuerza a numérico (mismo patrón que cantidad/precio_lista);
      lo no convertible se trata como 0. existencia negativa -> 0 (el stock
      físico nunca es negativo).
    """
    df = df.drop_duplicates(subset=["producto_id", "bodega"]).copy()
 
    df["bodega"] = df["bodega"].str.strip()
 
    # CORRECCIÓN: Convertir a numérico antes de truncar con .clip()
    df["existencia"] = pd.to_numeric(df["existencia"], errors="coerce")
    df["existencia"] = df["existencia"].fillna(0).clip(lower=0)
 
    return df.reset_index(drop=True)
 
 
def limpiar_movimientos_inventario(df: pd.DataFrame) -> pd.DataFrame:
    """- id duplicado: se conserva el primero.
    - cantidad: se fuerza a numérico; lo no convertible se descarta (un
      movimiento de inventario sin cantidad válida no es utilizable).
    - cantidad negativa -> valor absoluto: la dirección la indica `tipo`.
    """
    df = df.drop_duplicates(subset="id").copy()
 
    df["tipo"] = df["tipo"].str.strip()
 
    # CORRECCIÓN: Convertir a numérico antes de aplicar .abs()
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
 
    filas_antes = len(df)
    df = df.dropna(subset=["cantidad"]).copy()
    if len(df) < filas_antes:
        logger.warning("%s movimiento(s) descartado(s) por cantidad no numérica", filas_antes - len(df))
 
    df["cantidad"] = df["cantidad"].abs()
    df["fecha"] = _normalizar_fecha(df["fecha"])
 
    return df.reset_index(drop=True)
 
 
def limpiar_campanas(df: pd.DataFrame) -> pd.DataFrame:
 
    df = df.drop_duplicates(subset="campaña_id").copy()
 
    df["plataforma"] = _normalizar_categoria(df["plataforma"], _ALIAS_PLATAFORMA, "plataforma")
    df["fecha"] = _normalizar_fecha(df["fecha"])
 
    for col in ("impresiones", "clics", "costo", "leads", "conversiones"):
        df[col] = pd.to_numeric(df[col], errors="coerce").clip(lower=0)
 
    return df.reset_index(drop=True)
 