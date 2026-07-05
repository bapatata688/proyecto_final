# Hallazgos de calidad de datos — Día 2

_Generado automáticamente el 2026-07-03 00:27._

Este reporte se regenera cada vez que se ejecuta este script. No editar a mano: los hallazgos deben salir siempre del perfilado real sobre los datos en `data/interim/`.

## Ventas

- Filas: 5
- Duplicados (fila completa): 0
- Duplicados por llave: 0
- Nulos por columna: ninguno
- Tipos de dato al leer el archivo crudo:
  - `venta_id`: int64
  - `fecha_venta`: str
  - `cliente_id`: int64
  - `producto_id`: int64
  - `sucursal_id`: int64
  - `canal_venta`: str
  - `cantidad`: int64
  - `precio_unitario`: int64
  - `descuento`: int64
  - `total_venta`: int64
  - `metodo_pago`: str
- Rangos numéricos (revisar valores fuera de lo esperado):
  - `venta_id`: min=1001, max=1005
  - `cliente_id`: min=501, max=504
  - `producto_id`: min=2001, max=2004
  - `sucursal_id`: min=1, max=3
  - `cantidad`: min=1, max=5
  - `precio_unitario`: min=250, max=4500
  - `descuento`: min=0, max=125
  - `total_venta`: min=750, max=9000

## Productos

- Filas: 4
- Duplicados (fila completa): 0
- Duplicados por llave: 0
- Nulos por columna: ninguno
- Tipos de dato al leer el archivo crudo:
  - `producto_id`: int64
  - `nombre_producto`: str
  - `categoria`: str
  - `subcategoria`: str
  - `marca`: str
  - `costo_unitario`: int64
  - `precio_lista`: int64
  - `proveedor_id`: int64
- Rangos numéricos (revisar valores fuera de lo esperado):
  - `producto_id`: min=2001, max=2004
  - `costo_unitario`: min=120, max=3800
  - `precio_lista`: min=250, max=4500
  - `proveedor_id`: min=900, max=902

## Clientes

- Filas: 3
- Duplicados (fila completa): 0
- Duplicados por llave: 0
- Nulos por columna: ninguno
- Tipos de dato al leer el archivo crudo:
  - `cliente_id`: int64
  - `nombre`: str
  - `genero`: str
  - `edad`: int64
  - `departamento`: str
  - `municipio`: str
  - `fecha_registro`: str
  - `segmento_cliente`: str
- Rangos numéricos (revisar valores fuera de lo esperado):
  - `cliente_id`: min=501, max=503
  - `edad`: min=27, max=42

## Inventario actual

- Filas: 3
- Duplicados (fila completa): 0
- Duplicados por llave: 0
- Nulos por columna: ninguno
- Tipos de dato al leer el archivo crudo:
  - `producto_id`: int64
  - `bodega`: str
  - `existencia`: int64
- Rangos numéricos (revisar valores fuera de lo esperado):
  - `producto_id`: min=2001, max=2003
  - `existencia`: min=15, max=120

## Movimientos de inventario

- Filas: 2
- Duplicados (fila completa): 0
- Duplicados por llave: 0
- Nulos por columna: ninguno
- Tipos de dato al leer el archivo crudo:
  - `id`: int64
  - `producto_id`: int64
  - `fecha`: str
  - `tipo`: str
  - `cantidad`: int64
- Rangos numéricos (revisar valores fuera de lo esperado):
  - `id`: min=1, max=2
  - `producto_id`: min=2001, max=2002
  - `cantidad`: min=2, max=10

## Campañas (marketing)

- Filas: 2
- Duplicados (fila completa): 0
- Duplicados por llave: 0
- Nulos por columna: ninguno
- Tipos de dato al leer el archivo crudo:
  - `campaña_id`: int64
  - `fecha`: str
  - `plataforma`: str
  - `impresiones`: int64
  - `clics`: int64
  - `costo`: float64
  - `leads`: int64
  - `conversiones`: int64
- Rangos numéricos (revisar valores fuera de lo esperado):
  - `campaña_id`: min=1, max=2
  - `impresiones`: min=9800, max=12000
  - `clics`: min=350, max=420
  - `costo`: min=110.0, max=150.5
  - `leads`: min=22, max=30
  - `conversiones`: min=6, max=8

## Integridad referencial

- ventas.producto_id -> productos: sin huérfanos

- ventas.cliente_id -> clientes: 1 huérfano(s) -> 504

- inventario_actual.producto_id -> productos: sin huérfanos

- movimientos_inventario.producto_id -> productos: sin huérfanos
