from agno.vectordb.qdrant import Qdrant
from agno.vectordb.search import SearchType
import os

class QdrantManager:
    
    _instance = None
    vector_db = None
    timeout = 20

    def __new__(cls):
        """Singleton pattern to ensure only one instance of RedisManager exists."""
        if cls._instance is None:
            cls._instance = super(QdrantManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.vector_db = Qdrant(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY", None),
            search_type=SearchType.hybrid,
            timeout=self.timeout,
        )

        self._initialized = True

    def get_vector_db(self):
        """returns a Qdrant vector db instance"""
        return self.vector_db

qdrant_manager = QdrantManager()