# Internship Plan — Local LLM Chatbot Project

## 4-Week Learning Plan

### Week 1 — Foundations & Setup
**Goal:** Get a working local chatbot running end-to-end.
- Day 1–2: Install Ollama, pull a small model, chat with it via the CLI (`ollama run <model>`).
- Day 3: Install Docker Desktop, run Open WebUI against local Ollama, confirm chat works in the browser.
- Day 4: Read through `docker-compose.yml`, understand each service and why the network/volumes exist.
- Day 5: Mentor checkpoint — demo a working chat session; discuss how Open WebUI talks to Ollama.

### Week 2 — Backend Development
**Goal:** Understand and extend the FastAPI backend.
- Day 1–2: Read `main.py` and `schemas.py` line by line; run the backend locally with `uvicorn`.
- Day 3: Use `/docs` (Swagger UI) to manually test `/chat`, `/health`, `/conversations/{id}`.
- Day 4: Modify the system prompt and observe behavior change; add one new field to a schema.
- Day 5: Mentor checkpoint — walk through a request end-to-end (client → backend → Ollama → back).

### Week 3 — Testing & Evaluation
**Goal:** Verify correctness and robustness.
- Day 1–2: Run the pytest suite, understand each test, add 2 new tests of your own (e.g. a new edge case).
- Day 3: Run the 10-question evaluation dataset (`docs/evaluation.md`), score results with the rubric.
- Day 4: Deliberately break things (stop Ollama, use a huge message, bad JSON) and confirm errors are handled gracefully.
- Day 5: Mentor checkpoint — present test results and evaluation scores.

### Week 4 — Polish, Security & Presentation
**Goal:** Finalize documentation, harden security, and prepare the demo.
- Day 1: Review the security section; change all default secrets; confirm the app isn't exposed to the internet.
- Day 2: Finish README and internal documentation.
- Day 3: Rehearse the demo and prepare answers to viva questions.
- Day 4: Final full run-through with a clean environment (`docker compose down -v && docker compose up -d`).
- Day 5: Final presentation and demo to mentor/team.

## Final Demo Checklist
- [ ] `docker compose up -d` starts all services without errors.
- [ ] Open WebUI loads at `http://localhost:3000` and lists the configured model.
- [ ] A multi-turn conversation works and remembers earlier context.
- [ ] Backend `/health` reports both backend and Ollama as healthy.
- [ ] At least one deliberate error case (e.g. Ollama stopped) is demoed with a graceful error message.
- [ ] Test suite passes (`pytest`).
- [ ] `.env` uses a non-default `WEBUI_SECRET_KEY`.
- [ ] README is complete and accurate.

## Final Report Structure
1. Title page
2. Problem statement & objective
3. Architecture overview (with diagram)
4. Implementation details (backend, Docker, configuration)
5. Testing approach and results
6. Evaluation results (scores against the rubric)
7. Challenges faced and how they were resolved
8. Security & privacy considerations
9. Limitations
10. Future enhancements
11. Conclusion & learning outcomes
12. Appendix: full source code / repo link

## Presentation Structure (10–15 min)
1. Problem & motivation (1–2 min)
2. Live architecture walkthrough (2–3 min)
3. Live demo — normal chat + one error scenario (4–5 min)
4. Testing & evaluation results (2–3 min)
5. Challenges & learnings (1–2 min)
6. Q&A

## Viva / Interview Questions & Answers

**Q: Why use Ollama instead of calling a cloud LLM API?**
A: Ollama runs models entirely on local hardware, so no data leaves the machine, there's no API cost, and it works offline — important for privacy-sensitive or budget-constrained use cases. The trade-off is lower raw model quality/speed compared to large hosted models.

**Q: Why does Open WebUI need to reach Ollama at `http://ollama:11434` instead of `localhost`?**
A: Inside Docker, each container has its own network namespace. `localhost` inside a container refers to that container itself, not the host or other containers. Docker Compose gives containers a shared network where they can reach each other by service name instead.

**Q: What happens if Ollama is down when a user sends a chat message?**
A: The backend's `httpx` call raises a `ConnectError`, which is caught and turned into an HTTP 503 response with a clear message, instead of the request hanging or crashing the server.

**Q: Why keep conversation history server-side instead of just in the browser?**
A: It lets any client (browser, script, another service) continue the same conversation consistently, and it's a required building block for more advanced features like logging or multi-user support later. The trade-off here is that this simple in-memory version resets on restart and doesn't scale across multiple backend instances — a real deployment would use a database like Redis.

**Q: How would you prevent this chatbot from being misused if exposed publicly?**
A: Don't expose it publicly without authentication and HTTPS in front of it; enable Open WebUI's built-in auth; change all default secrets; rate-limit requests; and keep an eye on prompt-injection attempts (a user trying to make the bot ignore its system prompt).

**Q: What's the difference between the model and Open WebUI?**
A: The model (run by Ollama) is the actual neural network that generates text. Open WebUI is just the interface layer — it renders chat history, handles user accounts, and forwards messages to Ollama's API. Swapping models doesn't require changing Open WebUI at all.

## Assessment Rubric

| Area | Weight | 5 (Excellent) | 3 (Adequate) | 1 (Needs work) |
|---|---|---|---|---|
| Working deployment | 25% | Full stack runs cleanly from a fresh clone | Runs with minor manual fixes | Doesn't run without significant help |
| Code understanding | 20% | Can explain any line of `main.py` and why it exists | General understanding, some gaps | Cannot explain core logic |
| Testing rigor | 15% | All tests pass, added meaningful new tests | Tests pass, no additions | Tests fail or weren't run |
| Evaluation quality | 15% | Thorough, honest scoring with clear notes | Evaluation completed but shallow | Evaluation missing or superficial |
| Security awareness | 10% | Secrets changed, exposure risks clearly explained | Partial awareness | Default secrets left in place |
| Documentation | 10% | Clear, complete, professional README | Present but incomplete | Missing or very thin |
| Presentation | 5% | Confident, clear, answers questions well | Adequate | Unprepared |
