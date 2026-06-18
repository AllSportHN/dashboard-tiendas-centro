import streamlit as st
import pandas as pd
import requests

# 🔗 🔁 CAMBIA AQUÍ TU LINK DE APIFY
url = "https://api.apify.com/v2/actor-tasks/ronaldoescobar.96~facebook-pages-scraper-task/runs?token=apify_api_zi0utLq19Lk36ng9rIzIejJjf0CkUQ3T6Csr"

st.set_page_config(page_title="Dashboard Competencia", layout="wide")

st.title("📊 Dashboard Automático - Competencia Facebook")
st.subheader("Tiendas CENTRO vs Competencia")

# ✅ Cargar datos de forma segura
@st.cache_data(ttl=3600)
def cargar_datos(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        return None

df = cargar_datos(url)

# ✅ Validación
if df is None or df.empty:
    st.error("⚠️ No se pudieron cargar los datos. Verifica el link de Apify.")
    st.stop()

# ✅ Ver columnas disponibles (solo para debug inicial)
# st.write(df.columns)

# ✅ Normalizar columnas (adaptado a Apify)
df["Marca"] = df.get("pageName", "Desconocido")
df["Texto_post"] = df.get("text", "")
df["Fecha"] = pd.to_datetime(df.get("time", None), errors="coerce")

df["Reacciones"] = df.get("likes", 0)
df["Comentarios"] = df.get("comments", 0)
df["Shares"] = df.get("shares", 0)

# ✅ Limpiar datos
df["Reacciones"] = pd.to_numeric(df["Reacciones"], errors="coerce").fillna(0)
df["Comentarios"] = pd.to_numeric(df["Comentarios"], errors="coerce").fillna(0)
df["Shares"] = pd.to_numeric(df["Shares"], errors="coerce").fillna(0)

# ✅ Seguidores (temporal — luego lo puedes mejorar)
df["Seguidores"] = 100000

# ✅ Calcular engagement
df["Engagement"] = (
    df["Reacciones"] + df["Comentarios"] + df["Shares"]
) / df["Seguidores"]

# ✅ Clasificar tipo de contenido automáticamente
def clasificar(texto):
    texto = str(texto).lower()
    if "oferta" in texto or "descuento" in texto:
        return "Promo"
    elif "nuevo" in texto:
        return "Producto"
    else:
        return "Branding"

df["Tipo_post"] = df["Texto_post"].apply(clasificar)

# ✅ Filtros
st.sidebar.header("🔎 Filtros")

marcas = df["Marca"].dropna().unique()
marca_select = st.sidebar.multiselect("Marca", marcas, default=marcas)

df_filtrado = df[df["Marca"].isin(marca_select)]

# ✅ KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Posts Analizados", len(df_filtrado))
col2.metric(
    "Engagement Promedio",
    f"{round(df_filtrado['Engagement'].mean()*100, 2)}%"
)
col3.metric("Comentarios", int(df_filtrado["Comentarios"].sum()))

# ✅ Frecuencia de posts
st.subheader("📅 Frecuencia de Publicación")
posts = df_filtrado.groupby("Marca").size().sort_values(ascending=False)
st.bar_chart(posts)

# ✅ Engagement por marca
st.subheader("💬 Engagement por Marca")
eng = df_filtrado.groupby("Marca")["Engagement"].mean().sort_values(ascending=False)
st.bar_chart(eng)

# ✅ Top posts
st.subheader("🔥 Top Posts")
top = df_filtrado.sort_values(by="Engagement", ascending=False).head(10)

st.dataframe(
    top[[
