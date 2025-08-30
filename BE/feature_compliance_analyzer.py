"""
Feature Compliance Analyzer - LLM/ML powered single feature analysis
Takes JSON input from frontend, uses same sophisticated analysis as enhanced_main.py
"""
import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import the sophisticated components from enhanced_main
from jargon_resolver import TikTokJargonResolver
from agents import MultiAgentOrchestrator
from code_analyzer_llm_clean import LLMCodeAnalyzer
from vector_store import get_vector_store
from config import ComplianceConfig

def call_openrouter(prompt, model=ComplianceConfig.OPENROUTER_MODEL, api_key=ComplianceConfig.OPENROUTER_API_KEY, timeout=30):
    """
    Call the OpenRouter API /v1/chat/completions with a simple user message.
    Returns the assistant text on success, or raises an exception on failure.
    """
    if not api_key:
        return f"Mock LLM Response: Analysis of '{prompt[:100]}...' - This is a simulated response as no API key is configured."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/JovianSanjaya/TechJam2025",
        "X-Title": "Legal Compliance RAG System"
    }
    
    # Enhanced prompt for better structured responses
    enhanced_prompt = f"""
Analyze the following feature for legal compliance requirements:

{prompt}

Please provide a structured analysis including:
1. Applicable regulations (COPPA, GDPR, CCPA, etc.)
2. Compliance risks (high/medium/low)
3. Required implementation steps
4. Potential legal concerns

Format your response as JSON with these fields:
- applicable_regulations: [list of relevant laws]
- risk_level: "high"/"medium"/"low"
- compliance_requirements: [list of specific requirements]
- recommendations: [list of actionable recommendations]
"""
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": enhanced_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    try:
        print(f"🌐 Calling OpenRouter API with model: {model}")
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content']
            print(f"✅ OpenRouter API response received: {len(content)} characters")
            return content
        else:
            return f"Error: No choices in response: {data}"
    
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenRouter API request failed: {e}")
        return f"Error processing with OpenRouter: {str(e)}"
    except Exception as e:
        print(f"❌ OpenRouter API error: {e}")
        return f"Error processing with OpenRouter: {str(e)}"

@dataclass
class FeatureComplianceResult:
    """Result of single feature compliance analysis"""
    feature_id: str
    feature_name: str
    analysis_type: str
    needs_compliance_logic: bool
    confidence: float
    risk_level: str
    action_required: str
    applicable_regulations: List[Dict]
    implementation_notes: List[str]
    code_analysis: Optional[Dict] = None
    agent_results: Optional[Dict] = None
    llm_analysis: Optional[Dict] = None
    timestamp: str = ""

class FeatureComplianceAnalyzer:
    """
    Sophisticated compliance analyzer for single features
    Uses the same LLM/ML components as enhanced_main.py but for API use
    """
    
    def __init__(self):
        self.config = ComplianceConfig()
        self.jargon_resolver = TikTokJargonResolver()
        self.code_analyzer = LLMCodeAnalyzer()
        self.vector_store = None
        self.orchestrator = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the sophisticated components"""
        if self.initialized:
            return
            
        print("🚀 Initializing Feature Compliance Analyzer...")
        
        # Initialize vector store
        try:
            self.vector_store = get_vector_store()
            print("✅ Vector store initialized")
        except Exception as e:
            print(f"⚠️ Vector store initialization failed: {e}")
            print("   Using fallback search capabilities")
        
        # Initialize multi-agent orchestrator with LLM client
        self.orchestrator = MultiAgentOrchestrator(
            vector_store=self.vector_store,
            jargon_resolver=self.jargon_resolver,
            llm_client=call_openrouter
        )
        print("✅ Multi-agent system initialized with LLM integration")
        print(f"🔗 OpenRouter model: {ComplianceConfig.OPENROUTER_MODEL}")
        print(f"🔑 API key configured: {'Yes' if ComplianceConfig.OPENROUTER_API_KEY else 'No (using mock responses)'}")
        
        self.initialized = True
        print("🎯 Feature analyzer ready!")
    
    async def analyze_single_feature(self, feature_data: Dict[str, Any]) -> FeatureComplianceResult:
        """
        Analyze a single feature using sophisticated LLM/ML analysis
        
        Args:
            feature_data: {
                "featureName": str,
                "description": str,
                "code": str (optional),
                "featureType": str (optional)
            }
        
        Returns:
            FeatureComplianceResult with comprehensive analysis
        """
        await self.initialize()
        
        feature_name = feature_data.get('featureName', 'Unknown Feature')
        description = feature_data.get('description', '')
        
        print(f"\n📊 Analyzing feature: {feature_name}")
        
        # Convert to format expected by agents
        feature_for_agents = {
            "id": f"feat_{int(datetime.now().timestamp())}",
            "feature_name": feature_name,
            "description": description
        }
        
        try:
            # 1. Multi-agent analysis (sophisticated AI analysis)
            print("🤖 Running multi-agent analysis...")
            agent_analysis = await self.orchestrator.analyze_feature(feature_for_agents)
            
            # 2. Direct LLM analysis for additional insights
            print("🧠 Running direct LLM analysis...")
            llm_prompt = f"""
Feature Name: {feature_name}
Description: {description}

Analyze this feature for TikTok compliance requirements.
"""
            llm_response = call_openrouter(llm_prompt)
            llm_analysis = self._parse_llm_response(llm_response)
            
            # 4. Combine all analyses into comprehensive result
            result = self._synthesize_analysis(
                feature_for_agents,
                agent_analysis,
                llm_analysis
            )
            
            print(f"✅ Analysis complete - Risk: {result.risk_level}, Action: {result.action_required}")
            return result
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            # Return error result
            return FeatureComplianceResult(
                feature_id=feature_for_agents["id"],
                feature_name=feature_name,
                analysis_type="error",
                needs_compliance_logic=False,
                confidence=0.0,
                risk_level="unknown",
                action_required="HUMAN_REVIEW",
                applicable_regulations=[],
                implementation_notes=[f"Analysis failed: {e}"],
                timestamp=datetime.now().isoformat()
            )
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into structured data"""
        try:
            # Try to extract JSON from LLM response
            if '{' in llm_response and '}' in llm_response:
                start = llm_response.find('{')
                end = llm_response.rfind('}') + 1
                json_str = llm_response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: parse text response
        return {
            "raw_response": llm_response,
            "parsed": False
        }
    
    def _synthesize_analysis(self, feature: Dict, agent_analysis: Dict, 
                           llm_analysis: Dict) -> FeatureComplianceResult:
        """Synthesize all analyses into final result"""
        
        # Determine risk level (highest from all analyses)
        risk_levels = ["minimal", "low", "medium", "high"]
        agent_risk = agent_analysis.get('risk_level', 'low')
        llm_risk = self._get_llm_risk_level(llm_analysis)
        
        all_risks = [agent_risk, llm_risk]
        final_risk = max(all_risks, key=lambda x: risk_levels.index(x) if x in risk_levels else 0)
        
        # Combine regulations from all sources
        regulations = []
        regulations.extend(agent_analysis.get('applicable_regulations', []))
        if llm_analysis.get('applicable_regulations'):
            regulations.extend(llm_analysis['applicable_regulations'])
        
        # Remove duplicates
        seen_regs = set()
        unique_regulations = []
        for reg in regulations:
            reg_name = reg.get('name', reg.get('regulation', 'Unknown'))
            if reg_name not in seen_regs:
                seen_regs.add(reg_name)
                unique_regulations.append(reg)
        
        # Combine implementation notes
        notes = []
        notes.extend(agent_analysis.get('implementation_notes', []))
        if llm_analysis.get('recommendations'):
            notes.extend(llm_analysis['recommendations'])
        
        # Calculate confidence (average of all confidences)
        confidences = [
            agent_analysis.get('confidence', 0.7),
            0.8 if llm_analysis.get('parsed') else 0.6
        ]
        final_confidence = sum(confidences) / len(confidences)
        
        return FeatureComplianceResult(
            feature_id=feature['id'],
            feature_name=feature['feature_name'],
            analysis_type="comprehensive_ml",
            needs_compliance_logic=agent_analysis.get('needs_compliance_logic', final_risk != 'minimal'),
            confidence=final_confidence,
            risk_level=final_risk,
            action_required=self._determine_action(final_risk, unique_regulations),
            applicable_regulations=unique_regulations,
            implementation_notes=list(set(notes))[:8],  # Unique notes, max 8

            agent_results=agent_analysis,
            llm_analysis=llm_analysis,
            timestamp=datetime.now().isoformat()
        )
    

    
    def _get_llm_risk_level(self, llm_analysis: Dict) -> str:
        """Extract risk level from LLM analysis"""
        if llm_analysis.get('risk_level'):
            return llm_analysis['risk_level'].lower()
        
        # Analyze raw response for risk indicators
        raw = llm_analysis.get('raw_response', '').lower()
        if any(word in raw for word in ['high risk', 'critical', 'urgent']):
            return "high"
        elif any(word in raw for word in ['medium risk', 'moderate', 'concern']):
            return "medium"
        elif any(word in raw for word in ['low risk', 'minor']):
            return "low"
        else:
            return "minimal"
    
    def _determine_action(self, risk_level: str, regulations: List[Dict]) -> str:
        """Determine required action based on risk and regulations"""
        reg_count = len(regulations)
        
        if risk_level == "high":
            return "Immediate compliance review required"
        elif risk_level == "medium" and reg_count >= 2:
            return "Compliance assessment recommended"
        elif risk_level == "medium":
            return "Review privacy implementation"
        elif risk_level == "low" and reg_count > 0:
            return "Basic compliance check needed"
        else:
            return "No immediate action required"
    
    async def analyze_json_input(self, json_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main API method: takes JSON input, returns JSON output
        Uses sophisticated LLM/ML analysis
        
        Args:
            json_input: Frontend JSON with feature data
            
        Returns:
            JSON response with comprehensive compliance analysis
        """
        try:
            result = await self.analyze_single_feature(json_input)
            
            # Convert to JSON-serializable format
            return {
                "status": "success",
                "analysis_results": [asdict(result)],  # Wrap in array for consistency
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "sophisticated_ml_llm"
            }
            
        except Exception as e:
            print(f"❌ Feature analysis error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "error"
            }

# Example usage for testing
if __name__ == "__main__":
    async def test_analyzer():
        analyzer = FeatureComplianceAnalyzer()
        
        # Test with sample input
        test_input = {
            "featureName": "User Profile with Age Verification",
            "description": "Collect user age and verify if they are 13+ for COPPA compliance"
        }
        
        result = await analyzer.analyze_json_input(test_input)
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_analyzer())
