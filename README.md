# Pocket LM - Server

Pocket LM is a browser extension RAG (Retrieval Augmented Generation) application designed to help users capture new knowledge and interact with an AI agent powered by their private knowledge bases. This server-side application handles the core logic for content extraction, embedding, knowledge base management, and AI agent interactions.

## Features

### Knowledge Capturing
The capturing process allows users to save useful materials into their selected knowledge bases.
*   **Content Extraction:** Supports extracting content from:
    *   Text selections (handled by the browser extension).
    *   Web URLs.
    *   PDF data files.
*   **Embedding and Storage:** Utilizes an embedding model to create vector representations of captured content, which are then saved into a selected PGVector knowledge base.
*   **Knowledge Base Management:** Provides functionality to create new knowledge bases.

### AI Agent Chat
Interact with an AI agent that has access to your private knowledge bases.
*   **New Chat Creation:** Initiate new conversational threads with the agent.
*   **Long-Term Memory:** Save relevant information to the agent's long-term memory.
*   **Multi-Turn Invocations:** Handle complex, multi-turn conversations.
*   **Context Window Management:** Efficiently manage the conversational context.
*   **Retrieval Tools:** Create and utilize specialized tools for the agent to retrieve information from knowledge bases.

## Technologies Used

*   **Agent Framework:** LangGraph
*   **Vector Database:** PGVector
*   **Content Extraction:** crawl4ai

## Building and Running

To run the server, execute the following command in your terminal:

```bash
python main.py
```

**TODO:** Add instructions for installing dependencies once they are added to the `pyproject.toml` file.

## Development Conventions

*   This project uses the standard Python project structure.
*   Dependencies are managed using the `pyproject.toml` file.
*   The main entry point of the application is `main.py`.