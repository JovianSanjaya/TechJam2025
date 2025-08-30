"""
Main compliance analysis service - orchestrates all analysis components
"""

from datetime import datetime
from typing import Dict, List, Optional

from ..types.compliance_types import ComplianceResult, CompliancePattern, AnalysisConfig
from ..analyzers.pattern_analyzer import PatternAnalyzer
from ..analyzers.simple_analyzer import SimpleAnalyzer
from ..services.llm_service import LLMService
from ..services.rag_service import RAGService
from ..utils.helpers import log_info, log_error, calculate_confidence


class ComplianceService:
    """Main service that orchestrates compliance analysis"""
    
    def __init__(self, config: AnalysisConfig = None, vector_store=None):
        self.config = config or AnalysisConfig()
        
        # Initialize services
        self.llm_service = LLMService() if self.config.use_llm else None
        self.rag_service = RAGService(vector_store) if self.config.use_rag else None
        
        # Initialize analyzers
        self.pattern_analyzer = PatternAnalyzer()
        self.simple_analyzer = SimpleAnalyzer()
        
        log_info(f"🚀 ComplianceService initialized")
        log_info(f"   LLM: {'✅' if self.llm_service and self.llm_service.is_available() else '❌'}")
        log_info(f"   RAG: {'✅' if self.rag_service and self.rag_service.is_available() else '❌'}")
    
    def analyze_code(self, code: str, feature_name: str) -> ComplianceResult:
        """Main analysis method"""
        log_info(f"🔍 Analyzing: {feature_name}")
        
        try:
            # Step 1: Pattern analysis (always run)
            patterns = self.pattern_analyzer.find_patterns(code)
            log_info(f"📊 Found {len(patterns)} patterns")
            
            # Step 2: RAG context retrieval
            rag_context = ""
            if self.rag_service and self.rag_service.is_available():
                query = f"{feature_name} {code[:500]}"  # Limit query length
                rag_context = self.rag_service.retrieve_relevant_context(query)
                log_info("📚 RAG context retrieved")
            
            # Step 3: LLM analysis (if available)
            llm_response = None
            if self.llm_service and self.llm_service.is_available():
                llm_response = self.llm_service.analyze_code(code, feature_name, rag_context)
                if llm_response:
                    log_info("🤖 LLM analysis completed")
                    # Merge LLM patterns with rule-based patterns
                    llm_patterns = self._convert_llm_patterns(llm_response.enhanced_patterns)
                    patterns.extend(llm_patterns)
            
            # Step 4: Generate final result
            if llm_response and len(patterns) > 0:
                # Use enhanced analysis when LLM is available
                result = self._generate_enhanced_result(feature_name, patterns, llm_response, code)
            else:
                # Fallback to simple analysis
                log_info("⚠️ Falling back to simple analysis")
                result = self.simple_analyzer.analyze(code, feature_name, patterns)
            
            log_info(f"✅ Analysis complete: {result.risk_level} risk, {result.confidence:.2f} confidence")
            return result
            
        except Exception as e:
            log_error(f"Analysis failed for {feature_name}: {str(e)}", e)
            # Return error result
            return ComplianceResult(
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
    
    def _convert_llm_patterns(self, llm_patterns: List[Dict]) -> List[CompliancePattern]:
        """Convert LLM response patterns to CompliancePattern objects"""
        patterns = []
        
        for pattern_data in llm_patterns:
            if isinstance(pattern_data, dict):
                pattern = CompliancePattern(
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
    
    def _generate_enhanced_result(self, feature_name: str, patterns: List[CompliancePattern], 
                                llm_response, code: str) -> ComplianceResult:
        """Generate enhanced result using LLM insights"""
        
        # Extract regulations from patterns and LLM response
        regulations = set()
        for pattern in patterns:
            regulations.update(pattern.regulation_hints)
        
        # Convert to regulation format expected by result
        applicable_regulations = []
        for reg in regulations:
            applicable_regulations.append({
                'regulation': reg,
                'relevance': 0.8,  # Default relevance
                'content_excerpt': f"Regulation {reg} applies to this feature",
                'requirements': [reg],
                'jurisdiction': 'Various',
                'compliance_risk': 'medium',
                'legal_basis': f"{reg} compliance requirements"
            })
        
        # Calculate risk level based on patterns and LLM insights
        risk_level = self._calculate_risk_level(patterns, llm_response)
        
        # Calculate confidence
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
        
        # Determine action required
        if risk_level == "high":
            action_required = "IMPLEMENT_COMPLIANCE"
        elif risk_level == "medium":
            action_required = "REVIEW_REQUIRED"
        else:
            action_required = "MONITOR"
        
        return ComplianceResult(
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
    
    def _calculate_risk_level(self, patterns: List[CompliancePattern], llm_response) -> str:
        """Calculate risk level based on patterns and LLM analysis"""
        risk_scores = []
        
        # Pattern-based risk
        high_risk_patterns = sum(1 for p in patterns if p.confidence > 0.8)
        medium_risk_patterns = sum(1 for p in patterns if 0.5 <= p.confidence <= 0.8)
        
        if high_risk_patterns >= 2:
            risk_scores.append("high")
        elif high_risk_patterns >= 1 or medium_risk_patterns >= 3:
            risk_scores.append("medium")
        else:
            risk_scores.append("low")
        
        # LLM-based risk
        if llm_response:
            insights = llm_response.compliance_insights
            key_risks = insights.get('key_risks', [])
            
            if len(key_risks) >= 3:
                risk_scores.append("high")
            elif len(key_risks) >= 2:
                risk_scores.append("medium")
            else:
                risk_scores.append("low")
        
        # Return highest risk level
        if "high" in risk_scores:
            return "high"
        elif "medium" in risk_scores:
            return "medium"
        else:
            return "low"
