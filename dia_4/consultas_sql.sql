-- Día 4 - Consultas SQL analíticas sobre dw_datacommerce
-- Puedes pegar cada una en BigQuery -> "Consulta en SQL" para verlas por separado,
-- o dejarlas documentadas aquí como evidencia del entregable "consultas SQL".

-- 1) Ventas totales y ticket promedio por canal de venta
SELECT
  ca.canal_venta,
  COUNT(*)                         AS num_ventas,
  SUM(v.total_venta)               AS ventas_totales,
  ROUND(AVG(v.total_venta), 2)     AS ticket_promedio
FROM `dw_datacommerce.fact_ventas` v
JOIN `dw_datacommerce.dim_canal` ca ON v.canal_key = ca.canal_key
GROUP BY ca.canal_venta
ORDER BY ventas_totales DESC;

-- 2) Top productos por monto vendido
SELECT
  p.nombre_producto,
  p.categoria,
  SUM(v.cantidad)      AS unidades_vendidas,
  SUM(v.total_venta)   AS monto_vendido
FROM `dw_datacommerce.fact_ventas` v
JOIN `dw_datacommerce.dim_producto` p ON v.producto_key = p.producto_key
GROUP BY p.nombre_producto, p.categoria
ORDER BY monto_vendido DESC;

-- 3) Ventas por sucursal
SELECT
  s.nombre_sucursal,
  COUNT(*)             AS num_ventas,
  SUM(v.total_venta)   AS ventas_totales
FROM `dw_datacommerce.fact_ventas` v
JOIN `dw_datacommerce.dim_sucursal` s ON v.sucursal_key = s.sucursal_key
GROUP BY s.nombre_sucursal
ORDER BY ventas_totales DESC;

-- 4) Método de pago más usado
SELECT
  mp.metodo_pago,
  COUNT(*)             AS num_ventas,
  SUM(v.total_venta)   AS monto_total
FROM `dw_datacommerce.fact_ventas` v
JOIN `dw_datacommerce.dim_metodo_pago` mp ON v.metodo_pago_key = mp.metodo_pago_key
GROUP BY mp.metodo_pago
ORDER BY num_ventas DESC;

-- 5) Top clientes por monto de compra (incluye "Cliente desconocido" si aplica)
SELECT
  c.nombre,
  c.segmento_cliente,
  COUNT(*)             AS num_compras,
  SUM(v.total_venta)   AS monto_total
FROM `dw_datacommerce.fact_ventas` v
JOIN `dw_datacommerce.dim_cliente` c ON v.cliente_key = c.cliente_key
GROUP BY c.nombre, c.segmento_cliente
ORDER BY monto_total DESC;

-- 6) Existencia actual de inventario por producto y bodega
SELECT
  p.nombre_producto,
  b.bodega,
  fi.existencia
FROM `dw_datacommerce.fact_inventario_existencia` fi
JOIN `dw_datacommerce.dim_producto` p ON fi.producto_key = p.producto_key
JOIN `dw_datacommerce.dim_bodega` b ON fi.bodega_key = b.bodega_key
ORDER BY fi.existencia ASC;

-- 7) Desempeño de campañas de marketing por plataforma (CTR, CPL, conversión)
SELECT
  pl.plataforma,
  SUM(m.impresiones)  AS impresiones,
  SUM(m.clics)        AS clics,
  SUM(m.costo)        AS costo_total,
  SUM(m.leads)         AS leads,
  SUM(m.conversiones) AS conversiones,
  ROUND(SAFE_DIVIDE(SUM(m.clics), SUM(m.impresiones)) * 100, 2)   AS ctr_pct,
  ROUND(SAFE_DIVIDE(SUM(m.costo), SUM(m.leads)), 2)               AS costo_por_lead,
  ROUND(SAFE_DIVIDE(SUM(m.conversiones), SUM(m.clics)) * 100, 2)  AS tasa_conversion_pct
FROM `dw_datacommerce.fact_marketing` m
JOIN `dw_datacommerce.dim_plataforma` pl ON m.plataforma_key = pl.plataforma_key
GROUP BY pl.plataforma
ORDER BY costo_total DESC;

-- 8) Movimientos de inventario por tipo (entradas vs salidas)
SELECT
  tipo,
  COUNT(*)         AS num_movimientos,
  SUM(cantidad)    AS unidades_movidas
FROM `dw_datacommerce.fact_movimiento_inventario`
GROUP BY tipo;
