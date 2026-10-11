# Asistente de análisis de devoluciones

**Enlace a la app:** https://devolucionesjjls.streamlit.app/
**Estado:** semana 1 · hola mundo desplegado, todavía sin IA.

## El problema

En PHIRA hay que revisar periódicamente las devoluciones para encontrar referencias con incidencias repetidas, cambios respecto a meses anteriores y casos pendientes de seguimiento. Hoy el responsable de Calidad lo hace a mano: consulta el Gestor de Devoluciones y los registros de reclamaciones y revisa los casos uno a uno. Esta app quiere ayudarle a detectar patrones y priorizar qué revisar.

## Qué hará

1. Cargar un archivo de devoluciones (fecha, referencia, cantidad, motivo).
2. Revisar los datos: campos incompletos y posibles duplicados.
3. Clasificar los motivos con IA, con la opción de corregir la categoría.
4. Mostrar estadísticas por referencia y por mes.
5. Generar un resumen que ayude a priorizar, con los datos que lo respaldan.

La primera versión se centra en devoluciones. Las reclamaciones de clientes y proveedores (IRC e IRP) quedan para después.

> La demostración usa solo datos ficticios.
