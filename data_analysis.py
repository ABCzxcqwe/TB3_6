from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = Path(__file__).resolve().parent
RUTA_DATASET = AQUI / "reservas.csv"
ASSETS = AQUI / "assets"
ASSETS.mkdir(exist_ok=True)

df = pd.read_csv(RUTA_DATASET)


# ========= 3.1 CONOCER LOS DATOS =========
print("== 3.1 Conocer los datos ==")
print("Filas y columnas:", df.shape)
print("Columnas:", list(df.columns))
print("Primeras filas:")
print(df.head(3).to_string(index=False))
print("Info de tipos:")
print(df.info())


# ========= 3.2 METRICAS DESCRIPTIVAS =========
print("\n== 3.2 Metricas descriptivas ==")

print("\n1) Cantidad por tipo de evento (value_counts):")
print(df["tipo_evento"].value_counts().to_string())

print("\n2) Porcentaje por tipo de evento (%):")
print((df["tipo_evento"].value_counts(normalize=True) * 100).round(1).to_string())

print("\n3) Monto:")
print("  Promedio: S/", round(df["monto"].mean(), 2))
print("  Total: S/", round(df["monto"].sum(), 2))
print("  Maximo: S/", round(df["monto"].max(), 2))
print("  Minimo: S/", round(df["monto"].min(), 2))

print("\n4) Monto total por tipo de evento (groupby):")
print(df.groupby("tipo_evento")["monto"].sum().round(2).to_string())

print("\n5) Monto promedio por tipo de evento (groupby):")
print(df.groupby("tipo_evento")["monto"].mean().round(2).to_string())

print("\n6) Valores NULOS por columna (isnull().sum()):")
nulos = df.isnull().sum()
print(nulos.to_string())
print("Columna con mas nulos:", nulos.idxmax(), "->", int(nulos.max()))
print("Total de celdas nulas:", int(nulos.sum()))


# ========= 3.3 VISUALIZACION (4+1 graficos) =========
print("\n== 3.3 Visualizacion de datos ==")

# g1 - Barras: monto por tipo de evento
df.groupby("tipo_evento")["monto"].mean().sort_values().plot(
    kind="bar", color="steelblue"
)
plt.title("Monto promedio por tipo de evento")
plt.xlabel("Tipo de evento"); plt.ylabel("Monto promedio (S/)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(ASSETS / "g1_barras_monto_tipo.png")
plt.close()
print("g1_barras_monto_tipo.png")

# g2 - Torta: proporcion de cada tipo de evento
df["tipo_evento"].value_counts().plot(kind="pie", autopct="%1.1f%%", ylabel="")
plt.title("Proporcion de reservas por tipo de evento")
plt.tight_layout()
plt.savefig(ASSETS / "g2_torta_tipos.png")
plt.close()
print("g2_torta_tipos.png")

# g3 - Histograma: distribucion del monto
plt.hist(df["monto"].dropna(), bins=40, color="coral", edgecolor="white")
plt.title("Distribucion del monto")
plt.xlabel("Monto (S/)"); plt.ylabel("Cantidad")
plt.tight_layout()
plt.savefig(ASSETS / "g3_histograma_monto.png")
plt.close()
print("g3_histograma_monto.png")

# g4 - Linea: monto por mes
df["mes"] = pd.to_datetime(df["fecha"]).dt.month
df.groupby("mes")["monto"].sum().plot(kind="line", marker="o", color="indianred")
plt.title("Monto total por mes")
plt.xlabel("Mes"); plt.ylabel("Monto (S/)")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(ASSETS / "g4_linea_por_mes.png")
plt.close()
print("g4_linea_por_mes.png")


# ========= 4 FUNCIONALIDADES A INVESTIGAR =========
print("\n== 4 Funcionalidades a Investigar (obligatorias) ==")

# F1: Filtrar registros con monto > 2500
print("\nF1) Registros con monto > 2500:")
filtro = df[df["monto"] > 2500]
print("  Cantidad:", len(filtro))
print("  % del total:", round(len(filtro) / len(df) * 100, 2))

# F2: Top 5 registros con mayor monto
print("\nF2) Top 5 registros con mayor monto:")
top5 = df.nlargest(5, "monto")
print(top5[["id", "tipo_evento", "ambiente", "capacidad", "horas", "monto"]].to_string(index=False))

# F3: Clasificar monto en bajo, medio, alto
print("\nF3) Clasificacion del monto (bajo, medio, alto):")
bins = [0, 1500, 2200, df["monto"].max()]
labels = ["Bajo", "Medio", "Alto"]
df["clasificacion_monto"] = pd.cut(df["monto"], bins=bins, labels=labels)
print(df["clasificacion_monto"].value_counts().to_string())

# F4: Grafico adicional - barras horizontales por tipo de evento
df["tipo_evento"].value_counts().plot(kind="barh", color="teal")
plt.title("Cantidad de reservas por tipo de evento")
plt.xlabel("Cantidad"); plt.ylabel("Tipo de evento")
plt.tight_layout()
plt.savefig(ASSETS / "g5_barras_horizontales.png")
plt.close()
print("\nF4) g5_barras_horizontales.png")
