"""
Día 4 - Paso 2: Construir gráficos a partir de los KPIs.

Lee los CSV generados por calcular_kpis.py en data/kpis/ y produce
gráficos PNG en graficos/, listos para el informe ejecutivo y el dashboard.
"""

import pandas as pd
import matplotlib.pyplot as plt
from config import DATA_KPIS_DIR, GRAFICOS_DIR

plt.rcParams["figure.autolayout"] = True


def grafico_ventas_por_canal():
    df = pd.read_csv(DATA_KPIS_DIR / "ventas_por_canal.csv")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["canal_venta"], df["ventas_totales"], color="#2c5282")
    ax.set_title("Ventas totales por canal")
    ax.set_ylabel("Ventas totales (Q)")
    fig.savefig(GRAFICOS_DIR / "ventas_por_canal.png", dpi=150)
    plt.close(fig)


def grafico_top_productos():
    df = pd.read_csv(DATA_KPIS_DIR / "top_productos.csv")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(df["nombre_producto"], df["monto_vendido"], color="#c05621")
    ax.set_title("Monto vendido por producto")
    ax.set_xlabel("Monto vendido (Q)")
    ax.invert_yaxis()
    fig.savefig(GRAFICOS_DIR / "top_productos.png", dpi=150)
    plt.close(fig)


def grafico_ventas_por_sucursal():
    df = pd.read_csv(DATA_KPIS_DIR / "ventas_por_sucursal.csv")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["nombre_sucursal"], df["ventas_totales"], color="#2f855a")
    ax.set_title("Ventas totales por sucursal")
    ax.set_ylabel("Ventas totales (Q)")
    fig.savefig(GRAFICOS_DIR / "ventas_por_sucursal.png", dpi=150)
    plt.close(fig)


def grafico_metodo_pago():
    df = pd.read_csv(DATA_KPIS_DIR / "metodo_pago_mas_usado.csv")
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(df["num_ventas"], labels=df["metodo_pago"], autopct="%1.0f%%",
           colors=["#2c5282", "#c05621", "#2f855a"])
    ax.set_title("Distribución de ventas por método de pago")
    fig.savefig(GRAFICOS_DIR / "metodo_pago.png", dpi=150)
    plt.close(fig)


def grafico_marketing():
    df = pd.read_csv(DATA_KPIS_DIR / "desempeno_marketing.csv")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["plataforma"], df["ctr_pct"], color="#805ad5")
    ax.set_title("CTR (%) por plataforma de marketing")
    ax.set_ylabel("CTR %")
    fig.savefig(GRAFICOS_DIR / "marketing_ctr.png", dpi=150)
    plt.close(fig)


def grafico_existencia_inventario():
    df = pd.read_csv(DATA_KPIS_DIR / "existencia_inventario.csv")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["nombre_producto"], df["existencia"], color="#dd6b20")
    ax.set_title("Existencia actual por producto")
    ax.set_ylabel("Unidades")
    fig.savefig(GRAFICOS_DIR / "existencia_inventario.png", dpi=150)
    plt.close(fig)


def main():
    grafico_ventas_por_canal()
    grafico_top_productos()
    grafico_ventas_por_sucursal()
    grafico_metodo_pago()
    grafico_marketing()
    grafico_existencia_inventario()
    print(f"Gráficos generados en {GRAFICOS_DIR}")


if __name__ == "__main__":
    main()
