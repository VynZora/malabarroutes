from django import template

from ..utils.image_optimizer import VARIANTS, variant_name

register = template.Library()


@register.filter
def srcset(field_file):
    """Build a srcset string from the generated variants + the main image."""
    if not field_file or not field_file.name:
        return ""

    storage = field_file.storage
    parts = []
    for width in sorted(VARIANTS):
        name = variant_name(field_file.name, width)
        if storage.exists(name):
            parts.append(f"{storage.url(name)} {width}w")
    parts.append(f"{field_file.url} 1920w")
    return ", ".join(parts)