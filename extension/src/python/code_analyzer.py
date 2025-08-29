import ast
import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass

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

class CodeAnalyzer:
    """Analyzes code for compliance patterns and requirements"""
    
    def __init__(self):
        self.compliance_patterns = self._load_compliance_patterns()
        self.privacy_keywords = self._load_privacy_keywords()
        self.data_collection_patterns = self._load_data_collection_patterns()
    
    def analyze_code_snippet(self, code: str, context: str = "") -> Dict:
        """Analyze a code snippet for compliance patterns"""
        analysis = {
            "compliance_patterns": [],
            "privacy_concerns": [],
            "data_collection": [],
            "age_verification": [],
            "geolocation": [],
            "content_moderation": [],
            "security_findings": [],
            "risk_score": 0.0,
            "recommendations": []
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
