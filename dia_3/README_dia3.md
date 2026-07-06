# Día 3 — Modelado Dimensional y Carga al Data Warehouse

## Objetivo del día
Tomar los datos ya limpios del Día 2 (`dia2_parte2_calidad_limpieza/data/processed`), diseñar el modelo dimensional (esquema estrella) y cargarlo al Data Warehouse en BigQuery (`dw_datacommerce`).

## Qué se hizo

1. **Diseño del modelo estrella**: 7 tablas de dimensión y 4 tablas de hechos.
2. **Construcción de las tablas** (`modelado.py`): lee los Parquet limpios del Día 2, genera llaves sustitutas (surrogate keys) donde no existía un ID de origen (canal, método de pago, plataforma, bodega), arma las dimensiones y las tablas de hechos, y las guarda en `data/dw/*.parquet`.
3. **Carga a BigQuery** (`cargar_bigquery.py`): sube cada tabla generada al dataset `dw_datacommerce`, reemplazando el contenido en cada corrida (`WRITE_TRUNCATE`) para que el pipeline sea reproducible.
4. **Orquestador** (`ejecutar_dia3.py`): corre los dos pasos anteriores con un solo comando.

## Estructura de archivos

| Archivo | Función |
|---|---|
| `config.py` | Configuración central: `PROJECT_ID`, dataset, rutas y ruta de la clave de credenciales |
| `esquema_dw.sql` | DDL de las 11 tablas del modelo estrella (correrlo una vez en BigQuery antes de cargar datos) |
| `modelado.py` | Construye dimensiones y hechos a partir de los datos limpios del Día 2 |
| `cargar_bigquery.py` | Sube las tablas generadas a BigQuery |
| `ejecutar_dia3.py` | Orquestador: corre `modelado.py` + `cargar_bigquery.py` |
| `generar_diagrama.py` | Genera `diagrama_modelo_estrella.svg` |
| `diagrama_modelo_estrella.svg` | Diagrama visual del modelo estrella |
| `diccionario_datos.md` | Diccionario de datos: cada tabla, columna, tipo y descripción |
| `data/dw/*.parquet` | Salida intermedia de `modelado.py` (se regenera en cada corrida, no se versiona) |

## Cómo correrlo

Requisitos: tener la carpeta `dia2_parte2_calidad_limpieza/` al mismo nivel que esta, con los datos limpios ya generados.

```bash
pip install google-cloud-bigquery pandas pyarrow --break-system-packages

# 1. Crear las tablas en BigQuery con el esquema correcto (una sola vez)
#    -> pegar el contenido de esquema_dw.sql en BigQuery, pestaña "Consulta en SQL"

# 2. Colocar la clave de la cuenta de servicio como:
#    dia3_modelado_carga/credenciales_bigquery.json

# 3. Correr el pipeline completo
python ejecutar_dia3.py
```

## Decisiones técnicas

- **Cliente huérfano**: la venta `1005` (cliente_id `504`) no tenía coincidencia en la tabla de clientes de origen (ver `hallazgos_calidad.md` del Día 2). En vez de descartar la venta, se creó el registro `cliente_key = -1` ("Cliente desconocido") en `dim_cliente`, para conservar el ingreso registrado sin romper el JOIN.
- **`dim_sucursal` genérica**: no se recibió un catálogo real de sucursales (nombres, direcciones); la dimensión se construyó solo con el `sucursal_id` disponible en las ventas, con nombres genéricos ("Sucursal 1/2/3"). Pendiente de enriquecer si aparece la fuente real.
- **Llaves sustitutas para catálogos pequeños**: canal de venta, método de pago, plataforma y bodega llegaban como texto libre dentro de las tablas de hechos; se generaron dimensiones tipo catálogo con llave autogenerada a partir de los valores únicos, evitando texto repetido en los hechos (buena práctica de modelado dimensional).

## Resultado

11 tablas cargadas en `dw_datacommerce`: `dim_producto`, `dim_cliente`, `dim_sucursal`, `dim_canal`, `dim_metodo_pago`, `dim_plataforma`, `dim_bodega`, `fact_ventas`, `fact_movimiento_inventario`, `fact_inventario_existencia`, `fact_marketing`.
