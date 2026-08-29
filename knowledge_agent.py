import os
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from dotenv import load_dotenv

load_dotenv()

# Initialize embeddings (you can replace with Groq embeddings if needed)
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Directory where FAISS index is persisted
FAISS_INDEX_DIR = os.path.abspath("faiss_index")

class KnowledgeAgent:
    def __init__(self):
        if os.path.isdir(FAISS_INDEX_DIR):
            self.vectorstore = FAISS.load_local(FAISS_INDEX_DIR, embeddings)
        else:
            self.vectorstore = FAISS.from_documents([], embeddings)

    def add_documents(self, docs: list[Document]):
        """Add documents to the store and persist the index."""
        self.vectorstore.add_documents(docs)
        self.vectorstore.save_local(FAISS_INDEX_DIR)

    def search(self, query: str, k: int = 3) -> str:
        """Return top‑k snippets concatenated for prompt use."""
        results = self.vectorstore.similarity_search(query, k=k)
        if not results:
            return ""
        return "\n\n---\n\n".join([doc.page_content for doc in results])

# Global instance for easy import
knowledge_agent = KnowledgeAgent()

def search_knowledge(query: str, k: int = 3) -> str:
    """Helper used by the orchestrator."""
    return knowledge_agent.search(query, k)
