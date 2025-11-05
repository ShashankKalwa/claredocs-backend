from .embeddings import DocumentEmbeddings
from .chunking import chunk_text

class DocumentRetriever:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        """
        Initialize the document retriever
        
        Args:
            chunk_size (int): Size of text chunks
            chunk_overlap (int): Overlap between chunks
        """
        self.embeddings_model = DocumentEmbeddings()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, document_text):
        """
        Process a document for retrieval
        
        Args:
            document_text (str): The document text
            
        Returns:
            tuple: (chunks, embeddings)
        """
        # Chunk the document
        chunks = chunk_text(document_text, self.chunk_size, self.chunk_overlap)
        
        # Generate embeddings
        embeddings = self.embeddings_model.get_embeddings(chunks)
        
        return chunks, embeddings
    
    def retrieve_relevant_chunks(self, query, chunks, embeddings, top_k=5):
        """
        Retrieve the most relevant chunks for a query
        
        Args:
            query (str): The query text
            chunks (list): List of document chunks
            embeddings (list): List of document embeddings
            top_k (int): Number of results to return
            
        Returns:
            list: List of relevant document chunks with scores
        """
        results = self.embeddings_model.similarity_search(query, chunks, embeddings, top_k)
        return results