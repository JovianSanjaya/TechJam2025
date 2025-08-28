import re
from typing import Dict, List
from config import ComplianceConfig

class TikTokJargonResolver:
    """Resolve TikTok-specific abbreviations and codenames"""
    
    def __init__(self):
        self.jargon_map = {
            # Common TikTok/social media abbreviations
            "ASL": "Age/Sex/Location verification system",
            "GH": "Geohashing/Geographic Hashing",
            "PF": "Personalized Feed",
            "NR": "Network Restrictions",
            "KR": "Korea (South Korea)",
            "PRD": "Product Requirements Document",
            "TRD": "Technical Requirements Document",
            "GDPR": "General Data Protection Regulation",
            "CCPA": "California Consumer Privacy Act",
            "COPPA": "Children's Online Privacy Protection Act",
            "DSA": "Digital Services Act",
            "SB976": "California Senate Bill 976",
            "FTC": "Federal Trade Commission",
            "CARU": "Children's Advertising Review Unit",
            "FERPA": "Family Educational Rights and Privacy Act",
            # TikTok specific terms
            "FYP": "For You Page",
            "UA": "User Acquisition",
            "UGC": "User Generated Content",
            "RTB": "Real-Time Bidding",
            "SDK": "Software Development Kit",
            "API": "Application Programming Interface",
            "ML": "Machine Learning",
            "AI": "Artificial Intelligence",
            "KYC": "Know Your Customer",
            "2FA": "Two-Factor Authentication",
            "SSO": "Single Sign-On",
            "CDN": "Content Delivery Network",
        }
        
        self.compliance_patterns = {
            "age_gate": ["age verification", "minor", "under 18", "parental consent", "COPPA", "child", "teen"],
            "data_localization": ["data residency", "local storage", "in-country", "jurisdiction", "sovereign", "regional"],
            "content_restriction": ["block", "filter", "restrict access", "geofence", "censor", "moderate"],
            "privacy_protection": ["PII", "personal data", "GDPR", "privacy", "anonymize", "pseudonymize"],
            "geographic_compliance": ["region", "country", "jurisdiction", "territory", "border", "cross-border"],
            "advertising_regulation": ["targeted ads", "behavioral advertising", "ad personalization", "marketing"]
        }
        
        # Regional compliance indicators
        self.regional_indicators = {
            "EU": ["GDPR", "DSA", "European", "EU", "Europe"],
            "US": ["COPPA", "CCPA", "FTC", "United States", "US", "America"],
            "APAC": ["Asia", "Pacific", "APAC", "Singapore", "Japan", "Australia"],
            "China": ["China", "Chinese", "PRC", "mainland"],
            "India": ["India", "Indian", "IT Rules"],
            "Brazil": ["Brazil", "Brazilian", "LGPD"],
            "Global": ["worldwide", "international", "multi-region", "cross-border"]
        }
    
    def expand_description(self, text: str) -> str:
        """Expand abbreviations and add context"""
        expanded = text
        for abbr, full in self.jargon_map.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(abbr) + r'\b'
            replacement = f"{abbr} ({full})"
            expanded = re.sub(pattern, replacement, expanded, flags=re.IGNORECASE)
        return expanded
    
    def detect_compliance_intent(self, text: str) -> Dict[str, float]:
        """Detect compliance intent vs business logic"""
        intent_scores = {"compliance": 0.0, "business": 0.0, "ambiguous": 0.0}
        
        compliance_keywords = [
            "comply", "regulation", "law", "legal", "requirement", "mandatory",
            "protection", "privacy", "GDPR", "COPPA", "restrict", "prohibit",
            "enforce", "violate", "penalty", "fine", "audit", "regulatory",
            "jurisdiction", "court", "litigation", "lawsuit", "settlement"
        ]
        
        business_keywords = [
            "market", "testing", "rollout", "launch", "pilot", "experiment", 
            "A/B test", "feature flag", "monetize", "revenue", "growth",
            "engagement", "retention", "conversion", "optimization", "performance",
            "user experience", "UX", "UI", "product", "strategic", "competitive"
        ]
        
        ambiguous_keywords = [
            "regional", "localization", "customization", "personalization",
            "targeting", "segmentation", "filtering", "recommendation"
        ]
        
        text_lower = text.lower()
        
        # Score based on keyword presence
        for keyword in compliance_keywords:
            if keyword in text_lower:
                intent_scores["compliance"] += 0.15
        
        for keyword in business_keywords:
            if keyword in text_lower:
                intent_scores["business"] += 0.15
        
        for keyword in ambiguous_keywords:
            if keyword in text_lower:
                intent_scores["ambiguous"] += 0.1
        
        # Additional scoring based on patterns
        for pattern_type, patterns in self.compliance_patterns.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    intent_scores["compliance"] += 0.1
        
        # Normalize scores
        total = sum(intent_scores.values())
        if total > 0:
            intent_scores = {k: v/total for k, v in intent_scores.items()}
        else:
            intent_scores["ambiguous"] = 1.0
            
        return intent_scores
    
    def extract_geographic_scope(self, text: str) -> List[str]:
        """Extract geographic regions mentioned in the text"""
        regions_found = []
        text_lower = text.lower()
        
        for region, indicators in self.regional_indicators.items():
            for indicator in indicators:
                if indicator.lower() in text_lower:
                    if region not in regions_found:
                        regions_found.append(region)
                    break
        
        return regions_found
    
    def detect_compliance_categories(self, text: str) -> Dict[str, float]:
        """Detect specific compliance categories with confidence scores"""
        category_scores = {}
        text_lower = text.lower()
        
        for category, patterns in self.compliance_patterns.items():
            score = 0.0
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    score += 1.0
            
            # Normalize by number of patterns
            category_scores[category] = min(score / len(patterns), 1.0)
        
        return category_scores
    
    def generate_expanded_analysis(self, feature: Dict) -> Dict:
        """Generate comprehensive analysis with expanded context"""
        description = feature.get('description', '')
        feature_name = feature.get('feature_name', '')
        
        # Combine feature name and description for analysis
        full_text = f"{feature_name}. {description}"
        
        analysis = {
            'original_text': full_text,
            'expanded_text': self.expand_description(full_text),
            'intent_scores': self.detect_compliance_intent(full_text),
            'geographic_scope': self.extract_geographic_scope(full_text),
            'compliance_categories': self.detect_compliance_categories(full_text),
            'jargon_detected': self._detect_jargon_usage(full_text),
            'complexity_score': self._calculate_complexity(full_text)
        }
        
        return analysis
    
    def _detect_jargon_usage(self, text: str) -> List[str]:
        """Detect which jargon terms are present in the text"""
        jargon_found = []
        text_upper = text.upper()
        
        for abbr in self.jargon_map.keys():
            pattern = r'\b' + re.escape(abbr) + r'\b'
            if re.search(pattern, text_upper):
                jargon_found.append(abbr)
        
        return jargon_found
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity based on jargon density and technical terms"""
        words = text.split()
        if not words:
            return 0.0
        
        jargon_count = len(self._detect_jargon_usage(text))
        technical_terms = ["system", "implementation", "mechanism", "algorithm", "protocol", "framework"]
        technical_count = sum(1 for word in words if word.lower() in technical_terms)
        
        complexity = (jargon_count + technical_count) / len(words)
        return min(complexity * 5, 1.0)  # Scale to 0-1 range
