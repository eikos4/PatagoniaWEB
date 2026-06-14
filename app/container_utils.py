"""Cálculo de ocupación de contenedores."""

from app.constants import CONTENEDOR_DIMENSIONES, MERCADOS_PESO


def _fmt_num(value, decimals=0, thousands_sep=".", decimal_sep=","):
    if value is None:
        return "0"
    rounded = round(float(value), decimals)
    sign = "-" if rounded < 0 else ""
    rounded = abs(rounded)
    if decimals == 0:
        int_part = int(round(rounded))
        frac_part = ""
    else:
        int_part = int(rounded)
        frac_val = round(rounded - int_part, decimals)
        frac_part = decimal_sep + f"{frac_val:.{decimals}f}".split(".")[1]
    s = str(int_part)
    if thousands_sep:
        parts = []
        while len(s) > 3:
            parts.insert(0, s[-3:])
            s = s[:-3]
        parts.insert(0, s)
        s = thousands_sep.join(parts)
    return sign + s + frac_part


def formatear_peso_mercado(kg, mercado_key):
    """Formatea un peso en kg según convención del mercado destino."""
    cfg = MERCADOS_PESO.get(mercado_key, MERCADOS_PESO["CL"])
    kg_val = float(kg or 0)
    ton = kg_val / 1000

    partes = {
        "kg": f"{_fmt_num(kg_val, cfg['kg_decimals'], cfg['thousands_sep'], cfg['decimal_sep'])} {cfg['label_kg']}",
        "toneladas": f"{_fmt_num(ton, cfg['t_decimals'], cfg['thousands_sep'], cfg['decimal_sep'])} {cfg['label_t']}",
    }
    if cfg.get("label_extra") == "qq":
        qq = kg_val / 100
        partes["extra"] = f"{_fmt_num(qq, 1, cfg['thousands_sep'], cfg['decimal_sep'])} qq"
    elif cfg.get("label_extra") == "lb":
        lb = kg_val * 2.20462
        partes["extra"] = f"{_fmt_num(lb, 0, cfg['thousands_sep'], cfg['decimal_sep'])} lb"
    else:
        partes["extra"] = None
    return partes


def peso_max_efectivo(tipo_contenedor, mercado_key):
    """Menor entre capacidad del contenedor y límite vial del mercado."""
    dims = CONTENEDOR_DIMENSIONES.get(tipo_contenedor, CONTENEDOR_DIMENSIONES["40"])
    mercado = MERCADOS_PESO.get(mercado_key, MERCADOS_PESO["CL"])
    limite_carretera = mercado.get("peso_max_carretera", {}).get(tipo_contenedor, dims["peso_max"])
    return min(dims["peso_max"], limite_carretera)


def calcular_contenedor(tipo, cajas_largo, cajas_ancho, cajas_alto, peso_caja, cantidad_cajas, mercado="CL"):
    dims = CONTENEDOR_DIMENSIONES.get(tipo, CONTENEDOR_DIMENSIONES["40"])
    mercado = mercado if mercado in MERCADOS_PESO else "CL"
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
    peso_max_contenedor = dims["peso_max"]
    peso_max = peso_max_efectivo(tipo, mercado)
    pct_peso = min((peso_total / peso_max) * 100, 999) if peso_max else 0
    peso_disponible = max(peso_max - peso_total, 0)
    limite_carretera = peso_max < peso_max_contenedor

    alertas = []
    estado = "valida"
    if pct_volumen > 100:
        alertas.append("Exceso de volumen: la carga supera la capacidad del contenedor.")
        estado = "invalida"
    elif pct_volumen > 90:
        alertas.append("Volumen casi al límite (>90%).")
        estado = "advertencia"
    if pct_peso > 100:
        if limite_carretera:
            alertas.append(
                f"Sobrepeso para {MERCADOS_PESO[mercado]['nombre']}: excede el límite vial/carretera del destino."
            )
        else:
            alertas.append("Sobrepeso: excede el peso máximo del contenedor.")
        estado = "invalida"
    elif pct_peso > 90:
        alertas.append("Peso casi al límite (>90%).")
        if estado == "valida":
            estado = "advertencia"

    peso_mercado = formatear_peso_mercado(peso_total, mercado)
    peso_max_fmt = formatear_peso_mercado(peso_max, mercado)
    peso_disp_fmt = formatear_peso_mercado(peso_disponible, mercado)
    peso_caja_fmt = formatear_peso_mercado(peso_caja, mercado)

    comparativa = {}
    for key in ("CL", "MX", "PE", "CO", "US", "BR", "AR"):
        if key in MERCADOS_PESO:
            comparativa[key] = {
                "nombre": MERCADOS_PESO[key]["nombre"],
                "codigo": MERCADOS_PESO[key]["codigo"],
                "carga": formatear_peso_mercado(peso_total, key),
                "maximo": formatear_peso_mercado(peso_max_efectivo(tipo, key), key),
                "disponible": formatear_peso_mercado(max(peso_max_efectivo(tipo, key) - peso_total, 0), key),
            }

    return {
        "tipo": tipo,
        "mercado": mercado,
        "mercado_nombre": MERCADOS_PESO[mercado]["nombre"],
        "mercado_codigo": MERCADOS_PESO[mercado]["codigo"],
        "mercado_nota": MERCADOS_PESO[mercado]["nota"],
        "volumen_contenedor_m3": round(vol_cont, 2),
        "volumen_carga_m3": round(vol_carga, 2),
        "pct_volumen": round(pct_volumen, 1),
        "cajas_estimadas_max": cajas_max_estimadas,
        "cajas_solicitadas": cantidad_cajas,
        "peso_total_kg": round(peso_total, 1),
        "peso_max_kg": peso_max,
        "peso_max_contenedor_kg": peso_max_contenedor,
        "peso_disponible_kg": round(peso_disponible, 1),
        "pct_peso": round(pct_peso, 1),
        "limite_carretera": limite_carretera,
        "peso_mercado": peso_mercado,
        "peso_max_fmt": peso_max_fmt,
        "peso_disp_fmt": peso_disp_fmt,
        "peso_caja_fmt": peso_caja_fmt,
        "comparativa": comparativa,
        "estado": estado,
        "alertas": alertas,
        "dims_contenedor": dims,
    }
