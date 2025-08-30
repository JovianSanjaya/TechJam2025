"""
API configuration and constants
"""

import os
from pathlib import Path


def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())


# Load environment variables
load_env_file()


class APIConfig:
    """API configuration"""
    # OpenRouter API
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-4-maverick:free")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # Request settings
    TIMEOUT = 30
    MAX_RETRIES = 3


class AnalysisConfig:
    """Analysis configuration"""
    # Processing settings
    RELEVANCE_THRESHOLD = 0.5
    MAX_STATUTES_PER_FEATURE = 10
    BATCH_SIZE = 5
    MAX_PATTERNS = 20
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.5
    

class VectorConfig:
    """Vector store configuration"""
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    VECTOR_DB_PATH = "./chroma_db"
    COLLECTION_NAME = "legal_documents"
    

class ComplianceConfig:
    """Legacy config class for backward compatibility"""
    # Delegate to new config classes
    OPENROUTER_API_KEY = APIConfig.OPENROUTER_API_KEY
    OPENROUTER_MODEL = APIConfig.OPENROUTER_MODEL
    RELEVANCE_THRESHOLD = AnalysisConfig.RELEVANCE_THRESHOLD
    MAX_STATUTES_PER_FEATURE = AnalysisConfig.MAX_STATUTES_PER_FEATURE
    BATCH_SIZE = AnalysisConfig.BATCH_SIZE
    EMBEDDING_MODEL = VectorConfig.EMBEDDING_MODEL
    VECTOR_DB_PATH = VectorConfig.VECTOR_DB_PATH
    
    # Geographic regions
    US_STATES = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
        "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
        "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
        "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
        "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
        "New Hampshire", "New Jersey", "New Mexico", "New York",
        "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
        "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
        "West Virginia", "Wisconsin", "Wyoming"
    ]
    
    # Compliance topics
    COMPLIANCE_TOPICS = [
        "data_collection", "privacy", "age_verification", "parental_consent",
        "user_tracking", "geolocation", "personal_data", "youth_protection"
    ]
