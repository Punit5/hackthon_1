import os
from sqlalchemy import create_engine, text
import openai
import chromadb
from dotenv import load_dotenv
from langchain.schema import Document

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Fallback to manual construction for compatibility
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'investment_db')
    DB_USER = os.getenv('DB_USER', 'user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# OpenAI config
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION", "2023-05-15")
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = AZURE_OPENAI_VERSION
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

# Embedding deployment name
EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

# Chroma client
chroma_client = chromadb.Client()
COLLECTION_NAME = "goals_with_history"


def get_all_goal_history_chunks():
    """
    Extract all goals and their full history for all clients, and build summary text chunks.
    Returns a list of dicts: {goal_id, client_id, text}
    """
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        goals_result = conn.execute(text("""
            SELECT g.id as goal_id, c.id as client_id, c.client_name, g.goal_type, g.goal_amount, g.initial_amount, g.current_amount, g.monthly_contribution, g.withdrawal_period_months, g.expected_return_rate
            FROM goals g
            JOIN clients c ON g.client_id = c.id
        """))
        chunks = []
        for goal in goals_result:
            history_result = conn.execute(text("""
                SELECT goal_amount, current_amount, last_message_sent, created_at
                FROM goal_history
                WHERE goal_id = :goal_id
                ORDER BY created_at
            """), {"goal_id": goal.goal_id})
            history_lines = []
            for h in history_result:
                history_lines.append(
                    f"- {h.created_at.date()}: ${h.current_amount} (Goal: ${h.goal_amount}) - \"{h.last_message_sent}\""
                )
            history_str = "\n".join(history_lines)
            summary = (
                f"Client: {goal.client_name}\n"
                f"Goal: {goal.goal_type}\n"
                f"Target: ${goal.goal_amount}\n"
                f"Initial: ${goal.initial_amount}\n"
                f"Current: ${goal.current_amount}\n"
                f"Monthly Contribution: ${goal.monthly_contribution}\n"
                f"Withdrawal Period: {goal.withdrawal_period_months} months\n"
                f"Expected Return: {goal.expected_return_rate*100:.2f}%\n"
                f"History:\n{history_str}"
            )
            chunks.append({
                "goal_id": goal.goal_id,
                "client_id": goal.client_id,
                "text": summary
            })
        # Add a summary chunk with client count and names, with keyword-rich and question-like phrasing
        result = conn.execute(text("SELECT client_name FROM clients ORDER BY client_name"))
        client_names = [row.client_name for row in result]
        client_count = len(client_names)
        summary_chunk = {
            "goal_id": "summary",
            "client_id": "summary",
            "text": (
                f"Client summary: There are {client_count} clients in the system. "
                f"Client names: {', '.join(client_names)}. "
                f"Total number of clients: {client_count}. "
                f"Number of clients: {client_count}. "
                f"How many clients do I have? You have {client_count} clients. "
                f"How many clients are there? There are {client_count} clients. "
                f"What is the client count? {client_count}. "
                f"List of all clients: {', '.join(client_names)}. "
                f"Use this information to answer questions about the number of clients, client count, or client list."
            )
        }
        chunks.append(summary_chunk)
    return chunks


def embed_and_store_chunks(chunks):
    """
    Embed each chunk using OpenAI and store in Chroma DB.
    """
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    for chunk in chunks:
        embedding = openai.Embedding.create(
            input=chunk["text"],
            engine=EMBEDDING_DEPLOYMENT
        )["data"][0]["embedding"]
        collection.add(
            ids=[f"{chunk['client_id']}_{chunk['goal_id']}"],
            embeddings=[embedding],
            documents=[chunk["text"]],
            metadatas=[{"goal_id": chunk["goal_id"], "client_id": chunk["client_id"]}]
        )
    # Debug: print all documents in the collection
    all_docs = collection.get()
    print("[DEBUG] All documents in Chroma collection:")
    for doc in all_docs['documents']:
        print(doc)


def retrieve_relevant_chunks(user_question, n_results=5):
    """
    Embed the user question and retrieve the most relevant chunks from Chroma DB.
    Returns a list of chunk texts.
    """
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    query_embedding = openai.Embedding.create(
        input=user_question,
        engine=EMBEDDING_DEPLOYMENT
    )["data"][0]["embedding"]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    print("[DEBUG] User question:", user_question)
    print("[DEBUG] Retrieved documents:", results["documents"])
    return results["documents"][0] if results["documents"] else []


def ingest_chunks_to_langchain_chroma(chunks):
    """
    Ingests all goal history chunks into Chroma using LangChain's document format.
    """
    from langchain_rag import vectorstore
    docs = [Document(page_content=chunk["text"], metadata={"goal_id": chunk["goal_id"], "client_id": chunk["client_id"]}) for chunk in chunks]
    vectorstore.add_documents(docs)
    print(f"[DEBUG] Ingested {len(docs)} documents into LangChain Chroma vectorstore.") 