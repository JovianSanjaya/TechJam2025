import ast
import re
import json
import requests
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from config import ComplianceConfig

@dataclass
class CompliancePattern:
    """Represents a compliance pattern found in code"""
    pattern_type: str
    pattern_name: str
    confidence: float
    location: str
    code_snippet: str
    description: str
    regulation_hints: List[str]
    llm_analysis: Optional[str] = None

class LLMCodeAnalyzer:
    """Enhanced code analyzer using LLM (Kimi v2) for intelligent compliance analysis"""
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm and ComplianceConfig.OPENROUTER_API_KEY
        self.api_key = ComplianceConfig.OPENROUTER_API_KEY
        self.model = "moonshotai/kimi-k2:free"  # Free Kimi v2 equivalent
        self.compliance_patterns = self._load_compliance_patterns()
        self.privacy_keywords = self._load_privacy_keywords()
        self.data_collection_patterns = self._load_data_collection_patterns()
        
        if not self.use_llm:
            print("⚠️  LLM analysis disabled - using static analysis only")
    
    
    def analyze_code_snippet(self, code: str, context: str = "") -> Dict:
        """Enhanced analysis combining static analysis with LLM insights"""
        # Start with static analysis
        static_analysis = self._perform_static_analysis(code, context)
        
        # Enhance with LLM analysis if available
        if self.use_llm:
            try:
                llm_analysis = self._perform_llm_analysis(code, context, static_analysis)
                enhanced_analysis = self._merge_analyses(static_analysis, llm_analysis)
                return enhanced_analysis
            except Exception as e:
                print(f"🤖 LLM analysis failed: {e}. Falling back to static analysis.")
                return static_analysis
        
        return static_analysis
    
    def _perform_static_analysis(self, code: str, context: str = "") -> Dict:
        """Original static analysis method"""
        analysis = {
            "compliance_patterns": [],
            "privacy_concerns": [],
            "data_collection": [],
            "age_verification": [],
            "geolocation": [],
            "content_moderation": [],
            "security_findings": [],
            "risk_score": 0.0,
            "recommendations": [],
            "analysis_method": "static"
        }
        
        try:
            # Try AST parsing for Python code
            tree = ast.parse(code)
            analysis.update(self._analyze_ast(tree, code))
        except SyntaxError:
            # Fallback to regex analysis for non-Python or malformed code
            analysis.update(self._analyze_regex(code))
        
        # Add context-based analysis
        if context:
            context_analysis = self._analyze_context(context, code)
            analysis = self._merge_analysis(analysis, context_analysis)
        
        # Calculate overall risk score
        analysis["risk_score"] = self._calculate_risk_score(analysis)
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _perform_llm_analysis(self, code: str, context: str, static_analysis: Dict) -> Dict:
        """Use LLM to enhance compliance analysis"""
        prompt = self._create_llm_prompt(code, context, static_analysis)
        
        try:
            response = self._call_openrouter(prompt)
            return self._parse_llm_response(response, static_analysis)
        except Exception as e:
            print(f"LLM API call failed: {e}")
            raise e
    
    def _create_llm_prompt(self, code: str, context: str, static_analysis: Dict) -> str:
        """Create a detailed prompt for LLM analysis"""
        prompt = f"""
You are an expert compliance analyst specializing in social media platforms like TikTok. 
Analyze the following code for regulatory compliance issues, particularly focusing on:

1. **COPPA (Children's Online Privacy Protection Act)** - Age verification, parental consent
2. **GDPR/Privacy Laws** - Data collection, consent, user rights  
3. **Content Moderation** - Age-appropriate content, harmful content filtering
4. **Geolocation Privacy** - Location tracking, data localization
5. **Platform-specific regulations** - Youth protection, algorithmic transparency

**Code to analyze:**
```
{code}
```

**Context:** {context if context else "No additional context provided"}

**Static Analysis Results:**
- Risk Score: {static_analysis.get('risk_score', 0):.2f}
- Patterns Found: {len(static_analysis.get('compliance_patterns', []))}
- Categories: {', '.join([k for k, v in static_analysis.items() if isinstance(v, list) and v and k != 'recommendations'])}

**Please provide a JSON response with:**
{{
  "enhanced_patterns": [
    {{
      "pattern_type": "category",
      "pattern_name": "specific_pattern",
      "confidence": 0.0-1.0,
      "location": "description",
      "code_snippet": "relevant_code",
      "description": "detailed_explanation",
      "regulation_hints": ["COPPA", "GDPR", etc.],
      "llm_analysis": "your_detailed_reasoning",
      "severity": "low|medium|high|critical"
    }}
  ],
  "compliance_insights": {{
    "overall_assessment": "summary",
    "key_risks": ["risk1", "risk2"],
    "regulatory_gaps": ["gap1", "gap2"],
    "implementation_suggestions": ["suggestion1", "suggestion2"]
  }},
  "enhanced_recommendations": [
    "actionable_recommendation_1",
    "actionable_recommendation_2"
  ],
  "confidence_adjustments": {{
    "reasoning": "why_adjustments_made",
    "adjusted_risk_score": 0.0-1.0
  }}
}}

Focus on practical, actionable insights that developers can implement immediately.
"""
        return prompt
    
    def _call_openrouter(self, prompt: str, timeout: int = 30) -> str:
        """Call OpenRouter API with Kimi v2 model"""
        if not self.api_key or self.api_key == "sk-or-v1-your-actual-api-key-here":
            raise RuntimeError("OpenRouter API key not configured")
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # Optional
            "X-Title": "TikTok Compliance Analyzer"  # Optional
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert legal compliance analyst for social media platforms. Provide detailed, accurate analysis in valid JSON format."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.3,  # Lower temperature for more consistent analysis
            "top_p": 0.9
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _parse_llm_response(self, response: str, static_analysis: Dict) -> Dict:
        """Parse LLM response and structure the analysis"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                llm_data = json.loads(json_str)
            else:
                # Fallback: create structured response from text
                llm_data = self._extract_insights_from_text(response)
            
            return {
                "enhanced_patterns": llm_data.get("enhanced_patterns", []),
                "compliance_insights": llm_data.get("compliance_insights", {}),
                "enhanced_recommendations": llm_data.get("enhanced_recommendations", []),
                "confidence_adjustments": llm_data.get("confidence_adjustments", {}),
                "llm_raw_response": response,
                "analysis_method": "llm_enhanced"
            }
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM JSON response: {e}")
            # Return text-based analysis
            return {
                "llm_raw_response": response,
                "analysis_method": "llm_text",
                "enhanced_recommendations": [
                    "Review LLM analysis in raw response",
                    "Manual interpretation may be required"
                ]
            }
    
    def _extract_insights_from_text(self, text: str) -> Dict:
        """Extract insights when JSON parsing fails"""
        insights = {
            "enhanced_patterns": [],
            "compliance_insights": {
                "overall_assessment": "LLM analysis available in raw response",
                "key_risks": [],
                "regulatory_gaps": [],
                "implementation_suggestions": []
            },
            "enhanced_recommendations": [],
            "confidence_adjustments": {}
        }
        
        # Simple text extraction for key terms
        if "COPPA" in text:
            insights["compliance_insights"]["key_risks"].append("COPPA compliance")
        if "GDPR" in text:
            insights["compliance_insights"]["key_risks"].append("GDPR compliance")
        if "age verification" in text.lower():
            insights["compliance_insights"]["key_risks"].append("Age verification required")
        
        return insights
    
    def _merge_analyses(self, static_analysis: Dict, llm_analysis: Dict) -> Dict:
        """Merge static analysis with LLM insights"""
        merged = static_analysis.copy()
        
        # Add LLM-enhanced patterns
        if "enhanced_patterns" in llm_analysis:
            for pattern in llm_analysis["enhanced_patterns"]:
                enhanced_pattern = CompliancePattern(
                    pattern_type=pattern.get("pattern_type", "llm_detected"),
                    pattern_name=pattern.get("pattern_name", "llm_pattern"),
                    confidence=pattern.get("confidence", 0.8),
                    location=pattern.get("location", "LLM Analysis"),
                    code_snippet=pattern.get("code_snippet", ""),
                    description=pattern.get("description", ""),
                    regulation_hints=pattern.get("regulation_hints", []),
                    llm_analysis=pattern.get("llm_analysis", "")
                )
                
                # Add to appropriate category
                category = pattern.get("pattern_type", "compliance_patterns")
                if category in merged:
                    merged[category].append(self._pattern_to_dict(enhanced_pattern))
        
        # Enhance recommendations
        if "enhanced_recommendations" in llm_analysis:
            merged["recommendations"].extend(llm_analysis["enhanced_recommendations"])
        
        # Adjust risk score if LLM provides insights
        if "confidence_adjustments" in llm_analysis:
            adj = llm_analysis["confidence_adjustments"]
            if "adjusted_risk_score" in adj:
                merged["risk_score"] = adj["adjusted_risk_score"]
                merged["risk_adjustment_reason"] = adj.get("reasoning", "LLM adjustment")
        
        # Add LLM insights
        merged["llm_insights"] = llm_analysis.get("compliance_insights", {})
        merged["analysis_method"] = "hybrid_llm_static"
        
        return merged

    # Include all static analysis methods from original code_analyzer.py
    def _analyze_ast(self, tree: ast.AST, code: str) -> Dict:
        """Analyze Python AST for compliance patterns"""
        patterns = []
        privacy_concerns = []
        data_collection = []
        age_verification = []
        geolocation = []
        content_moderation = []
        security_findings = []
        
        for node in ast.walk(tree):
            # Function calls analysis
            if isinstance(node, ast.Call):
                pattern = self._analyze_function_call(node, code)
                if pattern:
                    if pattern.pattern_type == "privacy":
                        privacy_concerns.append(pattern)
                    elif pattern.pattern_type == "data_collection":
                        data_collection.append(pattern)
                    elif pattern.pattern_type == "age_verification":
                        age_verification.append(pattern)
                    elif pattern.pattern_type == "geolocation":
                        geolocation.append(pattern)
                    elif pattern.pattern_type == "content_moderation":
                        content_moderation.append(pattern)
                    elif pattern.pattern_type == "security":
                        security_findings.append(pattern)
                    patterns.append(pattern)
            
            # Variable assignments
            elif isinstance(node, ast.Assign):
                pattern = self._analyze_assignment(node, code)
                if pattern:
                    patterns.append(pattern)
                    if pattern.pattern_type == "data_collection":
                        data_collection.append(pattern)
            
            # Import statements
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                pattern = self._analyze_import(node, code)
                if pattern:
                    patterns.append(pattern)
                    security_findings.append(pattern)
        
        return {
            "compliance_patterns": [self._pattern_to_dict(p) for p in patterns],
            "privacy_concerns": [self._pattern_to_dict(p) for p in privacy_concerns],
            "data_collection": [self._pattern_to_dict(p) for p in data_collection],
            "age_verification": [self._pattern_to_dict(p) for p in age_verification],
            "geolocation": [self._pattern_to_dict(p) for p in geolocation],
            "content_moderation": [self._pattern_to_dict(p) for p in content_moderation],
            "security_findings": [self._pattern_to_dict(p) for p in security_findings]
        }

    def _analyze_regex(self, code: str) -> Dict:
        """Fallback regex analysis for non-Python code"""
        patterns = []
        privacy_concerns = []
        data_collection = []
        age_verification = []
        geolocation = []
        content_moderation = []
        security_findings = []
        
        # Privacy patterns
        privacy_regex_patterns = [
            (r'\b(collect|gather|track|monitor|record)\s+\w*\s*(data|information|user)', "data_collection", 0.8),
            (r'\b(personal|private|sensitive)\s+\w*\s*(data|information)', "privacy_data", 0.9),
            (r'\b(cookie|session|tracking|analytics)', "tracking", 0.7),
            (r'\b(consent|permission|opt.?in|opt.?out)', "consent_management", 0.8)
        ]
        
        for pattern, pattern_name, confidence in privacy_regex_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                compliance_pattern = CompliancePattern(
                    pattern_type="privacy",
                    pattern_name=pattern_name,
                    confidence=confidence,
                    location=f"Line {self._get_line_number(code, match.start())}",
                    code_snippet=match.group(),
                    description=f"Privacy-related pattern: {pattern_name}",
                    regulation_hints=["COPPA", "GDPR", "CCPA"]
                )
                patterns.append(compliance_pattern)
                privacy_concerns.append(compliance_pattern)
        
        # Age verification patterns
        age_patterns = [
            (r'\b(age|birthday|birth.?date|dob)\b', "age_data", 0.9),
            (r'\b(verify|check|validate)\s+\w*\s*(age|minor|child)', "age_verification", 0.95),
            (r'\b(under|below|less.?than)\s*(13|16|18|21)', "age_threshold", 0.8),
            (r'\b(parental|parent|guardian)\s+\w*\s*(consent|permission)', "parental_consent", 0.9)
        ]
        
        for pattern, pattern_name, confidence in age_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                compliance_pattern = CompliancePattern(
                    pattern_type="age_verification",
                    pattern_name=pattern_name,
                    confidence=confidence,
                    location=f"Line {self._get_line_number(code, match.start())}",
                    code_snippet=match.group(),
                    description=f"Age verification pattern: {pattern_name}",
                    regulation_hints=["COPPA", "GDPR Article 8", "Age Appropriate Design Code"]
                )
                patterns.append(compliance_pattern)
                age_verification.append(compliance_pattern)
        
        return {
            "compliance_patterns": [self._pattern_to_dict(p) for p in patterns],
            "privacy_concerns": [self._pattern_to_dict(p) for p in privacy_concerns],
            "data_collection": [self._pattern_to_dict(p) for p in data_collection],
            "age_verification": [self._pattern_to_dict(p) for p in age_verification],
            "geolocation": [self._pattern_to_dict(p) for p in geolocation],
            "content_moderation": [self._pattern_to_dict(p) for p in content_moderation],
            "security_findings": [self._pattern_to_dict(p) for p in security_findings]
        }

    def _analyze_function_call(self, node: ast.Call, code: str) -> Optional[CompliancePattern]:
        """Analyze function calls for compliance patterns"""
        func_name = ""
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        # Check for compliance-related function calls
        compliance_functions = {
            "track_user": ("data_collection", "user_tracking", 0.9, ["GDPR", "CCPA"]),
            "collect_data": ("data_collection", "data_collection", 0.9, ["Privacy Laws"]),
            "verify_age": ("age_verification", "age_verification", 0.95, ["COPPA"]),
            "get_location": ("geolocation", "location_access", 0.8, ["Geolocation Privacy"]),
            "moderate_content": ("content_moderation", "content_moderation", 0.8, ["Content Policies"]),
            "encrypt": ("security", "encryption", 0.7, ["Data Security"]),
            "authenticate": ("security", "authentication", 0.7, ["Access Control"])
        }
        
        for pattern_func, (pattern_type, pattern_name, confidence, regulations) in compliance_functions.items():
            if pattern_func.lower() in func_name.lower():
                return CompliancePattern(
                    pattern_type=pattern_type,
                    pattern_name=pattern_name,
                    confidence=confidence,
                    location=f"Line {node.lineno}",
                    code_snippet=func_name,
                    description=f"Function call: {func_name}",
                    regulation_hints=regulations
                )
        
        return None

    def _analyze_assignment(self, node: ast.Assign, code: str) -> Optional[CompliancePattern]:
        """Analyze variable assignments"""
        # Look for privacy-related variable names
        privacy_vars = ["user_data", "personal_info", "age", "location", "tracking_id"]
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                for privacy_var in privacy_vars:
                    if privacy_var in var_name:
                        return CompliancePattern(
                            pattern_type="data_collection",
                            pattern_name="privacy_variable",
                            confidence=0.6,
                            location=f"Line {node.lineno}",
                            code_snippet=target.id,
                            description=f"Privacy-related variable: {target.id}",
                            regulation_hints=["Data Protection Laws"]
                        )
        
        return None

    def _analyze_import(self, node, code: str) -> Optional[CompliancePattern]:
        """Analyze import statements for compliance libraries"""
        compliance_libs = {
            "requests": ("security", "http_requests", 0.5, ["Data Transmission Security"]),
            "sqlite3": ("data_collection", "database", 0.6, ["Data Storage"]),
            "hashlib": ("security", "hashing", 0.7, ["Data Security"]),
            "cryptography": ("security", "encryption", 0.8, ["Data Encryption"]),
            "geoip": ("geolocation", "ip_geolocation", 0.8, ["Geolocation Privacy"])
        }
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                lib_name = alias.name.lower()
                for compliance_lib, (pattern_type, pattern_name, confidence, regulations) in compliance_libs.items():
                    if compliance_lib in lib_name:
                        return CompliancePattern(
                            pattern_type=pattern_type,
                            pattern_name=pattern_name,
                            confidence=confidence,
                            location=f"Line {node.lineno}",
                            code_snippet=alias.name,
                            description=f"Import: {alias.name}",
                            regulation_hints=regulations
                        )
        
        return None

    def _analyze_context(self, context: str, code: str) -> Dict:
        """Analyze context for additional compliance insights"""
        context_patterns = []
        
        # Look for TikTok-specific context
        tiktok_indicators = ["tiktok", "douyin", "bytedance", "social media", "short video"]
        if any(indicator in context.lower() for indicator in tiktok_indicators):
            context_patterns.append({
                "pattern_type": "platform_context",
                "pattern_name": "tiktok_platform",
                "confidence": 0.9,
                "location": "Context",
                "code_snippet": "TikTok platform context",
                "description": "Code appears to be for TikTok platform",
                "regulation_hints": ["COPPA", "State Privacy Laws", "Youth Protection"]
            })
        
        return {
            "compliance_patterns": context_patterns,
            "privacy_concerns": [],
            "data_collection": [],
            "age_verification": [],
            "geolocation": [],
            "content_moderation": [],
            "security_findings": []
        }

    def _merge_analysis(self, analysis1: Dict, analysis2: Dict) -> Dict:
        """Merge two analysis results"""
        merged = analysis1.copy()
        for key in analysis2:
            if key in merged and isinstance(merged[key], list):
                merged[key].extend(analysis2[key])
            elif key not in merged:
                merged[key] = analysis2[key]
        return merged

    def _calculate_risk_score(self, analysis: Dict) -> float:
        """Calculate overall risk score"""
        risk_factors = {
            "privacy_concerns": 0.3,
            "data_collection": 0.25,
            "age_verification": 0.35,
            "geolocation": 0.2,
            "content_moderation": 0.15,
            "security_findings": 0.25
        }
        
        total_risk = 0.0
        max_possible = 0.0
        
        for category, weight in risk_factors.items():
            if category in analysis:
                patterns = analysis[category]
                if patterns:
                    # Calculate average confidence for this category
                    avg_confidence = sum(p.get("confidence", 0.0) for p in patterns) / len(patterns)
                    total_risk += avg_confidence * weight
                    max_possible += weight
        
        return total_risk / max_possible if max_possible > 0 else 0.0

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if analysis.get("age_verification"):
            recommendations.append("Implement robust age verification mechanisms")
            recommendations.append("Consider parental consent requirements for minors")
        
        if analysis.get("privacy_concerns"):
            recommendations.append("Review data collection practices for privacy compliance")
            recommendations.append("Implement clear consent mechanisms")
        
        if analysis.get("geolocation"):
            recommendations.append("Consider data localization requirements")
            recommendations.append("Implement location-based content restrictions")
        
        if analysis.get("security_findings"):
            recommendations.append("Review security implementations")
            recommendations.append("Ensure proper encryption for sensitive data")
        
        if analysis.get("content_moderation"):
            recommendations.append("Implement age-appropriate content filtering")
            recommendations.append("Establish clear content moderation policies")
        
        return recommendations

    def _get_line_number(self, code: str, position: int) -> int:
        """Get line number for a character position"""
        return code[:position].count('\n') + 1

    def _pattern_to_dict(self, pattern: CompliancePattern) -> Dict:
        """Convert CompliancePattern to dictionary"""
        return {
            "pattern_type": pattern.pattern_type,
            "pattern_name": pattern.pattern_name,
            "confidence": pattern.confidence,
            "location": pattern.location,
            "code_snippet": pattern.code_snippet,
            "description": pattern.description,
            "regulation_hints": pattern.regulation_hints,
            "llm_analysis": getattr(pattern, 'llm_analysis', None)
        }

    def _load_compliance_patterns(self) -> Dict:
        """Load compliance patterns library"""
        return {
            "privacy": [
                "data_collection", "user_tracking", "personal_data", "consent_management"
            ],
            "age_verification": [
                "age_check", "minor_protection", "parental_consent", "age_gate"
            ],
            "geolocation": [
                "location_tracking", "geo_restriction", "data_localization"
            ],
            "content_moderation": [
                "content_filtering", "age_appropriate", "harmful_content"
            ],
            "security": [
                "encryption", "authentication", "access_control", "data_protection"
            ]
        }

    def _load_privacy_keywords(self) -> Set[str]:
        """Load privacy-related keywords"""
        return {
            "personal", "private", "sensitive", "confidential",
            "data", "information", "profile", "identity",
            "collect", "gather", "track", "monitor", "record",
            "consent", "permission", "opt-in", "opt-out",
            "cookie", "session", "analytics", "tracking"
        }

    def _load_data_collection_patterns(self) -> Dict:
        """Load data collection patterns"""
        return {
            "user_input": ["input", "form", "field", "text", "upload"],
            "tracking": ["track", "analytics", "pixel", "beacon", "fingerprint"],
            "storage": ["save", "store", "persist", "cache", "database"],
            "transmission": ["send", "post", "api", "request", "sync"]
        }


# Test function to demonstrate the enhanced analyzer
async def test_llm_analyzer():
    """Test the LLM-enhanced code analyzer"""
    print("🧪 Testing LLM-Enhanced Code Analyzer")
    print("=" * 50)
    
    # Sample code for testing
    test_code = '''
def verify_user_age(user_data):
    age = user_data.get('age')
    if age < 13:
        require_parental_consent()
        track_user(user_data, "minor_user")
    elif age < 16:
        apply_privacy_restrictions()
    return age >= 13

def get_user_location(ip_address):
    import geoip
    location = geoip.get_location(ip_address)
    collect_data(location, "geolocation")
    return location
'''
    
    # Test with both LLM and static analysis
    analyzer = LLMCodeAnalyzer(use_llm=True)
    result = analyzer.analyze_code_snippet(
        test_code, 
        context="TikTok age verification and geolocation feature"
    )
    
    print(f"Analysis Method: {result.get('analysis_method', 'unknown')}")
    print(f"Risk Score: {result.get('risk_score', 0):.2f}")
    print(f"Patterns Found: {len(result.get('compliance_patterns', []))}")
    
    if result.get('llm_insights'):
        print("\n🤖 LLM Insights:")
        insights = result['llm_insights']
        print(f"  Assessment: {insights.get('overall_assessment', 'N/A')}")
        print(f"  Key Risks: {', '.join(insights.get('key_risks', []))}")
    
    print(f"\n📋 Recommendations ({len(result.get('recommendations', []))}):")
    for i, rec in enumerate(result.get('recommendations', []), 1):
        print(f"  {i}. {rec}")
    
    return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_llm_analyzer())
        
        # Calculate overall risk score
        analysis["risk_score"] = self._calculate_risk_score(analysis)
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_ast(self, tree: ast.AST, code: str) -> Dict:
        """Analyze Python AST for compliance patterns"""
        patterns = []
        privacy_concerns = []
        data_collection = []
        age_verification = []
        geolocation = []
        content_moderation = []
        security_findings = []
        
        for node in ast.walk(tree):
            # Function calls analysis
            if isinstance(node, ast.Call):
                pattern = self._analyze_function_call(node, code)
                if pattern:
                    if pattern.pattern_type == "privacy":
                        privacy_concerns.append(pattern)
                    elif pattern.pattern_type == "data_collection":
                        data_collection.append(pattern)
                    elif pattern.pattern_type == "age_verification":
                        age_verification.append(pattern)
                    elif pattern.pattern_type == "geolocation":
                        geolocation.append(pattern)
                    elif pattern.pattern_type == "content_moderation":
                        content_moderation.append(pattern)
                    elif pattern.pattern_type == "security":
                        security_findings.append(pattern)
                    patterns.append(pattern)
            
            # Variable assignments
            elif isinstance(node, ast.Assign):
                pattern = self._analyze_assignment(node, code)
                if pattern:
                    patterns.append(pattern)
                    if pattern.pattern_type == "data_collection":
                        data_collection.append(pattern)
            
            # Import statements
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                pattern = self._analyze_import(node, code)
                if pattern:
                    patterns.append(pattern)
                    security_findings.append(pattern)
        
        return {
            "compliance_patterns": [self._pattern_to_dict(p) for p in patterns],
            "privacy_concerns": [self._pattern_to_dict(p) for p in privacy_concerns],
            "data_collection": [self._pattern_to_dict(p) for p in data_collection],
            "age_verification": [self._pattern_to_dict(p) for p in age_verification],
            "geolocation": [self._pattern_to_dict(p) for p in geolocation],
            "content_moderation": [self._pattern_to_dict(p) for p in content_moderation],
            "security_findings": [self._pattern_to_dict(p) for p in security_findings]
        }
    
    def _analyze_regex(self, code: str) -> Dict:
        """Fallback regex analysis for non-Python code"""
        patterns = []
        privacy_concerns = []
        data_collection = []
        age_verification = []
        geolocation = []
        content_moderation = []
        security_findings = []
        
        # Privacy patterns
        privacy_regex_patterns = [
            (r'\b(collect|gather|track|monitor|record)\s+\w*\s*(data|information|user)', "data_collection", 0.8),
            (r'\b(personal|private|sensitive)\s+\w*\s*(data|information)', "privacy_data", 0.9),
            (r'\b(cookie|session|tracking|analytics)', "tracking", 0.7),
            (r'\b(consent|permission|opt.?in|opt.?out)', "consent_management", 0.8)
        ]
        
        for pattern, pattern_name, confidence in privacy_regex_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                compliance_pattern = CompliancePattern(
                    pattern_type="privacy",
                    pattern_name=pattern_name,
                    confidence=confidence,
                    location=f"Line {self._get_line_number(code, match.start())}",
                    code_snippet=match.group(),
                    description=f"Privacy-related pattern: {pattern_name}",
                    regulation_hints=["COPPA", "GDPR", "CCPA"]
                )
                patterns.append(compliance_pattern)
                privacy_concerns.append(compliance_pattern)
        
        # Age verification patterns
        age_patterns = [
            (r'\b(age|birthday|birth.?date|dob)\b', "age_data", 0.9),
            (r'\b(verify|check|validate)\s+\w*\s*(age|minor|child)', "age_verification", 0.95),
            (r'\b(under|below|less.?than)\s*(13|16|18|21)', "age_threshold", 0.8),
            (r'\b(parental|parent|guardian)\s+\w*\s*(consent|permission)', "parental_consent", 0.9)
        ]
        
        for pattern, pattern_name, confidence in age_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                compliance_pattern = CompliancePattern(
                    pattern_type="age_verification",
                    pattern_name=pattern_name,
                    confidence=confidence,
                    location=f"Line {self._get_line_number(code, match.start())}",
                    code_snippet=match.group(),
                    description=f"Age verification pattern: {pattern_name}",
                    regulation_hints=["COPPA", "GDPR Article 8", "Age Appropriate Design Code"]
                )
                patterns.append(compliance_pattern)
                age_verification.append(compliance_pattern)
        
        # Geolocation patterns
        geo_patterns = [
            (r'\b(location|gps|coordinates|latitude|longitude|geolocation)', "location_access", 0.8),
            (r'\b(country|region|state|province|jurisdiction)', "geographic_data", 0.6),
            (r'\b(ip.?address|user.?agent|browser.?info)', "location_inference", 0.7)
        ]
        
        for pattern, pattern_name, confidence in geo_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                compliance_pattern = CompliancePattern(
                    pattern_type="geolocation",
                    pattern_name=pattern_name,
                    confidence=confidence,
                    location=f"Line {self._get_line_number(code, match.start())}",
                    code_snippet=match.group(),
                    description=f"Geolocation pattern: {pattern_name}",
                    regulation_hints=["GDPR", "CCPA", "Data Localization Requirements"]
                )
                patterns.append(compliance_pattern)
                geolocation.append(compliance_pattern)
        
        # Content moderation patterns
        content_patterns = [
            (r'\b(moderate|filter|censor|block|remove)\s+\w*\s*(content|post|message)', "content_moderation", 0.8),
            (r'\b(inappropriate|harmful|violent|adult)\s+\w*\s*(content|material)', "content_classification", 0.7),
            (r'\b(report|flag|complaint)\s+\w*\s*(content|user|violation)', "reporting_system", 0.8)
        ]
        
        for pattern, pattern_name, confidence in content_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                compliance_pattern = CompliancePattern(
                    pattern_type="content_moderation",
                    pattern_name=pattern_name,
                    confidence=confidence,
                    location=f"Line {self._get_line_number(code, match.start())}",
                    code_snippet=match.group(),
                    description=f"Content moderation pattern: {pattern_name}",
                    regulation_hints=["Platform Content Policies", "COPPA Safe Content", "DSA"]
                )
                patterns.append(compliance_pattern)
                content_moderation.append(compliance_pattern)
        
        return {
            "compliance_patterns": [self._pattern_to_dict(p) for p in patterns],
            "privacy_concerns": [self._pattern_to_dict(p) for p in privacy_concerns],
            "data_collection": [self._pattern_to_dict(p) for p in data_collection],
            "age_verification": [self._pattern_to_dict(p) for p in age_verification],
            "geolocation": [self._pattern_to_dict(p) for p in geolocation],
            "content_moderation": [self._pattern_to_dict(p) for p in content_moderation],
            "security_findings": [self._pattern_to_dict(p) for p in security_findings]
        }
    
    def _analyze_function_call(self, node: ast.Call, code: str) -> Optional[CompliancePattern]:
        """Analyze function calls for compliance patterns"""
        func_name = ""
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        # Check for compliance-related function calls
        compliance_functions = {
            "track_user": ("data_collection", "user_tracking", 0.9, ["GDPR", "CCPA"]),
            "collect_data": ("data_collection", "data_collection", 0.9, ["Privacy Laws"]),
            "verify_age": ("age_verification", "age_verification", 0.95, ["COPPA"]),
            "get_location": ("geolocation", "location_access", 0.8, ["Geolocation Privacy"]),
            "moderate_content": ("content_moderation", "content_moderation", 0.8, ["Content Policies"]),
            "encrypt": ("security", "encryption", 0.7, ["Data Security"]),
            "authenticate": ("security", "authentication", 0.7, ["Access Control"])
        }
        
        for pattern_func, (pattern_type, pattern_name, confidence, regulations) in compliance_functions.items():
            if pattern_func.lower() in func_name.lower():
                return CompliancePattern(
                    pattern_type=pattern_type,
                    pattern_name=pattern_name,
                    confidence=confidence,
                    location=f"Line {node.lineno}",
                    code_snippet=func_name,
                    description=f"Function call: {func_name}",
                    regulation_hints=regulations
                )
        
        return None
    
    def _analyze_assignment(self, node: ast.Assign, code: str) -> Optional[CompliancePattern]:
        """Analyze variable assignments"""
        # Look for privacy-related variable names
        privacy_vars = ["user_data", "personal_info", "age", "location", "tracking_id"]
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                for privacy_var in privacy_vars:
                    if privacy_var in var_name:
                        return CompliancePattern(
                            pattern_type="data_collection",
                            pattern_name="privacy_variable",
                            confidence=0.6,
                            location=f"Line {node.lineno}",
                            code_snippet=target.id,
                            description=f"Privacy-related variable: {target.id}",
                            regulation_hints=["Data Protection Laws"]
                        )
        
        return None
    
    def _analyze_import(self, node, code: str) -> Optional[CompliancePattern]:
        """Analyze import statements for compliance libraries"""
        compliance_libs = {
            "requests": ("security", "http_requests", 0.5, ["Data Transmission Security"]),
            "sqlite3": ("data_collection", "database", 0.6, ["Data Storage"]),
            "hashlib": ("security", "hashing", 0.7, ["Data Security"]),
            "cryptography": ("security", "encryption", 0.8, ["Data Encryption"]),
            "geoip": ("geolocation", "ip_geolocation", 0.8, ["Geolocation Privacy"])
        }
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                lib_name = alias.name.lower()
                for compliance_lib, (pattern_type, pattern_name, confidence, regulations) in compliance_libs.items():
                    if compliance_lib in lib_name:
                        return CompliancePattern(
                            pattern_type=pattern_type,
                            pattern_name=pattern_name,
                            confidence=confidence,
                            location=f"Line {node.lineno}",
                            code_snippet=alias.name,
                            description=f"Import: {alias.name}",
                            regulation_hints=regulations
                        )
        
        return None
    
    def _analyze_context(self, context: str, code: str) -> Dict:
        """Analyze context for additional compliance insights"""
        context_patterns = []
        
        # Look for TikTok-specific context
        tiktok_indicators = ["tiktok", "douyin", "bytedance", "social media", "short video"]
        if any(indicator in context.lower() for indicator in tiktok_indicators):
            context_patterns.append({
                "pattern_type": "platform_context",
                "pattern_name": "tiktok_platform",
                "confidence": 0.9,
                "location": "Context",
                "code_snippet": "TikTok platform context",
                "description": "Code appears to be for TikTok platform",
                "regulation_hints": ["COPPA", "State Privacy Laws", "Youth Protection"]
            })
        
        return {
            "compliance_patterns": context_patterns,
            "privacy_concerns": [],
            "data_collection": [],
            "age_verification": [],
            "geolocation": [],
            "content_moderation": [],
            "security_findings": []
        }
    
    def _merge_analysis(self, analysis1: Dict, analysis2: Dict) -> Dict:
        """Merge two analysis results"""
        merged = analysis1.copy()
        for key in analysis2:
            if key in merged and isinstance(merged[key], list):
                merged[key].extend(analysis2[key])
            elif key not in merged:
                merged[key] = analysis2[key]
        return merged
    
    def _calculate_risk_score(self, analysis: Dict) -> float:
        """Calculate overall risk score"""
        risk_factors = {
            "privacy_concerns": 0.3,
            "data_collection": 0.25,
            "age_verification": 0.35,
            "geolocation": 0.2,
            "content_moderation": 0.15,
            "security_findings": 0.25
        }
        
        total_risk = 0.0
        max_possible = 0.0
        
        for category, weight in risk_factors.items():
            if category in analysis:
                patterns = analysis[category]
                if patterns:
                    # Calculate average confidence for this category
                    avg_confidence = sum(p.get("confidence", 0.0) for p in patterns) / len(patterns)
                    total_risk += avg_confidence * weight
                    max_possible += weight
        
        return total_risk / max_possible if max_possible > 0 else 0.0
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if analysis.get("age_verification"):
            recommendations.append("Implement robust age verification mechanisms")
            recommendations.append("Consider parental consent requirements for minors")
        
        if analysis.get("privacy_concerns"):
            recommendations.append("Review data collection practices for privacy compliance")
            recommendations.append("Implement clear consent mechanisms")
        
        if analysis.get("geolocation"):
            recommendations.append("Consider data localization requirements")
            recommendations.append("Implement location-based content restrictions")
        
        if analysis.get("security_findings"):
            recommendations.append("Review security implementations")
            recommendations.append("Ensure proper encryption for sensitive data")
        
        if analysis.get("content_moderation"):
            recommendations.append("Implement age-appropriate content filtering")
            recommendations.append("Establish clear content moderation policies")
        
        return recommendations
    
    def _get_line_number(self, code: str, position: int) -> int:
        """Get line number for a character position"""
        return code[:position].count('\n') + 1
    
    def _pattern_to_dict(self, pattern: CompliancePattern) -> Dict:
        """Convert CompliancePattern to dictionary"""
        return {
            "pattern_type": pattern.pattern_type,
            "pattern_name": pattern.pattern_name,
            "confidence": pattern.confidence,
            "location": pattern.location,
            "code_snippet": pattern.code_snippet,
            "description": pattern.description,
            "regulation_hints": pattern.regulation_hints
        }
    
    def _load_compliance_patterns(self) -> Dict:
        """Load compliance patterns library"""
        return {
            "privacy": [
                "data_collection", "user_tracking", "personal_data", "consent_management"
            ],
            "age_verification": [
                "age_check", "minor_protection", "parental_consent", "age_gate"
            ],
            "geolocation": [
                "location_tracking", "geo_restriction", "data_localization"
            ],
            "content_moderation": [
                "content_filtering", "age_appropriate", "harmful_content"
            ],
            "security": [
                "encryption", "authentication", "access_control", "data_protection"
            ]
        }
    
    def _load_privacy_keywords(self) -> Set[str]:
        """Load privacy-related keywords"""
        return {
            "personal", "private", "sensitive", "confidential",
            "data", "information", "profile", "identity",
            "collect", "gather", "track", "monitor", "record",
            "consent", "permission", "opt-in", "opt-out",
            "cookie", "session", "analytics", "tracking"
        }
    
    def _load_data_collection_patterns(self) -> Dict:
        """Load data collection patterns"""
        return {
            "user_input": ["input", "form", "field", "text", "upload"],
            "tracking": ["track", "analytics", "pixel", "beacon", "fingerprint"],
            "storage": ["save", "store", "persist", "cache", "database"],
            "transmission": ["send", "post", "api", "request", "sync"]
        }
