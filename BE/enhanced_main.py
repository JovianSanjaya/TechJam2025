import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

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
class ComplianceAnalysisResult:
    """Result of comprehensive compliance analysis"""
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
    timestamp: str = ""

class EnhancedComplianceSystem:
    """Enhanced TikTok compliance system for competition requirements"""
    
    def __init__(self):
        self.config = ComplianceConfig()
        self.jargon_resolver = TikTokJargonResolver()
        self.code_analyzer = LLMCodeAnalyzer()
        self.vector_store = None
        self.orchestrator = None
        self.analysis_results = []
    
    async def initialize(self):
        """Initialize the system components"""
        print("🚀 Initializing Enhanced TikTok Compliance System...")
        
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
        
        print("🎯 System ready for compliance analysis!")
    
    async def analyze_feature_list(self, features: List[Dict], include_code_analysis: bool = True) -> Dict:
        """Analyze a list of features comprehensively"""
        print(f"\n📋 Starting comprehensive analysis of {len(features)} features...")
        
        results = {
            "analysis_summary": {
                "total_features": len(features),
                "features_requiring_compliance": 0,
                "high_risk_features": 0,
                "human_review_needed": 0,
                "analysis_timestamp": datetime.now().isoformat(),
                "system_version": "Enhanced v2.0"
            },
            "detailed_results": [],
            "recommendations": [],
            "audit_trail": []
        }
        
        for i, feature in enumerate(features, 1):
            print(f"\n📊 Analyzing feature {i}/{len(features)}: {feature.get('feature_name', 'Unknown')}")
            
            try:
                # Multi-agent analysis
                agent_analysis = await self.orchestrator.analyze_feature(feature)
                
                # Code analysis if code is provided
                code_analysis = None
                if include_code_analysis and 'code' in feature:
                    print(f"  🔍 Performing code analysis...")
                    code_analysis = self.code_analyzer.analyze_code_snippet(
                        feature['code'], 
                        context=f"Feature: {feature.get('feature_name', '')} - {feature.get('description', '')}"
                    )
                
                # Create comprehensive result
                analysis_result = ComplianceAnalysisResult(
                    feature_id=feature.get('id', f'feature_{i}'),
                    feature_name=feature.get('feature_name', 'Unknown'),
                    analysis_type="comprehensive",
                    needs_compliance_logic=agent_analysis.get('needs_compliance_logic', False),
                    confidence=agent_analysis.get('confidence', 0.0),
                    risk_level=agent_analysis.get('risk_level', 'low'),
                    action_required=agent_analysis.get('action_required', 'NO_ACTION'),
                    applicable_regulations=agent_analysis.get('applicable_regulations', []),
                    implementation_notes=agent_analysis.get('implementation_notes', []),
                    code_analysis=code_analysis,
                    agent_results=agent_analysis,
                    timestamp=datetime.now().isoformat()
                )
                
                self.analysis_results.append(analysis_result)
                results["detailed_results"].append(self._format_result_for_export(analysis_result))
                
                # Update summary statistics
                if analysis_result.needs_compliance_logic:
                    results["analysis_summary"]["features_requiring_compliance"] += 1
                
                if analysis_result.risk_level == "high":
                    results["analysis_summary"]["high_risk_features"] += 1
                
                if agent_analysis.get('human_review_needed', False):
                    results["analysis_summary"]["human_review_needed"] += 1
                
                # Add to audit trail
                results["audit_trail"].append({
                    "feature_id": analysis_result.feature_id,
                    "timestamp": analysis_result.timestamp,
                    "agents_used": agent_analysis.get('agents_used', []),
                    "confidence": analysis_result.confidence,
                    "action": analysis_result.action_required
                })
                
                print(f"  ✅ Analysis complete - Action: {analysis_result.action_required}")
                
            except Exception as e:
                print(f"  ❌ Analysis failed for feature {i}: {e}")
                # Add error result
                error_result = ComplianceAnalysisResult(
                    feature_id=feature.get('id', f'feature_{i}'),
                    feature_name=feature.get('feature_name', 'Unknown'),
                    analysis_type="error",
                    needs_compliance_logic=False,
                    confidence=0.0,
                    risk_level="unknown",
                    action_required="HUMAN_REVIEW",
                    applicable_regulations=[],
                    implementation_notes=[f"Analysis failed: {e}"],
                    timestamp=datetime.now().isoformat()
                )
                
                self.analysis_results.append(error_result)
                results["detailed_results"].append(self._format_result_for_export(error_result))
                results["analysis_summary"]["human_review_needed"] += 1
        
        # Generate system-wide recommendations
        results["recommendations"] = self._generate_system_recommendations(results)
        
        print(f"\n🎉 Analysis complete! Summary:")
        print(f"   📊 Total features: {results['analysis_summary']['total_features']}")
        print(f"   ⚖️ Compliance required: {results['analysis_summary']['features_requiring_compliance']}")
        print(f"   🚨 High risk: {results['analysis_summary']['high_risk_features']}")
        print(f"   👥 Human review needed: {results['analysis_summary']['human_review_needed']}")
        
        return results
    
    def _format_result_for_export(self, result: ComplianceAnalysisResult) -> Dict:
        """Format analysis result for export"""
        formatted = {
            "feature_id": result.feature_id,
            "feature_name": result.feature_name,
            "analysis_type": result.analysis_type,
            "needs_compliance_logic": result.needs_compliance_logic,
            "confidence": round(result.confidence, 3),
            "risk_level": result.risk_level,
            "action_required": result.action_required,
            "applicable_regulations_count": len(result.applicable_regulations),
            "applicable_regulations": result.applicable_regulations,
            "implementation_notes": result.implementation_notes,
            "timestamp": result.timestamp
        }
        
        # Add code analysis if available
        if result.code_analysis:
            formatted["code_analysis"] = {
                "risk_score": round(result.code_analysis.get("risk_score", 0.0), 3),
                "privacy_concerns_count": len(result.code_analysis.get("privacy_concerns", [])),
                "age_verification_patterns": len(result.code_analysis.get("age_verification", [])),
                "geolocation_patterns": len(result.code_analysis.get("geolocation", [])),
                "content_moderation_patterns": len(result.code_analysis.get("content_moderation", [])),
                "recommendations": result.code_analysis.get("recommendations", [])
            }
        
        # Add agent analysis summary
        if result.agent_results:
            formatted["agent_analysis"] = {
                "agents_used": result.agent_results.get("agents_used", []),
                "agent_consensus": result.agent_results.get("agent_consensus", 0.0),
                "successful_agents": result.agent_results.get("successful_agents", 0),
                "human_review_needed": result.agent_results.get("human_review_needed", False)
            }
        
        return formatted
    
    def _generate_system_recommendations(self, results: Dict) -> List[str]:
        """Generate system-wide recommendations"""
        recommendations = []
        summary = results["analysis_summary"]
        
        # High-level recommendations
        if summary["features_requiring_compliance"] > 0:
            recommendations.append(f"🔧 {summary['features_requiring_compliance']} features require compliance implementation")
        
        if summary["high_risk_features"] > 0:
            recommendations.append(f"🚨 {summary['high_risk_features']} features have high compliance risk - prioritize review")
        
        if summary["human_review_needed"] > 0:
            recommendations.append(f"👥 {summary['human_review_needed']} features need human expert review")
        
        # Pattern-based recommendations
        regulation_counts = {}
        for result in results["detailed_results"]:
            for reg in result.get("applicable_regulations", []):
                reg_name = reg.get("regulation", "Unknown")
                regulation_counts[reg_name] = regulation_counts.get(reg_name, 0) + 1
        
        if regulation_counts:
            top_regulations = sorted(regulation_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            recommendations.append(f"📚 Most relevant regulations: {', '.join([f'{reg} ({count} features)' for reg, count in top_regulations])}")
        
        # Code analysis recommendations
        code_risks = []
        for result in results["detailed_results"]:
            if result.get("code_analysis", {}).get("risk_score", 0) > 0.7:
                code_risks.append(result["feature_name"])
        
        if code_risks:
            recommendations.append(f"💻 High-risk code patterns found in: {', '.join(code_risks[:5])}")
        
        return recommendations
    
    async def export_results(self, results: Dict, formats: List[str] = None) -> Dict[str, Any]:
        """Export results in multiple formats - returns data directly instead of writing files"""
        if formats is None:
            formats = ["json", "csv", "summary"]
        
        export_data = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n📤 Preparing results in {len(formats)} formats...")
        
        # JSON export (comprehensive)
        if "json" in formats:
            export_data["json"] = results
            print(f"  ✅ JSON data prepared")
        
        # CSV export (flattened for competition submission)
        if "csv" in formats:
            export_data["csv"] = self._prepare_csv_data(results["detailed_results"])
            print(f"  ✅ CSV data prepared")
        
        # Summary export (executive summary)
        if "summary" in formats:
            export_data["summary"] = self._prepare_summary_data(results)
            print(f"  ✅ Summary data prepared")
        
        # Audit trail export
        if "audit" in formats:
            export_data["audit"] = {
                "audit_trail": results["audit_trail"],
                "system_metadata": {
                    "analysis_timestamp": results["analysis_summary"]["analysis_timestamp"],
                    "system_version": results["analysis_summary"]["system_version"],
                    "total_features": results["analysis_summary"]["total_features"]
                }
            }
            print(f"  ✅ Audit trail data prepared")
        
        return export_data
    
    def _prepare_csv_data(self, detailed_results: List[Dict]) -> List[Dict]:
        """Prepare detailed results as CSV data (list of dictionaries)"""
        csv_data = []
        
        for result in detailed_results:
            row = {
                "feature_id": result["feature_id"],
                "feature_name": result["feature_name"],
                "needs_compliance_logic": result["needs_compliance_logic"],
                "confidence": result["confidence"],
                "risk_level": result["risk_level"],
                "action_required": result["action_required"],
                "applicable_regulations_count": result["applicable_regulations_count"],
                "code_risk_score": result.get("code_analysis", {}).get("risk_score", 0),
                "privacy_concerns": result.get("code_analysis", {}).get("privacy_concerns_count", 0),
                "age_verification_patterns": result.get("code_analysis", {}).get("age_verification_patterns", 0),
                "geolocation_patterns": result.get("code_analysis", {}).get("geolocation_patterns", 0),
                "content_moderation_patterns": result.get("code_analysis", {}).get("content_moderation_patterns", 0),
                "agents_used": "|".join(result.get("agent_analysis", {}).get("agents_used", [])),
                "human_review_needed": result.get("agent_analysis", {}).get("human_review_needed", False),
                "timestamp": result["timestamp"]
            }
            csv_data.append(row)
        
        return csv_data
    
    def _prepare_summary_data(self, results: Dict) -> str:
        """Prepare executive summary as string data"""
        summary = results["analysis_summary"]
        summary_text = []
        
        summary_text.append("TikTok Compliance Analysis - Executive Summary")
        summary_text.append("=" * 50)
        summary_text.append("")
        
        summary_text.append(f"Analysis Date: {summary['analysis_timestamp']}")
        summary_text.append(f"System Version: {summary['system_version']}")
        summary_text.append("")
        
        summary_text.append("📊 OVERVIEW")
        summary_text.append("-" * 20)
        summary_text.append(f"Total Features Analyzed: {summary['total_features']}")
        summary_text.append(f"Features Requiring Compliance: {summary['features_requiring_compliance']}")
        summary_text.append(f"High Risk Features: {summary['high_risk_features']}")
        summary_text.append(f"Human Review Needed: {summary['human_review_needed']}")
        summary_text.append("")
        
        summary_text.append("🎯 KEY RECOMMENDATIONS")
        summary_text.append("-" * 25)
        for i, rec in enumerate(results["recommendations"], 1):
            summary_text.append(f"{i}. {rec}")
        
        summary_text.append("")
        summary_text.append("🔍 DETAILED ANALYSIS")
        summary_text.append("-" * 20)
        
        # High priority features
        high_priority = [r for r in results["detailed_results"] 
                       if r["risk_level"] == "high" or r["action_required"] == "URGENT_COMPLIANCE"]
        
        if high_priority:
            summary_text.append("")
            summary_text.append(f"🚨 HIGH PRIORITY FEATURES ({len(high_priority)}):")
            for feature in high_priority:
                summary_text.append(f"  • {feature['feature_name']} (ID: {feature['feature_id']})")
                summary_text.append(f"    Risk: {feature['risk_level']}, Action: {feature['action_required']}")
                if feature.get('applicable_regulations'):
                    reg_names = [reg.get('regulation', 'Unknown') for reg in feature['applicable_regulations'][:2]]
                    summary_text.append(f"    Regulations: {', '.join(reg_names)}")
                summary_text.append("")
        
        # Compliance features
        compliance_features = [r for r in results["detailed_results"] if r["needs_compliance_logic"]]
        if compliance_features:
            summary_text.append(f"⚖️ COMPLIANCE IMPLEMENTATION NEEDED ({len(compliance_features)}):")
            for feature in compliance_features[:10]:  # Top 10
                summary_text.append(f"  • {feature['feature_name']} (Confidence: {feature['confidence']:.2f})")
            
            if len(compliance_features) > 10:
                summary_text.append(f"  ... and {len(compliance_features) - 10} more features")
        
        summary_text.append("")
        summary_text.append("📋 For complete details, see the JSON and CSV data.")
        
        return "\n".join(summary_text)

async def main():
    """Main function for testing the enhanced system"""
    # Sample features for testing
    sample_features = [
        {
            "id": "feat_001",
            "feature_name": "Age Verification Gate",
            "description": "ASL verification system for users under 16 with PF restrictions",
            "code": '''
def verify_user_age(user_data):
    age = user_data.get('age')
    if age < 13:
        require_parental_consent()
    elif age < 16:
        apply_privacy_restrictions()
    return age >= 13
'''
        },
        {
            "id": "feat_002", 
            "feature_name": "Geolocation Service",
            "description": "GH-based location tracking for content localization with NR compliance",
            "code": '''
import geoip
def get_user_location(ip_address):
    location = geoip.get_location(ip_address)
    track_user(location, "geolocation")
    return location
'''
        },
        {
            "id": "feat_003",
            "feature_name": "Content Recommendation",
            "description": "ML-powered PF algorithm for personalized content delivery",
            "code": '''
def recommend_content(user_profile):
    personal_data = collect_user_preferences(user_profile)
    return generate_recommendations(personal_data)
'''
        }
    ]
    
    # Initialize and run analysis
    system = EnhancedComplianceSystem()
    await system.initialize()
    
    results = await system.analyze_feature_list(sample_features, include_code_analysis=True)
    
    # Export in all formats
    export_data = await system.export_results(results, formats=["json", "csv", "summary", "audit"])
    
    print(f"\n🎯 Analysis complete! Data prepared:")
    for format_type, data in export_data.items():
        if format_type == "json":
            print(f"  📄 {format_type.upper()}: {len(str(data))} characters of JSON data")
        elif format_type == "csv":
            print(f"  📄 {format_type.upper()}: {len(data)} rows of CSV data")
        elif format_type == "summary":
            print(f"  📄 {format_type.upper()}: {len(data)} characters of summary text")
        elif format_type == "audit":
            print(f"  📄 {format_type.upper()}: Audit trail with {len(data.get('audit_trail', []))} entries")

# Only run main when script is executed directly, not when imported
if __name__ == "__main__":
    asyncio.run(main())
