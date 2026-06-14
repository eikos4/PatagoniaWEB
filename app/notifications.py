import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import current_app

from app import db
from app.models import NotificationLog


def _smtp_configured():
    return bool(current_app.config.get("SMTP_HOST") and current_app.config.get("SMTP_FROM"))


def send_email(destinatario, titulo, mensaje, tipo="alerta", folder_id=None):
    """Envía email y registra en NotificationLog. Retorna (ok, log)."""
    log = NotificationLog(
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        destinatario=destinatario,
        canal="email",
        folder_id=folder_id,
    )
    db.session.add(log)

    if not _smtp_configured():
        log.estado = "error"
        log.error_detalle = "SMTP no configurado (SMTP_HOST / SMTP_FROM en variables de entorno)."
        return False, log

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = titulo
        msg["From"] = current_app.config["SMTP_FROM"]
        msg["To"] = destinatario
        html = f"""<html><body style="font-family:Inter,sans-serif;color:#111;">
        <div style="max-width:560px;margin:0 auto;padding:24px;">
        <h2 style="color:#587232;">Patagonia Sur SpA</h2>
        <p style="white-space:pre-wrap;">{mensaje}</p>
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
        <p style="font-size:12px;color:#6b7280;">Notificación automática del panel de exportación.</p>
        </div></body></html>"""
        msg.attach(MIMEText(mensaje, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        host = current_app.config["SMTP_HOST"]
        port = current_app.config.get("SMTP_PORT", 587)
        user = current_app.config.get("SMTP_USER")
        password = current_app.config.get("SMTP_PASSWORD")

        with smtplib.SMTP(host, port, timeout=15) as server:
            server.ehlo()
            if port == 587:
                server.starttls()
            if user and password:
                server.login(user, password)
            server.sendmail(current_app.config["SMTP_FROM"], [destinatario], msg.as_string())

        log.estado = "enviado"
        return True, log
    except Exception as e:
        log.estado = "error"
        log.error_detalle = str(e)[:500]
        return False, log


def enviar_resumen_alertas(alertas, destinatario=None):
    """Envía resumen de alertas críticas/advertencia por email."""
    dest = destinatario or current_app.config.get("NOTIFY_EMAIL")
    if not dest:
        return False, None
    criticas = [a for a in alertas if a["nivel"] == "critica"]
    advertencias = [a for a in alertas if a["nivel"] == "advertencia"]
    if not criticas and not advertencias:
        return False, None

    lineas = []
    if criticas:
        lineas.append(f"CRÍTICAS ({len(criticas)}):")
        for a in criticas[:10]:
            lineas.append(f"• {a['titulo']}: {a['mensaje']}")
    if advertencias:
        lineas.append(f"\nADVERTENCIAS ({len(advertencias)}):")
        for a in advertencias[:10]:
            lineas.append(f"• {a['titulo']}: {a['mensaje']}")

    cuerpo = "\n".join(lineas)
    titulo = f"Patagonia Sur — {len(criticas)} crítica(s), {len(advertencias)} advertencia(s)"
    return send_email(dest, titulo, cuerpo, tipo="resumen_alertas")
