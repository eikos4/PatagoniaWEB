"""Incrusta firmas digitales (imagen + metadatos) en el PDF del documento."""

import base64
import io
import os
import shutil
import tempfile

from pypdf import PdfReader, PdfWriter
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.constants import FIRMA_PARTES
from app.document_utils import document_file_path


def _is_pdf_document(doc):
    if not doc.stored_filename:
        return False
    if (doc.content_type or "").lower() == "application/pdf":
        return True
    return doc.stored_filename.lower().endswith(".pdf")


def _backup_path(pdf_path):
    return pdf_path + ".orig"


def _source_pdf_path(pdf_path):
    backup = _backup_path(pdf_path)
    if os.path.isfile(backup):
        return backup
    return pdf_path


def _decode_signature_png(signature_data):
    if not signature_data or "," not in signature_data:
        raise ValueError("Imagen de firma inválida.")
    return base64.b64decode(signature_data.split(",", 1)[1])


def _signature_slots(page_width, page_height, count):
    """Posiciones en la franja inferior de la última página."""
    margin_x = 1.5 * cm
    margin_y = 1.2 * cm
    block_w = min(8 * cm, (page_width - 3 * cm) / max(count, 1))
    block_h = 3.2 * cm
    y = margin_y
    slots = []
    if count == 1:
        x = (page_width - block_w) / 2
        slots.append((x, y, block_w, block_h))
    else:
        gap = 0.8 * cm
        total_w = block_w * 2 + gap
        start_x = (page_width - total_w) / 2
        slots.append((start_x, y, block_w, block_h))
        slots.append((start_x + block_w + gap, y, block_w, block_h))
    return slots


def _build_overlay(page_width, page_height, firmas):
    """Genera una página transparente con bloques de firma."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    ordered = sorted(firmas, key=lambda f: (0 if f.parte == "exportador" else 1, f.signed_at))
    slots = _signature_slots(page_width, page_height, len(ordered))

    for firma, (x, y, block_w, block_h) in zip(ordered, slots):
        label = FIRMA_PARTES.get(firma.parte, firma.parte)
        c.setFillColorRGB(1, 1, 1, alpha=0.92)
        c.setStrokeColorRGB(0.34, 0.45, 0.2)
        c.setLineWidth(0.5)
        c.roundRect(x, y, block_w, block_h, 6, fill=1, stroke=1)

        c.setFillColorRGB(0.34, 0.45, 0.2)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x + 0.3 * cm, y + block_h - 0.45 * cm, label[:42])

        sig_w = block_w - 0.6 * cm
        sig_h = 1.35 * cm
        sig_y = y + block_h - 0.55 * cm - sig_h
        try:
            png_bytes = _decode_signature_png(firma.signature_data)
            img = ImageReader(io.BytesIO(png_bytes))
            c.drawImage(img, x + 0.3 * cm, sig_y, width=sig_w, height=sig_h, preserveAspectRatio=True, mask="auto")
        except Exception:
            c.setFont("Helvetica-Oblique", 7)
            c.drawString(x + 0.3 * cm, sig_y + 0.4 * cm, "(firma no disponible)")

        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.setFont("Helvetica", 6)
        meta_y = y + 0.55 * cm
        c.drawString(x + 0.3 * cm, meta_y + 0.35 * cm, f"{firma.signer_name} · {firma.signer_email}")
        c.drawString(
            x + 0.3 * cm,
            meta_y,
            f"{firma.signed_at.strftime('%d/%m/%Y %H:%M:%S')} UTC · Token {firma.token}",
        )

    c.save()
    buffer.seek(0)
    return buffer


def stamp_pdf(source_path, firmas, dest_path):
    reader = PdfReader(source_path)
    if not reader.pages:
        raise ValueError("El PDF no tiene páginas.")

    last_page = reader.pages[-1]
    page_width = float(last_page.mediabox.width)
    page_height = float(last_page.mediabox.height)

    overlay_buffer = _build_overlay(page_width, page_height, firmas)
    overlay_page = PdfReader(overlay_buffer).pages[0]

    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i == len(reader.pages) - 1:
            page.merge_page(overlay_page)
        writer.add_page(page)

    with open(dest_path, "wb") as out:
        writer.write(out)


def apply_signatures_to_pdf(document):
    """
    Regenera el PDF firmado a partir del original (.orig) y todas las firmas del documento.
    Retorna mensaje de error o None si todo OK / sin PDF.
    """
    if not _is_pdf_document(document):
        return None

    firmas = list(document.firmas)
    if not firmas:
        return None

    pdf_path = document_file_path(document.stored_filename)
    if not os.path.isfile(pdf_path):
        return "No se encontró el archivo PDF en el servidor."

    backup = _backup_path(pdf_path)
    if not os.path.isfile(backup):
        shutil.copy2(pdf_path, backup)

    source = _source_pdf_path(pdf_path)
    fd, tmp_path = tempfile.mkstemp(suffix=".pdf", dir=os.path.dirname(pdf_path))
    os.close(fd)

    try:
        stamp_pdf(source, firmas, tmp_path)
        os.replace(tmp_path, pdf_path)
        document.size_bytes = os.path.getsize(pdf_path)
        document.content_type = "application/pdf"
        return None
    except Exception as exc:
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
        return f"No se pudo aplicar la firma al PDF: {exc}"


def resync_signed_documents():
    """Regenera PDFs firmados para documentos que ya tienen firmas en BD."""
    from app.models import ExportDocument

    updated = 0
    errors = []
    docs = (
        ExportDocument.query.filter(ExportDocument.stored_filename.isnot(None))
        .order_by(ExportDocument.id)
        .all()
    )
    for doc in docs:
        if not doc.firmas:
            continue
        err = apply_signatures_to_pdf(doc)
        if err:
            errors.append((doc.id, doc.titulo, err))
        else:
            updated += 1
    return updated, errors
