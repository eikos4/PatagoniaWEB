"""Utilidades PWA — manifiestos portal y admin (Patagonia Export)."""

PWA_APP_NAME = "Patagonia Export"

PWA_PROFILES = {
    "portal": {
        "id": "/portal/",
        "scope": "/portal/",
        "start_url": "/portal/login?source=pwa",
        "description": "Portal de clientes · seguimiento de embarques y exportación",
        "theme_color": "#587232",
        "background_color": "#F7F3EA",
        "icon": "pwa/ship-portal-192.png",
        "icon_512": "pwa/ship-portal-512.png",
        "sw_path": "/portal/sw.js",
        "profile": "clientes",
    },
    "admin": {
        "id": "/admin/",
        "scope": "/admin/",
        "start_url": "/admin/login?source=pwa",
        "description": "Panel administrativo · exportación Patagonia Sur",
        "theme_color": "#111111",
        "background_color": "#F7F3EA",
        "icon": "pwa/ship-admin-192.png",
        "icon_512": "pwa/ship-admin-512.png",
        "sw_path": "/admin/sw.js",
        "profile": "admin",
    },
}


def build_manifest(profile_key, static_url_fn):
    """Construye el dict del web app manifest para portal o admin."""
    cfg = PWA_PROFILES[profile_key]
    icon192 = static_url_fn(cfg["icon"])
    icon512 = static_url_fn(cfg["icon_512"])

    return {
        "id": cfg["id"],
        "name": PWA_APP_NAME,
        "short_name": PWA_APP_NAME,
        "description": cfg["description"],
        "start_url": cfg["start_url"],
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
            {
                "src": icon512,
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable",
            },
        ],
    }
