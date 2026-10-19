"""Comprobaciones de analisis.py. Ejecutar con: python test_analisis.py"""

import io

from analisis import cargar, estadisticas, revisar

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

print("OK")
