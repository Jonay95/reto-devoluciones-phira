# Pauta 1 · Semana 1 (notas personales, no se entrega)

## Candidatos

| Problema | ¿Me lo quedo? | Por qué |
|---|---|---|
| Analizador de devoluciones y reclamaciones de la empresa | ✅ Sí | Es un problema real de mi trabajo, con usuario claro y datos que conozco. La IA aporta algo que Excel no da: entender comentarios escritos en texto libre. |
| Clasificador de incidencias de soporte | ❌ No | Es útil, pero más genérico y no tengo un usuario concreto cerca. |
| Generador de resúmenes de actas | ❌ No | Lo resuelve casi cualquier chat de IA sin app propia; aporta poco valor diferencial. |

## Usuario

- **Quién:** el responsable de Calidad de la empresa y las personas que hacen el seguimiento de devoluciones y reclamaciones.
- **Cómo lo resuelve hoy:** consulta el gestor de devoluciones y los registros de reclamaciones de clientes y proveedores, revisa los casos y prepara sus análisis a mano.
- **Qué le molesta:** detectar patrones y asuntos pendientes obliga a revisar los registros uno a uno; el código de motivo es demasiado genérico y la causa real está en comentarios escritos de formas distintas para el mismo problema.

> En el repositorio público hablamos de "responsable de Calidad", nunca de nombres de personas.

## Preguntas guía

**¿Quién tiene exactamente el problema y cómo lo resuelve hoy?**
El responsable de Calidad. Hoy cruza a mano el gestor de devoluciones con los registros de reclamaciones y escribe sus conclusiones.

**¿Qué tendría que pasar para que la usara una segunda vez?**
Que en menos de cinco minutos, al subir el archivo del mes, le diga algo que no habría visto rápido a mano (por ejemplo, que una referencia acumula devoluciones por "montaje" aunque cada comentario esté redactado distinto) y que las cifras cuadren con el archivo original.

**¿Qué parte resuelve la IA y qué parte una hoja de cálculo?**
- Hoja de cálculo / Python: totales, rankings por referencia y motivo, evolución mensual, campos vacíos, duplicados, fechas imposibles y casos atascados en el mismo estado.
- IA: agrupar los comentarios libres en categorías ("no encajan las fijaciones" y "los soportes no coinciden" → montaje o compatibilidad) y redactar un resumen que priorice. La agrupación ayuda a investigar, pero no demuestra la causa.

## Hola mundo

- Repositorio: https://github.com/Jonay95/reto-devoluciones-phira
- URL de la app: https://devolucionesjjls.streamlit.app/
