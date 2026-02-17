from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from ..core import generate_from_text


app = FastAPI(title="Feeding AI", version="0.1.0")


class GenerateRequest(BaseModel):
    text: str = Field(..., description="User input containing height, weight, and sport.")
    llm_base_model: str | None = Field(
        default=None,
        description="Optional HuggingFace model name/path for stronger generation (requires transformers/torch).",
    )


class GenerateResponse(BaseModel):
    lang: str
    profile: dict
    plan: str


@app.get("/")
def root() -> dict:
    return {"ok": True, "service": "Feeding AI"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    res = generate_from_text(req.text, llm_base_model=req.llm_base_model)
    return GenerateResponse(
        lang=res.lang.code,
        profile={
            "height_cm": res.profile.height_cm,
            "weight_kg": res.profile.weight_kg,
            "sport": res.profile.sport,
            "sport_raw": res.profile.sport_raw,
        },
        plan=res.text,
    )

