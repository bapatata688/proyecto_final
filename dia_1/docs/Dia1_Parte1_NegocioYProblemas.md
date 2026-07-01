# Día 1 – Parte 1: Negocio, revisión de archivos e identificación de problemas
## DataCommerce GT

---

## 1. Comprender el negocio

DataCommerce GT es una empresa que vende productos tecnológicos a través de 4 canales: tiendas físicas, comercio electrónico, ventas corporativas y WhatsApp.

Con el crecimiento de la empresa, la información quedó dispersa en distintos sistemas lo que provoca que la gerencia no tenga reportes confiables ni oportunos, y que cada departamento genere resultados que no coinciden entre sí.

**¿Cómo se le dará solución?** Construyendo una plataforma de datos que integre todas las fuentes en un único Data Warehouse, de manera que exista una sola fuente de verdad para generar los indicadores que la gerencia necesita para tomar decisiones.

---

## 2. Revisar archivos

En esa revisión se hará una exploración inicial de cada fuente: cuántas filas y columnas tiene, qué tipos de datos contiene, y una primera mirada a posibles inconsistencias (duplicados, nulos, formatos de fecha, textos mal escritos, etc.).

---

## 3. Identificar problemas

El objetivo de hacerlo así es que, para cuando avancemos en el Día 2 con la limpieza y estandarización, ya tengamos claro:
- Qué columnas tienen valores nulos o faltantes.
- Qué registros están duplicados.
- Qué formatos son inconsistentes entre fuentes (fechas, nombres, categorías, IDs).
- Qué reglas de limpieza y estandarización se deben aplicar y por qué.

De esta manera, la limpieza del Día 2 no se hace hara a ciegas, sino con base en los problemas ya identificados y documentados.
