# Asistente de análisis de devoluciones

**Enlace a la app:** https://devolucionesjjls.streamlit.app/
**Estado:** semana 4 · versión final (revisión de datos, estadísticas, clasificación de comentarios con IA, prioridad por caso, aviso de comentarios que no cuadran con el motivo y resumen por referencia).

## El problema

En la empresa hay que revisar periódicamente las devoluciones para encontrar referencias con incidencias repetidas, cambios respecto a meses anteriores y casos que llevan demasiado tiempo sin cerrarse. Hoy el responsable de Calidad lo hace a mano: consulta el gestor de devoluciones y los registros de reclamaciones y revisa los casos uno a uno.

Cada devolución tiene un código de motivo con pocas opciones y muy genéricas, así que la mayoría cae en la misma. La causa real suele estar en los comentarios de seguimiento, escritos en texto libre y de formas distintas para el mismo problema. Esta app quiere ayudarle a detectar patrones y priorizar qué revisar.

## Qué hará

1. Cargar una exportación de devoluciones (código, fecha, referencia, motivo, estado y comentario).
2. Revisar los datos: campos incompletos, duplicados, fechas imposibles y casos que llevan demasiado tiempo en el mismo estado.
3. Clasificar los comentarios de texto libre con IA en categorías más concretas que el código de motivo, con la opción de corregir la categoría.
4. Mostrar estadísticas por referencia, motivo y mes, contando devoluciones.
5. Generar un resumen que ayude a priorizar, con los datos que lo respaldan.

La primera versión se centra en devoluciones. Las reclamaciones de clientes y proveedores quedan para después.

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

## Pitch

1. El responsable de Calidad tiene miles de devoluciones al año y no puede ver la causa real, porque el código de motivo es genérico.
2. La app lee una exportación en CSV, señala datos a revisar y casos atascados, y cuenta devoluciones por referencia, motivo y mes.
3. La IA lee los comentarios de texto libre, que dicen lo mismo de formas distintas, y los agrupa en categorías y en un resumen para priorizar, algo que una hoja de cálculo no hace.
4. El profesor probó la primera versión y la valoró útil, pero señaló que faltaba la IA, así que la añadí; al probarla yo, el primer modelo tardaba unos 200 segundos, así que medí varios y cambié a uno que contesta en segundos.
5. Después aceptaría fechas DD/MM/AAAA, que hoy se marcan como mal escritas, y cruzaría las devoluciones con las reclamaciones de clientes y proveedores.

> La demostración usa solo datos ficticios.
