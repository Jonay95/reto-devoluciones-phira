# AGENTS.md · Asistente de análisis de devoluciones

## Qué es este proyecto

App para el responsable de Calidad: sube una exportación de devoluciones de clientes y la app señala datos que revisar, casos que llevan demasiado tiempo abiertos y dónde se concentran las devoluciones. En la semana 3, la IA agrupará los comentarios de texto libre en categorías y redactará un resumen.

## Cómo está hecho

- Python 3.12.
- Interfaz: Streamlit (ruta A, Streamlit Community Cloud).
- `app.py`: solo la interfaz.
- `analisis.py`: la lógica en pandas, sin Streamlit (`cargar`, `revisar`, `estadisticas`).
- `test_analisis.py`: comprobaciones con `assert`.
- `datos/devoluciones_ejemplo.csv`: datos inventados.
- IA (semana 3): API de Gemini con el SDK `google-genai`; el modelo irá en una constante `MODELO`.
- La especificación completa está en `especificacion.md`. Léela antes de proponer cambios.

## Reglas

- El repositorio es público. Solo datos inventados. Nunca nombres reales de clientes, proveedores o personas, ni servidores, rutas internas, nombres de tablas o cifras reales de la empresa.
- La clave de la API va SIEMPRE en `st.secrets["GEMINI_API_KEY"]`. Nunca en el código, en el README ni en el chat.
- Cada llamada a la API va dentro de `try/except` y muestra un mensaje claro para el usuario. Si falla la IA, la revisión y las estadísticas siguen funcionando.
- La lógica nueva va en `analisis.py`, con su comprobación en `test_analisis.py`. `app.py` solo pinta.
- Las estadísticas cuentan devoluciones (filas), no unidades.
- Textos de la interfaz en español, con frases cortas y sin tecnicismos.
- Cambios pequeños: uno por petición. Al terminar, explica qué has cambiado y por qué.

## Cómo comprobar que funciona

- `python test_analisis.py` termina con `OK`.
- `streamlit run app.py` y marcar "Probar con los datos de ejemplo" (con `.streamlit/secrets.toml` en local, que está en `.gitignore`).
- Casos de prueba (entrada → lo que esperamos):
  1. El CSV de ejemplo → 61 devoluciones, 7 casos abiertos más de 30 días, REF-1045 la primera en la tabla de referencias.
  2. Un CSV sin la columna `comentario` → mensaje que dice qué columna falta, sin traza de Python.
  3. Un CSV de Excel con `;` y tildes → se lee bien.

## Qué no hacer

- No cambies el modelo, las columnas del CSV ni la arquitectura sin preguntar.
- No añadas librerías sin añadirlas a `requirements.txt` y avisar.
- No subas al repositorio documentos internos ni exportaciones reales.
- No hagas push ni despliegues sin que yo lo haya revisado.
