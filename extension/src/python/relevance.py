import re
from typing import List, Dict, Set
from config import ComplianceConfig

def extract_locations(text: str) -> List[str]:
    """Extract geographic locations from text"""
    locations = []
    text_lower = text.lower()
    
    for state in ComplianceConfig.US_STATES:
        if state.lower() in text_lower:
            locations.append(state)
    
    # Also check for common abbreviations
    state_abbreviations = {
        "ca": "California", "ny": "New York", "tx": "Texas", "fl": "Florida",
        "ut": "Utah", "wa": "Washington", "or": "Oregon", "nv": "Nevada"
    }
    
    for abbr, full_name in state_abbreviations.items():
        if f" {abbr} " in f" {text_lower} " or f" {abbr}." in text_lower:
            if full_name not in locations:
                locations.append(full_name)
    
    return locations

def extract_key_topics(text: str) -> List[str]:
    """Extract key compliance topics from text"""
    topics = []
    text_lower = text.lower()
    
    for topic in ComplianceConfig.COMPLIANCE_TOPICS:
        if topic.lower() in text_lower:
            topics.append(topic)
    
    # Additional topic detection patterns
    topic_patterns = {
        "age_verification": [r"age.{0,10}verify", r"age.{0,10}check", r"verify.{0,10}age"],
        "parental_consent": [r"parent.{0,10}consent", r"guardian.{0,10}approval"],
        "data_collection": [r"data.{0,10}collect", r"collect.{0,10}data", r"user.{0,10}data"],
        "content_filtering": [r"content.{0,10}filter", r"filter.{0,10}content", r"block.{0,10}content"],
        "time_restrictions": [r"time.{0,10}restrict", r"curfew", r"hours.{0,10}limit"]
    }
    
    for topic, patterns in topic_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                topics.append(topic)
                break
    
    return list(set(topics))  # Remove duplicates

def has_specific_regulation_match(feature_description: str, statute_content: str) -> bool:
    """Check if feature has specific regulation matches"""
    feature_lower = feature_description.lower()
    statute_lower = statute_content.lower()
    
    # Specific regulation keywords
    regulation_keywords = [
        "coppa", "sb-976", "sb976", "house bill", "senate bill",
        "digital services act", "dsa", "gdpr", "ccpa", "ferpa"
    ]
    
    feature_regulations = set()
    statute_regulations = set()
    
    for keyword in regulation_keywords:
        if keyword in feature_lower:
            feature_regulations.add(keyword)
        if keyword in statute_lower:
            statute_regulations.add(keyword)
    
    return len(feature_regulations & statute_regulations) > 0

def calculate_relevance_score(feature_description: str, statute_content: str, statute_metadata: Dict) -> float:
    """Calculate relevance score based on multiple factors"""
    score = 0.0
    
    # Geographic relevance (40% weight)
    feature_locations = set(extract_locations(feature_description))
    statute_locations = set(extract_locations(statute_content))
    if feature_locations & statute_locations:
        score += 0.4
    elif feature_locations and not statute_locations:
        # If feature is location-specific but statute isn't, lower relevance
        score += 0.1
    elif not feature_locations:
        # If no specific location in feature, federal/general laws are relevant
        score += 0.2
    
    # Topic relevance (40% weight)
    feature_topics = set(extract_key_topics(feature_description))
    statute_topics = set(extract_key_topics(statute_content))
    topic_overlap = len(feature_topics & statute_topics)
    topic_score = min(topic_overlap * 0.1, 0.4)
    score += topic_score
    
    # Specific regulation matching (20% weight)
    if has_specific_regulation_match(feature_description, statute_content):
        score += 0.2
    
    # Content type bonus
    if statute_metadata.get('content_type') == 'legal_statute':
        score += 0.05
    
    return min(score, 1.0)  # Cap at 1.0

def is_relevant_compliance(compliance_flag: Dict) -> bool:
    """Determine if a compliance flag is relevant (not a mock response)"""
    flag_text = compliance_flag.get('compliance_flag', '').lower()
    
    # Filter out mock responses and low-quality results
    mock_indicators = [
        "mock analysis",
        "error processing",
        "key considerations include user age verification, data protection, and geographical restrictions"
    ]
    
    for indicator in mock_indicators:
        if indicator.lower() in flag_text:
            return False
    
    # Check for meaningful content
    meaningful_indicators = [
        "requires", "must", "shall", "compliance", "violation",
        "penalty", "fine", "liability", "obligation", "prohibited"
    ]
    
    return any(indicator in flag_text for indicator in meaningful_indicators)

def parse_compliance_requirements(compliance_flag: Dict) -> Dict:
    """Parse compliance requirements from LLM response"""
    flag_text = compliance_flag.get('compliance_flag', '')
    statute = compliance_flag.get('statute', '')
    
    # Determine severity based on keywords
    high_severity_keywords = [
        "violation", "penalty", "fine", "criminal", "felony", "misdemeanor",
        "prohibited", "illegal", "ban", "suspend", "revoke"
    ]
    
    medium_severity_keywords = [
        "requires", "must", "shall", "mandatory", "obligation", "duty"
    ]
    
    severity = "low"
    flag_lower = flag_text.lower()
    
    if any(keyword in flag_lower for keyword in high_severity_keywords):
        severity = "high"
    elif any(keyword in flag_lower for keyword in medium_severity_keywords):
        severity = "medium"
    
    return {
        'statute': statute,
        'requirements': flag_text,
        'severity': severity,
        'keywords': extract_key_topics(flag_text)
    }

def generate_action_items(compliance_req: Dict) -> List[str]:
    """Generate action items based on compliance requirements"""
    action_items = []
    keywords = compliance_req.get('keywords', [])
    severity = compliance_req.get('severity', 'low')
    
    # Base action items based on keywords
    keyword_actions = {
        'age_verification': "Implement robust age verification system",
        'parental_consent': "Design parental consent workflow",
        'data_collection': "Review and limit data collection practices",
        'content_filtering': "Implement content filtering mechanisms",
        'time_restrictions': "Add time-based access controls",
        'minors': "Create minor-specific user flows",
        'privacy': "Conduct privacy impact assessment",
        'algorithmic transparency': "Document algorithmic decision-making processes"
    }
    
    for keyword in keywords:
        if keyword in keyword_actions:
            action_items.append(keyword_actions[keyword])
    
    # Severity-based action items
    if severity == "high":
        action_items.insert(0, "🚨 URGENT: Legal review required before deployment")
        action_items.append("Schedule meeting with legal counsel")
    elif severity == "medium":
        action_items.insert(0, "⚠️ Important: Compliance review needed")
        action_items.append("Document compliance measures")
    
    return list(set(action_items))  # Remove duplicates
