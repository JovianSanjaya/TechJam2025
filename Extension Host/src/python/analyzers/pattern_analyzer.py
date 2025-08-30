"""
Pattern-based analyzer for compliance patterns.

This module provides pattern detection capabilities for identifying compliance
issues in source code using regex, AST analysis, and keyword matching.
"""

import re
import ast
import sys
import os
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compliance_types.compliance_types import CompliancePattern
from utils.helpers import extract_code_snippets, normalize_pattern_name


class PatternAnalyzer:
    """
    Analyzes code for compliance patterns using rules and regex.
    
    Provides multiple detection methods including regex-based pattern matching,
    AST analysis for Python code, and keyword-based detection to identify
    potential compliance issues in source code.
    """
    
    def __init__(self):
        """Initialize the pattern analyzer with compliance patterns and keywords."""
        self.compliance_patterns = self._load_compliance_patterns()
        self.privacy_keywords = self._load_privacy_keywords()
        self.data_collection_patterns = self._load_data_collection_patterns()
    
    def find_patterns(self, code: str) -> List[CompliancePattern]:
        """
        Find all compliance patterns in the provided code.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of CompliancePattern objects representing detected patterns
        """
        patterns = []
        
        # Find regex-based patterns
        patterns.extend(self._find_regex_patterns(code))
        
        # Find AST-based patterns (for Python code)
        patterns.extend(self._find_ast_patterns(code))
        
        # Find keyword-based patterns
        patterns.extend(self._find_keyword_patterns(code))
        
        return patterns
    
    def _find_regex_patterns(self, code: str) -> List[CompliancePattern]:
        """
        Find patterns using regex matching.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of patterns found via regex matching
        """
        patterns = []
        
        for pattern_name, pattern_config in self.compliance_patterns.items():
            regex = pattern_config.get('regex')
            if not regex:
                continue
                
            matches = re.finditer(regex, code, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                # Get line number
                line_num = code[:match.start()].count('\n') + 1
                
                pattern = CompliancePattern(
                    pattern_type="regex",
                    pattern_name=pattern_name,
                    confidence=pattern_config.get('confidence', 0.7),
                    location=f"line {line_num}",
                    code_snippet=match.group(0),
                    description=pattern_config.get('description', ''),
                    regulation_hints=pattern_config.get('regulations', [])
                )
                patterns.append(pattern)
        
        return patterns
    
    def _find_ast_patterns(self, code: str) -> List[CompliancePattern]:
        """Find patterns using AST analysis (Python-specific)"""
        patterns = []
        
        try:
            tree = ast.parse(code)
            
            # Look for specific function calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    
                    if func_name in ['collect_user_data', 'track_user', 'get_location']:
                        pattern = CompliancePattern(
                            pattern_type="ast_call",
                            pattern_name=f"data_collection_{func_name}",
                            confidence=0.8,
                            location=f"line {node.lineno}",
                            code_snippet=func_name,
                            description=f"Data collection function: {func_name}",
                            regulation_hints=['GDPR', 'COPPA']
                        )
                        patterns.append(pattern)
                
                # Look for variable assignments that might indicate data collection
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id.lower()
                            if any(keyword in var_name for keyword in ['age', 'location', 'personal', 'user_data']):
                                pattern = CompliancePattern(
                                    pattern_type="ast_assignment",
                                    pattern_name=f"data_variable_{var_name}",
                                    confidence=0.6,
                                    location=f"line {node.lineno}",
                                    code_snippet=var_name,
                                    description=f"Data-related variable: {var_name}",
                                    regulation_hints=['GDPR', 'COPPA']
                                )
                                patterns.append(pattern)
        
        except (SyntaxError, TypeError):
            # Not valid Python code, skip AST analysis
            pass
        
        return patterns
    
    def _find_keyword_patterns(self, code: str) -> List[CompliancePattern]:
        """Find patterns based on privacy-related keywords"""
        patterns = []
        code_lower = code.lower()
        
        # Check for privacy keywords
        for category, keywords in self.privacy_keywords.items():
            for keyword in keywords:
                if keyword in code_lower:
                    # Find all occurrences
                    start = 0
                    while True:
                        pos = code_lower.find(keyword, start)
                        if pos == -1:
                            break
                        
                        line_num = code[:pos].count('\n') + 1
                        
                        pattern = CompliancePattern(
                            pattern_type="keyword",
                            pattern_name=f"{category}_{normalize_pattern_name(keyword)}",
                            confidence=0.5,
                            location=f"line {line_num}",
                            code_snippet=keyword,
                            description=f"{category.title()} keyword: {keyword}",
                            regulation_hints=self._get_regulations_for_category(category)
                        )
                        patterns.append(pattern)
                        start = pos + 1
        
        return patterns
    
    def _load_compliance_patterns(self) -> Dict:
        """Load regex-based compliance patterns"""
        return {
            'age_verification': {
                'regex': r'(age[_\s]*verif|check[_\s]*age|verify[_\s]*age|under[_\s]*\d+)',
                'confidence': 0.8,
                'description': 'Age verification logic',
                'regulations': ['COPPA', 'Utah Social Media Act']
            },
            'data_collection': {
                'regex': r'(collect[_\s]*data|gather[_\s]*info|track[_\s]*user|store[_\s]*personal)',
                'confidence': 0.7,
                'description': 'Data collection activity',
                'regulations': ['GDPR', 'CCPA', 'COPPA']
            },
            'location_tracking': {
                'regex': r'(geo[_\s]*location|gps[_\s]*coord|track[_\s]*location|user[_\s]*location)',
                'confidence': 0.8,
                'description': 'Location tracking functionality',
                'regulations': ['GDPR', 'CCPA']
            },
            'parental_consent': {
                'regex': r'(parent[_\s]*consent|guardian[_\s]*approval|parental[_\s]*permission)',
                'confidence': 0.9,
                'description': 'Parental consent mechanism',
                'regulations': ['COPPA']
            }
        }
    
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
    
    def _load_data_collection_patterns(self) -> List[str]:
        """Load data collection patterns"""
        return [
            'collect', 'gather', 'store', 'save', 'record',
            'capture', 'obtain', 'acquire', 'retrieve', 'fetch'
        ]
    
    def _get_regulations_for_category(self, category: str) -> List[str]:
        """Get applicable regulations for a privacy category"""
        regulation_map = {
            'personal_data': ['GDPR', 'CCPA', 'COPPA'],
            'tracking': ['GDPR', 'CCPA'],
            'age_related': ['COPPA', 'Utah Social Media Act'],
            'location': ['GDPR', 'CCPA'],
            'consent': ['GDPR', 'CCPA', 'COPPA']
        }
        return regulation_map.get(category, ['GDPR'])
