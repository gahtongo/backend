import re
import unicodedata


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^\w\s-]", "", ascii_text).strip().lower()
    return re.sub(r"[-\s]+", "-", cleaned)


def ensure_unique_slug(base_slug: str, existing_slugs: set[str]) -> str:
    if base_slug not in existing_slugs:
        return base_slug

    counter = 2
    while True:
        candidate = f"{base_slug}-{counter}"
        if candidate not in existing_slugs:
            return candidate
        counter += 1