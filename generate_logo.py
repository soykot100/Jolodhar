"""
JOLODHAR Logo Generator
Creates premium logo with sky blue theme + water/drain/IoT motifs
Output: static/images/logo.png
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "images")
OUTPUT_DIR = os.path.abspath(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_logo(size=512):
    """Create JOLODHAR logo - water drop + circuit pattern"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    primary = (14, 165, 233)    # #0EA5E9 sky-500
    accent = (56, 189, 248)     # #38BDF8 sky-400
    dark = (15, 23, 42)         # #0F172A slate-900
    light = (224, 242, 254)     # #E0F2FE sky-100

    # Outer circle (dark) - background plate
    draw.ellipse([cx - size*0.45, cy - size*0.45, cx + size*0.45, cy + size*0.45],
                 fill=dark + (255,))

    # Inner ring (sky blue)
    draw.ellipse([cx - size*0.42, cy - size*0.42, cx + size*0.42, cy + size*0.42],
                 outline=primary + (255,), width=int(size*0.025))

    # Water drop (teardrop) shape - centered
    drop_w = size * 0.22
    drop_top = cy - size * 0.21
    drop_bottom = cy + size * 0.18
    drop_radius = drop_w / 2
    drop_cx, drop_cy = cx, drop_bottom - drop_radius * 0.3

    # Build drop polygon
    drop_shape = []
    drop_shape.append((cx, drop_top))
    # Left side curve from top to circle
    for i in range(0, 25):
        t = i / 24
        # bezier-like curve: start at top, end at left edge of circle
        x = cx - drop_radius * (1 - (1-t)**2.5)
        y = drop_top + (drop_cy - drop_top) * t
        drop_shape.append((x, y))
    # Bottom half circle (left to right)
    for i in range(0, 31):
        angle = math.pi - (i / 30) * math.pi  # pi to 0
        x = drop_cx + drop_radius * math.cos(angle)
        y = drop_cy + drop_radius * math.sin(angle) * 0.95
        drop_shape.append((x, y))
    # Right side curve up
    for i in range(0, 25):
        t = i / 24
        x = cx + drop_radius * (1 - (1-t)**2.5)
        y = drop_cy + (drop_top - drop_cy) * t
        drop_shape.append((x, y))

    # Draw filled drop with gradient (simulate by drawing 3 layers)
    for layer, color, scale in [(0, accent + (255,), 1.0), (1, primary + (255,), 0.85), (2, light + (200,), 0.4)]:
        scaled_pts = []
        for px, py in drop_shape:
            sx = cx + (px - cx) * scale
            sy = drop_cy + (py - drop_cy) * scale
            scaled_pts.append((sx, sy))
        draw.polygon(scaled_pts, fill=color)

    # Highlight on drop
    hl_x = cx - drop_w * 0.18
    hl_y = drop_cy - drop_w * 0.15
    draw.ellipse([hl_x - drop_w*0.06, hl_y - drop_w*0.10,
                  hl_x + drop_w*0.06, hl_y + drop_w*0.10],
                 fill=(255, 255, 255, 100))

    # Circuit pattern around drop (IoT motif)
    circuit_color = accent + (220,)
    for i in range(6):
        angle = (i / 6) * 2 * math.pi - math.pi / 2
        r1 = size * 0.30
        r2 = size * 0.38
        x1 = cx + r1 * math.cos(angle)
        y1 = cy + r1 * math.sin(angle)
        x2 = cx + r2 * math.cos(angle)
        y2 = cy + r2 * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=circuit_color, width=max(2, int(size*0.012)))
        # Node dot
        node_r = max(3, int(size*0.02))
        draw.ellipse([x2 - node_r, y2 - node_r, x2 + node_r, y2 + node_r],
                     fill=accent + (255,))

    # Apply slight blur for premium feel
    img = img.filter(ImageFilter.SMOOTH)

    return img


def create_logo_with_text(size=512):
    """Create logo with JOLODHAR text below"""
    logo = create_logo(size)
    canvas = Image.new("RGBA", (size, int(size * 1.35)), (0, 0, 0, 0))
    canvas.paste(logo, (0, 0), logo)

    draw = ImageDraw.Draw(canvas)
    font_path = None
    for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(fp):
            font_path = fp
            break

    font_size = int(size * 0.11)
    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    text = "JOLODHAR"
    color = (14, 165, 233, 255)
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
    except Exception:
        text_w = font_size * len(text) * 0.6
    text_x = (size - text_w) // 2
    text_y = size + 12
    draw.text((text_x, text_y), text, fill=color, font=font)

    # Subtitle
    sub_size = int(size * 0.04)
    try:
        sub_font = ImageFont.truetype(font_path, sub_size) if font_path else ImageFont.load_default()
    except Exception:
        sub_font = ImageFont.load_default()
    sub = "Smart IoT-ML Drain Monitoring"
    try:
        bbox = draw.textbbox((0, 0), sub, font=sub_font)
        sub_w = bbox[2] - bbox[0]
    except Exception:
        sub_w = sub_size * len(sub) * 0.55
    sub_x = (size - sub_w) // 2
    sub_y = text_y + font_size + 4
    draw.text((sub_x, sub_y), sub, fill=(148, 163, 184, 255), font=sub_font)

    return canvas


def create_favicon(size=64):
    return create_logo(size)


if __name__ == "__main__":
    logo = create_logo(512)
    logo_path = os.path.join(OUTPUT_DIR, "logo.png")
    logo.save(logo_path, "PNG")
    print(f"Logo saved: {logo_path}")

    logo_text = create_logo_with_text(512)
    logo_text_path = os.path.join(OUTPUT_DIR, "logo_text.png")
    logo_text.save(logo_text_path, "PNG")
    print(f"Logo with text: {logo_text_path}")

    favicon = create_favicon(64)
    favicon_path = os.path.join(OUTPUT_DIR, "favicon.png")
    favicon.save(favicon_path, "PNG")
    print(f"Favicon: {favicon_path}")

    login_logo = create_logo(256)
    login_logo_path = os.path.join(OUTPUT_DIR, "logo_small.png")
    login_logo.save(login_logo_path, "PNG")
    print(f"Login logo: {login_logo_path}")
