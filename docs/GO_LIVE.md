# Go live: Llama-powered K.O.S.I.

## Architecture

```
CloudConnect UI (/kosi)
    → Supabase Edge Function `cai-chat` (provider=llama)
        → CAI_INFERENCE_URL/v1/chat/completions
            → kosi-inference (FastAPI)
                → Ollama (llama3.2 / kosi fine-tune)
```

Optional: point `CAI_INFERENCE_URL` at **Groq** (`https://api.groq.com/openai/v1`) with `CAI_MODEL_NAME=llama-3.3-70b-versatile` and `CAI_API_KEY=<groq key>` — same OpenAI-compatible path, no local GPU.

## A. Self-host (true “our model” path)

1. Install [Ollama](https://ollama.com), then:

```bash
ollama pull llama3.2
ollama cp llama3.2 kosi
```

2. Run inference API:

```bash
git clone https://github.com/Syl-Sichi/kosi-inference.git
cd kosi-inference
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export KOSI_MODEL=kosi
export KOSI_API_KEY=change-me-long-secret
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. Expose HTTPS (ngrok / Cloudflare Tunnel):

```bash
ngrok http 8000
# https://xxxx.ngrok-free.app
```

4. Supabase → Project **onkkdlkwmmgbcktbdfpc** → Edge Functions → Secrets:

| Secret | Value |
|--------|--------|
| `CAI_INFERENCE_URL` | `https://xxxx.ngrok-free.app/v1` |
| `CAI_MODEL_NAME` | `kosi` |
| `CAI_API_KEY` | same as `KOSI_API_KEY` |
| `CAI_DEFAULT_PROVIDER` | `llama` |

5. Redeploy:

```bash
supabase functions deploy cai-chat --project-ref onkkdlkwmmgbcktbdfpc
```

6. In the app: **K.O.S.I.** → provider **Llama** (now default).

## B. Fine-tune later

- Expand `data/examples/` → private JSONL (500+ turns)
- `docs/FINETUNE.md` + `scripts/train_lora.py`
- `ollama create kosi -f Modelfile` with your GGUF

## C. Smoke test

```bash
curl -s https://YOUR_HOST/health
curl -s https://YOUR_HOST/v1/chat/completions \
  -H "Authorization: Bearer change-me-long-secret" \
  -H "Content-Type: application/json" \
  -d '{"model":"kosi","messages":[{"role":"user","content":"Who are you?"}]}'
```

Expect identity: **K.O.S.I.**, not generic Llama branding in the reply (system prompt + optional fine-tune).
