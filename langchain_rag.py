import os
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

load_dotenv()

rag_available = True
embeddings = None
vectorstore = None
llm = None
qa_chain = None

try:
    embeddings = OpenAIEmbeddings(
        deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        openai_api_type="azure",
        openai_api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_VERSION", "2023-05-15"),
    )

    vectorstore = Chroma(
        collection_name="goals_with_history",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

    llm = AzureChatOpenAI(
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        openai_api_type="azure",
        openai_api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_VERSION", "2023-05-15"),
        temperature=0.0,
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        vectorstore.as_retriever(search_kwargs={"k": 7}),
        return_source_documents=True
    )
except Exception as e:
    rag_available = False
    print(f"[ERROR] Failed to initialize RAG pipeline: {e}")

def langchain_ai_chat(messages):
    if not rag_available:
        return (
            "Sorry, retrieval-augmented answers are temporarily unavailable. Please try again later or contact support.",
            []
        )
    chat_history = []
    for m in messages[:-1]:
        if m["role"] == "user":
            chat_history.append((m["role"], m["content"]))
        elif m["role"] == "assistant":
            chat_history.append((m["role"], m["content"]))
    system_message = (
        "system",
        "You are an Advisor AI Assistant. Only answer questions related to finance, financial goals, savings, or client progress. For other topics, politely decline."
    )
    chat_history = [system_message] + chat_history
    print("[DEBUG] Chat history sent to LangChain:", chat_history)
    question = messages[-1]["content"]
    result = qa_chain({"question": question, "chat_history": chat_history})
    return result["answer"], result.get("source_documents", []) 