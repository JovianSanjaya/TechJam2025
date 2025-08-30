#!/usr/bin/env python3
"""
Enhanced TikTok Compliance Analyzer for VS Code Extension
This script provides LLM-enhanced compliance analysis with RAG support
that can be called from the VS Code extension.

Refactored to use modular service architecture following FE patterns.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to use new modular services first
try:
    from services import ComplianceService
    from analyzers import SimpleAnalyzer
    from config import AnalysisConfig
    MODULAR_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: New modular services not available: {e}", file=sys.stderr)
    MODULAR_SERVICES_AVAILABLE = False

# Fallback to legacy services
try:
    from code_analyzer_llm_clean import LLMCodeAnalyzer
    from vector_store import get_vector_store
    from config import ComplianceConfig
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: LLM components not available: {e}", file=sys.stderr)
    LLM_AVAILABLE = False

def analyze_code_for_compliance_simple(code: str, feature_name: str) -> Dict:
    """
    Simple fallback compliance analysis for code snippets (when LLM is not available)
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
        "analysis_type": "simple_static",
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

def analyze_code_for_compliance_llm(code: str, feature_name: str, analyzer: LLMCodeAnalyzer) -> Dict:
    """
    Enhanced LLM-based compliance analysis with RAG support
    """
    try:
        # Use the LLM analyzer
        result = analyzer.analyze_code_snippet(code, context=f"Feature: {feature_name}")
        
        # Convert the LLM analyzer result to the expected format
        if isinstance(result, dict):
            # Extract meaningful data from the LLM analyzer result
            compliance_patterns = result.get('compliance_patterns', [])
            privacy_concerns = result.get('privacy_concerns', [])
            code_issues = result.get('code_issues', [])
            
            # Use adjusted risk score if available
            risk_score = result.get('risk_score', 50)
            confidence_adj = result.get('confidence_adjustments', {})
            if confidence_adj.get('adjusted_risk_score'):
                risk_score = confidence_adj['adjusted_risk_score'] * 100  # Convert to 0-100 scale
            
            # Determine risk level based on findings and adjusted risk score
            total_findings = len(compliance_patterns) + len(privacy_concerns) + len(code_issues)
            # Determine risk level based on LLM insights and code issues
            critical_issues = [issue for issue in code_issues if isinstance(issue, dict) and issue.get('severity') == 'critical']
            high_issues = [issue for issue in code_issues if isinstance(issue, dict) and issue.get('severity') == 'high']
            
            if risk_score > 80 or len(critical_issues) > 0 or total_findings >= 5:
                risk_level = "HIGH"
            elif risk_score > 50 or len(high_issues) > 0 or total_findings >= 2:
                risk_level = "MEDIUM"
            elif risk_score > 30 or total_findings >= 1:
                risk_level = "LOW"
            else:
                risk_level = "MINIMAL"
            
            # Extract applicable regulations
            applicable_regulations = []
            for pattern in compliance_patterns:
                if isinstance(pattern, dict) and 'regulation_hints' in pattern:
                    for reg in pattern['regulation_hints']:
                        if reg not in [r.get('name', '') for r in applicable_regulations]:
                            applicable_regulations.append({
                                "name": reg,
                                "description": f"Regulation: {reg}",
                                "relevance": "Detected in code analysis"
                            })
            
            # Extract implementation notes and code issues
            implementation_notes = result.get('recommendations', [])
            code_issues = result.get('code_issues', [])
            
            # Format code issues for the extension
            formatted_code_issues = []
            for issue in code_issues:
                if isinstance(issue, dict):
                    formatted_issue = {
                        "line_reference": issue.get('line_reference', 'Unknown'),
                        "problematic_code": issue.get('problematic_code', ''),
                        "violation_type": issue.get('violation_type', 'compliance'),
                        "severity": issue.get('severity', 'medium'),
                        "regulation_violated": issue.get('regulation_violated', 'General'),
                        "fix_description": issue.get('fix_description', ''),
                        "suggested_replacement": issue.get('suggested_replacement', ''),
                        "testing_requirements": issue.get('testing_requirements', '')
                    }
                    formatted_code_issues.append(formatted_issue)
            
            return {
                "feature_id": f"analysis_{hash(feature_name) % 10000}",
                "feature_name": feature_name,
                "analysis_type": result.get('analysis_method', 'hybrid_llm_static'),
                "needs_compliance_logic": total_findings > 0 or risk_score > 30,
                "confidence": min(max(risk_score / 100.0, 0.1), 1.0),
                "risk_level": risk_level,
                "action_required": "Compliance review recommended" if total_findings > 0 else "No immediate action required",
                "applicable_regulations": applicable_regulations,
                "implementation_notes": implementation_notes[:5],  # Limit to 5 notes
                "code_issues": formatted_code_issues,  # New: specific code problems
                "llm_analysis": {
                    "llm_insights": result.get('llm_insights', {}),
                    "confidence_adjustments": result.get('confidence_adjustments', {}),
                    "total_findings": total_findings,
                    "risk_score": risk_score
                },
                "static_analysis": {
                    "compliance_patterns": len(compliance_patterns),
                    "privacy_concerns": len(privacy_concerns),
                    "data_collection": len(result.get('data_collection', [])),
                    "security_findings": len(result.get('security_findings', []))
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Fallback formatting if result is unexpected
            print(f"Unexpected LLM result format: {type(result)}", file=sys.stderr)
            return analyze_code_for_compliance_simple(code, feature_name)
    except Exception as e:
        print(f"LLM analysis failed: {e}", file=sys.stderr)
        # Fallback to simple analysis
        return analyze_code_for_compliance_simple(code, feature_name)

def analyze_features(features: List[Dict]) -> Dict:
    """
    Analyze multiple features for compliance using new modular services when available,
    with fallback to legacy LLM+RAG analysis
    """
    detailed_results = []
    features_requiring_compliance = 0
    high_risk_features = 0
    human_review_needed = 0
    
    # Try to use new modular services first
    if MODULAR_SERVICES_AVAILABLE:
        try:
            # Initialize compliance service
            config = AnalysisConfig()
            compliance_service = ComplianceService(config)
            
            for feature in features:
                result = compliance_service.analyze_code(
                    code=feature.get('code', ''),
                    feature_name=feature.get('feature_name', 'Unknown Feature')
                )
                
                # Convert to legacy format for backward compatibility
                legacy_result = _convert_to_legacy_format(result)
                detailed_results.append(legacy_result)
                
                if legacy_result['needs_compliance_logic']:
                    features_requiring_compliance += 1
                
                if legacy_result['risk_level'] == 'HIGH':
                    high_risk_features += 1
                    human_review_needed += 1
                elif legacy_result['risk_level'] == 'MEDIUM':
                    human_review_needed += 1
            
            analysis_type = "modular_service"
            print("Using new modular compliance services", file=sys.stderr)
            
        except Exception as e:
            print(f"Modular services failed, falling back to legacy: {e}", file=sys.stderr)
            return _analyze_features_legacy(features)
    else:
        return _analyze_features_legacy(features)
    
    # Generate recommendations
    recommendations = _generate_recommendations(detailed_results, high_risk_features, 
                                               features_requiring_compliance, human_review_needed)
    
    return {
        "analysis_summary": {
            "total_features": len(features),
            "features_requiring_compliance": features_requiring_compliance,
            "high_risk_features": high_risk_features,
            "human_review_needed": human_review_needed,
            "analysis_timestamp": datetime.now().isoformat(),
            "system_version": f"VS Code Extension v2.0 ({analysis_type})",
            "rag_enabled": True,  # Always enabled in modular services
            "llm_enabled": True   # Always enabled in modular services
        },
        "detailed_results": detailed_results,
        "recommendations": recommendations[:5],
        "audit_trail": [
            {
                "action": "compliance_analysis",
                "timestamp": datetime.now().isoformat(),
                "features_analyzed": len(features),
                "analysis_type": analysis_type,
                "status": "completed"
            }
        ]
    }

def _convert_to_legacy_format(result) -> Dict:
    """Convert new ComplianceResult format to legacy format for backward compatibility"""
    # Convert risk level to uppercase
    risk_level = result.risk_level.upper() if hasattr(result, 'risk_level') else 'MEDIUM'
    
    # Convert regulations to legacy format
    applicable_regulations = []
    if hasattr(result, 'applicable_regulations'):
        for reg in result.applicable_regulations:
            if isinstance(reg, dict):
                applicable_regulations.append({
                    "name": reg.get('regulation', 'Unknown'),
                    "description": reg.get('regulation', 'Unknown'),
                    "relevance": reg.get('content_excerpt', 'Detected in analysis')
                })
    
    # Generate action required text
    action_required = "No immediate action required"
    if risk_level == "HIGH":
        action_required = "Immediate compliance review required"
    elif risk_level == "MEDIUM":
        action_required = "Compliance assessment recommended"
    elif risk_level == "LOW":
        action_required = "Basic compliance check needed"
    
    return {
        "feature_id": f"analysis_{hash(result.feature_name) % 10000}",
        "feature_name": result.feature_name,
        "analysis_type": "modular_service",
        "needs_compliance_logic": result.needs_compliance_logic,
        "confidence": result.confidence,
        "risk_level": risk_level,
        "action_required": action_required,
        "applicable_regulations": applicable_regulations,
        "implementation_notes": result.implementation_notes,
        "llm_analysis": {
            "llm_insights": result.llm_analysis.__dict__ if result.llm_analysis else {},
            "total_findings": len(result.patterns) if hasattr(result, 'patterns') else 0,
            "risk_score": result.confidence * 100
        },
        "timestamp": result.timestamp
    }

def _analyze_features_legacy(features: List[Dict]) -> Dict:
    """Legacy analysis using original LLM+RAG approach"""
    detailed_results = []
    features_requiring_compliance = 0
    high_risk_features = 0
    human_review_needed = 0
    
    # Initialize LLM analyzer with RAG if available
    analyzer = None
    vector_store = None
    
    if LLM_AVAILABLE:
        try:
            # Initialize vector store for RAG
            vector_store = get_vector_store()
            if vector_store:
                # Load legal documents if available
                legal_docs_path = os.path.join(os.path.dirname(__file__), 'legal_documents.json')
                if os.path.exists(legal_docs_path):
                    with open(legal_docs_path, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)

                        # support both formats: a list of documents, or {"metadata":..., "documents": [ ... ]}
                        if isinstance(loaded, dict) and isinstance(loaded.get('documents'), list):
                            legal_docs = loaded.get('documents', [])
                        elif isinstance(loaded, list):
                            legal_docs = loaded
                        elif isinstance(loaded, dict):
                            # single-document file
                            legal_docs = [loaded]
                        else:
                            legal_docs = []

                        if legal_docs:
                            # Preferred bulk API: add_documents expects a list of document dicts
                            try:
                                vector_store.add_documents(legal_docs)
                            except AttributeError:
                                # Older/alternate API: try per-document add_document(doc_content, metadata)
                                for doc in legal_docs:
                                    try:
                                        if hasattr(vector_store, 'add_document'):
                                            vector_store.add_document(doc.get('content', '') or doc.get('sections', ''), doc.get('metadata', {}))
                                        else:
                                            # as a last resort try adding as a single-item bulk
                                            vector_store.add_documents([doc])
                                    except Exception as e:
                                        print(f"Error adding doc to vector store: {e}", file=sys.stderr)
                        # Report how many documents we attempted to load (vector store may have filtered empties)
                        try:
                            loaded_count = vector_store.get_document_count()
                        except Exception:
                            loaded_count = len(legal_docs) if isinstance(legal_docs, list) else 0
                        print(f"Loaded {loaded_count} legal documents for RAG", file=sys.stderr)
            
            # Initialize LLM analyzer with vector store
            analyzer = LLMCodeAnalyzer(use_llm=True, force_llm=True, vector_store=vector_store)
            print("Using LLM+RAG analysis", file=sys.stderr)
        except Exception as e:
            print(f"Failed to initialize LLM analyzer: {e}", file=sys.stderr)
            analyzer = None
    
    if not analyzer:
        print("Using simple static analysis (fallback)", file=sys.stderr)
    
    for feature in features:
        if analyzer:
            result = analyze_code_for_compliance_llm(
                feature.get('code', ''),
                feature.get('feature_name', 'Unknown Feature'),
                analyzer
            )
        else:
            result = analyze_code_for_compliance_simple(
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
    recommendations = _generate_recommendations(detailed_results, high_risk_features, 
                                               features_requiring_compliance, human_review_needed)
    
    analysis_type = "hybrid_llm_rag" if (analyzer and vector_store) else "llm_only" if analyzer else "static_only"
    
    return {
        "analysis_summary": {
            "total_features": len(features),
            "features_requiring_compliance": features_requiring_compliance,
            "high_risk_features": high_risk_features,
            "human_review_needed": human_review_needed,
            "analysis_timestamp": datetime.now().isoformat(),
            "system_version": f"VS Code Extension v1.0 ({analysis_type})",
            "rag_enabled": vector_store is not None,
            "llm_enabled": analyzer is not None
        },
        "detailed_results": detailed_results,
        "recommendations": recommendations[:5],
        "audit_trail": [
            {
                "action": "compliance_analysis",
                "timestamp": datetime.now().isoformat(),
                "features_analyzed": len(features),
                "analysis_type": analysis_type,
                "status": "completed"
            }
        ]
    }

def _generate_recommendations(detailed_results: List[Dict], high_risk_features: int, 
                            features_requiring_compliance: int, human_review_needed: int) -> List[str]:
    """Generate recommendations based on analysis results"""
    recommendations = []
    
    # Extract AI-generated recommendations from detailed results
    for result in detailed_results:
        if result.get('llm_analysis', {}).get('llm_insights', {}).get('immediate_actions'):
            for action in result['llm_analysis']['llm_insights']['immediate_actions']:
                if action not in recommendations:
                    recommendations.append(f"🚨 CRITICAL: {action}")
        
        if result.get('llm_analysis', {}).get('llm_insights', {}).get('implementation_suggestions'):
            for suggestion in result['llm_analysis']['llm_insights']['implementation_suggestions'][:3]:
                if suggestion not in recommendations:
                    recommendations.append(f"💡 {suggestion}")
        
        # Extract enhanced recommendations from LLM
        if result.get('implementation_notes'):
            for note in result['implementation_notes'][:2]:  # Limit to avoid duplication
                if isinstance(note, str) and note not in recommendations:
                    recommendations.append(note)
    
    # Add generic recommendations only if no AI recommendations found
    if len(recommendations) < 3:
        if high_risk_features > 0:
            recommendations.append(f"⚠️ Prioritize {high_risk_features} high-risk features for immediate review")
        if features_requiring_compliance > 0:
            recommendations.append("📋 Implement compliance documentation for identified features")
        if human_review_needed > 0:
            recommendations.append("👨‍💼 Schedule legal review for flagged features")
    
    return recommendations
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
