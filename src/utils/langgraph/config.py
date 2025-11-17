from langchain_google_genai import ChatGoogleGenerativeAI
from src.configs.settings import settings

llm = ChatGoogleGenerativeAI(
    google_api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_LLM_MODEL
)

MESSAGE_LIMIT = 20  # Trigger summarization after this many messages
MESSAGES_TO_KEEP = 5  # Keep this many recent messages after summarization

SYSTEM_PROMPT = """You are a Retrieval-Augmented Generation (RAG) assistant with access to two types of information:

1. **retrieve_docs**: Search through document context/knowledge base for factual information, procedures, or specific content.
2. **retrieve_memory**: Recall personal information, preferences, or past conversation details about the user.

Choose the appropriate tool(s) based on the query:
- For factual/document queries: use retrieve_docs
- For personal/user-specific queries: use retrieve_memory  
- For queries needing both: call both tools

After retrieving context, answer the user's question using the provided information.

Rules:
- Never assume information not present in the provided context
- Prefer quotes, paraphrases, or summaries from the retrieved context
- If no relevant information is found, acknowledge this clearly
- Keep answers clear, structured, and concise"""

SUMMARY_PROMPT = """Previous conversation summary: {summary}

Please create a concise summary of the following conversation messages:
{messages}

Provide a brief summary that captures the key points and context."""

GENERATE_PROMPT = """Using the following context:
{context}

Conversation summary: {summary}

Recent messages:
{messages}

Generate a comprehensive response to the user's latest query."""
