# Image Generation API

A FastAPI service that generates images on demand with **per-image credit billing** via [Mainlayer](https://mainlayer.fr).

This is a production-ready template for monetizing image generation APIs. Swap the mock generator for any real image model (Stable Diffusion, DALL-E, Flux, Midjourney, etc.) and billing is handled automatically.

## Features

- `POST /generate` — generate images from text prompts
- Per-call credit billing: **1 credit per image** (configurable)
- Configurable output dimensions (64–2048 px) and format (PNG, JPEG, WebP)
- Mock generator for testing (replace with your model)
- Full Mainlayer payment integration with HTTP 402 Payment Required
- Deterministic mock generator for reproducible testing
- Comprehensive error handling and logging

## 5-Minute Quickstart

### 1. Prerequisites

```bash
git clone <this-repo>
cd image-generation-api
python -m venv venv
source venv/bin/activate  # or: .\venv\Scripts\activate on Windows
```

### 2. Install and configure

```bash
pip install -r requirements.txt
cp .env.example .env

# Edit .env with your Mainlayer credentials:
# MAINLAYER_API_KEY=sk_live_...
# MAINLAYER_RESOURCE_ID=res_...
# MAINLAYER_ENABLED=false  # for local testing
```

### 3. Run the server

```bash
# Development with auto-reload
uvicorn src.main:app --reload

# Open http://localhost:8000/docs for interactive API docs
```

### 4. Generate an image

```python
import httpx
import base64

client = httpx.Client()

response = client.post(
    "http://localhost:8000/generate",
    json={
        "prompt": "A serene mountain lake at sunset",
        "width": 512,
        "height": 512,
        "format": "png",
    },
    headers={"x-mainlayer-token": "token_abc123"}
)

data = response.json()
with open("output.png", "wb") as f:
    f.write(base64.b64decode(data["image_b64"]))
print(f"Generated {data['width']}x{data['height']} image ({data['credits_used']} credits)")
```

## API Reference

### `POST /generate`

Generate an image from a text prompt.

**Request:**
```json
{
  "prompt": "A serene mountain lake at sunset",
  "width": 512,
  "height": 512,
  "format": "png"
}
```

**Headers:**
- `x-mainlayer-token` (required) — Mainlayer payment token

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Text description of the image |
| `width` | int | 512 | Output width in pixels (64–2048) |
| `height` | int | 512 | Output height in pixels (64–2048) |
| `format` | string | `png` | Output format: `png`, `jpeg`, or `webp` |

**Response (200 OK):**
```json
{
  "image_b64": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "format": "png",
  "width": 512,
  "height": 512,
  "credits_used": 1
}
```

**Error (402 Payment Required):**
```json
{
  "error": "payment_required",
  "message": "Get access at mainlayer.fr",
  "resource_id": "res_images_123"
}
```

### Other Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive API documentation |

## Pricing

Configure when setting up your Mainlayer resource:

| Model | Cost | Use Case |
|-------|------|----------|
| Per-image (1 credit) | $0.10 | Fixed cost per image |
| Per-pixel ($0.00001/pixel) | Variable | Charged by output size |
| Subscription | $49/mo | Unlimited images |

## Using a Real Image Generator

Replace the mock generator in `src/generator.py` with a real model:

### Stable Diffusion (using Replicate API)

```python
import replicate

def generate_image(prompt: str, width: int, height: int, fmt: str) -> str:
    """Replace mock with real Stable Diffusion generation."""
    output = replicate.run(
        "stability-ai/stable-diffusion:db21e45d3f7023abc9e46f76bfdecf26",
        input={"prompt": prompt, "width": width, "height": height}
    )

    # Download image and encode to base64
    import httpx, base64
    img_bytes = httpx.get(output[0]).content
    return base64.b64encode(img_bytes).decode()
```

### DALL-E 3 (using OpenAI API)

```python
from openai import OpenAI

client = OpenAI(api_key="sk_...")

def generate_image(prompt: str, width: int, height: int, fmt: str) -> str:
    """Replace mock with real DALL-E 3 generation."""
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=f"{width}x{height}",
        n=1,
        response_format="b64_json"
    )
    return response.data[0].b64_json
```

## Local Development (no payment)

For testing without Mainlayer integration:

```bash
MAINLAYER_ENABLED=false uvicorn src.main:app --reload

# Now requests work without payment tokens
curl http://localhost:8000/generate \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A red car",
    "width": 256,
    "height": 256,
    "format": "png"
  }'
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MAINLAYER_API_KEY` | Yes* | — | Your Mainlayer API key |
| `MAINLAYER_RESOURCE_ID` | Yes* | — | Mainlayer resource ID for image generation |
| `MAINLAYER_ENABLED` | No | `true` | Set to `false` for local development |
| `MAINLAYER_BASE_URL` | No | `https://api.mainlayer.fr` | Override Mainlayer endpoint |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `PORT` | No | `8000` | Server port |

*Required only if `MAINLAYER_ENABLED=true`

## Running Tests

```bash
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/
```

## Deployment

### Docker

```bash
docker build -t image-generation-api .
docker run -e MAINLAYER_API_KEY=sk_... -e MAINLAYER_RESOURCE_ID=res_... -p 8000:8000 image-generation-api
```

### Railway

```bash
railway up
```

### Fly.io

```bash
fly launch
fly deploy
```

## Support

- Docs: [docs.mainlayer.fr](https://docs.mainlayer.fr)
- Issues: GitHub issues on this repository
- Community: [mainlayer.fr/discord](https://mainlayer.fr/discord)
