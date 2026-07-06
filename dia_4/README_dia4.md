# Día 4 — Consultas SQL, KPIs con Pandas y Gráficos

## Objetivo del día
Consultar el Data Warehouse construido en el Día 3 (`dw_datacommerce`), calcular indicadores de negocio (KPIs) con Pandas, validarlos y generar los gráficos que soportarán el dashboard y el informe ejecutivo del Día 5.

## Qué se hizo

1. **Consultas SQL analíticas** (`consultas_sql.sql`): 8 consultas directas sobre las tablas de BigQuery del Día 3, para responder preguntas de negocio (ventas por canal, top productos, ventas por sucursal, método de pago, top clientes, existencia de inventario, desempeño de marketing, movimientos de inventario).
2. **Cálculo de KPIs con Pandas** (`kpis.py` + `calcular_kpis.py`): en vez de calcular los indicadores solo en SQL, se trae cada tabla desde BigQuery a un DataFrame y se recalculan los mismos indicadores con Pandas, como pide el objetivo del curso ("construir indicadores con Python y Pandas"). Los resultados se guardan como CSV en `data/kpis/`.
3. **Gráficos** (`graficos.py`): a partir de esos CSV, se generan 6 gráficos PNG en `graficos/`, listos para el dashboard y la presentación ejecutiva.
4. **Orquestador** (`ejecutar_dia4.py`): corre el cálculo de KPIs y la generación de gráficos con un solo comando.

## Estructura de archivos

| Archivo | Función |
|---|---|
| `config.py` | Configuración central: `PROJECT_ID`, dataset, rutas y ruta de la clave de credenciales (reutiliza la del Día 3) |
| `consultas_sql.sql` | 8 consultas SQL analíticas para correr directamente en BigQuery |
| `kpis.py` | Funciones puras de cálculo de KPIs con Pandas (reciben DataFrames, no dependen de BigQuery, por lo que se pueden probar con datos locales) |
| `calcular_kpis.py` | Trae las tablas desde BigQuery y llama a `kpis.py` para calcular cada indicador; guarda los resultados en `data/kpis/*.csv` |
| `graficos.py` | Lee los CSV de `data/kpis/` y genera los gráficos PNG en `graficos/` |
| `ejecutar_dia4.py` | Orquestador: corre `calcular_kpis.py` + `graficos.py` |
| `data/kpis/*.csv` | Salida de los KPIs calculados (se regenera en cada corrida, no se versiona) |
| `graficos/*.png` | Gráficos generados (se regeneran en cada corrida, no se versionan) |

## KPIs calculados

1. Ventas totales y ticket promedio por canal de venta
2. Top productos por unidades y monto vendido
3. Ventas totales por sucursal
4. Método de pago más usado
5. Top clientes por monto de compra
6. Existencia actual de inventario por producto y bodega
7. Desempeño de campañas de marketing por plataforma: CTR, costo por lead, tasa de conversión
8. Movimientos de inventario por tipo (entradas vs. salidas)

## Cómo correrlo

Requisitos: haber corrido `ejecutar_dia3.py` al menos una vez (para que existan datos en `dw_datacommerce`), y tener `dia4_analisis_kpis/` al mismo nivel que `dia3_modelado_carga/`.

```bash
pip install google-cloud-bigquery pandas pyarrow matplotlib --break-system-packages

# Usa la misma clave del Día 3 (dia3_modelado_carga/credenciales_bigquery.json)
# o cópiala a esta carpeta si prefieres tenerla local.

python ejecutar_dia4.py
```

## Validación de resultados

Cada KPI calculado con Pandas corresponde a una de las consultas SQL de `consultas_sql.sql`; se puede validar corriendo la consulta en BigQuery y comparando el resultado contra el CSV generado en `data/kpis/`. Esto se hizo antes de entregar el pipeline, comparando manualmente ambos resultados sobre los mismos datos.

## Resultado

8 archivos CSV con los KPIs de negocio y 6 gráficos PNG (`ventas_por_canal`, `top_productos`, `ventas_por_sucursal`, `metodo_pago`, `marketing_ctr`, `existencia_inventario`), listos para alimentar el dashboard y el informe ejecutivo del Día 5.
