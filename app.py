import streamlit as st
import pandas as pd
import requests

# 🔗 ✅ CAMBIA AQUÍ TU DATASET DE APIFY (NO RUNS)
url = "https://api.apify.com/v2/datasets/6Cjc0dWdidlUZlipL/items?token=apify_api_zi0utLq19Lk36ng9rIzIejJjf0CkUQ3T6Csr&format=json&clean=true"

st.set_page_config(page_title="Dashboard Competencia", layout="wide")

st.title("📊 Dashboard Automático - Competencia Facebook")
st.subheader("Tiendas CENTRO vs Competidores")

# ✅ Cargar datos
@st.cache_data(ttl=3600)
def cargar_datos(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Convertir a DataFrame
        df = pd.DataFrame(data)

        return df

    except Exception as e:
        st.error("Error conectando con Apify")
        return None

df = cargar_datos(url)

# ✅ Validar datos
if df is None or df.empty:
    st.error("⚠️ No hay datos disponibles. Verifica tu dataset de Apify.")
    st.stop()

# ✅ DEBUG (puedes quitar después)
# st.write(df.head())
# st.write(df.columns)

# ✅ Normalizar columnas (adaptadas a Apify)
df["Marca"] = df.get("pageName", "Desconocido")
df["Texto_post"] = df.get("text", "")

df["Fecha"] = pd.to_datetime(
    df.get("time", None),
    errors="coerce"
)

df["Reacciones"] = pd.to_numeric(df.get("likes", 0), errors="coerce").fillna(0)
df["Comentarios"] = pd.to_numeric(df.get("comments", 0), errors="coerce").fillna(0)
df["Shares"] = pd.to_numeric(df.get("shares", 0), errors="coerce").fillna(0)

# ✅ Seguidores (puedes mejorar luego)
df["Seguidores"] = 100000

# ✅ Engagement
df["Engagement"] = (
    df["Reacciones"] +
    df["Comentarios"] +
    df["Shares"]
) / df["Seguidores"]

# ✅ Clasificación de contenido
def clasificar(texto):
    texto = str(texto).lower()

    if "oferta" in texto or "descuento" in texto:
        return "Promo"
    elif "nuevo" in texto or "llegó" in texto:
        return "Producto"
    else:
        return "Branding"

df["Tipo_post"] = df["Texto_post"].apply(clasificar)

# ✅ Filtros
st.sidebar.header("🔎 Filtros")

marcas = df["Marca"].dropna().unique()

marca_select = st.sidebar.multiselect(
    "Selecciona marcas",
    marcas,
    default=marcas
)

df_filtrado = df[df["Marca"].isin(marca_select)]

# ✅ KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Posts analizados", len(df_filtrado))

col2.metric(
    "Engagement promedio",
    f"{round(df_filtrado['Engagement'].mean()*100, 2)}%"
)

col3.metric(
    "Total comentarios",
    int(df_filtrado["Comentarios"].sum())
)

# ✅ Frecuencia
st.subheader("📅 Frecuencia de publicación")

frecuencia = (
    df_filtrado
    .groupby("Marca")
    .size()
    .sort_values(ascending=False)
)

st.bar_chart(frecuencia)

# ✅ Engagement por marca
st.subheader("💬 Engagement por marca")

engagement = (
    df_filtrado
    .groupby("Marca")["Engagement"]
    .mean()
    .sort_values(ascending=False)
)

st.bar_chart(engagement)

# ✅ Top posts
st.subheader("🔥 Top 10 posts")

top = df_filtrado.sort_values(
    by="Engagement",
    ascending=False
).head(10)

st.dataframe(
    top[
        [
            "Marca",
            "Texto_post",
            "Reacciones",
            "Comentarios",
            "Shares",
            "Engagement"
        ]
    ]
)

# ✅ Tipo de contenido
st.subheader("🧠 Tipo de contenido vs engagement")

tipo = (
    df_filtrado
    .groupby("Tipo_post")["Engagement"]
    .mean()
)

st.bar_chart(tipo)

# ✅ Sentimiento simple
st.subheader("🧾 Sentimiento (básico)")

def sentimiento(texto):
    texto = str(texto).lower()

    if "caro" in texto or "malo" in texto:
        return "Negativo"
    elif "bonito" in texto or "oferta" in texto:
        return "Positivo"
    else:
        return "Neutral"

df_filtrado["Sentimiento"] = df_filtrado["Texto_post"].apply(sentimiento)

sent = df_filtrado["Sentimiento"].value_counts()

st.bar_chart(sent)

# ✅ Tabla completa
st.subheader("📋 Datos completos")

st.dataframe(df_filtrado)
