"""
LLM Service for compliance analysis
"""

import json
import requests
import sys
from typing import Dict, List, Optional

from ..config import APIConfig
from ..types.compliance_types import LLMResponse
from ..utils.helpers import log_error, log_info, safe_json_loads


class LLMService:
    """Service for LLM-based analysis"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or APIConfig.OPENROUTER_API_KEY
        self.model = model or APIConfig.OPENROUTER_MODEL
        self.base_url = APIConfig.OPENROUTER_BASE_URL
        
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return bool(self.api_key.strip())
    
    def analyze_code(self, code: str, feature_name: str, rag_context: str = "") -> Optional[LLMResponse]:
        """Analyze code using LLM"""
        if not self.is_available():
            log_error("LLM service not available - missing API key")
            return None
            
        try:
            prompt = self._build_analysis_prompt(code, feature_name, rag_context)
            response = self._call_llm(prompt)
            return self._parse_llm_response(response)
            
        except Exception as e:
            log_error(f"LLM analysis failed: {str(e)}", e)
            return None
    
    def _build_analysis_prompt(self, code: str, feature_name: str, rag_context: str = "") -> str:
        """Build prompt for LLM analysis - KEEPING ORIGINAL PROMPTS UNCHANGED"""
        # Import the original prompt from the existing code
        from ..code_analyzer_llm_clean import LLMCodeAnalyzer
        
        # Create a temporary instance to get the original prompt
        temp_analyzer = LLMCodeAnalyzer(use_llm=False)
        
        # Use the original _build_enhanced_compliance_prompt method
        enhanced_patterns = []  # This would normally come from pattern analysis
        static_analysis = {"patterns": [], "compliance_categories": []}
        retrieved_docs = {"documents": [[rag_context]] if rag_context else [[""]]}
        
        # Build the exact same prompt as the original
        prompt = f"""
Analyze this TikTok platform feature code for comprehensive compliance requirements with a focus on youth protection, data privacy, and regulatory adherence.

Feature: {feature_name}

Code to analyze:
```
{code}
```

Legal Context (RAG):
{rag_context}

Provide a detailed JSON analysis with the following structure:
{{
    "enhanced_patterns": [
        {{
            "pattern_type": "category",
            "pattern_name": "specific_pattern_name",
            "confidence": 0.0-1.0,
            "location": "line_number_or_section",
            "code_snippet": "relevant_code_excerpt",
            "description": "detailed_description",
            "regulation_hints": ["COPPA", "GDPR", "etc"],
            "llm_analysis": "detailed_analysis",
            "severity": "low|medium|high",
            "legal_basis": "specific_regulation_reference"
        }}
    ],
    "compliance_insights": {{
        "overall_assessment": "comprehensive_assessment",
        "key_risks": ["risk1", "risk2"],
        "regulatory_gaps": ["gap1", "gap2"],
        "implementation_suggestions": ["suggestion1", "suggestion2"],
        "legal_references": ["reference1", "reference2"]
    }},
    "enhanced_recommendations": [
        "specific_actionable_recommendation1",
        "specific_actionable_recommendation2"
    ],
    "confidence_adjustments": {{
        "reasoning": "explanation_of_confidence_adjustments",
        "adjusted_risk_score": 0.0-1.0,
        "rag_influence": "explanation_of_how_legal_context_influenced_analysis"
    }}
}}

Focus on:
1. COPPA compliance for users under 13
2. Data collection and privacy patterns
3. Age verification mechanisms
4. Parental consent requirements
5. Youth protection features
6. GDPR/CCPA implications

Provide specific, actionable insights based on the code analysis."""

        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Make API call to LLM"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 3000
        }
        
        log_info(f"🌐 Calling LLM API: {self.model}")
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=APIConfig.TIMEOUT
        )
        
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        log_info(f"✅ LLM response received: {len(content)} characters")
        return content
    
    def _parse_llm_response(self, response_text: str) -> LLMResponse:
        """Parse LLM response into structured format"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                return LLMResponse(
                    enhanced_patterns=data.get("enhanced_patterns", []),
                    compliance_insights=data.get("compliance_insights", {}),
                    enhanced_recommendations=data.get("enhanced_recommendations", []),
                    confidence_adjustments=data.get("confidence_adjustments", {}),
                    raw_response=response_text
                )
            else:
                # Fallback if no valid JSON found
                return LLMResponse(
                    enhanced_patterns=[],
                    compliance_insights={"overall_assessment": "LLM analysis available in raw response"},
                    enhanced_recommendations=["Review raw LLM output for insights"],
                    confidence_adjustments={"reasoning": "JSON parsing failed", "adjusted_risk_score": 0.5},
                    raw_response=response_text
                )
                
        except json.JSONDecodeError as e:
            log_error(f"Failed to parse LLM JSON response: {e}")
            return LLMResponse(
                enhanced_patterns=[],
                compliance_insights={"overall_assessment": "JSON parsing failed"},
                enhanced_recommendations=["Manual review required"],
                confidence_adjustments={"reasoning": "Parse error", "adjusted_risk_score": 0.3},
                raw_response=response_text
            )
