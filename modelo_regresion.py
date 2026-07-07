from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score

AQUI = Path(__file__).resolve().parent
RUTA_DATASET = AQUI / "reservas.csv"
ASSETS = AQUI / "assets"
ASSETS.mkdir(exist_ok=True)
MODELO_PATH = ASSETS / "modelo_monto.pkl"


def fase1_cargar_datos():
    if not RUTA_DATASET.exists():
        raise FileNotFoundError(
            f"No se encontro '{RUTA_DATASET.name}' en {AQUI}. "
            "Coloca el dataset de reservas junto a este script antes de ejecutar."
        )
    df = pd.read_csv(RUTA_DATASET)
    print(f"FASE 1 - Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
    return df


def cargar_modelo_guardado():
    """
    Utilidad para TB4: carga el modelo ya entrenado (evita reentrenar
    en cada peticion del backend web / asistente de IA generativa).
    Devuelve None si aun no se ha ejecutado ejecutar_regresion_completa().
    """
    if not MODELO_PATH.exists():
        return None
    return joblib.load(MODELO_PATH)


def predecir_monto(datos_evento: dict) -> float:
    """
    Funcion lista para ser llamada desde un endpoint del backend web
    o desde el asistente de IA generativa en TB4.
    datos_evento: {"tipo_evento":..., "ambiente":..., "servicio":...,
                    "capacidad":..., "horas":...}
    """
    paquete = cargar_modelo_guardado()
    if paquete is None:
        raise RuntimeError(
            "El modelo aun no ha sido entrenado. Ejecuta "
            "ejecutar_regresion_completa() al menos una vez."
        )
    modelo, columnas = paquete["modelo"], paquete["columnas"]
    ejemplo = pd.DataFrame([datos_evento])
    ejemplo = pd.get_dummies(ejemplo).reindex(columns=columnas, fill_value=0)
    return float(modelo.predict(ejemplo)[0])


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


def fase9_validacion_cruzada(modelo, X, y, k=5):
    """
    Aplica K-Fold Cross-Validation al modelo de regresion lineal.
    Responde a la recomendacion propia registrada en el informe TB3
    ("aplicar K-Fold para garantizar que la precision no dependa
    de una sola division 80/20") y sirve como evidencia de mejora
    continua para TB4.
    """
    print(f"\nFASE 9 - Validacion cruzada K-Fold (k={k}):")
    kf = KFold(n_splits=k, shuffle=True, random_state=42)
    scores_r2 = cross_val_score(modelo, X, y, cv=kf, scoring="r2")
    scores_rmse = -cross_val_score(
        modelo, X, y, cv=kf, scoring="neg_root_mean_squared_error"
    )
    print(f"  R² por fold:   {np.round(scores_r2, 4)}")
    print(f"  RMSE por fold: {np.round(scores_rmse, 2)}")
    print(f"  R² promedio:   {scores_r2.mean():.4f}  (+/- {scores_r2.std():.4f})")
    print(f"  RMSE promedio: {scores_rmse.mean():.2f} S/  (+/- {scores_rmse.std():.2f})")
    print("  -> Si el R² promedio es cercano al obtenido en Fase 6, el modelo")
    print("     es estable y no depende de una particion afortunada de los datos.")
    return scores_r2, scores_rmse


def fase10_comparar_modelos(X_train, X_test, y_train, y_test):
    """
    Investigacion de modelos de Machine Learning (criterio 1 - TB4):
    compara Regresion Lineal, Ridge (regularizada) y Random Forest
    para justificar por que se eligio Regresion Lineal en el proyecto.
    """
    print("\nFASE 10 - Comparacion de modelos de ML:")
    candidatos = {
        "Regresion Lineal":   LinearRegression(),
        "Ridge (alpha=1.0)":  Ridge(alpha=1.0, random_state=42),
        "Random Forest (100 arboles)": RandomForestRegressor(
            n_estimators=100, random_state=42, n_jobs=-1
        ),
    }

    resultados = []
    for nombre, mdl in candidatos.items():
        mdl.fit(X_train, y_train)
        y_pred = mdl.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        resultados.append({"modelo": nombre, "rmse": rmse, "r2": r2})
        print(f"  {nombre:<30} RMSE: {rmse:8.2f} S/   R²: {r2:.4f}")

    tabla = pd.DataFrame(resultados).sort_values("r2", ascending=False)
    mejor = tabla.iloc[0]
    print(f"\n  -> Mejor modelo por R²: {mejor['modelo']} (R²={mejor['r2']:.4f})")
    print("  -> Se mantiene Regresion Lineal en produccion por su interpretabilidad")
    print("     (coeficientes claros para decisiones de negocio), salvo que Random")
    print("     Forest ofrezca una mejora sustancial que justifique perder esa lectura directa.")

    tabla.plot(x="modelo", y="r2", kind="bar", legend=False, color="seagreen")
    plt.title("Comparacion de modelos - R² en datos de prueba")
    plt.ylabel("R²")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(ASSETS / "3_comparacion_modelos.png")
    plt.close()
    print("  3_comparacion_modelos.png guardado")
    return tabla


def fase11_guardar_modelo(modelo, X):
    """
    Persiste el modelo entrenado y el listado de columnas esperadas
    (necesario para reconstruir el one-hot encoding al predecir).
    Este artefacto es el que se reutilizara en TB4 desde el backend
    web y/o el asistente de IA generativa, evitando reentrenar en
    cada peticion.
    """
    joblib.dump({"modelo": modelo, "columnas": list(X.columns)}, MODELO_PATH)
    print(f"\nFASE 11 - Modelo guardado en {MODELO_PATH.name} "
          f"(listo para reutilizar en el backend de TB4)")


def ejecutar_regresion_completa():
    df = fase1_cargar_datos()
    fase2_revisar_suciedad(df)
    df_clean = fase3_limpiar_datos(df)
    X, y = fase4_preparar_datos(df_clean)
    modelo, X_train, X_test, y_train, y_test = fase5_dividir_entrenar(X, y)
    fase6_evaluar(modelo, X_test, y_test)
    fase7_coeficientes(modelo, X)
    fase8_prediccion_ejemplo(modelo, X)
    fase9_validacion_cruzada(modelo, X, y, k=5)
    fase10_comparar_modelos(X_train, X_test, y_train, y_test)
    fase11_guardar_modelo(modelo, X)
    print("\n  ✔ Regresion completada. Graficos guardados en assets/")


if __name__ == "__main__":
    ejecutar_regresion_completa()