"""Lógica de la app, sin Streamlit, para poder probarla aparte (ver test_analisis.py)."""

import csv

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
