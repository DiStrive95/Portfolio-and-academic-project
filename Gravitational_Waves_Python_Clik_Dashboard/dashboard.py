import streamlit as st
import pandas as pd
from clickhouse_driver import Client

st.set_page_config(page_title = "Gravitational Waves", layout = "wide")
st.title("🌌 Каталог гравитационно-волновых событий")

@st.cache_data(ttl=60)
def load_data():
    client = Client(
        host="localhost",
        port=9000,
        user="default",
        password="clickhouse",
        database="gw",
    )

    rows = client.execute(
        '''SELECT common_name, total_mass_source, luminosity_distance,
               network_snr, merger_type
        FROM gw.events
        '''
    )

    return pd.DataFrame(rows, columns = ["common_name", "total_mass", "distance", "snr", "merger_type"])

df = load_data()

if df.empty:
    st.warning("Данных пока нет. Нужно всё проверить")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Всего событий", len(df))
col2.metric("Слияний чёрных дыр (BBH)", int((df["merger_type"] == "BBH").sum()))
col3.metric("Слияний нейтронных звёзд (BNS)", int((df["merger_type"] == "BNS").sum()))

# Сколько событий каждого типа
st.subheader("Типы слияний")
st.bar_chart(df["merger_type"].value_counts())
st.caption(
    "Почти все события — слияния чёрных дыр (BBH). Их видно с большого "
    "расстояния, поэтому ловят их чаще, чем лёгкие нейтронные звёзды (BNS)."
)

# Масса против расстояния — тяжёлые видно дальше
st.subheader("Масса и расстояние событий")
st.scatter_chart(
    df,
    x="total_mass",
    y="distance",
    color="merger_type",
)
st.caption(
    "Каждая точка — реальное слияние. Чем тяжелее событие (правее), тем "
    "дальше его видно (выше). Одинокая точка слева внизу — GW170817: "
    "лёгкое слияние нейтронных звёзд, которое поймали только потому, что "
    "оно произошло совсем близко."
)

# Таблица всех событий — с понятными заголовками и единицами
st.subheader("Все события")
st.markdown(
    """
    **Что означают колонки:**
    - **Событие** — название слияния (по дате, когда его поймали)
    - **Суммарная масса (☉)** — сколько весят оба объекта вместе, в массах Солнца
    - **Расстояние (Mpc)** — как далеко произошло слияние, в мегапарсеках
      (1 Mpc ≈ 3,26 млн световых лет)
    - **Сила сигнала (SNR)** — насколько уверенно детекторы поймали событие:
      чем больше, тем чётче сигнал на фоне шума
    - **Тип слияния** — BBH (две чёрные дыры) или BNS (две нейтронные звезды)
    """
)
st.dataframe(
    df.sort_values("total_mass", ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        "common_name": st.column_config.TextColumn(
            "Событие", help="Название слияния в каталоге"
        ),
        "total_mass": st.column_config.NumberColumn(
            "Суммарная масса (☉)",
            help="Сумма масс двух объектов, в массах Солнца",
            format="%.1f",
        ),
        "distance": st.column_config.NumberColumn(
            "Расстояние (Mpc)",
            help="Расстояние до источника в мегапарсеках",
            format="%.0f",
        ),
        "snr": st.column_config.NumberColumn(
            "Сила сигнала (SNR)",
            help="Отношение сигнал/шум: насколько уверенно поймали событие",
            format="%.1f",
        ),
        "merger_type": st.column_config.TextColumn(
            "Тип слияния",
            help="BBH — две чёрные дыры, BNS — две нейтронные звезды",
        ),
    },
)