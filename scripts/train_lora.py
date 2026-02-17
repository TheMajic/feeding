from __future__ import annotations

import argparse
import os


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", required=True, help="HuggingFace model name/path (instruct model recommended).")
    ap.add_argument("--data", required=True, help="JSONL dataset path from generate_dataset.py")
    ap.add_argument("--out", required=True, help="Output directory for LoRA adapters")
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--batch_size", type=int, default=1)
    ap.add_argument("--grad_accum", type=int, default=8)
    ap.add_argument("--max_seq_len", type=int, default=2048)
    args = ap.parse_args()

    from datasets import load_dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
    from trl import SFTTrainer
    import torch

    ds = load_dataset("json", data_files=args.data, split="train")

    def to_text(ex):
        lang = ex.get("lang", "en")
        if lang == "ar":
            system = (
                "أنت مساعد تغذية وتمارين للرياضيين. "
                "اعطِ خطة غذائية كاملة لثلاث وجبات مع العناصر الغذائية وأمثلة أطعمة، "
                "بالإضافة لخطة تمارين للجيم وخطة منزلية. التزم بالعربية."
            )
        else:
            system = (
                "You are a nutrition + workout coach for athletes. "
                "Return a complete 3-meal plan with nutrients and food examples, "
                "plus a gym workout plan and a home workout plan. Write in English."
            )
        prompt = ex["prompt"]
        completion = ex["completion"]
        ex["text"] = f"<|system|>\n{system}\n<|user|>\n{prompt}\n<|assistant|>\n{completion}"
        return ex

    ds = ds.map(to_text, remove_columns=[c for c in ds.column_names if c != "text"])

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )

    train_args = TrainingArguments(
        output_dir=args.out,
        num_train_epochs=float(args.epochs),
        learning_rate=float(args.lr),
        per_device_train_batch_size=int(args.batch_size),
        gradient_accumulation_steps=int(args.grad_accum),
        logging_steps=10,
        save_steps=200,
        save_total_limit=2,
        fp16=torch.cuda.is_available(),
        bf16=False,
        report_to=[],
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=ds,
        peft_config=peft_config,
        max_seq_length=int(args.max_seq_len),
        args=train_args,
        packing=False,
    )

    trainer.train()
    trainer.save_model(args.out)
    tokenizer.save_pretrained(args.out)

    print(f"Saved LoRA adapters to: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

