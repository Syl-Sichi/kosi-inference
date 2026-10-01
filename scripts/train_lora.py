#!/usr/bin/env python3
"""
Illustrative LoRA SFT skeleton for K.O.S.I.
Install GPU stack on a training machine, then adapt versions to current Unsloth/TRL docs.

  pip install unsloth trl datasets transformers accelerate bitsandbytes
  python scripts/train_lora.py --data data/examples/kosi_sft_sample.jsonl

This is NOT run inside the API container.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="K.O.S.I. LoRA SFT skeleton")
    parser.add_argument("--data", type=Path, default=Path("data/examples/kosi_sft_sample.jsonl"))
    parser.add_argument("--model", default="unsloth/Llama-3.2-3B-Instruct")
    parser.add_argument("--out", type=Path, default=Path("outputs/kosi-lora"))
    args = parser.parse_args()

    if not args.data.exists():
        raise SystemExit(f"Data file not found: {args.data}")

    print("K.O.S.I. LoRA skeleton")
    print(f"  data : {args.data}")
    print(f"  model: {args.model}")
    print(f"  out  : {args.out}")
    print()
    print("Next steps (install Unsloth/TRL on a GPU host):")
    print("  1. Load base model in 4-bit")
    print("  2. Attach LoRA (r=16) on q/k/v/o + MLP projections")
    print("  3. Map JSONL messages → chat template text")
    print("  4. SFTTrainer for 1–3 epochs")
    print("  5. Export GGUF → ollama create kosi -f Modelfile")
    print()
    print("See docs/FINETUNE.md for the full path.")
    print("Sample lines:", sum(1 for _ in args.data.open()))


if __name__ == "__main__":
    main()
