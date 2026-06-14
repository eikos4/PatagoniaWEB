import os
from io import BytesIO

from flask import current_app
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

VERDE = colors.HexColor("#587232")
VERDE_OSC = colors.HexColor("#3d5023")
VERDE_LIGHT = colors.HexColor("#eef3e8")
CREMA = colors.HexColor("#F7F3EA")
NEGRO = colors.HexColor("#111111")
GRIS = colors.HexColor("#6b7280")
GRIS_LIGHT = colors.HexColor("#f4f5f7")
GRIS_LINE = colors.HexColor("#e5e7eb")
NARANJA = colors.HexColor("#EA942A")
BLANCO = colors.white

PAGE_W, PAGE_H = A4
MARGIN_L = 1.5 * cm
MARGIN_R = 1.5 * cm
MARGIN_T = 1.2 * cm
MARGIN_B = 1.6 * cm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R
FOOTER_H = 1.0 * cm


def _logo_path():
    static = current_app.static_folder
    logo_rel = current_app.config.get("LOGO_FILENAME", "img/1.png")
    path = os.path.normpath(os.path.join(static, logo_rel.replace("/", os.sep)))
    if not os.path.isfile(path):
        path = os.path.normpath(os.path.join(static, "img", "1.png"))
    return path if os.path.isfile(path) else None


def _logo_image(max_w_cm=3.0, max_h_cm=2.6):
    """Carga el logo redimensionado. Usa BytesIO (compatible con ReportLab)."""
    path = _logo_path()
    if not path:
        return None
    try:
        from PIL import Image as PILImage

        with PILImage.open(path) as pil:
            pil = pil.convert("RGBA") if pil.mode in ("RGBA", "LA", "P") else pil.convert("RGB")
            pil.thumbnail((int(max_w_cm * 120), int(max_h_cm * 120)), PILImage.Resampling.LANCZOS)
            buf = BytesIO()
            if pil.mode == "RGBA":
                pil.save(buf, format="PNG", optimize=True)
            else:
                pil.save(buf, format="JPEG", quality=90, optimize=True)
            buf.seek(0)
            w, h = pil.size
            scale = min((max_w_cm * cm) / w, (max_h_cm * cm) / h)
            rw, rh = w * scale, h * scale
            return Image(buf, width=rw, height=rh)
    except Exception:
        try:
            from PIL import Image as PILImage
            with PILImage.open(path) as pil:
                w, h = pil.size
                scale = min((max_w_cm * cm) / w, (max_h_cm * cm) / h)
                return Image(path, width=w * scale, height=h * scale)
        except Exception:
            return None


def _fmt_money(amount, moneda="USD"):
    if moneda == "CLP":
        return f"${amount:,.0f}"
    return f"{amount:,.2f}"


def _p(text, style):
    return Paragraph(text, style)


def _styles():
    base = dict(fontName="Helvetica", wordWrap="CJK")
    return {
        "hero_title": ParagraphStyle("hero_title", fontName="Helvetica-Bold", fontSize=22, textColor=BLANCO, leading=26, alignment=TA_RIGHT),
        "hero_num": ParagraphStyle("hero_num", fontName="Helvetica-Bold", fontSize=12, textColor=NARANJA, alignment=TA_RIGHT, spaceAfter=4),
        "hero_estado": ParagraphStyle("hero_estado", fontSize=8, textColor=BLANCO, alignment=TA_RIGHT),
        "store": ParagraphStyle("store", fontName="Helvetica-Bold", fontSize=11, textColor=BLANCO, leading=14),
        "store_sub": ParagraphStyle("store_sub", fontSize=8.5, textColor=colors.HexColor("#c8d4b8"), leading=12),
        "label": ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=7, textColor=GRIS, letterSpacing=1, spaceAfter=5),
        "card_title": ParagraphStyle("card_title", fontName="Helvetica-Bold", fontSize=10, textColor=NEGRO, leading=13),
        "card_body": ParagraphStyle("card_body", fontSize=8.5, textColor=GRIS, leading=12, **base),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=9, textColor=VERDE_OSC, letterSpacing=0.6, spaceBefore=2, spaceAfter=6),
        "th": ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=7, textColor=GRIS, letterSpacing=0.4),
        "td": ParagraphStyle("td", fontSize=8, textColor=NEGRO, leading=11, **base),
        "td_num": ParagraphStyle("td_num", fontSize=8, textColor=NEGRO, alignment=TA_RIGHT),
        "td_bold": ParagraphStyle("td_bold", fontSize=8, textColor=NEGRO, fontName="Helvetica-Bold", alignment=TA_RIGHT),
        "total_lbl": ParagraphStyle("total_lbl", fontSize=8.5, textColor=GRIS, alignment=TA_RIGHT),
        "total_val": ParagraphStyle("total_val", fontName="Helvetica-Bold", fontSize=16, textColor=VERDE, alignment=TA_RIGHT, leading=20),
        "cond": ParagraphStyle("cond", fontSize=8, textColor=GRIS, leading=12, **base),
        "contact": ParagraphStyle("contact", fontSize=7.5, textColor=GRIS, alignment=TA_CENTER),
    }


def _draw_page_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(VERDE)
    canvas.rect(0, 0, 3 * mm, PAGE_H, fill=1, stroke=0)

    canvas.setFillColor(NEGRO)
    canvas.rect(0, 0, PAGE_W, FOOTER_H, fill=1, stroke=0)
    canvas.setFillColor(VERDE)
    canvas.rect(0, FOOTER_H, PAGE_W, 2, fill=1, stroke=0)

    store = current_app.config.get("STORE_NAME", "Patagonia Sur SpA")
    email = current_app.config.get("CONTACT_EMAIL", "")
    y_footer = 0.32 * cm
    canvas.setFillColor(colors.HexColor("#9ca3af"))
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(PAGE_W / 2, y_footer, f"{store}  ·  Exportación Chile → México  ·  {email}")
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawRightString(PAGE_W - MARGIN_R, y_footer, f"Pág. {canvas.getPageNumber()}")
    canvas.restoreState()


def _card_table(lines, width):
    t = Table(lines, colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRIS_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, GRIS_LINE),
        ("LINEBEFORE", (0, 0), (0, -1), 3, VERDE),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def _build_header(cotizacion, S, store, address):
    estado_labels = {
        "borrador": "BORRADOR", "enviada": "ENVIADA", "aceptada": "ACEPTADA",
        "rechazada": "RECHAZADA", "vencida": "VENCIDA",
    }
    estado_txt = estado_labels.get(cotizacion.estado, cotizacion.estado.upper())

    logo = _logo_image()
    left_parts = []
    if logo:
        logo_box = Table([[logo]], colWidths=[logo.drawWidth + 8])
        logo_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BLANCO),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        left_parts.append(logo_box)

    company_block = [
        _p(store, S["store"]),
        Spacer(1, 2),
        _p(address.replace("·", "·<br/>"), S["store_sub"]),
    ]
    if logo:
        brand_row = Table([[logo_box, company_block]], colWidths=[logo.drawWidth + 20, CONTENT_W * 0.55 - logo.drawWidth - 20])
        brand_row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        left_cell = brand_row
    else:
        left_cell = company_block

    right_cell = [
        _p("COTIZACIÓN", S["hero_title"]),
        _p(cotizacion.numero, S["hero_num"]),
        _p(f'<font color="#9ca3af">Estado:</font> <font color="#EA942A"><b>{estado_txt}</b></font>', S["hero_estado"]),
    ]

    header_inner = Table([[left_cell, right_cell]], colWidths=[CONTENT_W * 0.58, CONTENT_W * 0.42])
    header_inner.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))

    header = Table([[header_inner]], colWidths=[CONTENT_W])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NEGRO),
        ("LINEBELOW", (0, 0), (-1, -1), 3, VERDE),
    ]))
    return header


def _col_widths():
    """Anchos proporcionales que siempre suman CONTENT_W."""
    ratios = [0.05, 0.38, 0.09, 0.10, 0.19, 0.19]
    return [CONTENT_W * r for r in ratios]


def generar_pdf_cotizacion(cotizacion):
    buffer = BytesIO()
    doc = BaseDocTemplate(
        buffer, pagesize=A4,
        leftMargin=MARGIN_L, rightMargin=MARGIN_R,
        topMargin=MARGIN_T, bottomMargin=MARGIN_B + FOOTER_H,
    )
    frame_h = PAGE_H - MARGIN_T - MARGIN_B - FOOTER_H
    frame = Frame(MARGIN_L, MARGIN_B + FOOTER_H, CONTENT_W, frame_h, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_draw_page_bg)])

    S = _styles()
    store = current_app.config.get("STORE_NAME", "Patagonia Sur SpA")
    email = current_app.config.get("CONTACT_EMAIL", "")
    phone = current_app.config.get("WHATSAPP_PHONE", "")
    address = current_app.config.get("COMPANY_ADDRESS", "Sur de Chile · Exportación a México")
    moneda = cotizacion.moneda or "USD"
    elements = []

    elements.append(_build_header(cotizacion, S, store, address))
    elements.append(Spacer(1, 0.45 * cm))

    card_w = (CONTENT_W - 0.35 * cm) / 2
    cliente_lines = [
        [_p("CLIENTE", S["label"])],
        [_p(f"<b>{cotizacion.cliente_nombre}</b>", S["card_title"])],
    ]
    if cotizacion.cliente_empresa:
        cliente_lines.append([_p(cotizacion.cliente_empresa, S["card_body"])])
    contact = [x for x in [cotizacion.cliente_email, cotizacion.cliente_telefono] if x]
    if contact:
        cliente_lines.append([_p("<br/>".join(contact), S["card_body"])])
    if cotizacion.cliente_pais:
        cliente_lines.append([_p(cotizacion.cliente_pais, S["card_body"])])

    detalle_lines = [
        [_p("DETALLES", S["label"])],
        [_p(f"<b>Emisión:</b> {cotizacion.fecha_emision.strftime('%d/%m/%Y')}", S["card_body"])],
    ]
    if cotizacion.fecha_vencimiento:
        detalle_lines.append([_p(
            f"<b>Válida hasta:</b> {cotizacion.fecha_vencimiento.strftime('%d/%m/%Y')}", S["card_body"],
        )])
    detalle_lines += [
        [_p(f"<b>Incoterm:</b> {cotizacion.incoterm or 'FOB'}", S["card_body"])],
        [_p(f"<b>Moneda:</b> {moneda}", S["card_body"])],
        [_p(f"<b>Validez:</b> {cotizacion.validez_dias or 15} días", S["card_body"])],
    ]

    meta = Table(
        [[_card_table(cliente_lines, card_w), "", _card_table(detalle_lines, card_w)]],
        colWidths=[card_w, 0.35 * cm, card_w],
    )
    meta.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements += [meta, Spacer(1, 0.5 * cm)]

    elements.append(_p("DETALLE DE PRODUCTOS", S["section"]))
    col_w = _col_widths()
    th_r = ParagraphStyle("thr", parent=S["th"], alignment=TA_RIGHT)

    rows = [[
        _p("#", S["th"]), _p("DESCRIPCIÓN", S["th"]),
        _p("CANT.", S["th"]), _p("UNID.", S["th"]),
        _p("P. UNIT.", th_r), _p("SUBTOTAL", th_r),
    ]]
    for i, ln in enumerate(cotizacion.lineas, 1):
        desc = ln.descripcion.replace("&", "&amp;").replace("<", "&lt;")
        rows.append([
            _p(f'{i:02d}', S["td"]),
            _p(desc, S["td"]),
            _p(f"{ln.cantidad:g}", S["td_num"]),
            _p(ln.unidad, S["td"]),
            _p(_fmt_money(ln.precio_unitario), S["td_num"]),
            _p(f"<b>{_fmt_money(ln.subtotal)}</b>", S["td_bold"]),
        ])

    line_table = Table(rows, colWidths=col_w, repeatRows=1)
    line_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CREMA),
        ("LINEBELOW", (0, 0), (-1, 0), 1, VERDE),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, GRIS_LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("ALIGN", (4, 0), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, colors.HexColor("#fafbfc")]),
    ]))
    elements += [line_table, Spacer(1, 0.3 * cm)]

    total_rows = [
        ["", _p("Subtotal", S["total_lbl"]), _p(f"{_fmt_money(cotizacion.subtotal)} {moneda}", S["total_lbl"])],
    ]
    if cotizacion.descuento_pct and cotizacion.descuento_pct > 0:
        desc = cotizacion.subtotal * cotizacion.descuento_pct / 100
        total_rows.append([
            "", _p(f"Descuento ({cotizacion.descuento_pct:g}%)", S["total_lbl"]),
            _p(f"- {_fmt_money(desc)} {moneda}", S["total_lbl"]),
        ])

    totals_table = Table(total_rows, colWidths=[CONTENT_W * 0.42, CONTENT_W * 0.28, CONTENT_W * 0.30])
    totals_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 0.12 * cm))

    total_hero = Table([[
        _p("TOTAL COTIZADO", ParagraphStyle("tl", fontName="Helvetica-Bold", fontSize=8, textColor=GRIS, letterSpacing=0.8)),
        _p(f'{_fmt_money(cotizacion.total)} <font size="10" color="#587232">{moneda}</font>', S["total_val"]),
    ]], colWidths=[CONTENT_W * 0.38, CONTENT_W * 0.62])
    total_hero.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), VERDE_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c5d4b0")),
        ("LINEBEFORE", (0, 0), (0, -1), 4, VERDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    elements.append(Table([[total_hero]], colWidths=[CONTENT_W], style=TableStyle([("ALIGN", (0, 0), (-1, -1), "RIGHT")])))
    elements.append(Spacer(1, 0.5 * cm))

    cond_parts = []
    if cotizacion.condiciones:
        cond_parts.append(cotizacion.condiciones.replace("&", "&amp;").replace("<", "&lt;"))
    cond_parts.append(
        f"Precios en {moneda}. Validez {cotizacion.validez_dias or 15} días. "
        "Sujeto a disponibilidad y calendario de embarque. Origen: Chile."
    )
    if cotizacion.notas:
        cond_parts.append(f"Notas: {cotizacion.notas}")

    cond_box = Table([
        [_p("<b>CONDICIONES COMERCIALES</b>", ParagraphStyle("cl", fontName="Helvetica-Bold", fontSize=8, textColor=VERDE_OSC))],
        [_p("<br/>".join(cond_parts).replace("\n", "<br/>"), S["cond"])],
    ], colWidths=[CONTENT_W])
    cond_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafafa")),
        ("BOX", (0, 0), (-1, -1), 0.5, GRIS_LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(cond_box)

    contact_bits = []
    if email:
        contact_bits.append(email)
    if phone:
        contact_bits.append(f"WhatsApp +{phone}")
    if contact_bits:
        elements.append(Spacer(1, 0.35 * cm))
        elements.append(_p(" · ".join(contact_bits), S["contact"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer
