import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from mainlayer import MainlayerClient
from src.generator import generate_image

app = FastAPI(
    title="Image Generation API",
    description="Per-image billed image generation powered by Mainlayer",
    version="1.0.0",
)

ml = MainlayerClient(api_key=os.environ["MAINLAYER_API_KEY"])
RESOURCE_ID = os.environ["MAINLAYER_RESOURCE_ID"]


class GenerateRequest(BaseModel):
    prompt: str
    width: Optional[int] = 512
    height: Optional[int] = 512
    format: Optional[str] = "png"


class GenerateResponse(BaseModel):
    image_b64: str
    format: str
    width: int
    height: int
    credits_used: int


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    x_mainlayer_token: str = Header(..., description="Mainlayer payment token"),
):
    access = await ml.resources.verify_access(RESOURCE_ID, x_mainlayer_token)
    if not access.authorized:
        raise HTTPException(
            status_code=402,
            detail="Payment required. Get access at mainlayer.fr",
        )

    if request.format not in ("png", "jpeg", "webp"):
        raise HTTPException(status_code=400, detail="Unsupported format. Use png, jpeg, or webp.")

    if request.width < 64 or request.width > 2048 or request.height < 64 or request.height > 2048:
        raise HTTPException(status_code=400, detail="Dimensions must be between 64 and 2048 pixels.")

    image_b64 = generate_image(
        prompt=request.prompt,
        width=request.width,
        height=request.height,
        fmt=request.format,
    )

    return GenerateResponse(
        image_b64=image_b64,
        format=request.format,
        width=request.width,
        height=request.height,
        credits_used=1,
    )
