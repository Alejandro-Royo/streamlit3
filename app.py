import streamlit as st

from src.data import load_data
from src import metrics
from src.charts import bar, line, box

st.set_page_config(page_title="Dashboard Dirección - Ventas Retail", layout="wide",)

st.title("Dashboard para Dirección")
st.caption("KPIs y visualizaciones.")

# Ruta por defecto parte_1.csv
DEFAULT_CSV_PATH = "parte_1.csv"

with st.sidebar:
    st.header("Datos")
    csv_path = st.text_input("Ruta del CSV", value=DEFAULT_CSV_PATH)
    st.divider()
    st.header("Filtros globales")
    st.write("Estos filtros afectan a todas las pestañas.")
    # Los filtros se rellenan tras cargar los datos

df = load_data(csv_path)

# Sidebar filters
with st.sidebar:
    min_date = df["date"].min()
    max_date = df["date"].max()
    date_range = st.date_input("Rango de fechas",value=(min_date.date(), max_date.date()),min_value=min_date.date(),max_value=max_date.date())
    states = sorted(df["state"].dropna().unique().tolist()) if "state" in df.columns else []
    state_filter = st.multiselect("Filtrar por estado (opcional)", options=states, default=[])

# Aplica los filtros globales
df_f = df.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    df_f = df_f[(df_f["date"] >= str(start)) & (df_f["date"] <= str(end))]

if state_filter:
    df_f = df_f[df_f["state"].isin(state_filter)]

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["1) Visión global", "2) Por tienda", "3) Por estado", "4) Insights"])


# TAB 1 - Visión global
with tab1:
    st.subheader("Conteos generales")
    counts = metrics.global_counts(df_f)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nº de tiendas", f"{counts['stores']}")
    c2.metric("Nº de productos (familias)", f"{counts['products']}")
    c3.metric("Estados donde opera", f"{counts['states']}")
    c4.metric("Meses con datos", f"{counts['months']}")

    st.divider()
    st.subheader("Análisis en términos medios")

    left, right = st.columns(2)

    with left:
        top_prod = metrics.top_products_mean_sales(df_f, top_n=10)
        st.plotly_chart(bar(top_prod, x="mean_sales", y="family", title="Top 10 familias por ventas medias"), use_container_width=True)

    with right:
        store_mean = metrics.store_sales_distribution_mean(df_f)
        # Boxplot de la distribución
        st.plotly_chart(box(store_mean.assign(_all="Tiendas"), x="_all", y="mean_sales", title="Distribución de ventas medias por tienda"), use_container_width=True)
        st.caption("Variabilidad de la venta media entre tiendas")

    st.divider()
    st.subheader("Top 10 tiendas con ventas en productos en promoción")
    top_promo = metrics.top_stores_promo_sales(df_f, top_n=10)
    st.plotly_chart(bar(top_promo, x="promo_sales", y="store_nbr", title="Top 10 tiendas por ventas en promoción"), use_container_width=True)

    st.divider()
    st.subheader("Estacionalidad")

    s1, s2 = st.columns([1, 2])

    with s1:
        dow = metrics.seasonality_day_of_week(df_f)
        if not dow.empty:
            max_row = dow.sort_values("mean_sales", ascending=False).iloc[0]
            st.metric("Día con mayor venta media", f"{max_row['day_name']}", f"{max_row['mean_sales']:.2f}")
        st.plotly_chart(bar(dow, x="day_name", y="mean_sales", title="Ventas medias por día de la semana"), use_container_width=True)

    with s2:
        week = metrics.seasonality_week(df_f)
        st.plotly_chart(line(week, x="week", y="mean_sales", title="Ventas medias por semana del año"), use_container_width=True)

    month = metrics.seasonality_month(df_f)
    st.plotly_chart(bar(month, x="month", y="mean_sales", title="Ventas medias por mes del año"), use_container_width=True)


# TAB 2 - Por tienda
with tab2:
    st.subheader("Análisis por tienda")

    stores = sorted(df_f["store_nbr"].dropna().unique().tolist())
    if not stores:
        st.warning("No hay tiendas disponibles con los filtros actuales.")
    else:
        store_sel = st.selectbox("Selecciona una tienda (store_nbr)", options=stores, index=0)
        df_store = df_f[df_f["store_nbr"] == store_sel]

        k = metrics.store_tab_metrics(df_store)
        c1, c2 = st.columns(2)
        c1.metric("Unidades totales vendidas", f"{k['total_units']:.2f}")
        c2.metric("Unidades en promoción vendidas", f"{k['promo_units']:.2f}")

        st.divider()
        by_year = metrics.store_sales_by_year(df_store)
        st.plotly_chart(line(by_year, x="year", y="total_sales", title="Ventas totales por año"), use_container_width=True)


# TAB 3 - Por estado
with tab3:
    st.subheader("Análisis por estado")

    states_all = sorted(df_f["state"].dropna().unique().tolist()) if "state" in df_f.columns else []
    if not states_all:
        st.warning("No hay estados disponibles con los filtros actuales.")
    else:
        state_sel = st.selectbox("Selecciona un estado (state)", options=states_all, index=0)
        df_state = df_f[df_f["state"] == state_sel]

        st.write(f"Estado seleccionado: **{state_sel}**")

        st.divider()
        st.subheader("Transacciones por año")
        tx = metrics.state_transactions_by_year(df_state)
        st.plotly_chart(line(tx, x="year", y="total_transactions", title="Nº total de transacciones por año"), use_container_width=True)

        st.divider()
        st.subheader("Ranking de tiendas por ventas")
        rank = metrics.state_store_sales_ranking(df_state, top_n=10)
        st.plotly_chart(bar(rank, x="total_sales", y="store_nbr", title="Top 10 tiendas por ventas"), use_container_width=True)

        st.divider()
        st.subheader("Producto más vendido en la tienda")

        stores_state = sorted(df_state["store_nbr"].dropna().unique().tolist())
        if not stores_state:
            st.info("No hay tiendas en este estado con los filtros actuales.")
        else:
            # Por defecto, sugerimos la tienda top del ranking si existe
            default_store = int(rank.iloc[0]["store_nbr"]) if not rank.empty else int(stores_state[0])
            store_in_state = st.selectbox("Selecciona una tienda dentro del estado", options=stores_state, index=stores_state.index(default_store) if default_store in stores_state else 0,)

            top_prod = metrics.top_product_in_store(df_state, store_in_state)
            if top_prod["family"] is None:
                st.info("No hay ventas para esa tienda con los filtros actuales.")
            else:
                st.metric("Familia más vendida", top_prod["family"], f"{top_prod['total_sales']:.2f}")


# TAB 4 - Insights extra
with tab4:
    st.subheader("Insights adicionales")

    st.markdown(
        """
        Esta pestaña añade análisis complementarios que suelen ser útiles:
        - Impacto de promociones (uplift) por producto.
        - Comparativa de ventas en días festivos vs no festivos.
        """)

    left, right = st.columns(2)

    with left:
        st.markdown("### Uplift de promociones por familia")
        uplift = metrics.promo_uplift_by_family(df_f)
        if uplift.empty:
            st.info("No hay suficientes observaciones para calcular uplift.")
        else:
            top_uplift = uplift.head(15)
            st.plotly_chart(bar(top_uplift, x="uplift", y="family", title="Top familias por uplift (mean promo / mean no promo)"), use_container_width=True)

    with right:
        st.markdown("### Festivos vs no festivos")
        hvn = metrics.holiday_vs_nonholiday_sales(df_f)
        if hvn.empty:
            st.info("No se puede calcular el efecto festivos con los filtros actuales.")
        else:
            st.plotly_chart(
                bar(hvn, x="is_holiday", y="mean_sales", title="Ventas medias: festivos vs no festivos"), use_container_width=True)

    st.divideradar = st.divider()
    st.subheader("Muestra rápida del dataset filtrado")
    st.dataframe(df_f.head(50), use_container_width=True)
