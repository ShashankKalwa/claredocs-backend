from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    """
    Split text into manageable chunks for processing
    
    Args:
        text (str): The text to be chunked
        chunk_size (int): The size of each chunk
        chunk_overlap (int): The overlap between chunks
        
    Returns:
        list: List of text chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    return chunks