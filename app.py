import streamlit as st
import pandas as pd

# 🔗 API de Apify (REEMPLAZA con tu link)
url = "https://api.apify.com/v2/actor-tasks/ronaldoescobar.96~facebook-pages-scraper-task/runs?token=apify_api_zi0utLq19Lk36ng9rIzIejJjf0CkUQ3T6Csr"

# Cargar datos automáticamente
df = pd.read_csv(url)

# 🧹 LIMPIEZA DE DATOS (adaptar según Apify output)
# Renombrar columnas si es necesario
df = df.rename(columns={
    "pageName": "Marca",
    "likes": "Reacciones",
    "comments": "Comentarios",
    "shares": "Shares",
    "time": "Fecha",
    "text": "Texto_post"
})

# Convertir fecha
df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')

# Agregar seguidores estimados (puedes mejorarlo después)
df["Seguidores"] = 100000  # temporal

# Calcular engagement
df["Engagement"] = (
    df["Reacciones"] + df["Comentarios"] + df["Shares"]
) / df["Seguidores"]

# Clasificación automática de contenido
def clasificar(texto):
    if "oferta" in str(texto).lower() or "descuento" in str(texto).lower():
        return "Promo"
    elif "nuevo" in str(texto).lower():
        return "Producto"
    else:
        return "Branding"

df["Tipo_post"] = df["Texto_post"].apply(clasificar)

# Sidebar filtros
st.sidebar.title("Filtros")
marca = st.sidebar.multiselect(
    "Marca", df["Marca"].dropna().unique(),
    default=df["Marca"].dropna().unique()
)

df_filtrado = df[df["Marca"].isin(marca)]

# Título
st.title("📊 Dashboard Automático - Competencia Facebook")
st.subheader("Tiendas CENTRO vs Competencia")

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Posts Analizados", len(df_filtrado))
col2.metric("Engagement Promedio", f"{round(df_filtrado['Engagement'].mean()*100, 2)}%")
col3.metric("Comentarios Totales", int(df_filtrado["Comentarios"].sum()))

# Frecuencia de posts
st.subheader("📅 Frecuencia")
posts = df_filtrado.groupby("Marca").size()
st.bar_chart(posts)

# Engagement
st.subheader("💬 Engagement por Marca")
eng = df_filtrado.groupby("Marca")["Engagement"].mean()
st.bar_chart(eng)

# Top posts
st.subheader("🔥 Top Posts")
top = df_filtrado.sort_values(by="Engagement", ascending=False).head(10)
st.dataframe(top[["Marca", "Texto_post", "Reacciones", "Comentarios", "Engagement"]])

# Tipo de contenido
st.subheader("🧠 Tipo de contenido")
tipo = df_filtrado.groupby("Tipo_post")["Engagement"].mean()
st.bar_chart(tipo)

# Comentarios insights (simple)
st.subheader("🧾 Insights de comentarios")

def sentimiento(c):
    c = str(c).lower()
    if "caro" in c or "malo" in c:
        return "Negativo"
    elif "bonito" in c or "oferta" in c:
        return "Positivo"
    return "Neutral"

df["Sentimiento"] = df["Texto_post"].apply(sentimiento)

sent = df["Sentimiento"].value_counts()
st.bar_chart(sent)