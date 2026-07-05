"""
Día 3 - Orquestador.

Corre todo el pipeline del día 3 en un solo comando:
  1. modelado.py     -> construye dim/fact a partir de calidad/data/processed
  2. cargar_bigquery.py -> sube esas tablas al Data Warehouse

Uso:
    python ejecutar_dia3.py
"""

import modelado
import cargar_bigquery


def main():
    print("=== PASO 1: Modelado dimensional ===")
    modelado.main()

    print("\n=== PASO 2: Carga a BigQuery ===")
    cargar_bigquery.main()

    print("\nDía 3 completado: modelo dimensional generado y cargado al DW.")


if __name__ == "__main__":
    main()
