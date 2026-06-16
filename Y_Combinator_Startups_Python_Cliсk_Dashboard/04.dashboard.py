import streamlit as st
import pandas as pd
import clickhouse_connect

st.set_page_config(page_title = "YC Startups", layout = "wide")
st.title("🚀 YC Startups — 6000 стартапов Y Combinator")

@st.cache_resource
def get_client():
    return clickhouse_connect.get_client(
        host = "localhost", username ="default", password = "ycpass"
    )

client = get_client()

def fetch_df(sql, columns):
    rows = client.query(sql).result_rows
    return pd.DataFrame(rows, columns = columns)


# Числа сверху
total = client.query("SELECT count() FROM yc_companies").result_rows[0][0]
top = client.query("SELECT countIf(has_badge = 1) FROM yc_companies").result_rows[0][0]

col1, col2 = st.columns(2)
col1.metric("Всего компаний", total)
col2.metric("С бейджем Top Company", top)

# Рост по годам
st.subheader("Сколько компаний по годам")
by_year = fetch_df("""
    SELECT toUInt16('20' || substring(batch, 2)) AS year, count() AS companies
    FROM yc_companies
    GROUP BY year ORDER BY year
""", columns=["year", "companies"])
st.bar_chart(by_year, x="year", y="companies")

# Топ тегов
st.subheader("Топ тегов")
top_tags = fetch_df("""
    SELECT arrayJoin(tags) AS tag, count() AS companies
    FROM yc_companies
    GROUP BY tag ORDER BY companies DESC LIMIT 15
""", columns=["tag", "companies"])
st.bar_chart(top_tags, x="tag", y="companies")