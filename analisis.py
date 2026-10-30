"""Lógica de la app, sin Streamlit, para poder probarla aparte (ver test_analisis.py)."""

import csv
import json

import pandas as pd

COLUMNAS = ["codigo", "fecha", "referencia", "motivo", "estado", "comentario"]
ESTADOS_ABIERTOS = ["Pendiente", "En proceso", "Pendiente de abono"]


def cargar(archivo):
    """Lee el CSV (ruta o archivo subido). Si no se puede usar, lanza ValueError con un mensaje para el usuario."""
    # Excel en español guarda con ";" y en latin-1: se detecta el separador y se prueba primero UTF-8
    for codificacion in ("utf-8-sig", "latin-1"):
        if hasattr(archivo, "seek"):
            archivo.seek(0)
        try:
            df = pd.read_csv(archivo, sep=None, engine="python", dtype=str,
                             keep_default_na=False, encoding=codificacion)
            break
        except UnicodeDecodeError:
            continue
        except (pd.errors.EmptyDataError, pd.errors.ParserError, csv.Error):
            raise ValueError("Está vacío o no es un CSV con columnas separadas por comas o punto y coma.")

    df.columns = df.columns.str.strip().str.lower()
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        raise ValueError("Le faltan estas columnas: " + ", ".join(faltan) + ".")

    df = df.apply(lambda columna: columna.str.strip())
    # shortcut: solo fechas AAAA-MM-DD; si el gestor exporta DD/MM/AAAA, añadir ese formato aquí
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="coerce")
    return df


def revisar(df, hoy, dias):
    """Devuelve {problema: filas afectadas}. Un caso está atascado si sigue abierto más de `dias` días."""
    hoy = pd.Timestamp(hoy)
    texto = [c for c in COLUMNAS if c != "fecha"]
    antiguedad = (hoy - df["fecha"]).dt.days

    atascados = df[df["estado"].isin(ESTADOS_ABIERTOS) & (antiguedad > dias)]
    return {
        "Campos vacíos": df[(df[texto] == "").any(axis=1)],
        "Códigos repetidos": df[(df["codigo"] != "") & df.duplicated("codigo", keep=False)],
        "Posibles duplicados (misma referencia, fecha y comentario)":
            df[df.duplicated(["referencia", "fecha", "comentario"], keep=False)],
        "Fechas vacías, mal escritas o imposibles":
            df[df["fecha"].isna() | (df["fecha"].dt.year < 2000) | (df["fecha"] > hoy)],
        f"Casos abiertos hace más de {dias} días":
            atascados.assign(dias_abierto=antiguedad).sort_values("dias_abierto", ascending=False),
    }


def estadisticas(df):
    """Cuenta devoluciones (filas, no unidades) por referencia, motivo y mes."""
    def contar(serie):
        return serie.replace("", "(vacío)").value_counts().rename("devoluciones")

    fechas_validas = df["fecha"][df["fecha"].dt.year >= 2000]
    return {
        "referencia": contar(df["referencia"]),
        "motivo": contar(df["motivo"]),
        "mes": fechas_validas.dt.strftime("%Y-%m").value_counts().sort_index().rename("devoluciones"),
    }


MODELO = "gemini-3.8-flash"
CATEGORIAS = ["Montaje o compatibilidad", "Daño en transporte", "Pieza incompleta", "Error de cliente", "Otro"]
SIN_COMENTARIO = "Sin comentario"
LOTE = 50  # comentarios por llamada, para cuidar la cuota gratuita


def parsear_categorias(texto, cuantas):
    """Convierte la respuesta JSON de la IA en una lista de `cuantas` categorías. Lo que no esté en la lista pasa a "Otro"."""
    try:
        lista = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        raise ValueError("La IA no ha devuelto una respuesta que pueda leer.")
    if not isinstance(lista, list) or len(lista) != cuantas:
        raise ValueError("La IA no ha devuelto una categoría por comentario.")
    return [c if c in CATEGORIAS else "Otro" for c in lista]


def clasificar(df, cliente):
    """Devuelve una serie con la categoría de cada devolución. Los comentarios vacíos no se envían a la IA."""
    categorias = pd.Series(SIN_COMENTARIO, index=df.index)
    con_texto = df.index[df["comentario"] != ""]
    for i in range(0, len(con_texto), LOTE):
        indices = con_texto[i:i + LOTE]
        numerados = "\n".join(f"{n}. {df.loc[ind, 'comentario']}" for n, ind in enumerate(indices, 1))
        pedido = (
            "Eres un asistente de Calidad. Clasifica cada comentario de una devolución en UNA de estas categorías: "
            + "; ".join(CATEGORIAS) + ".\n"
            f"Responde solo con una lista JSON de {len(indices)} textos, en el mismo orden, usando exactamente esos nombres.\n\n"
            + numerados
        )
        respuesta = cliente.models.generate_content(
            model=MODELO, contents=pedido, config={"response_mime_type": "application/json"})
        categorias[indices] = parsear_categorias(respuesta.text, len(indices))
    return categorias


def resumir(df, categorias, cliente):
    """Redacta un resumen corto para priorizar, a partir de las cifras (referencia x categoría) calculadas aquí."""
    tabla = pd.crosstab(df["referencia"], categorias)
    tabla = tabla.loc[tabla.sum(axis=1).sort_values(ascending=False).index[:5]]
    pedido = (
        "Eres un asistente de Calidad. Con esta tabla de devoluciones (filas, no unidades) por referencia y categoría, "
        "escribe en español, en 4 frases cortas y sin tecnicismos, qué conviene revisar primero. "
        "Usa solo las cifras de la tabla y recuerda que la agrupación ayuda a investigar pero no demuestra la causa.\n\n"
        + tabla.to_string()
    )
    return cliente.models.generate_content(model=MODELO, contents=pedido).text
