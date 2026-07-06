"""
Día 4 - Orquestador.

Corre todo el pipeline del día 4 en un solo comando:
  1. calcular_kpis.py -> lee el DW en BigQuery y calcula los KPIs (CSV)
  2. graficos.py       -> genera los gráficos PNG a partir de esos KPIs

Uso:
    python ejecutar_dia4.py
"""

import calcular_kpis
import graficos


def main():
    print("=== PASO 1: Cálculo de KPIs ===")
    calcular_kpis.main()

    print("\n=== PASO 2: Generación de gráficos ===")
    graficos.main()

    print("\nDía 4 completado: KPIs calculados y gráficos generados.")


if __name__ == "__main__":
    main()
