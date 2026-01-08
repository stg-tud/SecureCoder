# OpenAPI Bridge Server
This module contains the HTTP server. It exposes a minimal OpenAI-style `POST /v1/chat/completions` endpoint backed by the SecureCoder engine.

## Run with Docker

### Configuration
- OpenRouter mode:
  - `OPENROUTER_KEY` — your OpenRouter API key
  - `MODEL` — model ID (e.g.: `openai/gpt-oss-20b`)
- Ollama mode (used when `OPENROUTER_KEY` is not set):
  - `MODEL` — Ollama model name (e.g.: `gpt-oss:20`)
  - `OLLAMA_BASE_URL` — base URL to Ollama (default: 11434 on the host)
  - `OLLAMA_KEEP_ALIVE` — keep-alive duration (default: `5m`)

### Build and run
Make sure you have Docker installed and are in the project root directory.
```
docker build -f app/openai-bridge/Dockerfile -t openai-bridge:latest .
```

Run with Ollama on the host (macOS/Windows):
```
docker run --rm -p 8080:8080 \
  -e MODEL="gpt-oss:20b" \
  openai-bridge:latest
```

Run with Ollama on the host (Linux):
```
docker run --rm -p 8080:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e MODEL="gpt-oss:20b" \
  openai-bridge:latest
```

Run using OpenRouter instead of Ollama:
```
docker run --rm -p 8080:8080 \
  -e OPENROUTER_KEY=... \
  -e MODEL=openai/gpt-oss-20b \
  openai-bridge:latest
```

## Endpoint
- `POST /v1/chat/completions` — accepts a minimal OpenAI-style request and returns a single choice with the SecureCoder engine’s response.

Example request (from host):
```
curl -X POST "http://localhost:8080/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [
      {"role": "user", "content": "Create a Java class named Hello with a main method that prints Hello"}
    ],
    "stream": false
  }'
```
