"""Asistente de análisis de devoluciones · versión 0 (semana 2, ruta A, todavía sin IA)."""

import datetime
from pathlib import Path

import streamlit as st

from analisis import COLUMNAS, cargar, estadisticas, revisar

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

st.info(
    "🤖 Próximamente (semana 3): la IA agrupará los comentarios en categorías más concretas "
    "que el motivo y redactará un resumen para priorizar qué revisar."
)
