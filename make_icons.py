"""
Generate PWA and Play Store compliant app icons for KATCHO.
"""

import os
from PIL import Image, ImageDraw, ImageFont


def create_katcho_icon(size: int, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new("RGBA", (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background with vibrant gradient-like color
    corner_radius = int(size * 0.22)
    # Deep vibrant blue/dark background
    draw.rounded_rectangle(
        [(0, 0), (size, size)],
        radius=corner_radius,
        fill="#1E272E"
    )

    # Inner glowing border
    inner_pad = int(size * 0.04)
    draw.rounded_rectangle(
        [(inner_pad, inner_pad), (size - inner_pad, size - inner_pad)],
        radius=int(corner_radius * 0.85),
        outline="#3867D6",
        width=int(size * 0.03)
    )

    # Draw Mascot / Stylized letter "K" in center
    font_size = int(size * 0.48)
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    text = "K"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (size - text_w) / 2
    y = (size - text_h) / 2 - (size * 0.06)

    # Draw vibrant coral shadow and bright text
    draw.text((x + int(size * 0.02), y + int(size * 0.02)), text, fill="#FF4757", font=font)
    draw.text((x, y), text, fill="#FFEAA7", font=font)

    # Small subtitle dot or badge
    badge_pad = int(size * 0.12)
    badge_h = int(size * 0.08)
    draw.rounded_rectangle(
        [(size * 0.2, size * 0.78), (size * 0.8, size * 0.78 + badge_h)],
        radius=int(badge_h * 0.5),
        fill="#2ED573"
    )

    img.save(output_path, "PNG")
    print(f"Generated {output_path} ({size}x{size})")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(base_dir, "static", "icons")
    create_katcho_icon(192, os.path.join(icons_dir, "icon-192.png"))
    create_katcho_icon(512, os.path.join(icons_dir, "icon-512.png"))
