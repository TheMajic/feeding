from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..lang import Lang
from ..parser import Profile


def _system_prompt(lang: str) -> str:
    if lang == "ar":
        return (
            "أنت مساعد تغذية وتمارين للرياضيين. "
            "اعطِ خطة غذائية كاملة لثلاث وجبات (فطار/غداء/عشاء) مع العناصر الغذائية، "
            "وأمثلة أطعمة/منتجات لكل عنصر، بالإضافة لخطة تمارين للجيم وخطة منزلية. "
            "التزم باللغة العربية."
        )
    return (
        "You are a nutrition + workout coach for athletes. "
        "Return a complete 3-meal plan (breakfast/lunch/dinner) with nutrients, "
        "and food/product examples for each nutrient, plus a gym workout plan and a home workout plan. "
        "Write strictly in English."
    )


def _user_prompt(profile: Profile, lang: str) -> str:
    if lang == "ar":
        return (
            f"الطول: {profile.height_cm:.0f} سم\n"
            f"الوزن: {profile.weight_kg:.1f} كجم\n"
            f"الرياضة: {profile.sport_raw}\n"
            "مطلوب: خطة يومية واضحة بعناوين ونقاط."
        )
    return (
        f"Height: {profile.height_cm:.0f} cm\n"
        f"Weight: {profile.weight_kg:.1f} kg\n"
        f"Sport: {profile.sport_raw}\n"
        "Need: a clear daily plan with headings and bullet points."
    )


@dataclass(frozen=True)
class LLMGenerator:
    """
    Optional generator using a local HuggingFace causal LLM (GPU if available).
    This is intentionally isolated to avoid importing heavy deps unless used.
    """

    base_model: str
    max_new_tokens: int = 900
    temperature: float = 0.7
    top_p: float = 0.9

    def generate(self, profile: Profile, lang: Lang) -> str:
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "Transformers/torch not installed. Install requirements-train.txt or use RuleBasedGenerator."
            ) from e

        tokenizer = AutoTokenizer.from_pretrained(self.base_model, use_fast=True)
        model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            torch_dtype=getattr(torch, "float16", None),
            device_map="auto",
        )

        system = _system_prompt(lang.code)
        user = _user_prompt(profile, lang.code)

        # Generic chat formatting; works for many instruct models.
        prompt = f"<|system|>\n{system}\n<|user|>\n{user}\n<|assistant|>\n"
        inputs = tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=int(self.max_new_tokens),
                do_sample=True,
                temperature=float(self.temperature),
                top_p=float(self.top_p),
                eos_token_id=tokenizer.eos_token_id,
            )

        text = tokenizer.decode(out[0], skip_special_tokens=True)
        # Return only assistant continuation when possible
        if "<|assistant|>" in text:
            return text.split("<|assistant|>", 1)[-1].strip()
        return text.strip()

