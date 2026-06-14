#!/usr/bin/env python3
"""Carga datos de demostración para presentaciones."""
import sys

from app import create_app
from app.seed_demo import run_seed_demo

app = create_app()

if __name__ == "__main__":
    force = "--force" in sys.argv
    with app.app_context():
        result = run_seed_demo(force=force)
        if result.get("skipped"):
            print("La demo ya existe. Usa --force para recrearla.")
            print(f"\n  Portal: {result['portal_email']} / {result['portal_password']}")
        else:
            print("Demo cargada correctamente.\n")
            print("  ADMIN PANEL")
            print(f"    URL:      http://127.0.0.1:5000/admin/login")
            print(f"    Usuario:  {result['admin_user']}")
            print(f"    Password: {result['admin_password']}")
            print()
            print("  PORTAL CLIENTE")
            print(f"    URL:      http://127.0.0.1:5000/portal/login")
            print(f"    Email:    {result['portal_email']}")
            print(f"    Password: {result['portal_password']}")
            print(f"    Cliente:  {result['cliente_portal']}")
            print(f"    Embarques demo: {result['embarques']} (entregado, tránsito, puerto, prep., programado)")
