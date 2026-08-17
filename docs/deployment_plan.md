# Deployment Plan — Local LLM Chatbot

## 1. Deployment Target
This chatbot is designed to run on a single machine (a laptop, a desktop, or a lightweight internal server) with no cloud dependency. Recommended baseline: 8GB+ RAM, 10GB free disk, Docker installed.

## 2. Deployment Steps
1. Provision the target machine: install Docker Desktop (Windows/macOS) or Docker Engine + Compose plugin (Linux).
2. Copy the project folder to the machine (or `git clone` if version-controlled).
3. Copy `.env.example` to `.env` and set a strong, unique `WEBUI_SECRET_KEY`.
4. Run `docker compose up -d` to start Ollama, Open WebUI, and the backend.
5. Pull the chosen model: `docker exec -it ollama ollama pull llama3.2:3b`.
6. Verify health: `curl http://localhost:11434/api/tags` and the backend's `/health` endpoint.
7. Share the access URL (`http://<machine-ip>:3000`) with intended users on the same local network only.

## 3. Environment Strategy
- **Development:** run the backend outside Docker with `uvicorn --reload` for fast iteration; Ollama and Open WebUI still run via Compose.
- **Demo/staging:** full `docker compose up -d` stack, matching what reviewers will see.
- **Production (future):** would require a reverse proxy (e.g. Nginx or Caddy) providing HTTPS, real user authentication beyond Open WebUI's default, and a persistent database in place of in-memory history — flagged here as a known gap, not solved in this version.

## 4. Rollback Plan
- All state lives in named Docker volumes (`ollama-data`, `open-webui-data`). To roll back a bad change: `docker compose down`, restore the previous code/version, `docker compose up -d` — data persists across this because volumes aren't touched.
- To fully reset (e.g. corrupted state): `docker compose down -v` removes volumes and starts clean; the model will need to be re-pulled.

## 5. Monitoring in Demo/Small Deployments
- `docker compose logs -f` for live logs across all services.
- `docker stats` to watch CPU/RAM usage during a live demo — useful to show resource-awareness during presentation.
- Backend `/health` endpoint can be polled manually or via a simple uptime check script if left running unattended.

## 6. Handoff Checklist
- [ ] `.env` uses a non-default secret key (never commit real `.env` to version control).
- [ ] README, evaluation results, and troubleshooting guide are up to date with any changes made in Week 4.
- [ ] Whoever inherits this can run `docker compose up -d` from a clean checkout and have it work without undocumented manual steps.
- [ ] Known limitations (in-memory history, no RAG, no HTTPS) are explicitly stated, not left implicit.
