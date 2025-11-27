# from sentence_transformers import SentenceTransformer
# import numpy as np

# class DocumentEmbeddings:
#     def __init__(self, model_name="all-MiniLM-L6-v2"):
#         """
#         Initialize the embeddings model
        
#         Args:
#             model_name (str): Name of the sentence-transformers model to use
#         """
#         self.model = SentenceTransformer(model_name)
    
#     def get_embeddings(self, texts):
#         """
#         Generate embeddings for a list of text chunks
        
#         Args:
#             texts (list): List of text chunks
            
#         Returns:
#             list: List of embeddings as numpy arrays
#         """
#         if not texts:
#             return []
        
#         embeddings = self.model.encode(texts)
#         return embeddings
    
#     def similarity_search(self, query, documents, embeddings, top_k=5):
#         """
#         Find the most similar documents to a query
        
#         Args:
#             query (str): The query text
#             documents (list): List of document chunks
#             embeddings (list): List of document embeddings
#             top_k (int): Number of results to return
            
#         Returns:
#             list: List of (document, score) tuples
#         """
#         query_embedding = self.model.encode(query)
        
#         # Calculate cosine similarity
#         similarities = []
#         for i, doc_embedding in enumerate(embeddings):
#             similarity = np.dot(query_embedding, doc_embedding) / (
#                 np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
#             )
#             similarities.append((documents[i], similarity))
        
#         # Sort by similarity score (descending)
#         similarities.sort(key=lambda x: x[1], reverse=True)
        
#         return similarities[:top_k]