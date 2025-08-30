"""
Utility functions for compliance analysis
"""

import re
import json
import sys
from typing import List, Dict, Any, Optional


def extract_code_snippets(code: str, patterns: List[str]) -> List[Dict[str, str]]:
    """Extract code snippets that match given patterns"""
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
    """Calculate confidence score based on pattern matches"""
    if total_patterns == 0:
        return base_confidence
    
    pattern_ratio = patterns_found / total_patterns
    confidence = base_confidence + (pattern_ratio * 0.4)
    return min(confidence, 1.0)


def format_compliance_output(result: Dict[str, Any]) -> str:
    """Format compliance analysis result for display"""
    output = []
    output.append(f"🔍 Compliance Analysis: {result.get('feature_name', 'Unknown')}")
    output.append("=" * 50)
    
    # Status
    confidence = result.get('confidence', 0)
    output.append(f"📊 Confidence: {confidence:.2f}")
    output.append(f"⚖️  Needs Compliance: {'Yes' if result.get('needs_compliance_logic', False) else 'No'}")
    output.append(f"🎯 Risk Level: {result.get('risk_level', 'Unknown').upper()}")
    
    # Regulations
    regulations = result.get('applicable_regulations', [])
    if regulations:
        output.append(f"\n📋 Applicable Regulations ({len(regulations)}):")
        for reg in regulations:
            output.append(f"  • {reg.get('regulation', 'Unknown')} (confidence: {reg.get('relevance', 0):.2f})")
    
    # Implementation notes
    notes = result.get('implementation_notes', [])
    if notes:
        output.append(f"\n💡 Implementation Notes:")
        for note in notes:
            output.append(f"  • {note}")
    
    # Action required
    action = result.get('action_required', 'None')
    output.append(f"\n🚀 Action Required: {action}")
    
    return '\n'.join(output)


def log_error(message: str, exception: Optional[Exception] = None):
    """Log error message to stderr"""
    print(f"❌ Error: {message}", file=sys.stderr)
    if exception:
        print(f"   Details: {str(exception)}", file=sys.stderr)


def log_info(message: str):
    """Log info message to stderr"""
    print(f"ℹ️  {message}", file=sys.stderr)


def log_debug(message: str):
    """Log debug message to stderr"""
    print(f"🐛 Debug: {message}", file=sys.stderr)


def safe_json_loads(json_str: str, default: Dict = None) -> Dict:
    """Safely parse JSON string with fallback"""
    if default is None:
        default = {}
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def normalize_pattern_name(name: str) -> str:
    """Normalize pattern name for consistent matching"""
    return re.sub(r'[^\w]+', '_', name.lower()).strip('_')
