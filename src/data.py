import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def load_data(csv_path: str) -> pd.DataFrame:
    """
    - Lee el CSV
    - Convierte tipos (fechas, numéricos)
    - Garantiza columnas temporales (year, month, week, quarter, day_of_week)
    - Devuelve un DataFrame listo para agregaciones y gráficos
    """
    df = pd.read_csv(csv_path)

    # Elimina la primera columna vacía
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Conversión de datos
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["sales", "onpromotion", "transactions", "dcoilwtico", "store_nbr", "cluster"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Asegurar columnas temporales (por si faltan o vienen corruptas) ----------------------------------------------------------------------
    if "date" in df.columns:
        if "year" not in df.columns or df["year"].isna().all():
            df["year"] = df["date"].dt.year
        if "month" not in df.columns or df["month"].isna().all():
            df["month"] = df["date"].dt.month
        if "week" not in df.columns or df["week"].isna().all():
            # ISO week (1-53)
            df["week"] = df["date"].dt.isocalendar().week.astype("int64")
        if "quarter" not in df.columns or df["quarter"].isna().all():
            df["quarter"] = df["date"].dt.quarter
        if "day_of_week" not in df.columns or df["day_of_week"].isna().all():
            # 0=Lunes ... 6=Domingo
            df["day_of_week"] = df["date"].dt.dayofweek

    # Etiquetas para día de la semana
    df["day_name"] = df["day_of_week"].map({0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"})

    # Columna booleana "en promoción"
    if "onpromotion" in df.columns:
        df["is_promo"] = df["onpromotion"].fillna(0) > 0
    # Si no viene dada lo asumimos falso
    else:
        df["is_promo"] = False 

    return df
