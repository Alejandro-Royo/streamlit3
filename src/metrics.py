import pandas as pd

def global_counts(df: pd.DataFrame) -> dict:
    """
    Devuelve conteos solicitados: tiendas, productos, estados, meses con datos
    """
    n_stores = df["store_nbr"].nunique() if "store_nbr" in df.columns else 0
    n_products = df["family"].nunique() if "family" in df.columns else 0
    n_states = df["state"].nunique() if "state" in df.columns else 0

    # Meses con datos = combinaciones (year, month)
    if {"year", "month"}.issubset(df.columns):
        n_months = df[["year", "month"]].dropna().drop_duplicates().shape[0]
    else:
        n_months = 0

    return {"stores": int(n_stores), "products": int(n_products), "states": int(n_states), "months": int(n_months)}


def top_products_mean_sales(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Devuelve el top 10 productos más vendidos en términos medios
    """
    out = (df.groupby("family", as_index=False)["sales"].mean().rename(columns={"sales": "mean_sales"}).sort_values("mean_sales", ascending=False).head(top_n))
    return out


def store_sales_distribution_mean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve ventas medias por tienda
    """
    out = (df.groupby("store_nbr", as_index=False)["sales"].mean().rename(columns={"sales": "mean_sales"}).sort_values("mean_sales", ascending=False))
    return out


def top_stores_promo_sales(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Devuelve el top 10 tiendas con ventas en productos en promoción
    """
    promo_df = df[df["is_promo"]]
    out = (promo_df.groupby("store_nbr", as_index=False)["sales"].sum().rename(columns={"sales": "promo_sales"}).sort_values("promo_sales", ascending=False).head(top_n))
    return out


def seasonality_day_of_week(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve el día de la semana con más ventas en promedio
    """
    order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    out = (df.groupby("day_name", as_index=False)["sales"].mean().rename(columns={"sales": "mean_sales"}))
    # Ordena el df por el orden de los días de la semana
    out["day_name"] = pd.Categorical(out["day_name"], categories=order, ordered=True)
    out = out.sort_values("day_name")
    return out


def seasonality_week(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve las ventas medias por semana del año, agregando todos los años
    """
    out = (df.groupby("week", as_index=False)["sales"].mean().rename(columns={"sales": "mean_sales"}).sort_values("week"))
    return out


def seasonality_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve las ventas medias por mes, agregando todos los años
    """
    out = (df.groupby("month", as_index=False)["sales"].mean().rename(columns={"sales": "mean_sales"}).sort_values("month"))
    return out

def store_tab_metrics(df_store: pd.DataFrame) -> dict:
    """
    Por tienda hace:
      - productos vendidos
      - productos vendidos en promoción
    """
    total_units = float(df_store["sales"].sum())
    promo_units = float(df_store.loc[df_store["is_promo"], "sales"].sum())

    return {"total_units": total_units, "promo_units": promo_units}


def store_sales_by_year(df_store: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve las ventas totales por año en orden cronológico
    """
    out = (df_store.groupby("year", as_index=False)["sales"].sum().rename(columns={"sales": "total_sales"}).sort_values("year"))
    return out


def state_transactions_by_year(df_state: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve el número total de transacciones por año en orden cronológico
    """
    s = df_state.copy()
    # Rellena con 0 los que sean NaN
    if "transactions" in s.columns:
        s["transactions"] = s["transactions"].fillna(0)
    out = (s.groupby("year", as_index=False)["transactions"].sum().rename(columns={"transactions": "total_transactions"}).sort_values("year"))
    return out


def state_store_sales_ranking(df_state: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Devuelve el ranking de tiendas con más ventas en el estado seleccionado
    """
    # Devuelve el top 10 si no se especifica que top se quiere
    out = (df_state.groupby("store_nbr", as_index=False)["sales"].sum().rename(columns={"sales": "total_sales"}).sort_values("total_sales", ascending=False).head(top_n))
    return out


def top_product_in_store(df: pd.DataFrame, store_nbr: int) -> dict:
    """
    Devuelve el producto más vendido en la tienda
    """
    sub = df[df["store_nbr"] == store_nbr]
    # Si no existe esa tienda las ventas son 0
    if sub.empty:
        return {"family": None, "total_sales": 0.0}

    agg = (sub.groupby("family", as_index=False)["sales"].sum().rename(columns={"sales": "total_sales"}).sort_values("total_sales", ascending=False))
    # Se queda con el mayor
    top_row = agg.iloc[0]
    return {"family": str(top_row["family"]), "total_sales": float(top_row["total_sales"])}


def promo_uplift_by_family(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el uplift de promoción por producto: uplift = mean_sales_promo / mean_sales_no_promo
    """
    base = df[["family", "sales", "is_promo"]].dropna(subset=["family", "sales"])

    promo = base[base["is_promo"]].groupby("family")["sales"].mean().rename("mean_promo")
    nopromo = base[~base["is_promo"]].groupby("family")["sales"].mean().rename("mean_no_promo")

    # Elimina los valores nulos
    out = pd.concat([promo, nopromo], axis=1).dropna()

    # Evitar divisiones si mean_no_promo = 0
    out = out[out["mean_no_promo"] != 0]

    out["uplift"] = out["mean_promo"] / out["mean_no_promo"]
    out = out.reset_index().sort_values("uplift", ascending=False)
    return out


def holiday_vs_nonholiday_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compara las ventas medias en días festivos vs no festivos
    """
    s = df.copy()
    # df con booleanos, si holiday, True, si no False
    is_holiday = s["holiday_type"].notna() if "holiday_type" in s.columns else False
    s["is_holiday"] = is_holiday

    out = (s.groupby("is_holiday", as_index=False)["sales"].mean().rename(columns={"sales": "mean_sales"}).replace({True: "Con festivo", False: "Sin festivo"}))
    return out
