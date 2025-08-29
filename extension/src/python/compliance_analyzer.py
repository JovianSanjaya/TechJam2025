#!/usr/bin/env python3
"""
Simplified TikTok Compliance Analyzer for VS Code Extension
This script provides a simplified version of the compliance analysis
that can be easily called from the VS Code extension.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

def analyze_code_for_compliance(code: str, feature_name: str) -> Dict:
    """
    Simple compliance analysis for code snippets
    """
    # Define compliance keywords and patterns
    privacy_keywords = [
        'user_data', 'personal_data', 'age', 'location', 'tracking',
        'geoip', 'collect_user', 'user_profile', 'parental_consent',
        'privacy_restrictions', 'geolocation', 'track_user'
    ]
    
    gdpr_keywords = [
        'gdpr', 'consent', 'data_processing', 'user_consent',
        'personal_information', 'data_collection', 'privacy_policy'
    ]
    
    coppa_keywords = [
        'coppa', 'under_13', 'age_verification', 'parental_consent',
        'child_data', 'minor'
    ]
    
    # Count keyword occurrences
    code_lower = code.lower()
    privacy_score = sum(1 for keyword in privacy_keywords if keyword in code_lower)
    gdpr_score = sum(1 for keyword in gdpr_keywords if keyword in code_lower)
    coppa_score = sum(1 for keyword in coppa_keywords if keyword in code_lower)
    
    total_score = privacy_score + gdpr_score + coppa_score
    
    # Determine compliance requirements
    needs_compliance = total_score > 0
    
    # Calculate risk level
    if total_score >= 5:
        risk_level = "HIGH"
    elif total_score >= 2:
        risk_level = "MEDIUM"
    elif total_score >= 1:
        risk_level = "LOW"
    else:
        risk_level = "MINIMAL"
    
    # Generate applicable regulations
    applicable_regulations = []
    if gdpr_score > 0:
        applicable_regulations.append({
            "name": "GDPR",
            "description": "General Data Protection Regulation",
            "relevance": "Data processing and user consent"
        })
    
    if coppa_score > 0:
        applicable_regulations.append({
            "name": "COPPA",
            "description": "Children's Online Privacy Protection Act",
            "relevance": "Protection of children's data"
        })
    
    if privacy_score > 0:
        applicable_regulations.append({
            "name": "Privacy Framework",
            "description": "General privacy protection requirements",
            "relevance": "User data protection"
        })
    
    # Generate implementation notes
    implementation_notes = []
    if 'age' in code_lower:
        implementation_notes.append("Implement age verification mechanism")
    if 'location' in code_lower or 'geolocation' in code_lower:
        implementation_notes.append("Add location consent prompts")
    if 'user_data' in code_lower or 'personal_data' in code_lower:
        implementation_notes.append("Ensure data encryption and secure storage")
    if 'consent' in code_lower:
        implementation_notes.append("Implement proper consent management")
    
    # Determine action required
    if risk_level == "HIGH":
        action_required = "Immediate compliance review required"
    elif risk_level == "MEDIUM":
        action_required = "Compliance assessment recommended"
    elif risk_level == "LOW":
        action_required = "Basic compliance check needed"
    else:
        action_required = "No immediate action required"
    
    # Calculate confidence score
    confidence = min(0.95, max(0.3, total_score * 0.15 + 0.3))
    
    return {
        "feature_id": f"analysis_{hash(feature_name) % 10000}",
        "feature_name": feature_name,
        "analysis_type": "code_analysis",
        "needs_compliance_logic": needs_compliance,
        "confidence": confidence,
        "risk_level": risk_level,
        "action_required": action_required,
        "applicable_regulations": applicable_regulations,
        "implementation_notes": implementation_notes,
        "code_analysis": {
            "privacy_keywords_found": privacy_score,
            "gdpr_keywords_found": gdpr_score,
            "coppa_keywords_found": coppa_score,
            "total_compliance_indicators": total_score
        },
        "timestamp": datetime.now().isoformat()
    }

def analyze_features(features: List[Dict]) -> Dict:
    """
    Analyze multiple features for compliance
    """
    detailed_results = []
    features_requiring_compliance = 0
    high_risk_features = 0
    human_review_needed = 0
    
    for feature in features:
        result = analyze_code_for_compliance(
            feature.get('code', ''),
            feature.get('feature_name', 'Unknown Feature')
        )
        
        detailed_results.append(result)
        
        if result['needs_compliance_logic']:
            features_requiring_compliance += 1
        
        if result['risk_level'] == 'HIGH':
            high_risk_features += 1
            human_review_needed += 1
        elif result['risk_level'] == 'MEDIUM':
            human_review_needed += 1
    
    # Generate recommendations
    recommendations = []
    if high_risk_features > 0:
        recommendations.append(f"Prioritize {high_risk_features} high-risk features for immediate review")
    if features_requiring_compliance > 0:
        recommendations.append("Implement compliance documentation for identified features")
    if human_review_needed > 0:
        recommendations.append("Schedule legal review for flagged features")
    
    recommendations.extend([
        "Establish regular compliance auditing process",
        "Create developer training on privacy requirements",
        "Implement automated compliance checking in CI/CD pipeline"
    ])
    
    return {
        "analysis_summary": {
            "total_features": len(features),
            "features_requiring_compliance": features_requiring_compliance,
            "high_risk_features": high_risk_features,
            "human_review_needed": human_review_needed,
            "analysis_timestamp": datetime.now().isoformat(),
            "system_version": "VS Code Extension v1.0"
        },
        "detailed_results": detailed_results,
        "recommendations": recommendations[:5],  # Limit to top 5 recommendations
        "audit_trail": [
            {
                "action": "compliance_analysis",
                "timestamp": datetime.now().isoformat(),
                "features_analyzed": len(features),
                "status": "completed"
            }
        ]
    }

def main():
    """
    Main function to handle VS Code extension requests
    """
    try:
        # Read input from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            # If no input from stdin, use sample data for testing
            sample_features = [
                {
                    "id": "test_001",
                    "feature_name": "Sample Feature",
                    "description": "Test feature for compliance analysis",
                    "code": """
def collect_user_data(user_id):
    personal_data = get_user_profile(user_id)
    if user_age < 13:
        require_parental_consent()
    return personal_data
"""
                }
            ]
            result = analyze_features(sample_features)
        else:
            # Parse input JSON
            data = json.loads(input_data)
            features = data.get('features', [])
            result = analyze_features(features)
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
        
    except json.JSONDecodeError as e:
        error_result = {
            "error": f"Invalid JSON input: {str(e)}",
            "status": "failed"
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        error_result = {
            "error": f"Analysis failed: {str(e)}",
            "status": "failed"
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
