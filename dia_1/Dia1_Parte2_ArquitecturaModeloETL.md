# Día 1 – Parte 2: Arquitectura, modelo relacional y plan del ETL
## DataCommerce GT

---

## 4. Diseño de la arquitectura de la solución propuesta

```
[Fuentes de datos]
  CSV (Ventas) | Excel (Productos) | JSON (Clientes) | SQLite (Inventario) | API REST (Campañas)
        │
        ▼
[Extracción] → scripts Python (pandas, requests, sqlite3, openpyxl)
        │
        ▼
[Staging] → datos crudos unificados, sin transformar (para trazabilidad)
        │
        ▼
[Transformación / Calidad de datos]
  - Limpieza (duplicados, nulos, formatos)
  - Estandarización (nombres, categorías, fechas, monedas)
  - Validación de reglas de negocio
        │
        ▼
[Data Warehouse] → modelo dimensional (esquema estrella) en BigQuery / Snowflake
        │
        ▼
[Consumo] → consultas SQL, KPIs con Pandas, Dashboard
```

**Stack tecnológico:**
- Python + Pandas → extracción y transformación (ETL)
- BigQuery / Snowflake / SQLite → Data Warehouse
- SQL → consultas analíticas
- Herramienta de visualización (a definir en base a la información proporcionada) dashboard

**Por qué esta arquitectura:**
- Se separa staging de transformación para no perder los datos crudos originales.
- El pipeline se diseña para ser reproducible por que debe poder ejecutarse de nuevo sin intervención manual.
- El modelo dimensional facilita las consultas analíticas y el cálculo de KPIs para gerencia.

---

## 5. Modelo relacional (entidad-relación, preliminar)

A partir de lo que describe el enunciado del proyecto se tiene

**Entidades identificadas:**
- **Cliente** 
- **Producto** 
- **Venta** 
- **Inventario** 
- **Tienda/Canal** 
- **Campaña** 

**Relaciones esperadas:**
- Un Cliente puede tener muchas Ventas (1:N)
- Un Producto puede aparecer en muchas Ventas (1:N)
- Un Producto tiene inventario en varias Tiendas (N:M, vía Inventario)
- Una Campaña puede influir en varias Ventas 

---

## 6. Plan del ETL

**Extracción (por fuente):**
- CSV → `pandas.read_csv()`
- Excel → `pandas.read_excel()`
- JSON → `pandas.read_json()` o `json.load()` si hay anidamiento
- SQLite → `sqlite3` / `pandas.read_sql()`
- API REST → `requests.get()` con manejo de paginación/errores

**Transformaciones esperadas a realizar, aunque variara dependiendo de los datos:**
- Eliminar duplicados por clave primaria
- Normalizar fechas a formato `YYYY-MM-DD`
- Estandarizar nombres y categorías (mayúsculas, sin espacios extra)
- Definir regla para valores nulos (eliminar, imputar o marcar)
- Unificar IDs entre fuentes

**Carga:**
- Primero a staging (datos crudos)
- Luego, transformación y carga al modelo dimensional en el Data Warehouse
