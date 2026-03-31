"""
Example: generate an image using the Image Generation API.

Usage:
    MAINLAYER_TOKEN=<your-token> python examples/generate_image.py
"""

import base64
import os
import sys

import httpx

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
TOKEN = os.getenv("MAINLAYER_TOKEN")

if not TOKEN:
    print("Error: set MAINLAYER_TOKEN environment variable")
    sys.exit(1)


def main() -> None:
    payload = {
        "prompt": "A serene mountain lake at sunrise",
        "width": 512,
        "height": 512,
        "format": "png",
    }

    response = httpx.post(
        f"{API_BASE}/generate",
        json=payload,
        headers={"x-mainlayer-token": TOKEN},
        timeout=60,
    )

    if response.status_code == 402:
        print("Payment required — get access at https://mainlayer.fr")
        sys.exit(1)

    response.raise_for_status()
    data = response.json()

    output_path = "generated.png"
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(data["image_b64"]))

    print(f"Image saved to {output_path}")
    print(f"Credits used: {data['credits_used']}")


if __name__ == "__main__":
    main()
