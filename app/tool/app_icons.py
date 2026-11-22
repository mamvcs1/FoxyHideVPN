"""Generate Foxy Hide VPN artwork for every supported platform.

The single source of truth is docs/images/logo.png. Run from app/:
    python tool/app_icons.py
Requires Pillow. The script updates Android, Windows, Linux/core, tray,
dashboard and Flutter app assets so every release carries the same Foxy mark.
"""
import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(APP, '..'))
CORE = os.path.join(ROOT, 'core')
SOURCE = os.path.join(ROOT, 'docs', 'images', 'logo.png')
RES = os.path.join(APP, 'android', 'app', 'src', 'main', 'res')
DENSITY = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
WINDOWS_SIZES = [16, 20, 24, 32, 40, 48, 64, 128, 256]
TRAY_SIZES = [16, 20, 24, 32, 48, 64]
BLUE = (27, 91, 145, 255)
DOT_GOOD, DOT_BAD, DOT_SET = (63, 225, 176), (226, 40, 80), (96, 165, 250)

ADAPTIVE = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@mipmap/ic_launcher_background" />
    <foreground android:drawable="@mipmap/ic_launcher_foreground" />
</adaptive-icon>
'''


def fit_art(art, size, share=0.82):
    """Place the full transparent artwork, preserving aspect ratio."""
    art = art.crop(art.getchannel('A').getbbox())
    scale = size * share / max(art.size)
    w = max(1, round(art.width * scale))
    h = max(1, round(art.height * scale))
    layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    layer.alpha_composite(art.resize((w, h), Image.Resampling.LANCZOS),
                          ((size - w) // 2, (size - h) // 2))
    return layer


def tile(art, size):
    canvas = Image.new('RGBA', (size, size), (7, 12, 24, 255))
    canvas.alpha_composite(fit_art(art, size, 0.88))
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=size // 5, fill=255)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask)
    return out


def android(art):
    for dpi, factor in DENSITY.items():
        folder = os.path.join(RES, 'mipmap-' + dpi)
        os.makedirs(folder, exist_ok=True)
        px = round(108 * factor)
        fit_art(art, px, 0.78).save(
            os.path.join(folder, 'ic_launcher_foreground.png'), optimize=True)
        Image.new('RGBA', (px, px), (7, 12, 24, 255)).save(
            os.path.join(folder, 'ic_launcher_background.png'), optimize=True)
        tile(art, round(48 * factor)).save(
            os.path.join(folder, 'ic_launcher.png'), optimize=True)
    folder = os.path.join(RES, 'mipmap-anydpi-v26')
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, 'ic_launcher.xml'), 'w', newline='\n') as f:
        f.write(ADAPTIVE)

    # A white Foxy silhouette for the Android status bar and Quick Settings.
    for dpi, factor in DENSITY.items():
        px = round(24 * factor)
        mask = fit_art(art, px * 4, 0.92).getchannel('A')
        mask = mask.point(lambda value: 255 if value > 48 else 0)
        mask = mask.filter(ImageFilter.MaxFilter(5)).resize(
            (px, px), Image.Resampling.LANCZOS)
        icon = Image.new('RGBA', (px, px), (255, 255, 255, 0))
        icon.putalpha(mask)
        folder = os.path.join(RES, 'drawable-' + dpi)
        os.makedirs(folder, exist_ok=True)
        icon.save(os.path.join(folder, 'ic_stat_logo.png'), optimize=True)

    # Android TV banner: same Foxy shield, no Spider artwork.
    banner = Image.new('RGBA', (320, 180), (10, 17, 38, 255))
    banner.alpha_composite(fit_art(art, 170, 0.88), (12, 5))
    ImageDraw.Draw(banner).text((190, 75), 'Foxy Hide VPN',
                                fill=(245, 247, 252, 255), anchor='lm')
    folder = os.path.join(RES, 'drawable-xhdpi')
    os.makedirs(folder, exist_ok=True)
    banner.save(os.path.join(folder, 'banner.png'), optimize=True)


def crisp(art, size):
    image = fit_art(art, size, 1.0)
    alpha = image.getchannel('A')
    rgb = image.convert('RGB').filter(
        ImageFilter.UnsharpMask(radius=0.7, percent=125, threshold=0))
    rgb = ImageEnhance.Contrast(rgb).enhance(1.05)
    out = rgb.convert('RGBA')
    out.putalpha(alpha)
    return out


def write_ico(path, art, sizes=WINDOWS_SIZES):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    images = [crisp(art, n) if n <= 48 else fit_art(art, n, 1.0)
              for n in sizes]
    images[-1].save(path, format='ICO',
                    sizes=[(n, n) for n in sizes],
                    append_images=images[:-1])


def desktop_and_web(art):
    desktop = os.path.join(CORE, 'internal', 'desktop')
    write_ico(os.path.join(desktop, 'appicon.ico'), art)
    web = os.path.join(CORE, 'internal', 'service', 'web')
    os.makedirs(web, exist_ok=True)
    tile(art, 192).save(os.path.join(web, 'icon.png'), optimize=True)


def flutter_assets(art):
    assets = os.path.join(APP, 'assets')
    os.makedirs(assets, exist_ok=True)
    tile(art, 256).save(os.path.join(assets, 'logo.png'), optimize=True)


def tray_icon(art, dot=None, opacity=1.0):
    icon = fit_art(art, 80, 0.72)
    if opacity != 1.0:
        icon.putalpha(icon.getchannel('A').point(
            lambda value: round(value * opacity)))
    draw = ImageDraw.Draw(icon)
    if dot:
        draw.ellipse((49, 49, 77, 77), fill=(7, 12, 24, 255))
        draw.ellipse((54, 54, 74, 74), fill=dot + (255,))
    # Preserve the tray's white upright status stroke. The core tray icon
    # contract checks its center pixel, and it remains legible at 16–32 px.
    draw.rectangle((38, 24, 42, 44), fill=(255, 255, 255, 255))
    return icon


def save_tray_set(folder, art, states, png_size):
    os.makedirs(folder, exist_ok=True)
    for name, icon in states.items():
        write_ico(os.path.join(folder, name + '.ico'), icon, TRAY_SIZES)
        icon.resize((png_size, png_size), Image.Resampling.LANCZOS).save(
            os.path.join(folder, name + '.png'), optimize=True)


def tray(art):
    app_states = {
        'off': tray_icon(art),
        'on': tray_icon(art, DOT_GOOD),
        'idle': tray_icon(art, DOT_GOOD),
        'error': tray_icon(art, DOT_BAD),
        'busy1': tray_icon(art, opacity=0.40),
        'busy2': tray_icon(art, opacity=0.62),
        'busy3': tray_icon(art, opacity=0.82),
        'busy4': tray_icon(art),
    }
    save_tray_set(os.path.join(APP, 'assets', 'tray'), art,
                  app_states, 64)
    def asleep(color):
        return tuple(round(c * 0.45 + g * 0.55)
                     for c, g in zip(color, (150, 160, 158)))
    core_states = {
        'running': tray_icon(art, DOT_GOOD),
        'set': tray_icon(art, DOT_SET),
        'running-asleep': tray_icon(art, asleep(DOT_GOOD)),
        'set-asleep': tray_icon(art, asleep(DOT_SET)),
        'waiting': tray_icon(art, opacity=0.55),
        'error': tray_icon(art, DOT_BAD),
        'off': tray_icon(art),
    }
    save_tray_set(os.path.join(CORE, 'internal', 'desktop', 'tray'),
                  art, core_states, 32)



def macos_icons(art):
    """Generate every macOS AppIcon.appiconset image from the same Foxy mark."""
    folder = os.path.join(APP, 'macos', 'Runner', 'Assets.xcassets',
                          'AppIcon.appiconset')
    os.makedirs(folder, exist_ok=True)
    sizes = {
        'app_icon_16.png': 16, 'app_icon_32.png': 32,
        'app_icon_64.png': 64, 'app_icon_128.png': 128,
        'app_icon_256.png': 256, 'app_icon_512.png': 512,
        'app_icon_1024.png': 1024,
    }
    for name, size in sizes.items():
        canvas = Image.new('RGBA', (size, size), (7, 12, 24, 255))
        canvas.alpha_composite(fit_art(art, size, 0.88))
        canvas.save(os.path.join(folder, name), optimize=True)

def main():
    if not os.path.isfile(SOURCE):
        raise SystemExit('Foxy source logo not found: ' + SOURCE)
    art = Image.open(SOURCE).convert('RGBA')
    art.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    if art.size != (1024, 1024):
        canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        canvas.alpha_composite(art, ((1024 - art.width) // 2, (1024 - art.height) // 2))
        art = canvas
    if art.getchannel('A').getbbox() is None:
        raise SystemExit('Foxy source logo is fully transparent')
    android(art)
    flutter_assets(art)
    write_ico(os.path.join(APP, 'windows', 'runner', 'resources',
                           'app_icon.ico'), art)
    desktop_and_web(art)
    macos_icons(art)
    tray(art)
    print('Generated Foxy Hide VPN icons for Android, Windows, Linux and web.')


if __name__ == '__main__':
    main()
