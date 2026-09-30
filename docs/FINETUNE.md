# Fine-tuning K.O.S.I. (LoRA)

Goal: teach a small open model CloudConnect tone, product facts, and mode styles — without training a foundation model from scratch.

## 1. Data format (JSONL)

One chat per line. Same shape as OpenAI / many SFT tools:

```json
{"messages":[
  {"role":"system","content":"You are K.O.S.I...."},
  {"role":"user","content":"..."},
  {"role":"assistant","content":"..."}
]}
```

See `data/examples/kosi_sft_sample.jsonl`.

### What to collect

| Source | Use |
|--------|-----|
| Approved K.O.S.I. chats | Real tone |
| Product FAQ (Gaming, Stream, stickers, auth) | Accuracy |
| Mode exemplars (Cruise, Church, Pro…) | Style |
| Founder-approved bio facts only | Identity |

**Do not** include passwords, private DMs, or payment data.

Aim for **500–5,000** high-quality turns before expecting a clear lift. Quality > quantity.

## 2. Base model picks

| Model | Notes |
|-------|--------|
| Llama 3.2 3B / 8B | Good default for Ollama |
| Mistral 7B | Strong general chat |
| Qwen2.5 7B | Strong instruction following |

Start small (3B–8B) so you can iterate on a single GPU or a rented cloud GPU.

## 3. Training stack (outline)

Recommended path: **Unsloth** or **Hugging Face PEFT + TRL SFTTrainer**.

```text
pip install unsloth  # or peft transformers datasets trl accelerate bitsandbytes
```

Conceptual steps:

1. Load base model in 4-bit.
2. Attach LoRA adapters (attention + MLP modules).
3. Train on your JSONL with SFT.
4. Export adapter or merge weights.
5. Convert to GGUF for Ollama **or** serve with vLLM.

Example Unsloth-style skeleton (adapt versions to current docs):

```python
# train_lora.py — illustrative skeleton, not pinned versions
from unsloth import FastLanguageModel
from trl import SFTTrainer
from datasets import load_dataset

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.2-3B-Instruct",
    max_seq_length=2048,
    load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
)

dataset = load_dataset("json", data_files="data/private/kosi_sft.jsonl", split="train")
# Map messages → text with your chat template, then SFTTrainer(...)
```

Keep full training scripts out of the main API image; run them on a GPU machine and commit only **small** sample data.

## 4. Register in Ollama after train

If you export GGUF:

```bash
# Create a Modelfile
# FROM ./kosi-lora.gguf
# SYSTEM You are K.O.S.I....

ollama create kosi -f Modelfile
```

Point this API at it:

```bash
export KOSI_MODEL=kosi
```

## 5. Connect to CloudConnect

Same as the serve path:

- Public HTTPS base URL → `CAI_INFERENCE_URL` (include `/v1`)
- `CAI_MODEL_NAME=kosi`
- UI provider: **Llama**

System prompts from the edge function still apply on top of your fine-tune — that is good (modes stay consistent).

## 6. Evaluation checklist

Before calling it “production K.O.S.I.”:

- [ ] “Who are you?” → K.O.S.I., not Llama/ChatGPT
- [ ] Cruise / Church / Pro modes still feel distinct
- [ ] Product questions don’t invent features
- [ ] No regurgitation of private training leaks
- [ ] Latency acceptable on your host

## 7. Cost / hardware ballpark

| Setup | Expectation |
|-------|-------------|
| Laptop CPU + Ollama 3B | Slow but works for demos |
| Single 24GB GPU | Comfortable 7B–8B LoRA |
| Rented A100/H100 | Faster experiments, larger batches |

---

When the adapter is stable, bump this repo’s default `KOSI_MODEL` and document the exact base + adapter hash in a release tag.
