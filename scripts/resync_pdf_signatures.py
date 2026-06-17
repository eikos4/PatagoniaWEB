"""Regenera PDFs con firmas incrustadas para documentos ya firmados en BD."""
from app import create_app, db
from app.pdf_signature import resync_signed_documents

app = create_app()

with app.app_context():
    updated, errors = resync_signed_documents()
    if updated:
        db.session.commit()
        print(f"PDFs actualizados: {updated}")
    if errors:
        print("Errores:")
        for doc_id, titulo, err in errors:
            print(f"  #{doc_id} {titulo}: {err}")
    if not updated and not errors:
        print("No hay documentos firmados con PDF para actualizar.")
