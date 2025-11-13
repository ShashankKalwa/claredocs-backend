from .chunking import chunk_text
import re

def _tokenize(text: str):
    """
    Simple tokenizer: lowercase and split on non-alphanumeric.
    """
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]

class DocumentRetriever:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        """
        Initialize the document retriever
        
        Args:
            chunk_size (int): Size of text chunks
            chunk_overlap (int): Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, document_text):
        """
        Process a document for retrieval
        
        Args:
            document_text (str): The document text
            
        Returns:
            list: chunks
        """
        # Chunk the document
        chunks = chunk_text(document_text, self.chunk_size, self.chunk_overlap)
        return chunks
    
    def retrieve_relevant_chunks(self, query, chunks, top_k=5):
        """
        Retrieve the most relevant chunks for a query
        
        Args:
            query (str): The query text
            chunks (list): List of document chunks
            top_k (int): Number of results to return
            
        Returns:
            list: List of relevant document chunks with scores
        """
        query_tokens = set(_tokenize(query))
        scored = []
        for idx, ch in enumerate(chunks):
            ch_tokens = set(_tokenize(ch))
            # Simple relevance score: token overlap count
            score = len(query_tokens & ch_tokens)
            if score > 0:
                scored.append({"index": idx, "chunk": ch, "score": score})
        # Sort by score desc, then index asc for stability
        scored.sort(key=lambda x: (-x["score"], x["index"]))
        return scored[:top_k]