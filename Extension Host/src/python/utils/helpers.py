"""
Utility functions for compliance analysis.

This module provides common utility functions used throughout the compliance
analysis system including code extraction, confidence calculation, logging,
and data formatting operations.
"""

import re
import json
import sys
from typing import List, Dict, Any, Optional


def extract_code_snippets(code: str, patterns: List[str]) -> List[Dict[str, str]]:
    """
    Extract code snippets that match given patterns.
    
    Args:
        code: Source code to analyze
        patterns: List of regex patterns to match
        
    Returns:
        List of dictionaries containing matched snippets with context
    """
    snippets = []
    lines = code.split('\n')
    
    for i, line in enumerate(lines):
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Get context (2 lines before and after)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = '\n'.join(lines[start:end])
                
                snippets.append({
                    'line': i + 1,
                    'pattern': pattern,
                    'code': line.strip(),
                    'context': context
                })
    
    return snippets


def calculate_confidence(patterns_found: int, total_patterns: int, base_confidence: float = 0.5) -> float:
    """
    Calculate confidence score based on pattern matches.
    
    Args:
        patterns_found: Number of patterns detected
        total_patterns: Total number of possible patterns
        base_confidence: Base confidence level to start from
        
    Returns:
        Calculated confidence score between 0.0 and 1.0
    """
    if total_patterns == 0:
        return base_confidence
    
    pattern_ratio = patterns_found / total_patterns
    confidence = base_confidence + (pattern_ratio * 0.4)
    return min(confidence, 1.0)


def format_compliance_output(result: Dict[str, Any]) -> str:
    """
    Format compliance analysis result for display.
    
    Args:
        result: Compliance analysis result dictionary
        
    Returns:
        Formatted string representation of the analysis result
    """
    output = []
    output.append(f"Compliance Analysis: {result.get('feature_name', 'Unknown')}")
    output.append("=" * 50)
    
    # Status
    confidence = result.get('confidence', 0)
    output.append(f"Confidence: {confidence:.2f}")
    output.append(f"Needs Compliance: {'Yes' if result.get('needs_compliance_logic', False) else 'No'}")
    output.append(f"Risk Level: {result.get('risk_level', 'Unknown').upper()}")
    
    # Regulations
    regulations = result.get('applicable_regulations', [])
    if regulations:
        output.append(f"\nApplicable Regulations ({len(regulations)}):")
        for reg in regulations:
            output.append(f"  • {reg.get('regulation', 'Unknown')} (confidence: {reg.get('relevance', 0):.2f})")
    
    # Implementation notes
    notes = result.get('implementation_notes', [])
    if notes:
        output.append(f"\nImplementation Notes:")
        for note in notes:
            output.append(f"  • {note}")
    
    # Action required
    action = result.get('action_required', 'None')
    output.append(f"\nAction Required: {action}")
    
    return '\n'.join(output)


def log_error(message: str, exception: Optional[Exception] = None):
    """
    Log error messages to stderr.
    
    Args:
        message: Error message to log
        exception: Optional exception object for additional context
    """
    print(f"ERROR: {message}", file=sys.stderr)
    if exception:
        print(f"       Details: {str(exception)}", file=sys.stderr)


def log_info(message: str):
    """
    Log informational messages to stderr.
    
    Args:
        message: Information message to log
    """
    print(f"INFO: {message}", file=sys.stderr)


def log_debug(message: str):
    """
    Log debug messages to stderr.
    
    Args:
        message: Debug message to log
    """
    print(f"DEBUG: {message}", file=sys.stderr)


def safe_json_loads(json_str: str, default: Dict = None) -> Dict:
    """
    Safely parse JSON string with fallback.
    
    Args:
        json_str: JSON string to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed dictionary or default value
    """
    if default is None:
        default = {}
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def normalize_pattern_name(name: str) -> str:
    """
    Normalize pattern name for consistent matching.
    
    Args:
        name: Pattern name to normalize
        
    Returns:
        Normalized pattern name with consistent formatting
    """
    return re.sub(r'[^\w]+', '_', name.lower()).strip('_')
