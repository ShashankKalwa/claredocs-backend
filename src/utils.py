import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env.local only
env_path = os.path.join(os.path.dirname(__file__), "..", ".env.local")
load_dotenv(env_path)

def get_env_variable(key, default=None):
    """
    Get environment variable or return default value
    """
    value = os.environ.get(key, default)
    if value is None:
        raise EnvironmentError(f"Missing environment variable: {key}")
    return value

def validate_file_extension(filename):
    """
    Validate if the file has a PDF extension
    """
    return filename.lower().endswith('.pdf')

def create_response(status, message, data=None):
    """
    Create a standardized API response
    """
    response = {
        "status": status,
        "message": message
    }
    
    if data:
        response["data"] = data
        
    return response
