# Diccionario de Datos — dw_datacommerce (Día 3)

Data Warehouse en BigQuery, modelo estrella con 7 dimensiones y 4 tablas de hechos.
Generado por `modelado.py` a partir de los datos limpios del Día 2 y cargado con `cargar_bigquery.py`.

## Dimensiones

### dim_producto
| Columna | Tipo | Descripción |
|---|---|---|
| producto_key | INT64 (PK) | Identificador único del producto |
| nombre_producto | STRING | Nombre comercial del producto |
| categoria | STRING | Categoría general (ej. Electrónica) |
| subcategoria | STRING | Subcategoría específica |
| marca | STRING | Marca del producto |
| costo_unitario | NUMERIC | Costo de adquisición por unidad |
| precio_lista | NUMERIC | Precio de venta sugerido |
| proveedor_id | INT64 | Identificador del proveedor |

### dim_cliente
| Columna | Tipo | Descripción |
|---|---|---|
| cliente_key | INT64 (PK) | Identificador único del cliente. **`-1` = "Cliente desconocido"**, fila creada para ventas cuyo cliente_id no existía en el origen (ver hallazgos_calidad.md, día 2) |
| nombre | STRING | Nombre del cliente |
| genero | STRING | Género del cliente |
| edad | INT64 | Edad del cliente |
| departamento | STRING | Departamento de residencia |
| municipio | STRING | Municipio de residencia |
| fecha_registro | DATE | Fecha de alta del cliente |
| segmento_cliente | STRING | Segmento comercial (ej. Corporativo, Individual) |

### dim_sucursal
| Columna | Tipo | Descripción |
|---|---|---|
| sucursal_key | INT64 (PK) | Identificador de sucursal, tomado directo de `ventas.sucursal_id` |
| nombre_sucursal | STRING | Nombre genérico ("Sucursal 1/2/3"). **No se recibió un catálogo real de sucursales**; si aparece, se debe reemplazar esta dimensión con los nombres reales |

### dim_canal
| Columna | Tipo | Descripción |
|---|---|---|
| canal_key | INT64 (PK) | Llave sustituta generada a partir de los valores distintos de `canal_venta` |
| canal_venta | STRING | Canal de venta: Tienda, Web o WhatsApp |

### dim_metodo_pago
| Columna | Tipo | Descripción |
|---|---|---|
| metodo_pago_key | INT64 (PK) | Llave sustituta generada a partir de los valores distintos de `metodo_pago` |
| metodo_pago | STRING | Método de pago: Tarjeta, Efectivo o Transferencia |

### dim_plataforma
| Columna | Tipo | Descripción |
|---|---|---|
| plataforma_key | INT64 (PK) | Llave sustituta generada a partir de los valores distintos de `plataforma` |
| plataforma | STRING | Plataforma de marketing: Facebook o Instagram |

### dim_bodega
| Columna | Tipo | Descripción |
|---|---|---|
| bodega_key | INT64 (PK) | Llave sustituta generada a partir de los valores distintos de `bodega` |
| bodega | STRING | Nombre de la bodega (ej. Central) |

## Tablas de hechos

### fact_ventas
Granularidad: **una fila por venta**.
| Columna | Tipo | Descripción |
|---|---|---|
| venta_id | INT64 (PK) | Identificador de la venta |
| fecha_venta | DATE | Fecha en que se realizó la venta |
| cliente_key | INT64 (FK → dim_cliente) | Cliente que realizó la compra |
| producto_key | INT64 (FK → dim_producto) | Producto vendido |
| sucursal_key | INT64 (FK → dim_sucursal) | Sucursal donde se vendió |
| canal_key | INT64 (FK → dim_canal) | Canal por el que se vendió |
| metodo_pago_key | INT64 (FK → dim_metodo_pago) | Forma de pago usada |
| cantidad | INT64 | Unidades vendidas |
| precio_unitario | NUMERIC | Precio por unidad al momento de la venta |
| descuento | NUMERIC | Descuento aplicado |
| total_venta | NUMERIC | Monto total de la venta |

### fact_movimiento_inventario
Granularidad: **una fila por movimiento de inventario** (entrada o salida).
| Columna | Tipo | Descripción |
|---|---|---|
| id | INT64 (PK) | Identificador del movimiento |
| producto_key | INT64 (FK → dim_producto) | Producto afectado |
| fecha | DATE | Fecha del movimiento |
| tipo | STRING | Tipo de movimiento (entrada/salida) |
| cantidad | INT64 | Unidades movidas |

### fact_inventario_existencia
Granularidad: **una fila por producto y bodega** (snapshot de existencias actuales).
| Columna | Tipo | Descripción |
|---|---|---|
| producto_key | INT64 (FK → dim_producto) | Producto |
| bodega_key | INT64 (FK → dim_bodega) | Bodega donde está el inventario |
| existencia | INT64 | Unidades disponibles al momento del corte |

### fact_marketing
Granularidad: **una fila por campaña**.
| Columna | Tipo | Descripción |
|---|---|---|
| campana_id | INT64 (PK) | Identificador de la campaña |
| fecha | DATE | Fecha de la campaña |
| plataforma_key | INT64 (FK → dim_plataforma) | Plataforma donde corrió la campaña |
| impresiones | INT64 | Número de impresiones |
| clics | INT64 | Número de clics |
| costo | NUMERIC | Costo de la campaña |
| leads | INT64 | Leads generados |
| conversiones | INT64 | Conversiones logradas |

## Decisiones técnicas documentadas

1. **Cliente huérfano (venta 1005, cliente_id 504):** en lugar de descartar la venta, se creó el registro `cliente_key = -1` ("Cliente desconocido") en `dim_cliente`, para no perder el ingreso registrado ni romper el JOIN entre `fact_ventas` y `dim_cliente`.
2. **dim_sucursal genérica:** no se recibió un archivo fuente con el catálogo real de sucursales (nombres, direcciones), por lo que la dimensión se construyó solo con el ID disponible en `ventas.sucursal_id`. Pendiente de enriquecer si aparece la fuente real.
3. **Llaves sustitutas para catálogos pequeños** (canal, método de pago, plataforma, bodega): estos campos llegaban como texto libre dentro de las tablas de hechos; se generaron dimensiones tipo catálogo con `producto_key` autogenerado a partir de los valores únicos, siguiendo buenas prácticas de modelado dimensional (evitar texto repetido en la tabla de hechos).
