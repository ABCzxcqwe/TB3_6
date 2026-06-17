from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

AQUI = Path(__file__).resolve().parent
RUTA_DATASET = AQUI / "reservas.csv"
ASSETS = AQUI / "assets"
ASSETS.mkdir(exist_ok=True)


# ---------- FASE 1: CARGAR LOS DATOS ----------
df = pd.read_csv(RUTA_DATASET)
print(f"FASE 1 - Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")


# ---------- FASE 2: REVISAR LA SUCIEDAD (justifica limpiar) ----------
nulos = df.isnull().sum()
print("\nFASE 2 - Datos vacios por columna:")
print(nulos[nulos > 0].to_string())

nulos[nulos > 0].plot(kind="bar", color="tomato")
plt.title("Datos vacios antes de limpiar")
plt.ylabel("Cantidad de nulos")
plt.tight_layout()
plt.savefig(ASSETS / "1_datos_sucios.png")
plt.close()


# ---------- FASE 3: LIMPIAR LOS DATOS ----------
columnas_con_nulos = ["capacidad", "horas", "monto", "tipo_evento", "servicio", "evento_grande"]
df_clean = df.dropna(subset=columnas_con_nulos)
print(f"\nFASE 3 - Datos limpios: {df_clean.shape[0]} filas, {df.shape[0] - df_clean.shape[0]} eliminadas")


# ---------- FASE 4: PREPARAR LOS DATOS ----------
y = df_clean["monto"]
X = df_clean[["capacidad", "horas", "tipo_evento", "servicio", "evento_grande"]]
X = pd.get_dummies(X)
print(f"FASE 4 - Listo. Columnas para predecir: {X.shape[1]}")


# ---------- FASE 5: DIVIDIR Y ENTRENAR ----------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = LinearRegression()
modelo.fit(X_train, y_train)
print(f"FASE 5 - Modelo entrenado con {len(X_train)} filas")


# ---------- FASE 6: EVALUAR ----------
y_pred = modelo.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
print(f"\nFASE 6 - RMSE: {rmse:.2f} S/, R²: {r2:.4f}")

plt.scatter(y_test, y_pred, s=4, alpha=0.2)
plt.plot([y.min(), y.max()], [y.min(), y.max()], "r--", label="prediccion perfecta")
plt.xlabel("Monto real (S/)")
plt.ylabel("Monto predicho (S/)")
plt.title("Real vs predicho (R² = {:.4f})".format(r2))
plt.legend()
plt.tight_layout()
plt.savefig(ASSETS / "2_prediccion.png")
plt.close()
print("2_prediccion.png guardado")


# ---------- FASE 7: COEFICIENTES ----------
print("\nFASE 7 - Coeficientes del modelo (que variables influyen mas):")
coefs = pd.Series(modelo.coef_, index=X.columns)
print("\nTop 5 que MAS aumentan el monto:")
print(coefs.sort_values(ascending=False).head(5).to_string())
print("\nTop 5 que MAS reducen el monto:")
print(coefs.sort_values(ascending=True).head(5).to_string())
print(f"\nIntercept (monto base): S/ {modelo.intercept_:.2f}")


# ---------- FASE 8: PREDICCION DE EJEMPLO ----------
print("\nFASE 8 - Prediccion de ejemplo:")
ejemplo = pd.DataFrame([{
    "capacidad": 300, "horas": 6,
    "tipo_evento": "Boda", "servicio": "Catering", "evento_grande": "Si"
}])
ejemplo = pd.get_dummies(ejemplo).reindex(columns=X.columns, fill_value=0)
pred = modelo.predict(ejemplo)[0]
print(f"  Boda, 300 personas, 6 horas, Catering -> S/ {pred:.2f}")
