"""Utilidades PWA — manifiestos portal y admin (Patagonia Export)."""

from flask import url_for

PWA_APP_NAME = "Patagonia Export"

PWA_PROFILES = {
    "portal": {
        "id": "/portal/",
        "scope": "/portal/",
        "description": "Portal de clientes · seguimiento de embarques y exportación",
        "theme_color": "#587232",
        "background_color": "#F7F3EA",
        "icon_192": "img/pwa/ship-portal-192.png",
        "icon_512": "img/pwa/ship-portal-512.png",
        "login_endpoint": "portal.login",
    },
    "admin": {
        "id": "/admin/",
        "scope": "/admin/",
        "description": "Panel administrativo · exportación Patagonia Sur",
        "theme_color": "#111111",
        "background_color": "#F7F3EA",
        "icon_192": "img/pwa/ship-admin-192.png",
        "icon_512": "img/pwa/ship-admin-512.png",
        "login_endpoint": "admin.login",
    },
}


def build_manifest(profile_key):
    """Construye el dict del web app manifest para portal o admin."""
    cfg = PWA_PROFILES[profile_key]
    icon192 = url_for("static", filename=cfg["icon_192"], _external=True)
    icon512 = url_for("static", filename=cfg["icon_512"], _external=True)
    start_url = url_for(cfg["login_endpoint"], source="pwa", _external=True)

    return {
        "id": cfg["id"],
        "name": PWA_APP_NAME,
        "short_name": PWA_APP_NAME,
        "description": cfg["description"],
        "start_url": start_url,
        "scope": cfg["scope"],
        "display": "standalone",
        "orientation": "portrait-primary",
        "theme_color": cfg["theme_color"],
        "background_color": cfg["background_color"],
        "lang": "es",
        "categories": ["business", "productivity"],
        "icons": [
            {
                "src": icon192,
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": icon512,
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any",
            },
        ],
    }
