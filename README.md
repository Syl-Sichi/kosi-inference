# K.O.S.I. Inference

**Knowledge Operating System Intelligence** — Python inference API for [CloudConnect](https://github.com/Syl-Sichi/cloud-connect).

This repo has two tracks:

1. **Serve** — FastAPI proxy that speaks OpenAI-compatible `/v1/chat/completions` (works with CloudConnect’s `llama` provider).
2. **Train** — LoRA fine-tune path so your own weights can become the real “K.O.S.I. model.”

Live product UI: CloudConnect → **K.O.S.I.** (`/kosi`).  
Edge function still named `cai-chat`; it forwards to this server when provider = Llama.

---

## Quick start (serve with Ollama)

### 1. Install Ollama and pull a base model

```bash
# https://ollama.com
ollama pull llama3.2
# optional: tag it as kosi for clarity
ollama cp llama3.2 kosi
```

### 2. Run this API

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export OLLAMA_BASE_URL=http://127.0.0.1:11434
export KOSI_MODEL=kosi          # or llama3.2
export KOSI_API_KEY=change-me   # optional shared secret

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check: `GET http://localhost:8000/health`  
Chat: `POST http://localhost:8000/v1/chat/completions`

### 3. Expose HTTPS (required for Supabase)

Supabase Edge Functions cannot call your laptop’s `localhost`. Use a tunnel for testing:

```bash
# example: Cloudflare Tunnel or ngrok
ngrok http 8000
# copy the https://....ngrok-free.app URL
```

### 4. Wire CloudConnect

In **Supabase → Project `onkkdlkwmmgbcktbdfpc` → Edge Functions → Secrets**:

| Secret | Value |
|--------|--------|
| `CAI_INFERENCE_URL` | `https://YOUR-TUNNEL/v1` |
| `CAI_MODEL_NAME` | `kosi` |
| `CAI_API_KEY` | same as `KOSI_API_KEY` (if set) |

Redeploy if needed:

```bash
supabase functions deploy cai-chat --project-ref onkkdlkwmmgbcktbdfpc
```

In the K.O.S.I. UI, select provider **Llama**.

---

## API contract (OpenAI-compatible)

```http
POST /v1/chat/completions
Authorization: Bearer <KOSI_API_KEY>   # if KOSI_API_KEY is set
Content-Type: application/json

{
  "model": "kosi",
  "stream": true,
  "temperature": 0.7,
  "messages": [
    { "role": "system", "content": "..." },
    { "role": "user", "content": "Who are you?" }
  ]
}
```

CloudConnect’s edge function already sends the K.O.S.I. identity + mode prompts as the system message.

---

## Fine-tune (LoRA) path

See **[docs/FINETUNE.md](docs/FINETUNE.md)** for:

- JSONL chat data format
- Example training script outline (Unsloth / Hugging Face PEFT)
- How to register the adapter in Ollama or serve with vLLM

Starter data folder: `data/examples/`.

---

## Docker

```bash
docker build -t kosi-inference .
docker run --rm -p 8000:8000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e KOSI_MODEL=kosi \
  -e KOSI_API_KEY=change-me \
  kosi-inference
```

(On Linux, use the host network or the host’s LAN IP for Ollama.)

---

## Layout

```
app/
  main.py           # FastAPI server
  auth.py           # optional API key
  ollama_client.py  # proxy to Ollama
data/
  examples/         # sample fine-tune JSONL
docs/
  FINETUNE.md       # LoRA guide
Dockerfile
requirements.txt
```

---

## Security notes

- Always set `KOSI_API_KEY` in production.
- Prefer a private host / VPN over a long-lived public ngrok URL.
- Do not commit real API keys or private chat exports.

---

Built for **CloudConnect** · Founder: Syl
