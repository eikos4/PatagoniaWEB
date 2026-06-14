"""Cálculo de ocupación de contenedores."""

from app.constants import CONTENEDOR_DIMENSIONES


def calcular_contenedor(tipo, cajas_largo, cajas_ancho, cajas_alto, peso_caja, cantidad_cajas):
    dims = CONTENEDOR_DIMENSIONES.get(tipo, CONTENEDOR_DIMENSIONES["40"])
    vol_cont = dims["largo"] * dims["ancho"] * dims["alto"]
    vol_caja = (cajas_largo / 100) * (cajas_ancho / 100) * (cajas_alto / 100)
    if vol_caja <= 0:
        vol_caja = 0.001

    cajas_por_piso_largo = int(dims["largo"] / (cajas_largo / 100)) if cajas_largo else 0
    cajas_por_piso_ancho = int(dims["ancho"] / (cajas_ancho / 100)) if cajas_ancho else 0
    cajas_por_piso = cajas_por_piso_largo * cajas_por_piso_ancho
    pisos = int(dims["alto"] / (cajas_alto / 100)) if cajas_alto else 0
    cajas_max_estimadas = cajas_por_piso * pisos if pisos else 0

    vol_carga = vol_caja * cantidad_cajas
    pct_volumen = min((vol_carga / vol_cont) * 100, 999) if vol_cont else 0
    peso_total = peso_caja * cantidad_cajas
    peso_max = dims["peso_max"]
    pct_peso = min((peso_total / peso_max) * 100, 999) if peso_max else 0
    peso_disponible = max(peso_max - peso_total, 0)

    alertas = []
    estado = "valida"
    if pct_volumen > 100:
        alertas.append("Exceso de volumen: la carga supera la capacidad del contenedor.")
        estado = "invalida"
    elif pct_volumen > 90:
        alertas.append("Volumen casi al límite (>90%).")
        estado = "advertencia"
    if pct_peso > 100:
        alertas.append("Sobrepeso: excede el peso máximo del contenedor.")
        estado = "invalida"
    elif pct_peso > 90:
        alertas.append("Peso casi al límite (>90%).")
        if estado == "valida":
            estado = "advertencia"

    return {
        "tipo": tipo,
        "volumen_contenedor_m3": round(vol_cont, 2),
        "volumen_carga_m3": round(vol_carga, 2),
        "pct_volumen": round(pct_volumen, 1),
        "cajas_estimadas_max": cajas_max_estimadas,
        "cajas_solicitadas": cantidad_cajas,
        "peso_total_kg": round(peso_total, 1),
        "peso_max_kg": peso_max,
        "peso_disponible_kg": round(peso_disponible, 1),
        "pct_peso": round(pct_peso, 1),
        "estado": estado,
        "alertas": alertas,
        "dims_contenedor": dims,
    }
