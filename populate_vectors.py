from rag_utils import get_all_goal_history_chunks, ingest_chunks_to_langchain_chroma

if __name__ == "__main__":
    print("Extracting all goal history chunks...")
    chunks = get_all_goal_history_chunks()
    print(f"Found {len(chunks)} chunks. Ingesting into LangChain Chroma...")
    ingest_chunks_to_langchain_chroma(chunks)
    print("LangChain Chroma vector DB populated successfully.") 