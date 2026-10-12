import io
import os

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

MAX_DIMENSION = 1920
TARGET_KB = 200
MIN_QUALITY = 40

# width in px -> target size in KB
VARIANTS = {480: 60, 900: 120}


def convert_to_webp(file_obj, original_name, target_kb=TARGET_KB, max_dimension=MAX_DIMENSION):
    """Return a ContentFile (.webp) from any image, kept under target_kb."""
    file_obj.seek(0)
    img = Image.open(file_obj)
    img = ImageOps.exif_transpose(img)

    has_alpha = img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    )
    img = img.convert("RGBA" if has_alpha else "RGB")
    img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

    target = target_kb * 1024
    min_side = min(400, max_dimension // 2)

    while True:
        quality = 85
        while True:
            buf = io.BytesIO()
            img.save(buf, "WEBP", quality=quality, method=6)
            if buf.tell() <= target or quality <= MIN_QUALITY:
                break
            quality -= 5

        if buf.tell() <= target or min(img.size) <= min_side:
            break
        w, h = img.size
        img = img.resize((int(w * 0.85), int(h * 0.85)), Image.LANCZOS)

    base = os.path.splitext(os.path.basename(original_name))[0]
    return ContentFile(buf.getvalue(), name=f"{base}.webp")


def variant_name(name, width):
    root, _ = os.path.splitext(name)
    return f"{root}_{width}.webp"


def generate_variants(field_file):
    """Create the small versions next to the main image (skips existing ones)."""
    storage = field_file.storage
    for width, kb in VARIANTS.items():
        name = variant_name(field_file.name, width)
        if storage.exists(name):
            continue
        with storage.open(field_file.name) as src:
            webp = convert_to_webp(src, name, kb, width)
        storage.save(name, webp)


def delete_variants(field_file):
    for width in VARIANTS:
        name = variant_name(field_file.name, width)
        if field_file.storage.exists(name):
            field_file.storage.delete(name)