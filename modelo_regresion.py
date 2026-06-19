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


def fase1_cargar_datos():
    df = pd.read_csv(RUTA_DATASET)
    print(f"FASE 1 - Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
    return df


def fase2_revisar_suciedad(df):
    nulos = df.isnull().sum()
    print("\nFASE 2 - Datos vacios por columna:")
    print(nulos[nulos > 0].to_string())

    nulos[nulos > 0].plot(kind="bar", color="tomato")
    plt.title("Datos vacios antes de limpiar")
    plt.ylabel("Cantidad de nulos")
    plt.tight_layout()
    plt.savefig(ASSETS / "1_datos_sucios.png")
    plt.close()


def fase3_limpiar_datos(df):
    columnas_a_usar = ["tipo_evento", "ambiente", "servicio", "capacidad", "horas", "monto"]
    df_clean = df.dropna(subset=columnas_a_usar)
    print(f"\nFASE 3 - Datos limpios: {df_clean.shape[0]} filas, {df.shape[0] - df_clean.shape[0]} eliminadas")
    return df_clean


def fase4_preparar_datos(df_clean):
    y = df_clean["monto"]
    X = df_clean[["tipo_evento", "ambiente", "servicio", "capacidad", "horas"]]
    X = pd.get_dummies(X)
    print(f"FASE 4 - Listo. Columnas para predecir: {X.shape[1]}")
    return X, y


def fase5_dividir_entrenar(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    print(f"FASE 5 - Modelo entrenado con {len(X_train)} filas")
    return modelo, X_train, X_test, y_train, y_test


def fase6_evaluar(modelo, X_test, y_test):
    y_pred = modelo.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    print(f"\nFASE 6 - RMSE: {rmse:.2f} S/, R²: {r2:.4f}")

    plt.scatter(y_test, y_pred, s=4, alpha=0.2)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--", label="prediccion perfecta")
    plt.xlabel("Monto real (S/)")
    plt.ylabel("Monto predicho (S/)")
    plt.title("Real vs predicho (R² = {:.4f})".format(r2))
    plt.legend()
    plt.tight_layout()
    plt.savefig(ASSETS / "2_prediccion.png")
    plt.close()
    print("2_prediccion.png guardado")
    return y_pred


def fase7_coeficientes(modelo, X):
    print("\nFASE 7 - Coeficientes del modelo (que variables influyen mas):")
    coefs = pd.Series(modelo.coef_, index=X.columns)
    print("\nTop 5 que MAS aumentan el monto:")
    print(coefs.sort_values(ascending=False).head(5).to_string())
    print("\nTop 5 que MAS reducen el monto:")
    print(coefs.sort_values(ascending=True).head(5).to_string())
    print(f"\nIntercept (monto base): S/ {modelo.intercept_:.2f}")


def fase8_prediccion_ejemplo(modelo, X):
    print("\nFASE 8 - Prediccion de ejemplo:")
    ejemplo = pd.DataFrame([{
        "tipo_evento": "Boda", "ambiente": "Salon 12",
        "servicio": "Catering", "capacidad": 300, "horas": 6
    }])
    ejemplo = pd.get_dummies(ejemplo).reindex(columns=X.columns, fill_value=0)
    pred = modelo.predict(ejemplo)[0]
    print(f"  Boda, Salon 12, 300 personas, 6 horas, Catering -> S/ {pred:.2f}")


def ejecutar_regresion_completa():
    df = fase1_cargar_datos()
    fase2_revisar_suciedad(df)
    df_clean = fase3_limpiar_datos(df)
    X, y = fase4_preparar_datos(df_clean)
    modelo, X_train, X_test, y_train, y_test = fase5_dividir_entrenar(X, y)
    fase6_evaluar(modelo, X_test, y_test)
    fase7_coeficientes(modelo, X)
    fase8_prediccion_ejemplo(modelo, X)
    print("\n  ✔ Regresion completada. Graficos guardados en assets/")


if __name__ == "__main__":
    ejecutar_regresion_completa()
