import hashlib

from django import template
from django.core.cache import cache

from ..utils.image_optimizer import VARIANTS, variant_name

register = template.Library()

CACHE_SECONDS = 60 * 60 * 24  # 1 day
FALLBACK_WIDTH = 1920


def _original_width(field_file):
    """Real width of the original image, or a fallback if it can't be read."""
    try:
        return field_file.width
    except Exception:
        return FALLBACK_WIDTH


@register.filter
def srcset(field_file):
    """Build a srcset string from the generated variants + the main image."""
    if not field_file or not getattr(field_file, "name", None):
        return ""

    key = "srcset:" + hashlib.md5(field_file.name.encode("utf-8")).hexdigest()
    cached = cache.get(key)
    if cached is not None:
        return cached

    storage = field_file.storage
    original_w = _original_width(field_file)

    parts = []
    for width in sorted(VARIANTS):
        if width >= original_w:      # never advertise a variant bigger than the original
            continue
        name = variant_name(field_file.name, width)
        if storage.exists(name):
            parts.append(f"{storage.url(name)} {width}w")

    parts.append(f"{field_file.url} {original_w}w")

    result = ", ".join(parts)
    cache.set(key, result, CACHE_SECONDS)
    return result