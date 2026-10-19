# Especificación · Asistente de análisis de devoluciones

## 1. Problema y usuario

**Usuario:** el responsable de Calidad de PHIRA, que revisa periódicamente las devoluciones de clientes.

**Cómo lo resuelve hoy:** consulta el Gestor de Devoluciones y los registros de reclamaciones en Excel y revisa los casos uno a uno para encontrar referencias con problemas repetidos y casos que no se cierran.

**Qué le molesta:**
- Son miles de devoluciones al año.
- El código de motivo tiene muy pocas opciones y casi todo cae en "Pedido por error", así que no sirve para encontrar la causa.
- La causa real está en los comentarios de seguimiento, en texto libre: el mismo problema aparece escrito de formas distintas ("no encaja con el soporte", "los taladros no cuadran").

**Qué parte resuelve la IA:** agrupar esos comentarios en categorías concretas y redactar un resumen que priorice. El resto (totales, duplicados, casos atascados) lo resuelve pandas.

## 2. Qué hace el producto

1. **Revisión de datos:** carga una exportación de devoluciones y señala:
   - campos vacíos,
   - códigos repetidos,
   - posibles duplicados,
   - fechas imposibles,
   - casos que llevan más de N días abiertos.
2. **Clasificación de comentarios con IA (semana 3):** asigna a cada comentario una categoría más concreta que el motivo (montaje o compatibilidad, daño en transporte, pieza incompleta, error de cliente…). El usuario puede corregirla.
3. **Estadísticas y resumen:** devoluciones por referencia, motivo y mes, y un resumen de qué revisar primero con las cifras que lo respaldan (el resumen, en la semana 3).

## 3. Entradas y salidas

**El usuario da:** un CSV separado por `;` o `,`, en UTF-8 o latin-1, con una fila por devolución y estas columnas:

| Columna | Contenido | Ejemplo |
|---|---|---|
| `codigo` | Código de la devolución | `26/0045W` |
| `fecha` | Fecha de alta, AAAA-MM-DD | `2026-07-12` |
| `referencia` | Referencia del artículo | `REF-1045` |
| `motivo` | Motivo del gestor (Pedido por error, Rotura / rayado, Error de envío, Defecto de pieza, Facturado pero no enviado) | `Pedido por error` |
| `estado` | Pendiente, En proceso, Pendiente de abono, Abono finalizado o Rechazada | `Pendiente` |
| `comentario` | Texto libre del seguimiento; puede ir vacío | `no encaja con el soporte que tiene` |

**La app devuelve:**
- una lista de problemas de datos con las filas afectadas,
- los casos abiertos más antiguos primero,
- tablas y gráficos de devoluciones (filas, no unidades) por referencia, motivo y mes,
- en la semana 3, la categoría de cada comentario y un resumen.

**Ejemplo:** con `datos/devoluciones_ejemplo.csv` (61 filas inventadas), la app señala 4 filas con campos vacíos, 2 con el mismo código, 1 fecha de 1900 y 7 casos abiertos más de 30 días. Muestra también que REF-1045 es la referencia con más devoluciones. Con IA, debería decir que la mayoría de sus "Pedido por error" son en realidad problemas de montaje.

## 4. La pieza de IA

API de Gemini con el SDK `google-genai`, porque los comentarios dicen lo mismo con palabras distintas y un LLM puede agruparlos sin entrenar un modelo propio. Se llama una vez por lote de comentarios con una lista cerrada de categorías y respuesta en JSON. El system prompt y el modelo se cierran en la sesión 3.

## 5. Flujo del usuario

1. Entra en la app y sube el CSV, o marca la casilla del ejemplo.
2. Ajusta los días a partir de los que un caso cuenta como atascado (30 por defecto).
3. En **Revisión de datos** abre cada aviso y ve las filas afectadas.
4. En **Estadísticas** ve qué referencias, motivos y meses concentran devoluciones.
5. (Semana 3) Revisa y corrige las categorías propuestas por la IA y lee el resumen.

## 6. Restricciones

- Coste cero: Streamlit Community Cloud y la capa gratuita de Gemini.
- La clave de la API va en `st.secrets["GEMINI_API_KEY"]`, nunca en el código ni en el README.
- Solo datos inventados. El repositorio es público: ni datos reales ni nombres de clientes, proveedores, personas, servidores o rutas internas.
- Interfaz en español, con frases cortas y sin tecnicismos.

## 7. Criterios de aceptación

| Caso | Entrada | Resultado esperado |
|---|---|---|
| Normal | `datos/devoluciones_ejemplo.csv` | 61 devoluciones; los avisos de arriba; REF-1045 encabeza la tabla de referencias |
| Límite | CSV de Excel con `;` y tildes en latin-1 | Se lee igual y las tildes se ven bien |
| Límite | Fecha `1900-01-01` o `12/10/2026` | Aparece en "Fechas vacías, mal escritas o imposibles" y no cuenta en el gráfico por mes |
| Error | CSV sin la columna `comentario` | Mensaje "No he podido usar el archivo. Le faltan estas columnas: comentario." y nada más |
| Error | Archivo vacío | Mensaje claro, sin traza de Python |
| Error (semana 3) | Se acaba la cuota de Gemini | Aviso claro; la revisión y las estadísticas siguen funcionando |

## 8. Fuera de alcance

- Reclamaciones de clientes y proveedores (IRC e IRP) y su cruce con las devoluciones.
- Conexión directa al ERP o a la base de datos: solo se sube un archivo.
- Fotos de las devoluciones.
- Fechas en formato DD/MM/AAAA (se marcan como mal escritas).
- Usuarios, permisos o guardar históricos.

## 9. Despliegue

Ruta A: Streamlit Community Cloud, que se actualiza con cada push a `main`. Trabajo individual.
