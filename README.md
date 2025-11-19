# Pocket LM - Server

Pocket LM is a browser extension RAG (Retrieval Augmented Generation) application designed to help users capture new knowledge and interact with an AI agent powered by their private knowledge bases. This server-side application handles the core logic for content extraction, embedding, knowledge base management, and AI agent interactions.

## Features

### Knowledge Capturing
The capturing process allows users to save useful materials into their selected knowledge bases.
*   **Content Extraction:** Supports extracting content from:
    *   Text selections (handled by the browser extension)
    *   Web URLs
    *   PDF data files
*   **Embedding and Storage:** Utilizes embedding models (Ollama or Google Gemini) to create vector representations of captured content, which are saved into a PGVector knowledge base
*   **Knowledge Base Management:** Provides functionality to create, list, and delete knowledge bases (collections)

### AI Agent Chat
Interact with an AI agent that has access to your private knowledge bases.
*   **New Chat Creation:** Initiate new conversational threads with the agent
*   **Long-Term Memory:** Save relevant information to the agent's long-term memory using Mem0
*   **Multi-Turn Invocations:** Handle complex, multi-turn conversations with context management
*   **Retrieval Tools:** Specialized tools for the agent to retrieve information from knowledge bases
*   **Chat History:** View and manage conversation history
*   **Re-ranking:** Uses Cohere for re-ranking search results to improve retrieval accuracy

### API Endpoints
*   **Health Check:** `GET /health` - Service health monitoring
*   **Capture:** `POST /api/v1/capture` - Capture content from URL, selection, or PDF
*   **Collections:** `GET/POST/DELETE /api/v1/collection` - Manage knowledge bases
*   **Chat:** `POST /api/v1/chat/message` - Send messages to the AI agent
*   **Chat History:** `GET /api/v1/chat/history` - Retrieve conversation history
*   **Clear Chat:** `DELETE /api/v1/chat/clear` - Clear chat history

## Technologies Used

*   **Web Framework:** FastAPI with Uvicorn
*   **Agent Framework:** LangGraph (v1.0.3) with checkpoint support
*   **Vector Database:** PostgreSQL with PGVector extension
*   **Content Extraction:** Crawl4AI (v0.7.6) with Playwright
*   **LLM Providers:**
    *   Ollama (local models)
    *   Google Gemini (via LangChain)
    *   LiteLLM for unified interface
*   **Embeddings:** Ollama or Google Gemini
*   **Memory Management:** Mem0AI (v1.0.1+)
*   **Re-ranking:** Cohere (v5.20.0+)
*   **PDF Processing:** LangChain PyMuPDF4LLM
*   **Database ORM:** SQLAlchemy with asyncpg
*   **Tracing:** LangSmith (optional)

## Project Structure

```
server/
├── src/
│   ├── apis/              # API business logic
│   │   ├── capture.py     # Content capture logic
│   │   ├── collection.py  # Collection management
│   │   └── chat.py        # Chat functionality
│   ├── configs/           # Configuration modules
│   │   ├── settings.py    # Application settings
│   │   ├── crawler.py     # Crawl4AI configuration
│   │   ├── cohere.py      # Cohere setup
│   │   ├── memzero.py     # Mem0 configuration
│   │   └── glob_ctx.py    # Global context
│   ├── db/                # Database layer
│   │   ├── session.py     # Database session management
│   │   └── vectorstore.py # Vector store operations
│   ├── middlewares/       # FastAPI middlewares
│   ├── routers/           # API route definitions
│   │   ├── entry.py       # Main router
│   │   ├── capture.py     # Capture endpoints
│   │   ├── collection.py  # Collection endpoints
│   │   └── chat.py        # Chat endpoints
│   ├── schemas/           # Pydantic models
│   │   ├── capture.py     # Capture schemas
│   │   ├── response.py    # Response models
│   │   └── langgraph.py   # LangGraph schemas
│   ├── utils/             # Utility functions
│   │   ├── logging.py     # Logging configuration
│   │   ├── response_builder.py
│   │   └── langgraph/     # LangGraph utilities
│   │       ├── agent.py   # Agent definition
│   │       ├── config.py  # Agent configuration
│   │       ├── nodes.py   # Graph nodes
│   │       ├── runner.py  # Agent runner
│   │       └── tools.py   # Agent tools
│   └── main.py            # Application entry point
├── docs/                  # Documentation
│   ├── api.md            # API documentation
│   ├── architecture.png  # Architecture diagram
│   └── agent_graph.png   # Agent graph visualization
├── test/                 # Test files
├── pyproject.toml        # Project dependencies
├── requirements.txt      # Generated requirements
├── uv.lock              # Lock file for uv package manager
├── .env.example         # Environment variables template
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
└── README.md            # This file
```

## Prerequisites

*   Python 3.13 or higher
*   PostgreSQL with PGVector extension
*   Ollama (optional, for local embeddings/LLM) or Google Gemini API key
*   Mem0 API key
*   Cohere API key (for re-ranking)

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd server
```

### 2. Install Dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Or using uv (recommended):
```bash
uv sync
```

### 3. Set Up PostgreSQL with PGVector

Ensure you have PostgreSQL installed with the PGVector extension enabled.

```sql
CREATE DATABASE pocketlm;
\c pocketlm
CREATE EXTENSION vector;
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your configuration:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Application configuration
ENVIRONMENT=development
NAME=PocketLM Server
VERSION=0.1.0
API_PREFIX=/api/v1

# LangSmith configuration (optional)
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=pocketlm

# PostgreSQL/PGVector configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/pocketlm

# Ollama configuration (if using local models)
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=llama3.2

# PGVector table names
COLLECTIONS_TABLE=langchain_pg_collection
EMBEDDINGS_TABLE=langchain_pg_embedding

# PocketLM default settings
DEFAULT_COLLECTION_NAME=default
DEFAULT_USER_ID=default_user
DEFAULT_SESSION_ID=default_session

# Google GenAI configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
GEMINI_LLM_MODEL=gemini-2.0-flash-exp
GEMINI_EMBEDDING_DIMS=768

# Mem0 configuration
MEM0_API_KEY=your_mem0_api_key
MEM0_RERANKER_MODEL=your_reranker_model

# Cohere configuration
COHERE_API_KEY=your_cohere_api_key
COHERE_RERANKING_MODEL=rerank-v3.5
```

## Running the Server

### Development Mode

Run the server with auto-reload enabled:

```bash
python src/main.py
```

Or using uvicorn directly:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
docker-compose up
```

The server will start on `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

*   **Interactive API Documentation (Swagger UI):** `http://localhost:8000/docs`
*   **Alternative API Documentation (ReDoc):** `http://localhost:8000/redoc`
*   **Detailed API Reference:** See [docs/api.md](docs/api.md)
*   **Architecture Diagram:** See [docs/architecture.png](docs/architecture.png)
*   **Agent Graph:** See [docs/agent_graph.png](docs/agent_graph.png)

## Development

### Project Conventions

*   Uses standard Python project structure with `src/` layout
*   Dependencies managed via `pyproject.toml`
*   Type hints and Pydantic models for data validation
*   FastAPI for RESTful API development
*   Async/await patterns throughout
*   Structured logging with custom logger

### Key Dependencies

*   **fastapi[standard]==0.121.1** - Web framework
*   **langchain>=1.0.7** - LLM framework
*   **langgraph==1.0.3** - Agent framework
*   **crawl4ai==0.7.6** - Web content extraction
*   **pgvector==0.3.6** - Vector similarity search
*   **mem0ai>=1.0.1** - Long-term memory management
*   **cohere>=5.20.0** - Re-ranking
*   **google-genai>=1.50.1** - Google Gemini integration
*   **pydantic==2.12.4** - Data validation
*   **sqlalchemy==2.0.44** - Database ORM
*   **asyncpg==0.30.0** - Async PostgreSQL driver

### Testing

```bash
pytest test/
```

## License

See [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.