"""Asistente de análisis de devoluciones · versión 1 (semana 3, ruta A, con IA de Gemini)."""

import datetime
import logging
import time
from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types

from analisis import (CATEGORIAS, COLUMNAS, cargar, clasificar, estadisticas, incoherentes, prioridad,
                      resumir, resumir_referencia, revisar)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")  # sale en la terminal de streamlit
EJEMPLO = Path(__file__).parent / "datos" / "devoluciones_ejemplo.csv"
FORMATO_FECHA = {"fecha": st.column_config.DateColumn("fecha", format="DD/MM/YYYY")}
# Si Gemini está saturado, el SDK reintenta 5 veces sin tope (unos 200 s): mejor avisar pronto
LIMITES_IA = types.HttpOptions(timeout=30_000, retry_options=types.HttpRetryOptions(attempts=2))

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


def con_ia(tarea):
    """Ejecuta tarea(cliente) y devuelve su resultado. Si la IA falla, avisa y devuelve None: lo de arriba sigue funcionando."""
    try:
        cliente = genai.Client(api_key=st.secrets["GEMINI_API_KEY"], http_options=LIMITES_IA)
        with st.spinner("Leyendo los comentarios…"):
            inicio = time.perf_counter()
            resultado = tarea(cliente)
            logging.info("IA completa en %.1f s", time.perf_counter() - inicio)
            return resultado
    except (KeyError, FileNotFoundError):
        st.warning("Falta la clave de la IA. Añádela en los secretos de la app (GEMINI_API_KEY).")
    except Exception as error:
        logging.exception("Fallo de la IA")
        codigo = getattr(error, "code", None)
        if isinstance(error, ValueError):
            st.warning("La IA ha contestado algo que no entiendo. Inténtalo de nuevo.")
        elif "Timeout" in type(error).__name__:
            st.warning("La IA está tardando demasiado. Espera unos minutos e inténtalo de nuevo.")
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


def clasificar_y_resumir(cliente):
    df["categoria"] = clasificar(df, cliente)
    return df, resumir(df, df["categoria"], cliente)


if st.button("Clasificar comentarios con IA"):
    resultado = con_ia(clasificar_y_resumir)
    if resultado:
        st.session_state["ia"] = resultado

if "ia" in st.session_state:
    clasificado, texto = st.session_state["ia"]
    clasificado = clasificado.assign(prioridad=prioridad(clasificado, datetime.date.today(), dias))
    st.write("Puedes corregir la categoría de cualquier fila. Las abiertas hace más tiempo salen primero.")
    st.data_editor(
        clasificado[["codigo", "referencia", "comentario", "categoria", "prioridad"]]
        .sort_values("prioridad", key=lambda s: s.map({"Alta": 0, "Media": 1, "Baja": 2}), kind="stable"),
        hide_index=True, disabled=["codigo", "referencia", "comentario", "prioridad"],
        column_config={"categoria": st.column_config.SelectboxColumn(
            "categoria", options=CATEGORIAS + ["Sin comentario"])},
    )
    raros = incoherentes(clasificado, clasificado["categoria"])
    with st.expander(f"{'✅' if raros.empty else '⚠️'} Comentario y motivo que no cuadran: {len(raros)}"):
        if raros.empty:
            st.write("Nada que revisar.")
        else:
            st.write("El motivo registrado y lo que dice el comentario parecen distintos. Puede ser un error al apuntar el motivo.")
            st.dataframe(raros[["codigo", "referencia", "motivo", "comentario", "categoria"]], hide_index=True)
    st.subheader("Resumen para priorizar")
    st.write(texto)

    st.subheader("Resumen de una referencia")
    referencia = st.selectbox("Referencia", sorted(r for r in clasificado["referencia"].unique() if r))
    if st.button("Resumir esta referencia"):
        resumen = con_ia(lambda cliente: resumir_referencia(clasificado, referencia, cliente))
        if resumen:
            st.session_state["resumen_ref"] = (referencia, resumen)
    if st.session_state.get("resumen_ref", (None,))[0] == referencia:
        st.write(st.session_state["resumen_ref"][1])
    st.caption("La IA ayuda a investigar, pero no demuestra la causa.")
