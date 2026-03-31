# image-generation-api

[![CI](https://github.com/mainlayer/image-generation-api/actions/workflows/ci.yml/badge.svg)](https://github.com/mainlayer/image-generation-api/actions/workflows/ci.yml)

A FastAPI service that generates images on demand with **per-image credit billing** via [Mainlayer](https://mainlayer.fr).

## Features

- `POST /generate` — generate an image from a text prompt
- Per-call credit billing through Mainlayer payment tokens
- Configurable output dimensions (64–2048 px) and format (png / jpeg / webp)
- Ready to plug in any real image-generation backend

## Quickstart

```bash
pip install mainlayer
```

```bash
export MAINLAYER_API_KEY=your_api_key
export MAINLAYER_RESOURCE_ID=your_resource_id
uvicorn src.main:app --reload
```

### Generate an image

```python
import httpx, base64

resp = httpx.post(
    "http://localhost:8000/generate",
    json={"prompt": "A serene mountain lake", "width": 512, "height": 512, "format": "png"},
    headers={"x-mainlayer-token": "<your-token>"},
)
resp.raise_for_status()
data = resp.json()
with open("output.png", "wb") as f:
    f.write(base64.b64decode(data["image_b64"]))
```

## API Reference

### `POST /generate`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prompt` | string | required | Text description of the image |
| `width` | int | 512 | Output width in pixels (64–2048) |
| `height` | int | 512 | Output height in pixels (64–2048) |
| `format` | string | `png` | Output format: `png`, `jpeg`, or `webp` |

**Headers:** `x-mainlayer-token` (required)

**Response:**
```json
{
  "image_b64": "<base64-encoded image>",
  "format": "png",
  "width": 512,
  "height": 512,
  "credits_used": 1
}
```

## Payment

Access is gated through Mainlayer payment tokens. Get your token at [mainlayer.fr](https://mainlayer.fr).

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```
