import os
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

load_dotenv()

# Set up embeddings and vector store
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
    persist_directory="./chroma_db"  # optional, for persistence
)

# Set up the conversational retrieval chain
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

def langchain_ai_chat(messages):
    # Extract chat history and latest question
    chat_history = []
    for m in messages[:-1]:
        if m["role"] == "user":
            chat_history.append((m["role"], m["content"]))
        elif m["role"] == "assistant":
            chat_history.append((m["role"], m["content"]))
    # Prepend system message to encourage name memory and personalization
    system_message = ("system", "You are a helpful financial assistant for Puneet. Always try to personalize your answers.")
    chat_history = [system_message] + chat_history
    print("[DEBUG] Chat history sent to LangChain:", chat_history)
    question = messages[-1]["content"]
    result = qa_chain({"question": question, "chat_history": chat_history})
    return result["answer"], result.get("source_documents", []) 