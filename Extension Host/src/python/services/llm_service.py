"""
LLM Service for compliance analysis.

This module provides an interface for Large Language Model-based compliance analysis,
including prompt generation, API communication, and response parsing for enhanced
code compliance assessment.
"""

import json
import requests
import sys
import os
from typing import Dict, List, Optional

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import APIConfig
import compliance_types.compliance_types as ct
from utils.helpers import log_error, log_info, safe_json_loads


class LLMService:
    """
    Service for LLM-based compliance analysis.
    
    Handles communication with OpenRouter API to perform enhanced compliance
    analysis using Large Language Models, with support for custom prompts
    and structured response parsing.
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the LLM service.
        
        Args:
            api_key: OpenRouter API key (optional, uses config default)
            model: Model identifier (optional, uses config default)
        """
        self.api_key = api_key or APIConfig.OPENROUTER_API_KEY
        self.model = model or APIConfig.OPENROUTER_MODEL
        self.base_url = APIConfig.OPENROUTER_BASE_URL
        
    def is_available(self) -> bool:
        """
        Check if LLM service is available.
        
        Returns:
            True if API key is configured, False otherwise
        """
        return bool(self.api_key.strip())
    
    def analyze_code(self, code: str, feature_name: str, rag_context: str = "") -> Optional[ct.LLMResponse]:
        """
        Analyze code using LLM for compliance assessment.
        
        Args:
            code: Source code to analyze
            feature_name: Name of the feature being analyzed
            rag_context: Additional context from RAG retrieval
            
        Returns:
            LLMResponse object with analysis results, or None if analysis fails
        """
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
        """
        Build enhanced prompt for LLM analysis focusing on problematic code identification.
        
        Args:
            code: Source code to analyze
            feature_name: Name of the feature
            rag_context: Additional legal context
            
        Returns:
            Formatted prompt string for LLM analysis
        """
        
        prompt = f"""
You are an expert compliance analyst specializing in social media platforms like TikTok. Your primary task is to identify SPECIFIC problematic code snippets and provide ACTIONABLE fixes.

**YOUR MISSION:** 
1. 🔍 **IDENTIFY EXACT PROBLEMATIC CODE** - Quote the exact lines that violate regulations
2. ⚠️ **EXPLAIN WHY IT'S PROBLEMATIC** - Specify which regulation is violated and how
3. 🛠️ **PROVIDE SPECIFIC FIXES** - Give exact code replacements, not general advice
4. 📋 **PRIORITIZE BY SEVERITY** - Critical issues first, then high, medium, low

**COMPLIANCE FOCUS AREAS:**
1. **COPPA (Children's Online Privacy Protection Act)** - Age verification, parental consent, data minimization for under-13 users
2. **GDPR/Privacy Laws** - Data collection consent, user rights (deletion, portability), data processing transparency  
3. **Content Moderation** - Age-appropriate content filtering, harmful content detection, algorithmic bias prevention
4. **Geolocation Privacy** - Location tracking consent, data localization requirements, precision limiting
5. **Platform-specific regulations** - Youth protection mechanisms, algorithmic transparency, time limits

{rag_context}

**📝 CODE TO ANALYZE:**
```
{code}
```

**🎯 FEATURE CONTEXT:** Feature: {feature_name}

**🚨 CRITICAL ANALYSIS REQUIREMENTS:**
- Line-by-line examination of the provided code
- Identify EXACT code snippets that violate regulations (quote them exactly)
- Provide SPECIFIC replacement code, not general recommendations
- Explain the legal/regulatory basis for each issue
- Include severity assessment and business impact

**🎯 REQUIRED JSON RESPONSE FORMAT:**
{{
  "problematic_code_analysis": [
    {{
      "line_number": "exact_line_number_or_function_name",
      "problematic_code": "EXACT_CODE_SNIPPET_FROM_INPUT_THAT_VIOLATES",
      "violation_type": "privacy_violation|age_verification_missing|consent_bypass|data_collection_unauthorized|location_tracking_unconsented|content_moderation_gap",
      "severity": "critical|high|medium|low",
      "regulation_violated": "COPPA|GDPR|CCPA|DSA|SB-976|COPPA-Rule-2013",
      "why_problematic": "detailed_explanation_of_specific_legal_violation",
      "business_risk": "potential_fines_or_legal_consequences",
      "suggested_replacement": "EXACT_IMPROVED_CODE_TO_REPLACE_PROBLEMATIC_SECTION",
      "fix_explanation": "step_by_step_implementation_guide",
      "testing_verification": "how_to_test_the_fix_works_correctly",
      "related_requirements": ["additional_compliance_steps_needed"]
    }}
  ],
  "compliance_gaps": [
    {{
      "missing_feature": "specific_compliance_mechanism_not_implemented",
      "regulation_requirement": "exact_legal_requirement_not_met", 
      "severity": "critical|high|medium|low",
      "suggested_implementation": "complete_code_example_to_add",
      "integration_points": ["where_to_integrate_in_existing_code"],
      "effort_estimate": "hours_or_days_to_implement"
    }}
  ],
  "actionable_recommendations": [
    {{
      "priority": "critical|high|medium|low",
      "title": "short_specific_action_title",
      "description": "detailed_actionable_recommendation_with_business_context",
      "code_changes_required": "exact_code_to_add_modify_or_remove",
      "affected_functions": ["specific_function_names"],
      "implementation_steps": ["step_1", "step_2", "step_3"],
      "compliance_benefit": "how_this_addresses_regulatory_requirement",
      "timeline": "recommended_implementation_timeframe",
      "dependencies": ["other_changes_needed_first"]
    }}
  ],
  "compliance_insights": {{
    "overall_assessment": "comprehensive_summary_with_severity_and_urgency",
    "critical_findings": ["most_severe_violations_requiring_immediate_action"],
    "immediate_actions": ["fixes_needed_within_24_hours"],
    "testing_requirements": ["compliance_testing_needed_after_fixes"]
  }}
}}

**🎯 ANALYSIS INSTRUCTIONS:**
- Read every line of the provided code carefully
- Flag any code that collects user data without proper consent mechanisms
- Identify missing age verification before data collection
- For each violation, provide the EXACT replacement code
- Prioritize by compliance urgency and business risk
"""
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM API with the provided prompt.
        
        Args:
            prompt: Formatted prompt for analysis
            
        Returns:
            Raw response text from the LLM
            
        Raises:
            RuntimeError: If API key is not configured
            requests.RequestException: If API call fails
        """
        if not self.api_key:
            raise RuntimeError("OpenRouter API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/JovianSanjaya/TechJam2025",
            "X-Title": "TikTok Compliance Analyzer Enhanced"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": """You are an expert legal compliance analyst specializing in social media platform regulations. Your expertise includes COPPA, GDPR, CCPA, DSA, and emerging youth protection laws.

Your primary task is to identify SPECIFIC problematic code and provide ACTIONABLE fixes:

1. IDENTIFY: Quote exact code snippets that violate regulations
2. EXPLAIN: Specify which law is violated and why
3. FIX: Provide complete replacement code, not generic advice
4. PRIORITIZE: Order by legal risk and implementation urgency

Always respond in valid JSON format with detailed code analysis. Focus on practical, implementable solutions that developers can apply immediately to achieve compliance."""
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 3000,
            "temperature": 0.2,
            "top_p": 0.85
        }
        
        log_info("Calling OpenRouter API for enhanced analysis")
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        log_info(f"Enhanced LLM response received: {len(content)} characters")
        return content
    
    def _parse_llm_response(self, response_text: str) -> ct.LLMResponse:
        """
        Parse enhanced LLM response into structured format.
        
        Args:
            response_text: Raw response text from LLM
            
        Returns:
            LLMResponse object with parsed data
        """
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                return ct.LLMResponse(
                    enhanced_patterns=data.get("enhanced_patterns", []),
                    compliance_insights=data.get("compliance_insights", {}),
                    enhanced_recommendations=data.get("actionable_recommendations", []),
                    confidence_adjustments=data.get("confidence_adjustments", {}),
                    raw_response=response_text,
                    problematic_code_analysis=data.get("problematic_code_analysis", []),
                    compliance_gaps=data.get("compliance_gaps", []),
                    code_quality_improvements=data.get("code_quality_improvements", [])
                )
            else:
                # Fallback if no valid JSON found
                return ct.LLMResponse(
                    enhanced_patterns=[],
                    compliance_insights={"overall_assessment": "Enhanced LLM analysis available in raw response"},
                    enhanced_recommendations=["Review raw LLM output for specific code fixes"],
                    confidence_adjustments={"reasoning": "JSON parsing failed", "adjusted_risk_score": 0.5},
                    raw_response=response_text,
                    problematic_code_analysis=[],
                    compliance_gaps=[],
                    code_quality_improvements=[]
                )
                
        except json.JSONDecodeError as e:
            log_error(f"Failed to parse enhanced LLM JSON response: {e}")
            return ct.LLMResponse(
                enhanced_patterns=[],
                compliance_insights={"overall_assessment": "JSON parsing failed"},
                enhanced_recommendations=["Manual review required"],
                confidence_adjustments={"reasoning": "Parse error", "adjusted_risk_score": 0.3},
                raw_response=response_text,
                problematic_code_analysis=[],
                compliance_gaps=[],
                code_quality_improvements=[]
            )
