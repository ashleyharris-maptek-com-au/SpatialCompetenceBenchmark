import base64
import mimetypes
import os
import re
from urllib.parse import urlparse

_IMAGE_TAG_RE = re.compile(r"\[\[\s*image\s*:\s*([^\]]+?)\s*\]\]",
                           re.IGNORECASE)

_SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp"
}


def parse_prompt_parts(prompt: str) -> list[tuple[str, str]]:
    if not prompt:
        return [("text", "")]

    parts: list[tuple[str, str]] = []
    last_end = 0
    for m in _IMAGE_TAG_RE.finditer(prompt):
        if m.start() > last_end:
            text_part = prompt[last_end:m.start()]
            if text_part:
                parts.append(("text", text_part))

        ref = m.group(1).strip()
        if (len(ref) >= 2) and ((ref[0] == '"' and ref[-1] == '"') or
                                (ref[0] == "'" and ref[-1] == "'")):
            ref = ref[1:-1].strip()
        if ref:
            parts.append(("image", ref))

        last_end = m.end()

    if last_end < len(prompt):
        tail = prompt[last_end:]
        if tail:
            parts.append(("text", tail))

    if not parts:
        return [("text", prompt)]

    return parts


def extract_image_tags(prompt: str) -> tuple[str, list[str]]:
    if not prompt:
        return "", []

    matches = list(_IMAGE_TAG_RE.finditer(prompt))
    if not matches:
        return prompt, []

    refs: list[str] = []
    for m in matches:
        ref = m.group(1).strip()
        if (len(ref) >= 2) and ((ref[0] == '"' and ref[-1] == '"') or
                                (ref[0] == "'" and ref[-1] == "'")):
            ref = ref[1:-1].strip()
        if ref:
            refs.append(ref)

    cleaned = _IMAGE_TAG_RE.sub("", prompt)
    return cleaned, refs


def is_data_uri(ref: str) -> bool:
    return ref.startswith("data:")


def is_url(ref: str) -> bool:
    return ref.startswith("http://") or ref.startswith("https://")


def resolve_local_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def guess_image_mime_type_from_path(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime:
        mime = mime.lower()

    if mime in _SUPPORTED_IMAGE_MIME_TYPES:
        return mime

    ext = os.path.splitext(path)[1].lower()
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".gif":
        return "image/gif"
    if ext == ".webp":
        return "image/webp"

    raise ValueError(f"Unsupported image type: {path}")


def guess_image_mime_type_from_ref(ref: str) -> str:
    if is_data_uri(ref):
        mime_type, _ = decode_data_uri(ref)
        return mime_type

    if is_url(ref):
        parsed = urlparse(ref)
        return guess_image_mime_type_from_path(parsed.path)

    return guess_image_mime_type_from_path(ref)


def read_file_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def file_to_base64(path: str) -> tuple[str, str]:
    mime_type = guess_image_mime_type_from_path(path)
    data = read_file_bytes(path)
    return mime_type, base64.b64encode(data).decode("utf-8")


def bytes_to_data_uri(data: bytes, mime_type: str) -> str:
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def file_to_data_uri(path: str) -> str:
    mime_type, b64 = file_to_base64(path)
    return f"data:{mime_type};base64,{b64}"


def decode_data_uri(data_uri: str) -> tuple[str, bytes]:
    if not is_data_uri(data_uri):
        raise ValueError("Not a data URI")

    header, b64_data = data_uri.split(",", 1)
    meta = header[5:]

    if ";base64" not in meta:
        raise ValueError("Only base64 data URIs are supported")

    mime_type = meta.split(";base64", 1)[0].strip().lower()
    if not mime_type:
        raise ValueError("Missing MIME type in data URI")

    if mime_type not in _SUPPORTED_IMAGE_MIME_TYPES:
        raise ValueError(f"Unsupported image MIME type: {mime_type}")

    return mime_type, base64.b64decode(b64_data)


def data_uri_to_base64(data_uri: str) -> tuple[str, str]:
    mime_type, data = decode_data_uri(data_uri)
    return mime_type, base64.b64encode(data).decode("utf-8")
