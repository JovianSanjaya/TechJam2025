"""
Configuration module for TikTok Compliance Analyzer.

This module provides centralized configuration management for the compliance
analysis system, including API settings, processing parameters, cache
configuration, and regional filtering options.

All configuration values can be overridden via environment variables or
a local .env file for secure API key management.
"""
import os
from pathlib import Path

# Load environment variables from .env file if it exists
def load_env_file():
    """
    Load environment variables from .env file if present.
    
    Reads key=value pairs from .env file and sets them as environment
    variables if not already defined. Supports comments with # prefix.
    """
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env_file()

class ComplianceConfig:
    """
    Configuration class for TikTok compliance analysis system.
    
    Contains all configuration parameters including API credentials,
    processing thresholds, cache settings, and regional filtering options.
    Values can be overridden via environment variables for deployment.
    """
    # API Configuration - read from environment or .env; default to empty (disabled)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "moonshotai/kimi-k2:free")  # Free model
    
    # Processing Configuration
    RELEVANCE_THRESHOLD = 0.5
    MAX_STATUTES_PER_FEATURE = 10
    BATCH_SIZE = 5
    
    # Cache Configuration
    ENABLE_CACHE = True
    CACHE_EXPIRY_DAYS = 30
    
    # Vector Store Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    VECTOR_DB_PATH = "./chroma_db"
    
    # Geographic regions for filtering
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
    
    # Key compliance topics
    COMPLIANCE_TOPICS = [
        "minors", "children", "age verification", "social media", "privacy",
        "data protection", "parental consent", "COPPA", "curfew", "addiction",
        "content moderation", "algorithmic transparency", "targeted advertising"
    ]
