"""Genera iconos PNG de barco para las PWAs portal y admin."""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "static" / "img" / "pwa"
OUT.mkdir(parents=True, exist_ok=True)


def _draw_ship(draw, size, hull, sail, accent):
    s = size
    cx = s // 2
    # casco
    draw.polygon(
        [
            (cx - s * 0.34, s * 0.58),
            (cx + s * 0.34, s * 0.58),
            (cx + s * 0.22, s * 0.74),
            (cx - s * 0.22, s * 0.74),
        ],
        fill=hull,
    )
    # mástil
    draw.rectangle(
        (cx - s * 0.02, s * 0.18, cx + s * 0.02, s * 0.6),
        fill=accent,
    )
    # vela principal
    draw.polygon(
        [
            (cx + s * 0.02, s * 0.2),
            (cx + s * 0.28, s * 0.52),
            (cx + s * 0.02, s * 0.52),
        ],
        fill=sail,
    )
    # vela proa
    draw.polygon(
        [
            (cx - s * 0.02, s * 0.28),
            (cx - s * 0.22, s * 0.5),
            (cx - s * 0.02, s * 0.5),
        ],
        fill=sail,
    )
    # olas
    for i, xoff in enumerate((-0.18, 0.02, 0.22)):
        y = s * (0.8 + (i % 2) * 0.02)
        draw.arc(
            (
                cx + s * xoff - s * 0.12,
                y - s * 0.04,
                cx + s * xoff + s * 0.12,
                y + s * 0.08,
            ),
            start=0,
            end=180,
            fill=accent,
            width=max(2, s // 64),
        )


def make_icon(size, bg, hull, sail, accent, outfile):
    img = Image.new("RGBA", (size, size), bg)
    draw = ImageDraw.Draw(img)
    radius = size // 5
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
    rounded = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rounded.paste(img, mask=mask)
    draw = ImageDraw.Draw(rounded)
    _draw_ship(draw, size, hull, sail, accent)
    rounded.save(outfile, "PNG")
    print(f"  {outfile.name}")


def main():
    print("Generando iconos PWA…")
    make_icon(
        192,
        (88, 114, 50, 255),
        (247, 243, 234, 255),
        (234, 148, 42, 255),
        (70, 92, 40, 255),
        OUT / "ship-portal-192.png",
    )
    make_icon(
        512,
        (88, 114, 50, 255),
        (247, 243, 234, 255),
        (234, 148, 42, 255),
        (70, 92, 40, 255),
        OUT / "ship-portal-512.png",
    )
    make_icon(
        192,
        (17, 17, 17, 255),
        (234, 148, 42, 255),
        (247, 243, 234, 255),
        (88, 114, 50, 255),
        OUT / "ship-admin-192.png",
    )
    make_icon(
        512,
        (17, 17, 17, 255),
        (234, 148, 42, 255),
        (247, 243, 234, 255),
        (88, 114, 50, 255),
        OUT / "ship-admin-512.png",
    )
    print("Listo.")


if __name__ == "__main__":
    main()
