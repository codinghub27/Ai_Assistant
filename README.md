# AI Research Assistant

An intelligent research assistant built with Django and LangChain agents. Ask any question and the agent searches the web, reads relevant pages, and delivers a structured answer with sources.

---

## What it does

- Accepts a research question from the user
- Runs a LangChain ReAct agent with 4 tools to gather information
- Returns a structured answer with key findings and sources
- Remembers conversation history within a session (multi-turn)
- Saves all queries and answers to PostgreSQL

---

## Architecture

```
User Question
     │
     ▼
Django REST API (JWT Auth)
     │
     ▼
LangChain ReAct Agent
     │
     ├── web_search_tool    → Tavily API (current web results)
     ├── url_reader_tool    → BeautifulSoup (fetch page content)
     ├── wikipedia_tool     → Wikipedia API (factual summaries)
     └── summarizer_tool    → LLM (condense long text)
     │
     ▼
Structured Answer + Sources
     │
     ▼
Saved to PostgreSQL (Query model)
     │
     ▼
Returned as JSON + Rendered in Chat UI
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5, Django REST Framework |
| Agent | LangChain, LangChain Classic |
| LLM | Groq (llama-3.1-8b-instant) |
| Web Search | Tavily API |
| Web Scraping | BeautifulSoup4, Requests |
| Database | PostgreSQL |
| Auth | JWT (SimpleJWT) |
| API Docs | DRF Spectacular (Swagger UI) |
| Rate Limiting | django-ratelimit |
| Frontend | Django Templates, Tailwind CSS |

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/token/` | Login — get access & refresh tokens | No |
| POST | `/api/token/refresh/` | Refresh access token | No |
| POST | `/api/research/` | Ask a research question | JWT |
| GET | `/api/research/history/` | Get past queries | JWT |
| DELETE | `/api/research/delete/` | Clear session history | JWT |
| GET | `/api/docs/` | Swagger API documentation | No |

---

## Pages

| URL | Description |
|---|---|
| `/login/` | Login page |
| `/register/` | Register page |
| `/chat/` | Chat interface |
| `/history/` | Research history |
| `/` | Swagger API docs |

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-research-assistant.git
cd ai-research-assistant
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
DB_NAME=research_db
DB_USER=postgres
DB_PASSWORD=your_db_password
SECRET_KEY=your_django_secret_key
```

### 5. Setup PostgreSQL

Create a database named `research_db` in PostgreSQL, then run:

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the server

```bash
python manage.py runserver
```

Visit `http://localhost:8000/login/` to get started.

---

## Agent Tools

| Tool | Purpose |
|---|---|
| `web_search` | Searches the web using Tavily API for current information |
| `url_reader` | Fetches and extracts clean text from a URL using BeautifulSoup |
| `wikipedia_tool` | Gets Wikipedia summaries for factual/background topics |
| `summarizer_tool` | Condenses long text into structured bullet points using LLM |

---

## Key Concepts (LangGraph Ready)

This project was built to learn agent fundamentals before LangGraph:

| This Project | LangGraph Equivalent |
|---|---|
| `@tool` functions | Graph nodes |
| `AgentExecutor` loop | Graph cycle |
| LLM tool selection | Conditional edges |
| `agent_scratchpad` | State object |
| `max_iterations` | END node condition |
| DB session memory | Persistent state |

---

## Project Structure

```
research/
├── agent/
│   ├── agent.py          # AgentExecutor setup
│   ├── tools.py          # 4 LangChain tools
│   ├── models.py         # ResearchSession, Query
│   ├── views.py          # API views + template views
│   ├── urls.py           # URL routing
│   ├── serializers.py    # DRF serializers
│   └── templates/
│       └── agent/
│           ├── chat.html
│           └── history.html
├── users/
│   ├── views.py          # Register, Login, Logout
│   ├── urls.py
│   └── templates/
│       └── users/
│           ├── login.html
│           ├── register.html
│           └── base.html
├── research/
│   ├── settings.py
│   └── urls.py
├── .env                  # API keys (not committed)
├── requirements.txt
└── README.md
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key from console.groq.com |
| `TAVILY_API_KEY` | Tavily API key from app.tavily.com |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `SECRET_KEY` | Django secret key |

---

## Built by

Sravani — B.Tech AI&DS, learning LangChain agents as a bridge to LangGraph.
