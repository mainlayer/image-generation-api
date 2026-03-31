"""
Mock image generator.

In production, replace `generate_image` with a real image generation
backend (e.g. Stable Diffusion, DALL-E, Flux, etc.).  The function
must return a base64-encoded string of the image bytes.
"""

import base64
import struct
import zlib


def _minimal_png(width: int, height: int) -> bytes:
    """Build a tiny solid-colour PNG (grey gradient) without PIL."""

    def chunk(name: bytes, data: bytes) -> bytes:
        c = name + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    ihdr = chunk(b"IHDR", ihdr_data)

    raw_rows = []
    for y in range(height):
        row = b"\x00"  # filter type None
        for x in range(width):
            v = (x + y) % 256
            row += bytes([v, (v + 80) % 256, (v + 160) % 256])
        raw_rows.append(row)

    idat = chunk(b"IDAT", zlib.compress(b"".join(raw_rows)))
    iend = chunk(b"IEND", b"")
    return signature + ihdr + idat + iend


def generate_image(prompt: str, width: int = 512, height: int = 512, fmt: str = "png") -> str:
    """
    Generate a placeholder image and return it as a base64 string.

    Args:
        prompt: Text prompt describing the desired image.
        width:  Output image width in pixels.
        height: Output image height in pixels.
        fmt:    Output format — 'png', 'jpeg', or 'webp'.

    Returns:
        Base64-encoded image data (no data-URI prefix).
    """
    png_bytes = _minimal_png(width, height)
    return base64.b64encode(png_bytes).decode()
