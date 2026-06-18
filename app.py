import streamlit as st
import pandas as pd
import requests

# ✅ URL CON TU TOKEN (CORREGIDA)
url = "https://api.apify.com/v2/datasets/6Cjc0dWdidlUZlipL/items?token=apify_api_zi0utLq19Lk36ng9rIzIejJjf0CkUQ3T6Csr&format=json&clean=true"

st.set_page_config(page_title="Dashboard Competencia", layout="wide")

st.title("📊 Dashboard Automático - Competencia Facebook")
st.subheader("Tiendas CENTRO vs Competidores")

# ✅ CARGA SEGURA DE DATOS
@st.cache_data(ttl=3600)
def cargar_datos(url):
    try:
        response = requests.get(url)

        if response.status_code != 200:
            st.error(f"Error API: {response.status_code}")
            return None

        data = response.json()

        if not isinstance(data, list):
            st.error("Formato inesperado de datos")
            return None

        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = cargar_datos(url)

# ✅ VALIDACIÓN
if df is None or df.empty:
    st.error("⚠️ No hay datos disponibles")
    st.stop()

# ✅ TRANSFORMACIÓN (SOLO CAMPOS QUE EXISTEN)
df["Marca"] = df.get("name", "")
df["Seguidores"] = pd.to_numeric(df.get("followers", 0), errors="coerce").fillna(0)
df["Categoria"] = df.get("categories", "")
df["URL"] = df.get("url", "")

# ✅ KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Total Marcas", len(df))
col2.metric("Total Seguidores", f"{int(df['Seguidores'].sum()):,}")
col3.metric("Promedio Seguidores", f"{int(df['Seguidores'].mean()):,}")

# ✅ RANKING
st.subheader("🏆 Ranking por Seguidores")

ranking = df.sort_values(by="Seguidores", ascending=False)

st.bar_chart(ranking.set_index("Marca")["Seguidores"])

# ✅ COMPARACIÓN
st.subheader("📊 Comparación de Marcas")

st.bar_chart(df.set_index("Marca")["Seguidores"])

# ✅ TOP Y BOTTOM
top = ranking.iloc[0]
bottom = ranking.iloc[-1]

st.subheader("🧠 Insights")

st.success(
    f"✅ Mayor audiencia: {top['Marca']} con {int(top['Seguidores']):,} seguidores"
)

st.warning(
    f"⚠️ Menor audiencia: {bottom['Marca']} con {int(bottom['Seguidores']):,} seguidores"
)

# ✅ TABLA COMPLETA
st.subheader("📋 Datos completos")

st.dataframe(
    df[["Marca", "Seguidores", "Categoria", "URL"]]
)
