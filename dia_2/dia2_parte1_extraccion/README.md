# Día 2 — Extracción, Calidad y Limpieza
## DataCommerce GT — Proyecto Final Integrador (Ingeniería de Datos)

## 1. Qué se hizo

Según el cronograma del proyecto (`tarea.md`, Día 2): extraer datos de las 5
fuentes, documentar los hallazgos de calidad y desarrollar la limpieza y
estandarización.

Se trabajó directamente sobre los 5 archivos reales entregados por el
instructor (`ventas.csv`, `productos.xlsx`, `clientes.json`, `inventario.db`,
`api_marketing_response.json`) — no se usaron datos inventados.
`inventario.db` resultó tener **2 tablas** (`inventario_actual` y
`movimientos_inventario`), así que el pipeline extrae y limpia **6 tablas**
en total.

## 2. Los dos ZIP — IMPORTANTE

**Extrae ambos ZIP en la misma carpeta antes de ejecutar nada.** La parte 2
depende de `config.py` y de los datos que genera la parte 1 en
`data/interim/`.

- **Parte 1 — Extracción**: `config.py`, `extract.py`, el script de
  extracción, los 5 archivos fuente entregados, y su resultado ya extraído
  (`data/interim/`).
- **Parte 2 — Calidad y Limpieza**: `quality.py`, `clean.py`, los scripts de
  perfilado y limpieza, el resultado ya limpio (`data/processed/`) y el
  reporte de hallazgos.

## 3. Estructura completa (ambas partes combinadas)

```
dia2/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── config.py                # rutas, variables de entorno, logging
├── extract.py                # 6 funciones de extracción (una por tabla)
├── quality.py                 # perfilado de calidad + integridad referencial
├── clean.py                   # 6 funciones de limpieza (una por tabla)
├── ejecutar_extraccion.py
├── ejecutar_perfilado.py
├── ejecutar_limpieza.py
├── data/
│   ├── raw/          # archivos originales entregados por el instructor
│   ├── interim/       # extraído tal cual, sin limpiar (parquet)
│   └── processed/     # limpio y estandarizado (parquet), listo para día 3
└── reports/
    └── hallazgos_calidad.md
```

## 4. Instalación

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 5. Cómo correr el pipeline

En orden, desde la raíz del proyecto:

```bash
python ejecutar_extraccion.py    # lee data/raw/       -> data/interim/*.parquet
python ejecutar_perfilado.py     # perfila data/interim/ -> reports/hallazgos_calidad.md
python ejecutar_limpieza.py      # limpia data/interim/ -> data/processed/*.parquet
```

Cada script se puede volver a ejecutar cuantas veces sea necesario sin
intervención manual (regla del proyecto, `tarea.md` sección 7).

## 6. Las 6 tablas y su fuente real

| Tabla | Fuente | Origen |
|---|---|---|
| ventas | CSV | `data/raw/ventas.csv` |
| productos | Excel | `data/raw/productos.xlsx` |
| clientes | JSON | `data/raw/clientes.json` |
| inventario_actual | SQLite (tabla `inventario_actual`) | `data/raw/inventario.db` |
| movimientos_inventario | SQLite (tabla `movimientos_inventario`) | `data/raw/inventario.db` |
| campanas | API REST (mock si no hay URL configurada) | `data/raw/api_marketing_response.json` |

### Esquema real de columnas

- **ventas**: venta_id, fecha_venta, cliente_id, producto_id, sucursal_id, canal_venta, cantidad, precio_unitario, descuento, total_venta, metodo_pago
- **productos**: producto_id, nombre_producto, categoria, subcategoria, marca, costo_unitario, precio_lista, proveedor_id
- **clientes**: cliente_id, nombre, genero, edad, departamento, municipio, fecha_registro, segmento_cliente
- **inventario_actual**: producto_id, bodega, existencia
- **movimientos_inventario**: id, producto_id, fecha, tipo (Entrada/Salida), cantidad
- **campanas** (desde la clave `campaigns` del JSON): campaña_id, fecha, plataforma, impresiones, clics, costo, leads, conversiones

**Nota sobre volumen:** los archivos entregados tienen solo encabezados y
unas pocas filas de ejemplo. Ningún script asume un número fijo de filas:
funcionarán igual cuando el instructor entregue el volumen completo,
siempre que se mantengan estos mismos nombres de columna. Si un archivo
real trae una columna con otro nombre, hay que ajustarlo en `extract.py` y
`clean.py` — son los únicos dos archivos que los referencian.

## 7. Placeholder de la API de campañas

`extraer_campanas()` en `extract.py`:

1. Si `API_CAMPANAS_URL` está definida en `.env` (copia `.env.example`),
   consulta la API real.
2. Si no está definida, o si la consulta falla, usa
   `data/raw/api_marketing_response.json`. Se probó forzando una URL
   inválida: la falla se registra como advertencia y el pipeline sigue sin
   detenerse.

Cuando el instructor entregue la API real: definir `API_CAMPANAS_URL` (y
`API_CAMPANAS_KEY` si requiere autenticación) en `.env`, y volver a correr
`ejecutar_extraccion.py`. No hay que tocar código.

## 8. Hallazgos de calidad reales (resumen)

El reporte completo, generado automáticamente, está en
`reports/hallazgos_calidad.md`. Con 2 a 5 filas por fuente los hallazgos son
limitados, pero ya aparecen problemas concretos:

- **`ventas.fecha_venta` mezcla 3 formatos** en la misma columna:
  `2026-07-01` (AAAA-MM-DD), `01/07/2026` (DD/MM/AAAA) y `2026/07/02`
  (AAAA/MM/DD). Ver sección 9: no fue un caso trivial de resolver.
- **`clientes.municipio` llega como string vacío (`""`)**, no nulo, para un
  cliente (María Gómez). Un perfilador de nulos estándar no lo detecta
  porque `""` no es `NaN`; se corrige explícitamente en la limpieza.
- **Integridad referencial**: `cliente_id 504` aparece en una venta pero no
  existe en `clientes.json` — huérfano real, detectado automáticamente
  (sección "Integridad referencial" del reporte).
- Por observación directa (no automatizado): `producto_id 2004` aparece en
  productos y en una venta, pero no tiene registro en `inventario_actual`.
  Puede ser normal (producto sin stock aún) o un hueco de datos — vale la
  pena confirmarlo con el instructor cuando llegue el volumen completo.

## 9. Decisión técnica destacada: parseo de fechas mixtas

`pd.to_datetime(..., format="mixed", dayfirst=True)` parece la solución
obvia para una columna con formatos de fecha mezclados, pero se probó
contra estos datos reales y **produce fechas incorrectas**: en pandas 3.0,
además de resolver la ambigüedad de `01/07/2026`, también invierte mes y
día en fechas año-primero como `2026-07-01` (las convierte en 7 de enero en
vez de 1 de julio).

La solución en `clean.py` (función `_parsear_fecha`) detecta el formato por
la posición del año, que nunca es ambigua (siempre tiene 4 dígitos):

- Año primero (`AAAA-MM-DD` o `AAAA/MM/DD`) → se parsea directo, sin asumir
  día primero.
- Año al final (`DD/MM/AAAA`) → sí es ambiguo, se asume día primero
  (convención de Guatemala).

## 10. Reglas de limpieza aplicadas y su justificación

| Tabla | Regla | Justificación |
|---|---|---|
| ventas | Elimina duplicados por venta_id | Un id de venta no puede repetirse |
| ventas | Normaliza fecha_venta (3 formatos mezclados) | Ver sección 9 |
| ventas | cantidad/descuento negativos → valor absoluto | No existen ventas ni descuentos negativos |
| ventas | total_venta recalculado (cantidad × precio_unitario − descuento) | No arrastrar errores de captura del archivo original |
| productos | Elimina duplicados por producto_id | Un producto no puede repetirse en el catálogo |
| productos | Recorta espacios extra en campos de texto | Error común de captura manual |
| productos | categoria/subcategoria nulas → "Sin Categoría"/"Sin Subcategoría" | No perder el producto en reportes agrupados |
| productos | precio_lista no convertible → se descarta la fila | No se puede vender un producto sin precio |
| clientes | Elimina duplicados por cliente_id | Un cliente no puede repetirse |
| clientes | municipio `""` → nulo | String vacío no es un municipio válido (hallazgo real, sección 8) |
| clientes | fecha_registro normalizada | Consistencia con el resto de fechas del proyecto |
| inventario_actual | Elimina duplicados por (producto_id, bodega) | Una bodega no puede tener 2 registros del mismo producto |
| inventario_actual | existencia negativa → 0 | El stock físico nunca es negativo |
| movimientos_inventario | Elimina duplicados por id | Es la llave primaria del movimiento |
| movimientos_inventario | cantidad negativa → valor absoluto | La dirección la indica `tipo`; cantidad es la magnitud |
| campañas | Elimina duplicados por campaña_id | Una campaña no puede repetirse |
| campañas | impresiones/clics/costo/leads/conversiones negativos → 0 | Son métricas de conteo o gasto, nunca negativas |

## 11. Chequeo automático (self-check)

`ejecutar_limpieza.py` valida, después de limpiar cada tabla, que sus
propias reglas se cumplieron (sin duplicados por llave, sin negativos donde
no debería haberlos). Si algo se rompe, el script falla con un
`AssertionError` explícito en vez de guardar datos incorrectos
silenciosamente. No es una prueba exhaustiva — es el chequeo mínimo que
demuestra que la lógica no está rota.

## 12. Qué sigue (Día 3 en adelante)

Fuera del alcance del día 2: modelo dimensional, tablas de hechos y
dimensiones, carga al Data Warehouse (`tarea.md`, sección 9).
`data/processed/*.parquet` queda listo como insumo para ese paso.
