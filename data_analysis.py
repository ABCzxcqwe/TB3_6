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

print("\n3) Monto promedio por tipo de evento (groupby):")
print(df.groupby("tipo_evento")["monto"].mean().round(2).to_string())

print("\n4) Horas promedio por servicio (groupby):")
print(df.groupby("servicio")["horas"].mean().round(2).to_string())

print("\n5) Capacidad:")
print("  Maximo:", round(df["capacidad"].max(), 0))
print("  Minimo:", round(df["capacidad"].min(), 0))
print("  Promedio:", round(df["capacidad"].mean(), 1))

print("\n6) Monto total por evento_grande (groupby):")
print(df.groupby("evento_grande")["monto"].sum().round(2).to_string())

print("\n7) Valores NULOS por columna (isnull().sum()):")
nulos = df.isnull().sum()
print(nulos.to_string())
print("Columna con mas nulos:", nulos.idxmax(), "->", int(nulos.max()))
print("Total de celdas nulas:", int(nulos.sum()))


# ========= 3.3 VISUALIZACION (4 graficos) =========
# g1 - Barras: cantidad por tipo de evento
df["tipo_evento"].value_counts().plot(kind="bar", color="steelblue")
plt.title("Cantidad de reservas por tipo de evento")
plt.xlabel("Tipo de evento"); plt.ylabel("Cantidad")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(ASSETS / "g1_barras_eventos.png")
plt.close()
print("\n== 3.3 Graficos guardados ==")
print("g1_barras_eventos.png")

# g2 - Barras: monto promedio por tipo de evento
df.groupby("tipo_evento")["monto"].mean().sort_values().plot(
    kind="bar", color="seagreen"
)
plt.title("Monto promedio por tipo de evento")
plt.xlabel("Tipo de evento"); plt.ylabel("Monto promedio (S/)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(ASSETS / "g2_barras_monto_tipo.png")
plt.close()
print("g2_barras_monto_tipo.png")

# g3 - Histograma: distribucion de montos
plt.hist(df["monto"].dropna(), bins=40, color="coral", edgecolor="white")
plt.title("Distribucion de montos")
plt.xlabel("Monto (S/)"); plt.ylabel("Cantidad")
plt.tight_layout()
plt.savefig(ASSETS / "g3_histograma_monto.png")
plt.close()
print("g3_histograma_monto.png")

# g4 - Dispersion: capacidad vs monto
muestra = df.sample(n=2000, random_state=42)
plt.scatter(muestra["capacidad"], muestra["monto"], s=5, alpha=0.3, c="purple")
plt.title("Capacidad vs Monto")
plt.xlabel("Capacidad (personas)"); plt.ylabel("Monto (S/)")
plt.tight_layout()
plt.savefig(ASSETS / "g4_dispersion_capacidad_monto.png")
plt.close()
print("g4_dispersion_capacidad_monto.png")
