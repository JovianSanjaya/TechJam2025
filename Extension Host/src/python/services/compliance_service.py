"""
Main compliance analysis service that orchestrates all analysis components.

This module provides the primary interface for compliance analysis by coordinating
pattern analysis, RAG context retrieval, and LLM-based analysis to produce
comprehensive compliance assessments.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import compliance_types.compliance_types as ct
from analyzers.pattern_analyzer import PatternAnalyzer
from analyzers.simple_analyzer import SimpleAnalyzer
from services.llm_service import LLMService
from services.rag_service import RAGService
from utils.helpers import log_info, log_error, calculate_confidence


class ComplianceService:
    """
    Main service that orchestrates compliance analysis.
    
    Coordinates multiple analysis components including pattern detection,
    RAG context retrieval, and LLM-based analysis to provide comprehensive
    compliance assessments for code features.
    """
    
    def __init__(self, config: ct.AnalysisConfig = None, vector_store=None):
        """
        Initialize the compliance service with optional configuration.
        
        Args:
            config: Analysis configuration settings
            vector_store: Optional vector store for RAG operations
        """
        self.config = config or ct.AnalysisConfig()
        
        # Initialize services based on configuration
        self.llm_service = LLMService() if self.config.use_llm else None
        self.rag_service = RAGService(vector_store) if self.config.use_rag else None
        
        # Initialize analyzers
        self.pattern_analyzer = PatternAnalyzer()
        self.simple_analyzer = SimpleAnalyzer()
        
        log_info("ComplianceService initialized")
        log_info(f"LLM service: {'available' if self.llm_service and self.llm_service.is_available() else 'unavailable'}")
        log_info(f"RAG service: {'available' if self.rag_service and self.rag_service.is_available() else 'unavailable'}")
    
    def analyze_code(self, code: str, feature_name: str) -> ct.ComplianceResult:
        """
        Perform comprehensive compliance analysis on the provided code.
        
        Args:
            code: Source code to analyze
            feature_name: Name of the feature being analyzed
            
        Returns:
            ComplianceResult containing analysis findings and recommendations
        """
        log_info(f"Starting analysis for feature: {feature_name}")
        
        try:
            # Step 1: Pattern analysis (always executed)
            try:
                patterns = self.pattern_analyzer.find_patterns(code)
                log_info(f"Pattern analysis found {len(patterns)} compliance patterns")
            except Exception as e:
                log_error(f"Pattern analysis failed: {e}")
                patterns = []
            
            # Step 2: RAG context retrieval
            rag_context = ""
            try:
                if self.rag_service and self.rag_service.is_available():
                    query = f"{feature_name} {code[:500]}"  # Limit query length
                    rag_context = self.rag_service.retrieve_relevant_context(query)
                    log_info("RAG context retrieved successfully")
            except Exception as e:
                log_error(f"RAG context retrieval failed: {e}")
                rag_context = ""
            
            # Step 3: LLM analysis (if available)
            llm_response = None
            try:
                if self.llm_service and self.llm_service.is_available():
                    llm_response = self.llm_service.analyze_code(code, feature_name, rag_context)
                    if llm_response:
                        log_info("LLM analysis completed successfully")
                        # Merge LLM patterns with rule-based patterns
                        llm_patterns = self._convert_llm_patterns(llm_response.enhanced_patterns)
                        patterns.extend(llm_patterns)
            except Exception as e:
                log_error(f"LLM analysis failed: {e}")
                llm_response = None
            
            # Step 4: Generate final result
            try:
                if llm_response and len(patterns) > 0:
                    # Use enhanced analysis when LLM is available
                    result = self._generate_enhanced_result(feature_name, patterns, llm_response, code)
                else:
                    # Fallback to simple analysis
                    log_info("Using simple analysis fallback")
                    result = self.simple_analyzer.analyze(code, feature_name, patterns)
            except Exception as e:
                log_error(f"Result generation failed: {e}")
                # Create a minimal fallback result
                result = ct.ComplianceResult(
                    feature_name=feature_name,
                    needs_compliance_logic=False,
                    confidence=0.2,
                    reasoning=[f"Fallback due to analysis error: {str(e)}"],
                    applicable_regulations=[],
                    action_required="MANUAL_REVIEW",
                    human_review_needed=True,
                    risk_level="medium",
                    implementation_notes=["Manual review recommended due to analysis error"],
                    patterns=[],
                    llm_analysis=None,
                    timestamp=datetime.now().isoformat()
                )
            
            log_info(f"Analysis complete: {result.risk_level} risk level, confidence: {result.confidence:.2f}")
            return result
            
        except Exception as e:
            log_error(f"Analysis failed for {feature_name}: {str(e)}", e)
            # Return error result
            return ct.ComplianceResult(
                feature_name=feature_name,
                needs_compliance_logic=True,
                confidence=0.1,
                reasoning=[f"Analysis failed: {str(e)}"],
                applicable_regulations=[],
                action_required="MANUAL_REVIEW",
                human_review_needed=True,
                risk_level="high",
                implementation_notes=["Manual review required due to analysis error"],
                patterns=[],
                llm_analysis=None,
                timestamp=datetime.now().isoformat()
            )
    
    def _convert_llm_patterns(self, llm_patterns: List[Dict]) -> List[ct.CompliancePattern]:
        """
        Convert LLM response patterns to CompliancePattern objects.
        
        Args:
            llm_patterns: List of pattern dictionaries from LLM response
            
        Returns:
            List of CompliancePattern objects
        """
        patterns = []
        
        for pattern_data in llm_patterns:
            if isinstance(pattern_data, dict):
                pattern = ct.CompliancePattern(
                    pattern_type=pattern_data.get('pattern_type', 'llm'),
                    pattern_name=pattern_data.get('pattern_name', 'unknown'),
                    confidence=pattern_data.get('confidence', 0.5),
                    location=pattern_data.get('location', 'unknown'),
                    code_snippet=pattern_data.get('code_snippet', ''),
                    description=pattern_data.get('description', ''),
                    regulation_hints=pattern_data.get('regulation_hints', []),
                    llm_analysis=pattern_data.get('llm_analysis'),
                    severity=pattern_data.get('severity'),
                    legal_basis=pattern_data.get('legal_basis')
                )
                patterns.append(pattern)
        
        return patterns
    
    def _generate_enhanced_result(self, feature_name: str, patterns: List[ct.CompliancePattern], 
                                llm_response, code: str) -> ct.ComplianceResult:
        """
        Generate enhanced compliance result using LLM insights.
        
        Args:
            feature_name: Name of the feature being analyzed
            patterns: List of compliance patterns found
            llm_response: LLM analysis response
            code: Source code being analyzed
            
        Returns:
            Enhanced ComplianceResult with LLM insights
        """
        
        # Extract regulations from patterns and LLM response
        regulations = set()
        for pattern in patterns:
            regulations.update(pattern.regulation_hints)
        
        # Convert to regulation format expected by result
        applicable_regulations = []
        for reg in regulations:
            applicable_regulations.append({
                'regulation': reg,
                'relevance': 0.8,  # Default relevance score
                'content_excerpt': f"Regulation {reg} applies to this feature",
                'requirements': [reg],
                'jurisdiction': 'Various',
                'compliance_risk': 'medium',
                'legal_basis': f"{reg} compliance requirements"
            })
        
        # Calculate risk level based on patterns and LLM insights
        risk_level = self._calculate_risk_level(patterns, llm_response)
        
        # Calculate confidence score
        base_confidence = 0.7 if llm_response else 0.5
        pattern_confidence = len(patterns) * 0.1
        confidence = min(base_confidence + pattern_confidence, 1.0)
        
        # Generate implementation notes
        implementation_notes = []
        if llm_response and llm_response.enhanced_recommendations:
            implementation_notes.extend(llm_response.enhanced_recommendations)
        
        # Add pattern-based notes
        for pattern in patterns:
            if pattern.description:
                implementation_notes.append(f"Pattern: {pattern.description}")
        
        # Determine action required based on risk level
        if risk_level == "high":
            action_required = "IMPLEMENT_COMPLIANCE"
        elif risk_level == "medium":
            action_required = "REVIEW_REQUIRED"
        else:
            action_required = "MONITOR"
        
        return ct.ComplianceResult(
            feature_name=feature_name,
            needs_compliance_logic=len(applicable_regulations) > 0,
            confidence=confidence,
            reasoning=[
                f"Found {len(patterns)} compliance patterns",
                f"LLM analysis available: {'Yes' if llm_response else 'No'}",
                f"Risk level: {risk_level}"
            ],
            applicable_regulations=applicable_regulations,
            action_required=action_required,
            human_review_needed=risk_level == "high",
            risk_level=risk_level,
            implementation_notes=implementation_notes,
            patterns=patterns,
            llm_analysis=llm_response,
            timestamp=datetime.now().isoformat()
        )
    
    def _calculate_risk_level(self, patterns: List[ct.CompliancePattern], llm_response) -> str:
        """
        Calculate risk level based on patterns and LLM analysis.
        
        Args:
            patterns: List of compliance patterns found
            llm_response: LLM analysis response
            
        Returns:
            Risk level as string: 'low', 'medium', or 'high'
        """
        risk_scores = []
        
        # Pattern-based risk assessment
        high_risk_patterns = sum(1 for p in patterns if p.confidence > 0.8)
        medium_risk_patterns = sum(1 for p in patterns if 0.5 <= p.confidence <= 0.8)
        
        if high_risk_patterns >= 2:
            risk_scores.append("high")
        elif high_risk_patterns >= 1 or medium_risk_patterns >= 3:
            risk_scores.append("medium")
        else:
            risk_scores.append("low")
        
        # LLM-based risk assessment
        if llm_response:
            try:
                insights = llm_response.compliance_insights
                # Handle case where insights might be a string or dict
                if isinstance(insights, dict):
                    key_risks = insights.get('key_risks', [])
                    critical_findings = insights.get('critical_findings', [])
                    overall_assessment = insights.get('overall_assessment', '')
                    
                    # Calculate risk based on LLM insights
                    total_risks = len(key_risks) + len(critical_findings)
                    if total_risks >= 3 or 'critical' in overall_assessment.lower():
                        risk_scores.append("high")
                    elif total_risks >= 2 or 'high' in overall_assessment.lower():
                        risk_scores.append("medium")
                    else:
                        risk_scores.append("low")
                else:
                    # If insights is not a dict, check for risk keywords in string
                    insights_str = str(insights).lower()
                    if 'critical' in insights_str or 'high risk' in insights_str:
                        risk_scores.append("high")
                    elif 'medium' in insights_str or 'moderate' in insights_str:
                        risk_scores.append("medium")
                    else:
                        risk_scores.append("low")
            except Exception as e:
                log_error(f"Error calculating LLM-based risk: {e}")
                risk_scores.append("medium")  # Default to medium if error occurs
        
        # Return highest risk level found
        if "high" in risk_scores:
            return "high"
        elif "medium" in risk_scores:
            return "medium"
        else:
            return "low"
