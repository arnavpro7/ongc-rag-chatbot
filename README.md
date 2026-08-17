# 🛢️ ONGC RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built using Ollama, Open WebUI, ChromaDB, and Docker. The chatbot answers questions based on ONGC's Annual Reports (FY 2021-22 and FY 2023-24) using semantic search and a local Large Language Model.

## Features

- Chat with ONGC's Annual Reports (multiple years)
- Semantic search using vector embeddings
- ChromaDB vector database (built into Open WebUI)
- Local LLM (Llama 3.2 via Ollama)
- Conversation memory
- Follow-up question support
- Open WebUI chat interface
- Source citations shown alongside AI responses
- Prevents hallucinations by answering only from retrieved context
- Fully containerized with Docker Compose
- Optional custom FastAPI backend

## Tech Stack

- Python
- Ollama
- Llama 3.2
- ChromaDB
- Open WebUI
- Docker / Docker Compose
- FastAPI

## Project Structure
ongc-rag-chatbot/
│
├── docker-compose.yml
├── start.bat
├── stop.bat
├── README.md
├── .env.example
│
├── backend/
│ ├── main.py
│ ├── schemas.py
│ ├── requirements.txt
│ └── Dockerfile
│
├── tests/
│ └── test_backend.py
│
└── docs/
├── evaluation.md
├── troubleshooting.md
├── system_prompt.md
└── deployment_plan.md


## Installation

**Clone the repository**

git clone https://github.com/arnavpro7/ongc-rag-chatbot.git
cd ongc-rag-chatbot


**Set up environment variables**

cp .env.example .env


**Install Docker Desktop**

https://www.docker.com/products/docker-desktop

**Start the application**

docker compose up -d


**Pull the required model**

docker exec -it ollama ollama pull llama3.2:3b


**Open the chatbot**

http://localhost:3000

## Workflow
PDF (Annual Report)
   |
   v
Document Upload (Open WebUI Knowledge Base)
   |
   v
Text Chunking
   |
   v
Embeddings
   |
   v
ChromaDB
   |
   v
Retriever
   |
   v
Llama 3.2 (Ollama)
   |
   v
Answer with Citation



## Example Questions

- What is ONGC's core business?
- Who is ONGC's Chairman?
- What was ONGC's net profit in FY 2023-24?
- How did ONGC's performance compare between FY 2021-22 and FY 2023-24?
- What are ONGC's sustainability goals?

## Future Improvements

- Multiple domain support
- Source citations with similarity scores
- Streaming responses
- Export chat history
- GPU acceleration
- Persistent backend conversation history


## Screenshots ![Grounded answer with citation](screenshots/01-grounded-answer-citation.png) ![Multi-turn conversation](screenshots/02-multi-turn-conversation.png) ![Context blending example](screenshots/03-context-blending-example.png) ![Model overview](screenshots/04-model-overview.png)

## Author

Arnav Choudhary





