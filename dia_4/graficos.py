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
 
 
TOP_N_PRODUCTOS = 15
TOP_N_SUCURSALES = 15
TOP_N_BAJO_STOCK = 15
 
 
def grafico_top_productos():
    df = pd.read_csv(DATA_KPIS_DIR / "top_productos.csv")
    # Con miles de productos, graficarlos TODOS vuelve el gráfico ilegible.
    # kpis.top_productos() ya viene ordenado descendente -> se toma el Top N.
    df = df.head(TOP_N_PRODUCTOS)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(df["nombre_producto"], df["monto_vendido"], color="#c05621")
    ax.set_title(f"Top {TOP_N_PRODUCTOS} productos por monto vendido")
    ax.set_xlabel("Monto vendido (Q)")
    ax.invert_yaxis()
    ax.tick_params(axis="y", labelsize=9)
    fig.savefig(GRAFICOS_DIR / "top_productos.png", dpi=150)
    plt.close(fig)
 
 
def grafico_ventas_por_sucursal():
    df = pd.read_csv(DATA_KPIS_DIR / "ventas_por_sucursal.csv")
    df = df.sort_values("ventas_totales", ascending=False).head(TOP_N_SUCURSALES)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(df["nombre_sucursal"], df["ventas_totales"], color="#2f855a")
    ax.set_title(f"Top {TOP_N_SUCURSALES} sucursales por ventas totales")
    ax.set_ylabel("Ventas totales (Q)")
    ax.tick_params(axis="x", labelrotation=45, labelsize=8)
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
    # Con miles de productos, lo útil para el negocio es ver los de MENOR
    # existencia (riesgo de quiebre de stock), no los 4,100 completos.
    df = df.sort_values("existencia", ascending=True).head(TOP_N_BAJO_STOCK)
    fig, ax = plt.subplots(figsize=(8, 6))
    barras = ax.barh(df["nombre_producto"], df["existencia"], color="#dd6b20")
    ax.set_title(f"{TOP_N_BAJO_STOCK} productos con menor existencia (riesgo de quiebre)")
    ax.set_xlabel("Unidades")
    ax.invert_yaxis()
    ax.tick_params(axis="y", labelsize=9)
    # Etiqueta numérica en cada barra: sin esto, una existencia de 0 se ve
    # como una barra "ausente" en vez de un 0 real -- con miles de productos
    # es común que varios de los de menor stock estén exactamente en 0.
    ax.bar_label(barras, padding=3, fontsize=8)
    maximo = max(df["existencia"].max(), 1)
    ax.set_xlim(0, maximo * 1.15)
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
 