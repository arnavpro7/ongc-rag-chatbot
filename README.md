# Local LLM Chatbot — Internship Project

A fully local, privacy-preserving AI chatbot built with **Ollama** (local LLM runtime), **Open WebUI** (chat interface), and an optional **Python/FastAPI** backend — no paid APIs, no cloud services, no internet dependency after setup.

## 1. Project Overview

**Problem statement:** Interns need hands-on experience building and deploying an LLM-based chatbot, but cloud LLM APIs cost money and raise data-privacy concerns for a training environment.

**Objective:** Introduce interns to LLM-based chatbot development using open-source tools (Ollama + Open WebUI), with hands-on experience building, testing, and deploying a functional chatbot.

**Scope:**
- In scope: local model serving, a chat UI, an optional custom backend, testing, evaluation, security basics, and deployment via Docker.
- Out of scope: fine-tuning models, retrieval-augmented generation (RAG) over private documents, multi-user authentication systems beyond what Open WebUI provides out of the box.

**Target users:** Interns learning LLM application development; internal teams wanting a private, offline chatbot for experimentation.

**Functional requirements:**
- Local LLM interaction through a web interface.
- Multi-turn conversation with memory.
- Configurable system prompt/personality.
- Graceful error handling (Ollama down, bad input, timeouts).
- Swappable model configuration.
- Automated tests and a documented evaluation process.

**Non-functional requirements:**
- Runs on a normal laptop (CPU-only, no GPU required).
- No data leaves the local machine.
- No paid APIs or cloud dependency.
- Reasonably fast setup (under 30 minutes on a decent connection).

**Expected outcome:** A working, documented, testable local chatbot, plus interns who understand the full request path from browser to model and back.

**Possible future enhancements:**
- Retrieval-augmented generation (RAG) over internal documents.
- Persistent database-backed conversation history instead of in-memory storage.
- User authentication and per-user rate limiting.
- Streaming responses (token-by-token) in the custom backend.
- Support for multiple simultaneous models with a model picker.

## 2. Architecture

```text
 ┌────────────┐        HTTP (browser)        ┌──────────────────┐
 │   User /   │ ───────────────────────────▶ │   Open WebUI      │
 │  Intern    │ ◀─────────────────────────── │  (port 3000)      │
 └────────────┘                               └─────────┬─────────┘
                                                          │ HTTP (internal
                                                          │ Docker network)
                                                          ▼
                                               ┌──────────────────┐
                                               │     Ollama        │
                                               │  (port 11434)     │
                                               │  runs the LLM      │
                                               └──────────────────┘
                                                          ▲
                                                          │ HTTP (optional path)
                                                          │
                                               ┌──────────────────┐
                                               │  FastAPI Backend  │
                                               │  (port 8000,       │
                                               │   OPTIONAL)        │
                                               └──────────────────┘
```

- **Open WebUI → Ollama** is the REQUIRED, primary path. Open WebUI talks directly to Ollama's HTTP API to send prompts and stream back responses. This alone is a complete, working chatbot.
- **FastAPI backend** is OPTIONAL and educational — it demonstrates calling the Ollama API yourself, adding validation, error handling, and custom conversation logic. It runs alongside Open WebUI, not in place of it.
- **Data flow:** user types in Open WebUI → Open WebUI sends the message (+ history) to Ollama's `/api/chat` → Ollama runs the model and returns generated text → Open WebUI renders it. If using the custom backend directly (e.g. via `curl` or a script), the flow is client → backend `/chat` → Ollama `/api/chat` → backend → client.
- Everything runs on `localhost` / the Docker-internal network — no data goes to the internet.

## 3. Model Selection

All models below are CPU-friendly; no GPU is assumed.

| Model | Approx. RAM needed | Performance | Pros | Cons | Pull command |
|---|---|---|---|---|---|
| `qwen2.5:0.5b` | ~1 GB | Fast, very basic reasoning | Extremely light, good for low-RAM laptops | Noticeably weaker answers | `ollama pull qwen2.5:0.5b` |
| `llama3.2:1b` | ~2 GB | Fast, decent for simple Q&A | Good balance for very limited hardware | Struggles with complex/multi-step reasoning | `ollama pull llama3.2:1b` |
| `llama3.2:3b` (recommended default) | ~4–6 GB | Good general quality, still responsive on CPU | Best overall balance for a laptop with 8GB+ RAM | Slower than 1B on very old hardware | `ollama pull llama3.2:3b` |
| `phi3:mini` | ~4 GB | Strong for its size, good at instructions | Well-suited to structured/step-by-step answers | Slightly slower first-load | `ollama pull phi3:mini` |

**Recommendation:** start with `llama3.2:3b` on any laptop with 8GB+ RAM. Drop to `llama3.2:1b` or `qwen2.5:0.5b` if the machine has 4–8GB RAM or responses feel too slow.

## 4. Project Structure

```text
local-llm-chatbot/
├── backend/
│   ├── main.py            # FastAPI app: /chat, /health, /conversations endpoints
│   ├── schemas.py         # Pydantic request/response models
│   ├── requirements.txt   # Backend Python dependencies
│   └── Dockerfile          # Container build for the backend
├── frontend/                # Reserved for optional custom UI work (Open WebUI covers this by default)
├── tests/
│   └── test_backend.py     # Pytest suite for the backend
├── docs/
│   ├── evaluation.md        # Evaluation criteria, test dataset, scoring rubric
│   ├── troubleshooting.md   # Common issues and fixes
│   ├── internship_plan.md   # 4-week plan, deliverables, rubric, viva Q&A
│   └── system_prompt.md     # System prompt design and how to configure it
├── docker-compose.yml       # Orchestrates ollama + open-webui + backend
├── .env.example              # Template for environment variables
└── README.md                 # This file
```

## 5. Installation

### Prerequisites
- Docker Desktop (Windows/macOS) or Docker Engine + Compose plugin (Linux).
- 8GB+ RAM recommended (4GB minimum with the smallest model).
- ~10GB free disk space.

### Step 1 — Install Ollama (needed if NOT running Ollama via Docker)

**Windows:** download and run the installer from https://ollama.com/download.

**macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
(or download the macOS app from https://ollama.com/download)

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify:
```bash
ollama --version
```

> This project's `docker-compose.yml` runs Ollama **inside Docker** by default, so a separate host install of Ollama is optional — only needed if you prefer running Ollama directly on your machine instead of in a container. If you do that, skip the `ollama` service in `docker-compose.yml` and point `OLLAMA_BASE_URL` at `http://host.docker.internal:11434`.

### Step 2 — Clone/copy this project and configure environment
```bash
cd local-llm-chatbot
cp .env.example .env
```
Edit `.env` and set a real `WEBUI_SECRET_KEY` (any long random string).

### Step 3 — Start everything with Docker Compose
```bash
docker compose up -d
```
This starts three containers: `ollama`, `open-webui`, and `chatbot-backend`.

### Step 4 — Pull the model into the running Ollama container
```bash
docker exec -it ollama ollama pull llama3.2:3b
```
(Swap the model name if you chose a different one.)

### Step 5 — Access the chatbot
Open your browser to:
```
http://localhost:3000
```
Create a local account on first launch (stored only in your local `open-webui-data` volume). Select the model in the top dropdown and start chatting.

### Step 6 — Verify Ollama and Open WebUI are connected
```bash
curl http://localhost:11434/api/tags
```
This should list the pulled model. If Open WebUI's model dropdown is empty, see `docs/troubleshooting.md` item 10.

### Optional — Run the backend outside Docker (for development)
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env         # then set OLLAMA_BASE_URL=http://localhost:11434
uvicorn main:app --reload --port 8000
```
Then visit `http://localhost:8000/docs` for interactive API docs.

**Host vs. Docker networking — the #1 source of confusion:**
| Where backend runs | Where Ollama runs | `OLLAMA_BASE_URL` value |
|---|---|---|
| Host machine | Host machine | `http://localhost:11434` |
| Docker container | Host machine | `http://host.docker.internal:11434` |
| Docker container (same compose project) | Docker container | `http://ollama:11434` |

## 6. Configuration — System Prompt

The default system prompt (see `docs/system_prompt.md` for the full explanation) instructs the bot to:
- Answer clearly and step by step.
- Admit uncertainty instead of inventing facts.
- Ask clarifying questions when a request is ambiguous.
- Avoid harmful/illegal/unsafe content.
- Never request or repeat confidential information.

**To configure it in Open WebUI:** Settings → General → System Prompt (or per-model under Workspace → Models → edit model → System Prompt), paste the prompt, save.

**To configure it in the custom backend:** set the `SYSTEM_PROMPT` environment variable in `.env` (a sensible default is built in if you don't set one).

## 7. Source Code
See `backend/main.py` and `backend/schemas.py`. Both are fully commented for interns — read them alongside `docs/internship_plan.md` Week 2.

## 8. Docker Setup
See `docker-compose.yml`. Common commands:
```bash
docker compose up -d          # start everything in the background
docker compose logs -f        # follow logs from all services
docker compose logs -f ollama # follow logs from one service
docker compose down           # stop and remove containers (keeps volumes/data)
docker compose down -v        # stop and ALSO delete volumes (fresh reset)
docker compose up -d --build  # rebuild the backend image after code changes
```

## 9. Testing
```bash
cd backend
pip install -r requirements.txt
cd ..
pytest tests/test_backend.py -v
```
The suite covers connectivity, health checks, valid/invalid/empty/oversized messages, Ollama-unavailable and timeout scenarios, and multi-turn conversation behavior — all using mocks, so it runs without Ollama installed. See `docs/evaluation.md` for the separate, manual quality-evaluation process (which does require a running model).

## 10. Troubleshooting
See `docs/troubleshooting.md` for a full symptom → cause → fix guide covering ports in use, connection failures, Docker crashes, out-of-memory errors, and Docker networking mistakes.

## 11. Security Notes
- **Nothing leaves your machine.** All model inference happens locally; no external API calls are made by Ollama, Open WebUI, or the backend.
- **Change default secrets.** `WEBUI_SECRET_KEY` in `.env` must be changed from the placeholder before any real use — it signs Open WebUI's session tokens.
- **Open WebUI authentication** is on by default (accounts created on first run); don't disable it if more than one person can reach the machine.
- **Do not expose these services to the public internet** (e.g. via port forwarding) without a reverse proxy providing HTTPS and proper authentication — as configured here, none of the three services encrypt traffic or rate-limit requests.
- **Environment variables**, not hardcoded values, hold all configuration; `.env` is excluded from version control (add it to `.gitignore`).
- **Prompt injection:** a user can try to make the model ignore its system prompt (e.g. "ignore previous instructions"). The system prompt reduces but does not eliminate this risk — never rely on the system prompt alone to enforce hard security boundaries.
- **Sensitive data:** don't paste real confidential/personal data into the chatbot during testing unless you've reviewed your organization's policy on local LLM use.
- **Logging:** the backend logs request metadata, not full message content, to avoid accidentally persisting sensitive conversation data in logs.

## 12. Limitations
- In-memory conversation history resets on backend restart and doesn't scale across multiple backend replicas.
- No built-in RAG — the bot only knows what the base model was trained on, not your private documents.
- Small CPU-friendly models are noticeably weaker than large hosted models, especially at math and complex multi-step reasoning.
- No streaming responses in the custom backend (Open WebUI itself does stream, via its direct connection to Ollama).

## 13. Internship Learning Outcomes
By completing this project, interns will understand:
- How local LLM serving works (Ollama) versus cloud APIs.
- How a chat interface communicates with a model server over HTTP.
- How to design and test a backend API with proper input validation and error handling.
- Docker and Docker Compose fundamentals, including container networking.
- How to write and run automated tests with `pytest` and mocking.
- How to structure a basic LLM evaluation process.
- Practical security and privacy considerations for local AI tooling.

See `docs/internship_plan.md` for the full 4-week plan, deliverables, and assessment rubric.
