"""
Unified Compliance Analyzer - Combines the best of enhanced_main.py and feature_compliance_analyzer.py
"""
import asyncio
import json
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from core.llm_client import LLMClient
from services.jargon_service import JargonService
from services.vector_service import VectorService, get_vector_store
from core.agents import MultiAgentOrchestrator
from core.cache import ComplianceCache
from config import ComplianceConfig

@dataclass
class ComplianceResult:
    """Result of compliance analysis"""
    feature_id: str
    feature_name: str
    analysis_type: str
    needs_compliance_logic: bool
    confidence: float
    risk_level: str
    action_required: str
    applicable_regulations: List[Dict]
    implementation_notes: List[str]
    agent_results: Optional[Dict] = None
    llm_analysis: Optional[Dict] = None
    timestamp: str = ""

class UnifiedComplianceAnalyzer:
    """
    Unified compliance analyzer that handles both single features and codebase analysis
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.jargon_service = JargonService()
        self.vector_service = get_vector_store()
        self.agent_orchestrator = MultiAgentOrchestrator(self.vector_service, self.jargon_service, self.llm_client)
        self.cache = ComplianceCache()
        
        print("🔗 Unified Compliance Analyzer initialized")
        print(f"🔗 OpenRouter model: {ComplianceConfig.OPENROUTER_MODEL}")
        print(f"🔑 API key configured: {'Yes' if ComplianceConfig.OPENROUTER_API_KEY else 'No (using mock responses)'}")
    
    async def analyze_feature(self, feature_data: Dict) -> Dict:
        """
        Analyze a single feature for compliance
        
        Args:
            feature_data: Dict with 'featureName' and 'description'
        
        Returns:
            Dict with analysis results
        """
        feature_name = feature_data.get('featureName', 'Unknown Feature')
        description = feature_data.get('description', '')
        
        print(f"🔍 Analyzing feature: {feature_name}")
        
        # Step 1: Resolve jargon
        resolved_description = self.jargon_service.expand_description(description)
        print(f"📝 Resolved description: {resolved_description}")
        
        # Step 2: Multi-agent analysis
        agent_results = await self.agent_orchestrator.analyze_feature({
            'feature_name': feature_name,
            'description': resolved_description
        })
        
        # Step 3: LLM analysis
        llm_analysis = await self._get_llm_analysis(feature_name, resolved_description)
        
        # Step 4: Synthesize results
        result = self._synthesize_analysis(
            feature_name, 
            resolved_description, 
            agent_results, 
            llm_analysis
        )
        
        return result
    
    async def _get_llm_analysis(self, feature_name: str, description: str) -> Dict:
        """Get LLM analysis of the feature"""
        prompt = f"""
        Feature: {feature_name}
        Description: {description}
        
        Analyze this feature for legal compliance requirements focusing on:
        1. COPPA (Children's Online Privacy Protection Act)
        2. GDPR (General Data Protection Regulation)  
        3. CCPA (California Consumer Privacy Act)
        4. Other relevant regulations
        
        Consider if this feature involves:
        - Data collection from minors
        - Personal data processing
        - Geolocation tracking
        - Behavioral targeting
        - Age verification requirements
        """
        
        try:
            response = await self.llm_client.analyze(prompt)
            return {
                "raw_response": response,
                "analysis_type": "llm_enhanced",
                "confidence": 0.8
            }
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}")
            return {
                "raw_response": f"LLM analysis unavailable: {str(e)}",
                "analysis_type": "fallback",
                "confidence": 0.3
            }
    
    def _synthesize_analysis(self, feature_name: str, description: str, 
                           agent_results: Dict, llm_analysis: Dict) -> Dict:
        """Synthesize all analysis results into final output"""
        
        # Determine risk level
        risk_level = self._calculate_risk_level(agent_results, llm_analysis)
        
        # Extract applicable regulations
        applicable_regulations = self._extract_regulations(agent_results, llm_analysis)
        
        # Generate implementation notes
        implementation_notes = self._generate_implementation_notes(
            feature_name, description, agent_results, llm_analysis
        )
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(agent_results, llm_analysis)
        
        # Create result
        result = ComplianceResult(
            feature_id=f"feat_{hash(feature_name) % 10000:04d}",
            feature_name=feature_name,
            analysis_type="unified_analysis",
            needs_compliance_logic=risk_level in ["high", "medium"],
            confidence=confidence,
            risk_level=risk_level,
            action_required="review_required" if risk_level == "high" else "monitor",
            applicable_regulations=applicable_regulations,
            implementation_notes=implementation_notes,
            agent_results=agent_results,
            llm_analysis=llm_analysis,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return asdict(result)
    
    def _calculate_risk_level(self, agent_results: Dict, llm_analysis: Dict) -> str:
        """Calculate overall risk level"""
        risk_factors = []
        
        # Check agent results
        if agent_results.get('legal_analysis', {}).get('risk_level'):
            risk_factors.append(agent_results['legal_analysis']['risk_level'])
        
        if agent_results.get('privacy_analysis', {}).get('risk_level'):
            risk_factors.append(agent_results['privacy_analysis']['risk_level'])
        
        # Simple risk aggregation
        if 'high' in risk_factors:
            return 'high'
        elif 'medium' in risk_factors:
            return 'medium'
        else:
            return 'low'
    
    def _extract_regulations(self, agent_results: Dict, llm_analysis: Dict) -> List[Dict]:
        """Extract applicable regulations from analysis"""
        regulations = []
        
        # From agent results
        if agent_results.get('legal_analysis', {}).get('applicable_regulations'):
            regulations.extend(agent_results['legal_analysis']['applicable_regulations'])
        
        # Add common regulations with frontend-compatible format
        common_regs = [
            {
                "name": "COPPA", 
                "applies": True, 
                "reason": "Children's Online Privacy Protection Act - applies to data collection from minors"
            },
            {
                "name": "GDPR", 
                "applies": True, 
                "reason": "General Data Protection Regulation - applies to personal data processing in EU"
            },
            {
                "name": "CCPA", 
                "applies": True, 
                "reason": "California Consumer Privacy Act - applies to personal data of California residents"
            }
        ]
        
        regulations.extend(common_regs)
        return regulations
    
    def _generate_implementation_notes(self, feature_name: str, description: str,
                                     agent_results: Dict, llm_analysis: Dict) -> List[str]:
        """Generate implementation notes"""
        notes = [
            f"Feature '{feature_name}' requires compliance review",
            "Implement proper data handling procedures",
            "Consider age verification if targeting minors",
            "Ensure transparent privacy policies",
            "Implement user consent mechanisms"
        ]
        
        # Add specific notes based on analysis
        if "age" in description.lower() or "minor" in description.lower():
            notes.append("⚠️ COPPA compliance required for minor-related features")
        
        if "location" in description.lower() or "geo" in description.lower():
            notes.append("⚠️ Geolocation features require explicit user consent")
        
        return notes
    
    def _calculate_confidence(self, agent_results: Dict, llm_analysis: Dict) -> float:
        """Calculate overall confidence score"""
        confidence_factors = []
        
        if agent_results:
            confidence_factors.append(0.7)
        
        if llm_analysis.get('confidence'):
            confidence_factors.append(llm_analysis['confidence'])
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
