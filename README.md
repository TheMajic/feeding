## Feeding AI (Bilingual Meal + Workout Generator)

Generates a complete **3-meal nutrition plan** + **gym/home workout plan** for athletes.

It reads a **single text message** from the user containing:
- height
- weight
- sport

And produces output in **Arabic or English**, automatically based on the user's input language.

> Disclaimer: This tool is for educational purposes and general fitness guidance. It is **not medical advice**.

## Features

- **Bilingual (AR/EN)**: output language follows the user's input language.
- **Nutrition**:
  - estimates daily calories and macro targets (protein/carbs/fats)
  - generates 3 meals with ingredients, nutrients, and food examples
- **Workouts**:
  - provides a gym plan and a home/fitness plan
  - sport-aware recommendations (endurance vs strength vs mixed)
- **Dataset creation**:
  - synthetic dataset generator for SFT/LoRA fine-tuning (JSONL)
- **Optional GPU model**:
  - plug in a local HuggingFace LLM for stronger generation
  - LoRA training script provided

## Quick start (PowerShell)

```powershell
cd "C:\Users\user\Sporton\Feeding"

# Create venv
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# If Arabic output looks broken in your console:
# $env:PYTHONUTF8 = "1"
# chcp 65001

# Install (core runtime)
pip install -U pip
pip install -r .\requirements.txt

# Run CLI (Arabic input -> Arabic output)
py -m feeding_ai.cli "طولي 175 سم ووزني 78 كجم وبمارس كرة قدم"

# Run CLI (English input -> English output)
py -m feeding_ai.cli "I am 180 cm, 82 kg, I play basketball"
```

## Run API (optional)

```powershell
cd "C:\Users\user\Sporton\Feeding"
.\.venv\Scripts\Activate.ps1

uvicorn feeding_ai.service.api:app --host 127.0.0.1 --port 8080
```

Then send a request:

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8080/generate `
  -ContentType "application/json" `
  -Body '{"text":"طولي 172 سم ووزني 70 كجم وبمارس السباحة"}'
```

## Dataset generation (JSONL)

```powershell
cd "C:\Users\user\Sporton\Feeding"
.\.venv\Scripts\Activate.ps1

py .\scripts\generate_dataset.py --out .\data\feeding_sft.jsonl --n 2000
```

Output schema (per line):
- `id`
- `lang` (`ar` / `en`)
- `prompt` (raw user message)
- `profile` (parsed structured fields)
- `completion` (generated plan)

## Optional: LoRA fine-tuning (GPU)

If you want a **very strong model**, you can fine-tune an instruct LLM (e.g., Llama/Mistral) with LoRA.

1) Install training deps:

```powershell
pip install -r .\requirements-train.txt
```

2) Generate dataset:

```powershell
py .\scripts\generate_dataset.py --out .\data\feeding_sft.jsonl --n 20000
```

3) Train LoRA:

```powershell
py .\scripts\train_lora.py `
  --base_model "mistralai/Mistral-7B-Instruct-v0.3" `
  --data .\data\feeding_sft.jsonl `
  --out .\runs\lora_feeding
```

> Note: downloading base models requires HuggingFace access + internet.

