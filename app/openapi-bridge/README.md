# OpenAPI Bridge Server
This module contains the HTTP server. It exposes a minimal OpenAI-style `POST /v1/chat/completions` endpoint backed by the SecureCoder engine.

## Prerequisites
- JDK 21
- Optional but recommended for security analysis features: CodeQL CLI in `PATH` (the Guardian uses it when analyzing code). If not present, some security analysis steps may fail.


## Configuration (Environment Variables)
The server reads its configuration from environment variables:

- `PORT` — HTTP port (default: `8080`)
- LLM selection (EngineFactory picks the first matching provider):
    - OpenRouter mode:
        - `OPENROUTER_KEY` — your OpenRouter API key
        - `MODEL` — model ID (default: `openai/gpt-oss-20b`)
    - Ollama mode (used when `OPENROUTER_KEY` is not set):
        - `MODEL` — Ollama model name, e.g. `llama3.1:8b`
        - `OLLAMA_BASE_URL` — base URL to Ollama (default: `http://127.0.0.1:11434`)
        - `OLLAMA_KEEP_ALIVE` — keep-alive duration (default: `5m`)


## How to run the server

On macOS/Linux:

```
./gradlew :app:openapi-bridge:run \
  -Dorg.gradle.jvmargs="-DOPENROUTER_KEY=... -DMODEL=..."
```

On Windows

```
set OPENROUTER_KEY=...
set MODEL=...
gradlew.bat :app:openapi-bridge:run
```

## Endpoint

- `POST /v1/chat/completions` — accepts a minimal OpenAI-style request and returns a single choice with the SecureCoder engine’s response.

Example request (curl):

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
