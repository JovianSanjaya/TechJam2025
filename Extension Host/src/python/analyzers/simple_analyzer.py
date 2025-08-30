"""
Simple fallback analyzer for when LLM is not available
"""

import sys
import os
from datetime import datetime
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compliance_types.compliance_types import ComplianceResult, CompliancePattern
from utils.helpers import calculate_confidence


class SimpleAnalyzer:
    """Simple rule-based analyzer as fallback when LLM is not available"""
    
    def __init__(self):
        self.privacy_keywords = self._load_privacy_keywords()
        self.regulation_keywords = self._load_regulation_keywords()
    
    def analyze(self, code: str, feature_name: str, patterns: List[CompliancePattern] = None) -> ComplianceResult:
        """Perform simple analysis based on keyword matching and patterns"""
        if patterns is None:
            patterns = []
        
        # Analyze code for keywords
        keyword_scores = self._analyze_keywords(code)
        
        # Determine regulations based on keywords and patterns
        applicable_regulations = self._determine_regulations(code, patterns, keyword_scores)
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(keyword_scores, patterns)
        
        # Calculate confidence
        confidence = self._calculate_confidence(keyword_scores, patterns)
        
        # Generate implementation notes
        implementation_notes = self._generate_implementation_notes(keyword_scores, patterns)
        
        # Determine action required
        action_required = self._determine_action_required(risk_level, len(applicable_regulations))
        
        return ComplianceResult(
            feature_name=feature_name,
            needs_compliance_logic=len(applicable_regulations) > 0,
            confidence=confidence,
            reasoning=self._generate_reasoning(keyword_scores, patterns),
            applicable_regulations=applicable_regulations,
            action_required=action_required,
            human_review_needed=risk_level == "high",
            risk_level=risk_level,
            implementation_notes=implementation_notes,
            patterns=patterns,
            llm_analysis=None,
            timestamp=datetime.now().isoformat()
        )
    
    def _analyze_keywords(self, code: str) -> Dict[str, int]:
        """Analyze code for privacy-related keywords"""
        code_lower = code.lower()
        scores = {}
        
        for category, keywords in self.privacy_keywords.items():
            score = sum(1 for keyword in keywords if keyword in code_lower)
            scores[category] = score
        
        return scores
    
    def _determine_regulations(self, code: str, patterns: List[CompliancePattern], 
                             keyword_scores: Dict[str, int]) -> List[Dict]:
        """Determine applicable regulations"""
        regulations = set()
        
        # From patterns
        for pattern in patterns:
            regulations.update(pattern.regulation_hints)
        
        # From keyword analysis
        if keyword_scores.get('age_related', 0) > 0:
            regulations.add('COPPA')
        
        if keyword_scores.get('personal_data', 0) > 0 or keyword_scores.get('tracking', 0) > 0:
            regulations.add('GDPR')
            regulations.add('CCPA')
        
        if keyword_scores.get('location', 0) > 0:
            regulations.add('GDPR')
            regulations.add('CCPA')
        
        # Convert to expected format
        result = []
        for reg in regulations:
            result.append({
                'regulation': reg,
                'relevance': 0.6,  # Simple analysis has lower confidence
                'content_excerpt': f"Simple analysis indicates {reg} may apply",
                'requirements': [reg],
                'jurisdiction': 'Various',
                'compliance_risk': 'medium',
                'legal_basis': f"{reg} requirements based on keyword analysis"
            })
        
        return result
    
    def _calculate_risk_level(self, keyword_scores: Dict[str, int], patterns: List[CompliancePattern]) -> str:
        """Calculate risk level based on scores and patterns"""
        total_keywords = sum(keyword_scores.values())
        high_confidence_patterns = sum(1 for p in patterns if p.confidence > 0.8)
        
        if total_keywords >= 5 or high_confidence_patterns >= 2:
            return "high"
        elif total_keywords >= 2 or high_confidence_patterns >= 1:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, keyword_scores: Dict[str, int], patterns: List[CompliancePattern]) -> float:
        """Calculate confidence score"""
        base_confidence = 0.4  # Lower for simple analysis
        
        total_keywords = sum(keyword_scores.values())
        keyword_boost = min(total_keywords * 0.05, 0.3)
        
        pattern_boost = min(len(patterns) * 0.1, 0.2)
        
        return min(base_confidence + keyword_boost + pattern_boost, 0.8)
    
    def _generate_implementation_notes(self, keyword_scores: Dict[str, int], 
                                     patterns: List[CompliancePattern]) -> List[str]:
        """Generate implementation notes based on findings"""
        notes = []
        
        if keyword_scores.get('age_related', 0) > 0:
            notes.append("⚠️ Age-related functionality detected - implement COPPA compliance")
        
        if keyword_scores.get('personal_data', 0) > 0:
            notes.append("📋 Personal data handling detected - ensure GDPR/CCPA compliance")
        
        if keyword_scores.get('tracking', 0) > 0:
            notes.append("👁️ User tracking detected - implement consent mechanisms")
        
        if keyword_scores.get('location', 0) > 0:
            notes.append("📍 Location functionality detected - ensure explicit consent")
        
        if keyword_scores.get('consent', 0) > 0:
            notes.append("✅ Consent mechanisms found - verify implementation completeness")
        
        # Add pattern-specific notes
        for pattern in patterns:
            if pattern.confidence > 0.7:
                notes.append(f"🔍 High-confidence pattern: {pattern.description}")
        
        if not notes:
            notes.append("ℹ️ Limited compliance indicators found - manual review recommended")
        
        return notes
    
    def _generate_reasoning(self, keyword_scores: Dict[str, int], patterns: List[CompliancePattern]) -> List[str]:
        """Generate reasoning for the analysis"""
        reasoning = []
        
        total_keywords = sum(keyword_scores.values())
        reasoning.append(f"Found {total_keywords} privacy-related keywords")
        reasoning.append(f"Identified {len(patterns)} compliance patterns")
        
        if keyword_scores.get('age_related', 0) > 0:
            reasoning.append("Age-related functionality suggests COPPA requirements")
        
        if keyword_scores.get('personal_data', 0) > 0 or keyword_scores.get('tracking', 0) > 0:
            reasoning.append("Data handling suggests GDPR/CCPA requirements")
        
        reasoning.append("Analysis based on keyword matching and pattern detection")
        
        return reasoning
    
    def _determine_action_required(self, risk_level: str, regulation_count: int) -> str:
        """Determine what action is required"""
        if risk_level == "high":
            return "IMPLEMENT_COMPLIANCE"
        elif risk_level == "medium" or regulation_count > 0:
            return "REVIEW_REQUIRED"
        else:
            return "MONITOR"
    
    def _load_privacy_keywords(self) -> Dict[str, List[str]]:
        """Load privacy-related keywords by category"""
        return {
            'personal_data': [
                'personal_data', 'user_data', 'personal_info', 'pii',
                'personally_identifiable', 'user_profile', 'profile_data'
            ],
            'tracking': [
                'track_user', 'user_tracking', 'behavior_tracking', 'activity_tracking',
                'analytics', 'usage_analytics', 'tracking_pixel'
            ],
            'age_related': [
                'age', 'date_of_birth', 'birth_date', 'minor', 'child',
                'under_13', 'underage', 'youth', 'juvenile'
            ],
            'location': [
                'location', 'gps', 'coordinates', 'latitude', 'longitude',
                'geolocation', 'geoip', 'geo_data', 'location_data'
            ],
            'consent': [
                'consent', 'permission', 'agreement', 'acceptance',
                'opt_in', 'opt_out', 'privacy_policy', 'terms_of_service'
            ]
        }
    
    def _load_regulation_keywords(self) -> Dict[str, List[str]]:
        """Load regulation-specific keywords"""
        return {
            'COPPA': ['coppa', 'under_13', 'parental_consent', 'child', 'minor'],
            'GDPR': ['gdpr', 'data_protection', 'right_to_be_forgotten', 'data_portability'],
            'CCPA': ['ccpa', 'california', 'consumer_privacy', 'personal_information']
        }
