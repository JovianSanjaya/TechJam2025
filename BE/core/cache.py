import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class ComplianceCache:
    def __init__(self, cache_file="compliance_cache.pkl", expiry_days=30):
        self.cache_file = cache_file
        self.expiry_days = expiry_days
        self.cache = self.load_cache()
    
    def load_cache(self) -> Dict:
        """Load cache from file"""
        try:
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}
    
    def save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
    
    def _generate_hash(self, text: str) -> str:
        """Generate hash for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get_cached_result(self, feature_description: str, statute_content: str) -> Optional[Dict]:
        """Get cached result if available and not expired"""
        feature_hash = self._generate_hash(feature_description)
        statute_hash = self._generate_hash(statute_content)
        cache_key = f"{feature_hash}_{statute_hash}"
        
        cached_item = self.cache.get(cache_key)
        if cached_item:
            # Check if not expired
            if datetime.now() - cached_item['timestamp'] < timedelta(days=self.expiry_days):
                return cached_item['result']
            else:
                # Remove expired entry
                del self.cache[cache_key]
        
        return None
    
    def cache_result(self, feature_description: str, statute_content: str, result: Any):
        """Cache a result"""
        feature_hash = self._generate_hash(feature_description)
        statute_hash = self._generate_hash(statute_content)
        cache_key = f"{feature_hash}_{statute_hash}"
        
        self.cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        self.save_cache()
    
    def clear_expired(self):
        """Remove all expired entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, item in self.cache.items():
            if current_time - item['timestamp'] > timedelta(days=self.expiry_days):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.save_cache()
            print(f"Cleared {len(expired_keys)} expired cache entries")
