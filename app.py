"""Asistente de análisis de devoluciones · versión 1 (semana 3, ruta A, con IA de Gemini)."""

import datetime
import logging
import time
from pathlib import Path

import streamlit as st
from google import genai

from analisis import CATEGORIAS, COLUMNAS, cargar, clasificar, estadisticas, resumir, revisar

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")  # sale en la terminal de streamlit
EJEMPLO = Path(__file__).parent / "datos" / "devoluciones_ejemplo.csv"
FORMATO_FECHA = {"fecha": st.column_config.DateColumn("fecha", format="DD/MM/YYYY")}

st.set_page_config(page_title="Análisis de devoluciones", page_icon="📦")
st.title("📦 Análisis de devoluciones")
st.write(
    "Sube una exportación de devoluciones y la app te dice qué datos revisar, "
    "qué casos llevan demasiado tiempo abiertos y dónde se concentran las devoluciones."
)
st.caption(f"El CSV necesita estas columnas: {', '.join(COLUMNAS)}. Fechas como 2026-10-19.")

archivo = st.file_uploader("Archivo de devoluciones (CSV)", type="csv")
if archivo is None and st.checkbox("Probar con los datos de ejemplo (inventados)"):
    archivo = EJEMPLO
if archivo is None:
    st.info("Sube un archivo o marca la casilla para probar con el ejemplo.")
    st.stop()

try:
    df = cargar(archivo)
except ValueError as error:
    st.error(f"No he podido usar el archivo. {error}")
    st.stop()

st.success(f"{len(df)} devoluciones cargadas.")
dias = st.slider("Días abierto a partir de los que un caso se considera atascado", 7, 180, 30)

pestana_revision, pestana_estadisticas = st.tabs(["🔍 Revisión de datos", "📊 Estadísticas"])

with pestana_revision:
    for problema, filas in revisar(df, datetime.date.today(), dias).items():
        icono = "✅" if filas.empty else "⚠️"
        with st.expander(f"{icono} {problema}: {len(filas)}"):
            if filas.empty:
                st.write("Nada que revisar.")
            else:
                st.dataframe(filas, hide_index=True, column_config=FORMATO_FECHA)

with pestana_estadisticas:
    conteos = estadisticas(df)
    st.subheader("Referencias con más devoluciones")
    st.dataframe(conteos["referencia"].head(10))
    st.subheader("Devoluciones por motivo")
    st.bar_chart(conteos["motivo"], horizontal=True)
    st.subheader("Devoluciones por mes")
    st.bar_chart(conteos["mes"])


st.divider()
st.subheader("🤖 Comentarios agrupados con IA")
if st.button("Clasificar comentarios con IA"):
    # Si la IA falla, la revisión y las estadísticas de arriba siguen funcionando
    try:
        cliente = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        with st.spinner("Leyendo los comentarios…"):
            inicio = time.perf_counter()
            df["categoria"] = clasificar(df, cliente)
            st.session_state["ia"] = (df, resumir(df, df["categoria"], cliente))
            logging.info("IA completa en %.1f s", time.perf_counter() - inicio)
    except (KeyError, FileNotFoundError):
        st.warning("Falta la clave de la IA. Añádela en los secretos de la app (GEMINI_API_KEY).")
    except Exception as error:
        logging.exception("Fallo de la IA")
        codigo = getattr(error, "code", None)
        if isinstance(error, ValueError):
            st.warning("La IA ha contestado algo que no entiendo. Inténtalo de nuevo.")
        elif codigo == 429:
            st.warning("Se ha agotado la cuota gratuita de la IA. Inténtalo más tarde.")
        elif codigo == 503:
            st.warning("La IA está saturada ahora mismo. Espera unos minutos e inténtalo de nuevo.")
        elif codigo in (400, 403):
            st.warning("La IA no acepta la clave. Revisa GEMINI_API_KEY en los secretos de la app.")
        elif codigo == 404:
            st.warning("El modelo de IA ya no está disponible. Avisa a quien mantiene la app.")
        elif codigo:
            st.warning("La IA ha tenido un fallo por su parte. Inténtalo de nuevo en un rato.")
        else:
            st.warning("No he podido conectar con la IA. Comprueba tu conexión e inténtalo de nuevo.")


if "ia" in st.session_state:
    clasificado, texto = st.session_state["ia"]
    st.write("Puedes corregir la categoría de cualquier fila.")
    st.data_editor(
        clasificado[["codigo", "referencia", "comentario", "categoria"]], hide_index=True,
        disabled=["codigo", "referencia", "comentario"],
        column_config={"categoria": st.column_config.SelectboxColumn(
            "categoria", options=CATEGORIAS + ["Sin comentario"])},
    )
    st.subheader("Resumen para priorizar")
    st.write(texto)
    st.caption("La IA ayuda a investigar, pero no demuestra la causa.")
