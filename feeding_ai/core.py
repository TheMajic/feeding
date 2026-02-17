from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .generators.rule_based import RuleBasedGenerator
from .lang import Lang, detect_lang
from .parser import Profile, parse_profile


@dataclass(frozen=True)
class GenerateResult:
    lang: Lang
    profile: Profile
    text: str


def generate_from_text(
    text: str,
    *,
    llm_base_model: Optional[str] = None,
) -> GenerateResult:
    lang = detect_lang(text)
    profile = parse_profile(text, lang)

    if llm_base_model:
        from .generators.llm import LLMGenerator

        gen = LLMGenerator(base_model=llm_base_model)
        out = gen.generate(profile, lang)
    else:
        gen = RuleBasedGenerator()
        out = gen.generate(profile, lang)

    return GenerateResult(lang=lang, profile=profile, text=out)

