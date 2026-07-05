-- Día 3 - Modelo dimensional (esquema estrella) para dw_datacommerce

CREATE SCHEMA IF NOT EXISTS `dw_datacommerce`;

-- ===================== DIMENSIONES =====================

CREATE OR REPLACE TABLE `dw_datacommerce.dim_producto` (
  producto_key    INT64 NOT NULL,
  nombre_producto STRING,
  categoria       STRING,
  subcategoria    STRING,
  marca           STRING,
  costo_unitario  NUMERIC,
  precio_lista    NUMERIC,
  proveedor_id    INT64
);

CREATE OR REPLACE TABLE `dw_datacommerce.dim_cliente` (
  cliente_key      INT64 NOT NULL,   -- -1 = cliente desconocido (huérfano en origen)
  nombre           STRING,
  genero           STRING,
  edad             INT64,
  departamento     STRING,
  municipio        STRING,
  fecha_registro   DATE,
  segmento_cliente STRING
);

CREATE OR REPLACE TABLE `dw_datacommerce.dim_sucursal` (
  sucursal_key     INT64 NOT NULL,
  nombre_sucursal  STRING
);

CREATE OR REPLACE TABLE `dw_datacommerce.dim_canal` (
  canal_key    INT64 NOT NULL,
  canal_venta  STRING
);

CREATE OR REPLACE TABLE `dw_datacommerce.dim_metodo_pago` (
  metodo_pago_key INT64 NOT NULL,
  metodo_pago     STRING
);

CREATE OR REPLACE TABLE `dw_datacommerce.dim_plataforma` (
  plataforma_key INT64 NOT NULL,
  plataforma     STRING
);

CREATE OR REPLACE TABLE `dw_datacommerce.dim_bodega` (
  bodega_key INT64 NOT NULL,
  bodega     STRING
);

-- ===================== HECHOS =====================

CREATE OR REPLACE TABLE `dw_datacommerce.fact_ventas` (
  venta_id         INT64 NOT NULL,
  fecha_venta      DATE,
  cliente_key      INT64,
  producto_key     INT64,
  sucursal_key     INT64,
  canal_key        INT64,
  metodo_pago_key  INT64,
  cantidad         INT64,
  precio_unitario  NUMERIC,
  descuento        NUMERIC,
  total_venta      NUMERIC
);

CREATE OR REPLACE TABLE `dw_datacommerce.fact_movimiento_inventario` (
  id            INT64 NOT NULL,
  producto_key  INT64,
  fecha         DATE,
  tipo          STRING,
  cantidad      INT64
);

CREATE OR REPLACE TABLE `dw_datacommerce.fact_inventario_existencia` (
  producto_key  INT64,
  bodega_key    INT64,
  existencia    INT64
);

CREATE OR REPLACE TABLE `dw_datacommerce.fact_marketing` (
  campana_id     INT64 NOT NULL,
  fecha          DATE,
  plataforma_key INT64,
  impresiones    INT64,
  clics          INT64,
  costo          NUMERIC,
  leads          INT64,
  conversiones   INT64
);
