"""Comprobaciones de analisis.py. Ejecutar con: python test_analisis.py"""

import io

import pandas as pd

from analisis import CATEGORIAS, SIN_COMENTARIO, cargar, clasificar, estadisticas, incoherentes, parsear_categorias, prioridad, resumir, resumir_referencia, revisar

# Como lo guardaría Excel en español: ";" y latin-1
CSV = """codigo;fecha;referencia;motivo;estado;comentario
26/0001W;2026-09-01;REF-1001;Defecto de pieza;Abono finalizado;falta una pieza
26/0001W;2026-09-01;REF-1001;Defecto de pieza;Abono finalizado;falta una pieza
26/0002W;2026-08-01;;Pedido por error;En proceso;
26/0003O;1900-01-01;REF-1002;Error de envío;Pendiente;llega otra referencia
26/0004W;2026-10-10;REF-1001;Rotura / rayado;Pendiente;rayada
26/0005W;12/10/2026;REF-1003;Pedido por error;Rechazada;ya no lo necesita
""".encode("latin-1")

df = cargar(io.BytesIO(CSV))
assert len(df) == 6
assert df.loc[3, "motivo"] == "Error de envío"

r = revisar(df, "2026-10-19", 30)
assert list(r["Campos vacíos"]["codigo"]) == ["26/0002W"]
assert len(r["Códigos repetidos"]) == 2
assert len(r["Posibles duplicados (misma referencia, fecha y comentario)"]) == 2
assert list(r["Fechas vacías, mal escritas o imposibles"]["codigo"]) == ["26/0003O", "26/0005W"]
atascados = r["Casos abiertos hace más de 30 días"]
assert list(atascados["codigo"]) == ["26/0003O", "26/0002W"]  # el más antiguo primero
assert atascados["dias_abierto"].iloc[1] == 79

e = estadisticas(df)
assert e["referencia"]["REF-1001"] == 3
assert e["referencia"]["(vacío)"] == 1
assert e["mes"].to_dict() == {"2026-08": 1, "2026-09": 2, "2026-10": 1}

for malo in (b"", b"codigo;fecha\n26/0001W;2026-09-01\n"):
    try:
        cargar(io.BytesIO(malo))
        raise AssertionError("debería haber fallado")
    except ValueError as error:
        print("Error esperado:", error)

# IA: se simula el cliente de Gemini, sin llamar a la API
assert parsear_categorias('["Daño en transporte", "inventada"]', 2) == ["Daño en transporte", "Otro"]
for malo in ("no es json", '["Otro"]'):
    try:
        parsear_categorias(malo, 2)
        raise AssertionError("debería haber fallado")
    except ValueError as error:
        print("Error esperado:", error)


class Falso:
    def __init__(self, texto):
        self.models = self
        self.texto = texto

    def generate_content(self, **kwargs):
        self.pedido = kwargs["contents"]
        self.config = kwargs.get("config")
        return self

    @property
    def text(self):
        return self.texto


falso = Falso('["Pieza incompleta", "Otro", "Otro", "Otro", "Otro"]')
cat = clasificar(df, falso)
assert cat[0] == "Pieza incompleta" and cat[2] == SIN_COMENTARIO  # fila 2 sin comentario: no se envía
assert "falta una pieza" in falso.pedido and cat.isin(CATEGORIAS + [SIN_COMENTARIO]).all()
# La IA solo puede contestar con categorías de la lista, y el pedido explica cada una
assert falso.config["response_schema"]["items"]["enum"] == CATEGORIAS and "no encaja" in falso.pedido
falso_resumen = Falso("Revisar REF-1001.")
assert resumir(df, cat, falso_resumen) == "Revisar REF-1001."
assert "Motivo registrado" in falso_resumen.pedido and "Defecto de pieza" in falso_resumen.pedido  # el resumen ve el motivo

# Motivo y comentario que no cuadran: "Defecto de pieza" + "Pieza incompleta" sí cuadra; "Pedido por error" + "Pieza incompleta" no
motivos = pd.DataFrame({"motivo": ["Defecto de pieza", "Pedido por error", "Pedido por error", "Pedido por error", "Motivo nuevo"]})
categorias = pd.Series(["Pieza incompleta", "Pieza incompleta", "Otro", SIN_COMENTARIO, "Daño en transporte"])
assert list(incoherentes(motivos, categorias).index) == [1]

# Prioridad: abierto y viejo = Alta, abierto reciente o sin fecha = Media, cerrado = Baja
p = prioridad(df, "2026-10-19", 30)
assert list(p) == ["Baja", "Baja", "Alta", "Alta", "Media", "Baja"]

assert resumir_referencia(df, "REF-9999", falso) == "Esta referencia no tiene comentarios que resumir."
assert resumir_referencia(df, "REF-1001", Falso("Falta una pieza.")) == "Falta una pieza."

print("OK")
