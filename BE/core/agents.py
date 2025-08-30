from typing import Dict, List, Any, Optional
import asyncio
import json
from datetime import datetime
from services.jargon_service import JargonService
from config import ComplianceConfig
from utils.relevance import calculate_relevance_score, is_relevant_compliance, parse_compliance_requirements

class ComplianceAgent:
    """Base agent class"""
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.confidence_threshold = 0.7
    
    async def analyze(self, feature: Dict) -> Dict:
        raise NotImplementedError
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate confidence score based on analysis results"""
        # Base implementation - override in specific agents
        if not analysis:
            return 0.0
        
        # Simple confidence calculation based on data availability
        factors = []
        if analysis.get('applicable_regulations'):
            factors.append(0.8)
        if analysis.get('reasoning'):
            factors.append(0.6)
        if analysis.get('evidence'):
            factors.append(0.7)
        
        return sum(factors) / len(factors) if factors else 0.1

class LegalAnalysisAgent(ComplianceAgent):
    """Analyzes legal requirements"""
    def __init__(self, vector_store, llm_client=None):
        super().__init__("Legal Analyst", "Identify applicable regulations")
        self.vector_store = vector_store
        self.llm_client = llm_client
    
    async def analyze(self, feature: Dict) -> Dict:
        # Find relevant regulations
        feature_description = feature.get('description', '')
        relevant_regs = self.vector_store.search_relevant_statutes(
            feature_description, n_results=10
        )
        
        analysis = {
            "agent": self.name,
            "applicable_regulations": [],
            "confidence": 0.0,
            "reasoning": "",
            "evidence": [],
            "risk_level": "low"
        }
        
        # Use LLM for enhanced analysis if available (with forced RAG)
        if self.llm_client:
            try:
                # Create enhanced static analysis context
                static_analysis = {
                    'patterns': ['legal_analysis'],
                    'regulations_found': len(relevant_regs.get('documents', [[]])[0]) if relevant_regs else 0,
                    'vector_search_results': relevant_regs
                }
                
                llm_prompt = f"""
Feature Name: {feature.get('feature_name', 'Unknown')}
Description: {feature_description}

Analyze this TikTok platform feature for comprehensive legal compliance requirements.
Focus on applicable regulations, risk assessment, and implementation requirements.
"""
                print(f"  🧠 Using enhanced LLM for legal analysis with RAG...")
                
                # Call enhanced LLM client with RAG support
                if hasattr(self.llm_client, 'analyze'):
                    llm_response = await self.llm_client.analyze(
                        llm_prompt, 
                        static_analysis=static_analysis,
                        retrieved_docs=relevant_regs
                    )
                else:
                    # Fallback for function-style LLM client
                    llm_response = self.llm_client(llm_prompt)
                
                # Parse enhanced response format
                analysis.update(self._parse_enhanced_llm_response(llm_response, relevant_regs))
                
            except Exception as e:
                print(f"    ⚠️ Enhanced LLM analysis failed: {e}")
                # Fall back to original logic
                pass
        
        # Fallback to original vector search analysis if no LLM or LLM failed
        if not analysis["applicable_regulations"] and relevant_regs['documents'] and relevant_regs['documents'][0]:
            # Analyze each regulation
            for i, (doc, metadata) in enumerate(zip(relevant_regs['documents'][0], relevant_regs['metadatas'][0])):
                if not doc or not metadata:
                    continue
                    
                # Calculate relevance score
                relevance_score = calculate_relevance_score(feature_description, doc, metadata)
                
                if relevance_score >= ComplianceConfig.RELEVANCE_THRESHOLD:
                    reg_analysis = {
                        "regulation": metadata.get('title', f'Document {i+1}'),
                        "relevance": relevance_score,
                        "content_excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                        "requirements": self._extract_requirements_simple(doc),
                        "jurisdiction": self._extract_jurisdiction(doc, metadata),
                        "compliance_risk": self._assess_risk(doc)
                    }
                    
                    analysis["applicable_regulations"].append(reg_analysis)
                    analysis["evidence"].append(f"Regulation '{reg_analysis['regulation']}' with relevance {relevance_score:.2f}")
        
        return analysis
    
    def _parse_enhanced_llm_response(self, llm_response: str, retrieved_docs: Dict) -> Dict:
        """Parse enhanced LLM response matching code_analyzer_llm_clean format"""
        try:
            import json
            # Try to extract JSON from response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = llm_response[json_start:json_end]
                llm_data = json.loads(json_str)
                
                enhanced_analysis = {
                    "reasoning": "Enhanced LLM analysis with RAG: " + llm_data.get('compliance_insights', {}).get('overall_assessment', 'Analysis completed'),
                    "confidence": 0.9,
                    "llm_enhanced": True,
                    "rag_influence": llm_data.get('confidence_adjustments', {}).get('rag_influence', 'RAG documents informed analysis')
                }
                
                # Extract applicable regulations from enhanced patterns
                if 'enhanced_patterns' in llm_data:
                    for pattern in llm_data['enhanced_patterns']:
                        enhanced_analysis.setdefault('applicable_regulations', []).append({
                            "regulation": pattern.get('pattern_name', 'Unknown'),
                            "relevance": pattern.get('confidence', 0.8),
                            "content_excerpt": pattern.get('description', 'LLM-identified pattern'),
                            "requirements": pattern.get('regulation_hints', []),
                            "jurisdiction": "Various",
                            "compliance_risk": pattern.get('severity', 'medium'),
                            "legal_basis": pattern.get('legal_basis', 'LLM analysis')
                        })
                
                # Extract risk level
                if 'confidence_adjustments' in llm_data and 'adjusted_risk_score' in llm_data['confidence_adjustments']:
                    risk_score = llm_data['confidence_adjustments']['adjusted_risk_score']
                    if risk_score > 0.8:
                        enhanced_analysis['risk_level'] = 'high'
                    elif risk_score > 0.5:
                        enhanced_analysis['risk_level'] = 'medium'
                    else:
                        enhanced_analysis['risk_level'] = 'low'
                
                return enhanced_analysis
            else:
                # Fallback text parsing
                return self._extract_insights_from_llm_text(llm_response)
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse enhanced LLM JSON response: {e}")
            return self._extract_insights_from_llm_text(llm_response)
    
    def _extract_insights_from_llm_text(self, text: str) -> Dict:
        """Extract insights when JSON parsing fails"""
        analysis = {
            "reasoning": f"LLM text analysis: {text[:200]}...",
            "confidence": 0.7,
            "llm_enhanced": True,
            "applicable_regulations": []
        }
        
        # Enhanced text extraction
        regulations = ["COPPA", "GDPR", "CCPA", "DSA", "DMA"]
        found_regs = [reg for reg in regulations if reg.lower() in text.lower()]
        
        for reg in found_regs:
            analysis["applicable_regulations"].append({
                "regulation": reg,
                "relevance": 0.8,
                "content_excerpt": "Mentioned in LLM text analysis",
                "requirements": ["See LLM analysis for details"],
                "jurisdiction": "Various",
                "compliance_risk": "medium"
            })
        
        # Risk assessment from text
        if "high risk" in text.lower() or "critical" in text.lower():
            analysis["risk_level"] = "high"
        elif "low risk" in text.lower() or "minimal" in text.lower():
            analysis["risk_level"] = "low"
        else:
            analysis["risk_level"] = "medium"
        
        return analysis
    
    def _extract_requirements_simple(self, regulation_text: str) -> List[str]:
        """Extract key requirements from regulation text"""
        requirements = []
        
        # Look for requirement keywords
        requirement_patterns = [
            r"must\s+([^.]+)",
            r"shall\s+([^.]+)",
            r"required\s+to\s+([^.]+)",
            r"prohibited\s+from\s+([^.]+)",
            r"mandatory\s+([^.]+)"
        ]
        
        for pattern in requirement_patterns:
            import re
            matches = re.findall(pattern, regulation_text.lower())
            requirements.extend(matches[:3])  # Limit to avoid noise
        
        return requirements[:5]  # Return top 5 requirements
    
    def _extract_jurisdiction(self, doc: str, metadata: Dict) -> str:
        """Extract jurisdiction from document"""
        doc_lower = doc.lower()
        
        jurisdictions = {
            "EU": ["european", "eu", "gdpr", "europe"],
            "US": ["united states", "america", "federal", "coppa", "ccpa"],
            "California": ["california", "ccpa", "sb976"],
            "Global": ["international", "worldwide", "cross-border"]
        }
        
        for jurisdiction, keywords in jurisdictions.items():
            if any(keyword in doc_lower for keyword in keywords):
                return jurisdiction
        
        return metadata.get('jurisdiction', 'Unknown')
    
    def _assess_risk(self, regulation_text: str) -> str:
        """Assess compliance risk based on regulation content"""
        text_lower = regulation_text.lower()
        
        high_risk_indicators = ["penalty", "fine", "criminal", "violation", "lawsuit", "prohibited"]
        medium_risk_indicators = ["required", "mandatory", "must", "shall", "obligation"]
        
        if any(indicator in text_lower for indicator in high_risk_indicators):
            return "high"
        elif any(indicator in text_lower for indicator in medium_risk_indicators):
            return "medium"
        else:
            return "low"

class IntentClassificationAgent(ComplianceAgent):
    """Classifies feature intent (compliance vs business)"""
    def __init__(self, jargon_resolver: JargonService):
        super().__init__("Intent Classifier", "Distinguish compliance from business logic")
        self.jargon_resolver = jargon_resolver
    
    async def analyze(self, feature: Dict) -> Dict:
        # Get comprehensive analysis from jargon resolver
        jargon_analysis = self.jargon_resolver.generate_expanded_analysis(feature)
        
        intent_scores = jargon_analysis['intent_scores']
        primary_intent = max(intent_scores, key=intent_scores.get)
        
        analysis = {
            "agent": self.name,
            "intent": primary_intent,
            "scores": intent_scores,
            "confidence": max(intent_scores.values()),
            "expanded_description": jargon_analysis['expanded_text'],
            "geographic_scope": jargon_analysis['geographic_scope'],
            "compliance_categories": jargon_analysis['compliance_categories'],
            "jargon_detected": jargon_analysis['jargon_detected'],
            "complexity_score": jargon_analysis['complexity_score'],
            "reasoning": self._generate_reasoning(intent_scores, jargon_analysis)
        }
        
        return analysis
    
    def _generate_reasoning(self, intent_scores: Dict, jargon_analysis: Dict) -> str:
        """Generate reasoning for intent classification"""
        primary_intent = max(intent_scores, key=intent_scores.get)
        confidence = max(intent_scores.values())
        
        reasoning_parts = [f"Primary intent: {primary_intent} (confidence: {confidence:.2f})"]
        
        if jargon_analysis['jargon_detected']:
            reasoning_parts.append(f"Technical jargon detected: {', '.join(jargon_analysis['jargon_detected'])}")
        
        if jargon_analysis['geographic_scope']:
            reasoning_parts.append(f"Geographic scope: {', '.join(jargon_analysis['geographic_scope'])}")
        
        # Add compliance category insights
        significant_categories = [
            cat for cat, score in jargon_analysis['compliance_categories'].items() 
            if score > 0.3
        ]
        if significant_categories:
            reasoning_parts.append(f"Compliance categories detected: {', '.join(significant_categories)}")
        
        return " | ".join(reasoning_parts)

class TechnicalAnalysisAgent(ComplianceAgent):
    """Analyzes technical implementation requirements"""
    def __init__(self):
        super().__init__("Technical Analyst", "Assess implementation complexity and requirements")
    
    async def analyze(self, feature: Dict) -> Dict:
        feature_description = feature.get('description', '')
        feature_name = feature.get('feature_name', '')
        
        analysis = {
            "agent": self.name,
            "implementation_complexity": "low",
            "technical_requirements": [],
            "integration_points": [],
            "data_flow_requirements": [],
            "security_considerations": [],
            "confidence": 0.0,
            "reasoning": ""
        }
        
        # Analyze implementation complexity
        complexity_indicators = self._assess_complexity(feature_description + " " + feature_name)
        analysis["implementation_complexity"] = complexity_indicators["level"]
        analysis["technical_requirements"] = complexity_indicators["requirements"]
        
        # Analyze integration points
        analysis["integration_points"] = self._identify_integrations(feature_description)
        
        # Analyze data flow
        analysis["data_flow_requirements"] = self._analyze_data_flow(feature_description)
        
        # Security considerations
        analysis["security_considerations"] = self._identify_security_needs(feature_description)
        
        # Calculate confidence and reasoning
        analysis["confidence"] = self._calculate_technical_confidence(analysis)
        analysis["reasoning"] = self._generate_technical_reasoning(analysis)
        
        return analysis
    
    def _assess_complexity(self, text: str) -> Dict:
        """Assess implementation complexity"""
        text_lower = text.lower()
        
        high_complexity_terms = [
            "machine learning", "ai", "algorithm", "real-time", "distributed",
            "microservices", "blockchain", "encryption", "authentication"
        ]
        
        medium_complexity_terms = [
            "api", "database", "integration", "middleware", "caching",
            "load balancing", "monitoring", "logging"
        ]
        
        low_complexity_terms = [
            "configuration", "toggle", "flag", "setting", "parameter"
        ]
        
        high_count = sum(1 for term in high_complexity_terms if term in text_lower)
        medium_count = sum(1 for term in medium_complexity_terms if term in text_lower)
        low_count = sum(1 for term in low_complexity_terms if term in text_lower)
        
        if high_count >= 2:
            return {"level": "high", "requirements": high_complexity_terms[:high_count]}
        elif medium_count >= 2 or high_count >= 1:
            return {"level": "medium", "requirements": medium_complexity_terms[:medium_count]}
        else:
            return {"level": "low", "requirements": low_complexity_terms[:low_count]}
    
    def _identify_integrations(self, text: str) -> List[str]:
        """Identify potential integration points"""
        integrations = []
        text_lower = text.lower()
        
        integration_patterns = {
            "user_service": ["user", "account", "profile", "authentication"],
            "location_service": ["location", "geo", "region", "country"],
            "content_service": ["content", "feed", "recommendation"],
            "analytics_service": ["analytics", "tracking", "metrics"],
            "notification_service": ["notification", "alert", "message"],
            "payment_service": ["payment", "billing", "subscription"]
        }
        
        for service, keywords in integration_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                integrations.append(service)
        
        return integrations
    
    def _analyze_data_flow(self, text: str) -> List[str]:
        """Analyze data flow requirements"""
        data_flows = []
        text_lower = text.lower()
        
        data_patterns = {
            "user_data_collection": ["collect", "gather", "capture", "input"],
            "data_processing": ["process", "analyze", "compute", "calculate"],
            "data_storage": ["store", "save", "persist", "database"],
            "data_transmission": ["send", "transmit", "sync", "share"],
            "data_validation": ["validate", "verify", "check", "confirm"]
        }
        
        for flow_type, keywords in data_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                data_flows.append(flow_type)
        
        return data_flows
    
    def _identify_security_needs(self, text: str) -> List[str]:
        """Identify security considerations"""
        security_needs = []
        text_lower = text.lower()
        
        security_patterns = {
            "authentication": ["login", "auth", "credential", "verify"],
            "authorization": ["permission", "access", "role", "privilege"],
            "encryption": ["encrypt", "secure", "protect", "privacy"],
            "audit_logging": ["log", "audit", "track", "monitor"],
            "data_protection": ["protection", "security", "safe", "compliance"]
        }
        
        for security_type, keywords in security_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                security_needs.append(security_type)
        
        return security_needs
    
    def _calculate_technical_confidence(self, analysis: Dict) -> float:
        """Calculate confidence in technical analysis"""
        factors = []
        
        if analysis["technical_requirements"]:
            factors.append(0.8)
        if analysis["integration_points"]:
            factors.append(0.7)
        if analysis["data_flow_requirements"]:
            factors.append(0.6)
        if analysis["security_considerations"]:
            factors.append(0.9)
        
        return sum(factors) / len(factors) if factors else 0.3
    
    def _generate_technical_reasoning(self, analysis: Dict) -> str:
        """Generate reasoning for technical analysis"""
        parts = [f"Implementation complexity: {analysis['implementation_complexity']}"]
        
        if analysis["integration_points"]:
            parts.append(f"Integrations needed: {len(analysis['integration_points'])}")
        
        if analysis["security_considerations"]:
            parts.append(f"Security requirements: {len(analysis['security_considerations'])}")
        
        return " | ".join(parts)

class ValidationAgent(ComplianceAgent):
    """Validates and consolidates findings"""
    def __init__(self):
        super().__init__("Validator", "Consolidate and validate findings")
    
    async def analyze(self, feature: Dict, agent_results: List[Dict]) -> Dict:
        """Consolidate results from all agents"""
        consolidated = {
            "feature_name": feature.get("feature_name", "Unknown"),
            "feature_id": feature.get("id", ""),
            "needs_compliance_logic": False,
            "confidence": 0.0,
            "reasoning": [],
            "applicable_regulations": [],
            "action_required": "NO_ACTION",
            "human_review_needed": False,
            "risk_level": "low",
            "implementation_notes": [],
            "agent_consensus": 0.0
        }
        
        # Extract results from each agent
        intent_result = next((r for r in agent_results if r["agent"] == "Intent Classifier"), None)
        legal_result = next((r for r in agent_results if r["agent"] == "Legal Analyst"), None)
        technical_result = next((r for r in agent_results if r["agent"] == "Technical Analyst"), None)
        
        # Analyze intent
        if intent_result:
            if intent_result["intent"] == "business":
                consolidated["reasoning"].append("Feature appears to be business-driven, not legally required")
                consolidated["confidence"] = intent_result["confidence"]
            elif intent_result["intent"] == "compliance":
                consolidated["needs_compliance_logic"] = True
                consolidated["reasoning"].append("Feature identified as compliance-driven")
                consolidated["confidence"] = intent_result["confidence"]
            elif intent_result["intent"] == "ambiguous":
                consolidated["human_review_needed"] = True
                consolidated["reasoning"].append("Intent is ambiguous - human review required")
                consolidated["confidence"] = intent_result["confidence"]
        
        # Analyze legal requirements
        if legal_result and legal_result.get("applicable_regulations"):
            consolidated["needs_compliance_logic"] = True
            consolidated["applicable_regulations"] = legal_result["applicable_regulations"]
            reg_count = len(legal_result["applicable_regulations"])
            consolidated["reasoning"].append(f"Found {reg_count} applicable regulations")
            
            # Update confidence with legal analysis
            legal_confidence = legal_result.get("confidence", 0.0)
            consolidated["confidence"] = max(consolidated["confidence"], legal_confidence)
            
            # Set risk level from legal analysis
            consolidated["risk_level"] = legal_result.get("risk_level", "low")
        
        # Add technical considerations
        if technical_result:
            tech_complexity = technical_result.get("implementation_complexity", "low")
            consolidated["implementation_notes"].append(f"Technical complexity: {tech_complexity}")
            
            if technical_result.get("security_considerations"):
                security_count = len(technical_result["security_considerations"])
                consolidated["implementation_notes"].append(f"Security considerations: {security_count}")
        
        # Calculate agent consensus
        confidences = [r.get("confidence", 0.0) for r in agent_results if r.get("confidence")]
        consolidated["agent_consensus"] = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Determine final action
        if consolidated["human_review_needed"]:
            consolidated["action_required"] = "HUMAN_REVIEW"
        elif consolidated["needs_compliance_logic"]:
            if consolidated["risk_level"] == "high":
                consolidated["action_required"] = "URGENT_COMPLIANCE"
            else:
                consolidated["action_required"] = "IMPLEMENT_COMPLIANCE"
        else:
            consolidated["action_required"] = "NO_ACTION"
        
        # Adjust confidence based on consensus
        if consolidated["agent_consensus"] < 0.5:
            consolidated["human_review_needed"] = True
            consolidated["reasoning"].append("Low agent consensus - human review recommended")
        
        return consolidated

class MultiAgentOrchestrator:
    """Orchestrates multiple agents for comprehensive analysis"""
    def __init__(self, vector_store, jargon_resolver: JargonService, llm_client=None):
        self.agents = [
            IntentClassificationAgent(jargon_resolver),
            LegalAnalysisAgent(vector_store, llm_client),
            TechnicalAnalysisAgent()
        ]
        self.validator = ValidationAgent()
        self.jargon_resolver = jargon_resolver
    
    async def analyze_feature(self, feature: Dict) -> Dict:
        """Run comprehensive multi-agent analysis"""
        print(f"  🤖 Running multi-agent analysis for: {feature.get('feature_name', 'Unknown')}")
        
        # Expand feature description first
        expanded_feature = feature.copy()
        if 'description' in feature:
            expanded_feature['expanded_description'] = self.jargon_resolver.expand_description(
                feature['description']
            )
        
        # Run all agents in parallel
        try:
            tasks = [agent.analyze(expanded_feature) for agent in self.agents]
            agent_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            valid_results = []
            for i, result in enumerate(agent_results):
                if isinstance(result, Exception):
                    print(f"    ⚠️ Agent {self.agents[i].name} failed: {result}")
                    # Create a minimal result for failed agents
                    valid_results.append({
                        "agent": self.agents[i].name,
                        "confidence": 0.0,
                        "reasoning": f"Agent failed: {result}",
                        "error": str(result)
                    })
                else:
                    valid_results.append(result)
            
            # Validate and consolidate
            final_result = await self.validator.analyze(expanded_feature, valid_results)
            
            # Add metadata
            final_result["analysis_timestamp"] = datetime.now().isoformat()
            final_result["agents_used"] = [agent.name for agent in self.agents]
            final_result["total_agents"] = len(self.agents)
            final_result["successful_agents"] = len([r for r in agent_results if not isinstance(r, Exception)])
            
            return final_result
            
        except Exception as e:
            print(f"    ❌ Multi-agent analysis failed: {e}")
            # Return a minimal result in case of total failure
            return {
                "feature_name": feature.get("feature_name", "Unknown"),
                "feature_id": feature.get("id", ""),
                "needs_compliance_logic": False,
                "confidence": 0.0,
                "reasoning": [f"Analysis failed: {e}"],
                "applicable_regulations": [],
                "action_required": "HUMAN_REVIEW",
                "human_review_needed": True,
                "risk_level": "unknown",
                "error": str(e)
            }
