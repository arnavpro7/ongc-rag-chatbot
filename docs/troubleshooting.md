# Troubleshooting Guide

Each entry: **Symptom → Likely cause → Fix**

### 1. `ollama: command not found`
**Cause:** Ollama isn't installed, or isn't on your PATH.
**Fix:**
- macOS/Linux: reinstall with `curl -fsSL https://ollama.com/install.sh | sh`, then open a new terminal.
- Windows: install from https://ollama.com/download, then restart your terminal (installer adds it to PATH automatically).
- Verify with `ollama --version`.

### 2. Model download fails / hangs
**Cause:** Network interruption, low disk space, or a firewall/proxy blocking the download.
**Fix:**
- Check free disk space (`df -h` on Linux/macOS, or File Explorer on Windows) — models need several GB.
- Retry: `ollama pull <model-name>` (downloads resume partially).
- If behind a corporate proxy, set `HTTPS_PROXY`/`HTTP_PROXY` environment variables before pulling.

### 3. Port `11434` already in use
**Cause:** Another Ollama instance (or another app) is already bound to that port.
**Fix:**
- Find what's using it: `lsof -i :11434` (macOS/Linux) or `netstat -ano | findstr 11434` (Windows).
- Stop the conflicting process, or if it's Ollama already running, you likely don't need to start it again.
- To run Ollama on a different port: set `OLLAMA_HOST=0.0.0.0:11435` before starting it, and update `OLLAMA_BASE_URL` everywhere accordingly.

### 4. Port `3000` already in use
**Cause:** Another service is using port 3000.
**Fix:**
- Change the host-side port mapping in `docker-compose.yml`, e.g. `"3001:8080"` instead of `"3000:8080"`, then access Open WebUI at `http://localhost:3001`.

### 5. Open WebUI cannot connect to Ollama
**Cause:** Wrong `OLLAMA_BASE_URL`, or Ollama isn't actually running.
**Fix:**
- If both run in Docker Compose (as in this project): the URL must be `http://ollama:11434` (the service name), not `localhost`.
- If Ollama runs on the host and Open WebUI runs in Docker: use `http://host.docker.internal:11434` (Windows/macOS). On Linux, you may need to add `extra_hosts: ["host.docker.internal:host-gateway"]` to the service in `docker-compose.yml`.
- Confirm Ollama is actually up: `curl http://localhost:11434/api/tags`.

### 6. Docker container exits unexpectedly
**Cause:** Often a crash on startup — bad environment variable, missing dependency, or out-of-memory kill.
**Fix:**
- Check logs immediately: `docker compose logs <service-name>`.
- Check exit code: `docker compose ps -a` (code 137 usually means it was killed for using too much memory).
- Try running it in the foreground to see the full error: `docker compose up <service-name>` (no `-d`).

### 7. Slow responses
**Cause:** Model too large for available CPU/RAM, or no GPU acceleration.
**Fix:**
- Switch to a smaller model (see model recommendations — e.g. `qwen2.5:1.5b` or `llama3.2:1b`).
- Close other heavy applications while testing.
- Reduce `MAX_HISTORY_MESSAGES` in `.env` so less context is sent per request.
- If you have a supported NVIDIA GPU, enable the GPU section in `docker-compose.yml`.

### 8. Out-of-memory errors
**Cause:** The chosen model's RAM requirement exceeds what your machine has free.
**Fix:**
- Check the model's minimum RAM requirement (see Model Selection section) and compare to your machine's total RAM.
- Pick a smaller/more quantized model.
- Close other applications, or increase Docker Desktop's memory allocation (Docker Desktop → Settings → Resources).

### 9. Incorrect `localhost` configuration inside Docker
**Cause:** Inside a container, `localhost` refers to the container itself, not your host machine or sibling containers — a very common beginner mistake.
**Fix:**
- Container-to-container (same compose file): use the **service name** (e.g. `http://ollama:11434`).
- Container-to-host: use `http://host.docker.internal:11434`.
- Never use `http://localhost:11434` from inside a container expecting to reach something outside it.

### 10. Model not appearing in Open WebUI
**Cause:** The model hasn't finished downloading, or Open WebUI hasn't refreshed its model list, or it's looking at the wrong Ollama instance.
**Fix:**
- Confirm it's actually pulled: `ollama list` (or `docker exec ollama ollama list` if Ollama runs in Docker).
- Refresh the model dropdown in Open WebUI (Settings → Models), or restart the Open WebUI container.
- Double-check `OLLAMA_BASE_URL` as in item 5 above.
