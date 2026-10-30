# Asistente de análisis de devoluciones

**Enlace a la app:** https://devolucionesjjls.streamlit.app/
**Estado:** semana 3 · versión 1 (revisión de datos, estadísticas y clasificación de comentarios con IA).

## El problema

En PHIRA hay que revisar periódicamente las devoluciones para encontrar referencias con incidencias repetidas, cambios respecto a meses anteriores y casos que llevan demasiado tiempo sin cerrarse. Hoy el responsable de Calidad lo hace a mano: consulta el Gestor de Devoluciones y los registros de reclamaciones y revisa los casos uno a uno.

Cada devolución tiene un código de motivo con pocas opciones y muy genéricas, así que la mayoría cae en la misma. La causa real suele estar en los comentarios de seguimiento, escritos en texto libre y de formas distintas para el mismo problema. Esta app quiere ayudarle a detectar patrones y priorizar qué revisar.

## Qué hará

1. Cargar una exportación de devoluciones (código, fecha, referencia, motivo, estado y comentario).
2. Revisar los datos: campos incompletos, duplicados, fechas imposibles y casos que llevan demasiado tiempo en el mismo estado.
3. Clasificar los comentarios de texto libre con IA en categorías más concretas que el código de motivo, con la opción de corregir la categoría.
4. Mostrar estadísticas por referencia, motivo y mes, contando devoluciones.
5. Generar un resumen que ayude a priorizar, con los datos que lo respaldan.

La primera versión se centra en devoluciones. Las reclamaciones de clientes y proveedores (IRC e IRP) quedan para después.

## Cómo probarla

Abre la app y marca **Probar con los datos de ejemplo**, o sube tu propio CSV con las columnas `codigo, fecha, referencia, motivo, estado, comentario`. Los detalles están en [especificacion.md](especificacion.md).

En local:

```bash
pip install -r requirements.txt
python test_analisis.py
streamlit run app.py
```

## La IA

Usa la API de Gemini (modelo `gemini-3.5-flash-lite`, constante `MODELO` en `analisis.py`) para agrupar los comentarios en categorías y redactar un resumen. La clave va en `st.secrets["GEMINI_API_KEY"]` (en local, `.streamlit/secrets.toml`, que no se sube). Si la IA falla (sin clave, cuota agotada, sin conexión), la app avisa y la revisión y las estadísticas siguen funcionando.

> La demostración usa solo datos ficticios.
