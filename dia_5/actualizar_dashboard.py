"""
Día 5 - Actualiza dashboard.html automáticamente con los KPIs más recientes.

Lee dia_4/data/kpis/kpis_resumen.json (generado por calcular_kpis.py) y
reemplaza el bloque de datos dentro de dashboard.html, entre los
comentarios ===DATOS_INICIO=== y ===DATOS_FIN===.

Así, cada vez que vuelvas a correr el pipeline del Día 4 con datos nuevos
(los oficiales del profesor, por ejemplo), solo necesitas correr este
script para que el dashboard quede al día -- sin editar nada a mano.

Uso:
    python actualizar_dashboard.py
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
# Ajusta esta ruta si tu carpeta del Día 4 tiene otro nombre en el repo
RESUMEN_JSON = BASE_DIR.parent / "dia_4" / "data" / "kpis" / "kpis_resumen.json"
DASHBOARD_HTML = BASE_DIR / "dashboard.html"

# Mapeo: nombre del KPI en el JSON -> nombre de la variable que usa dashboard.html
# y cómo renombrar sus columnas (dashboard.html espera nombres cortos como
# "segmento" en vez de "segmento_cliente", "ctr" en vez de "ctr_pct", etc.)
RENOMBRES = {
    "top_clientes": {"segmento_cliente": "segmento"},
    "existencia_inventario": {"nombre_producto": "producto"},
    "desempeno_marketing": {"ctr_pct": "ctr", "costo_por_lead": "cpl", "tasa_conversion_pct": "conv"},
}

CLAVE_JS = {
    "ventas_por_canal": "ventas_por_canal",
    "top_productos": "top_productos",
    "ventas_por_sucursal": "ventas_por_sucursal",
    "metodo_pago_mas_usado": "metodo_pago",
    "top_clientes": "top_clientes",
    "existencia_inventario": "existencia",
    "desempeno_marketing": "marketing",
}


def renombrar_columnas(nombre_kpi, filas):
    mapa = RENOMBRES.get(nombre_kpi, {})
    if not mapa:
        return filas
    nuevas = []
    for fila in filas:
        nueva = {mapa.get(k, k): v for k, v in fila.items()}
        nuevas.append(nueva)
    return nuevas


def main():
    if not RESUMEN_JSON.exists():
        raise FileNotFoundError(
            f"No encontré {RESUMEN_JSON}. Corre primero ejecutar_dia4.py "
            "(o calcular_kpis.py) para generar el resumen de KPIs."
        )

    with open(RESUMEN_JSON, encoding="utf-8") as f:
        resumen = json.load(f)

    bloque = {}
    for nombre_kpi, clave_js in CLAVE_JS.items():
        filas = resumen.get(nombre_kpi, [])
        bloque[clave_js] = renombrar_columnas(nombre_kpi, filas)

    js_datos = "const datos = " + json.dumps(bloque, ensure_ascii=False, indent=2) + ";"

    html = DASHBOARD_HTML.read_text(encoding="utf-8")
    patron = re.compile(
        r"(// ===DATOS_INICIO===.*?\n).*?(\n\s*// ===DATOS_FIN===)",
        re.DOTALL,
    )
    if not patron.search(html):
        raise RuntimeError(
            "No encontré los marcadores ===DATOS_INICIO=== / ===DATOS_FIN=== "
            "en dashboard.html. No se modificó el archivo."
        )

    html_nuevo = patron.sub(lambda m: m.group(1) + js_datos + m.group(2), html)
    DASHBOARD_HTML.write_text(html_nuevo, encoding="utf-8")
    print(f"dashboard.html actualizado con los KPIs de {RESUMEN_JSON}")


if __name__ == "__main__":
    main()
