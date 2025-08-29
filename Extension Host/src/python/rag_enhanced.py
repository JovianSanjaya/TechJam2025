import json
import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import our new modules
from config import ComplianceConfig
from cache import ComplianceCache
from relevance import (
    calculate_relevance_score, 
    is_relevant_compliance, 
    parse_compliance_requirements, 
    generate_action_items
)

try:
    from vector_store import LegalDocumentVectorStore
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    from vector_store import SimpleFallbackStore as LegalDocumentVectorStore
    VECTOR_STORE_AVAILABLE = False

# 1. Load the Legal Documents
def load_legal_documents(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        data = json.load(file)
    # Extract documents array from the JSON structure
    return data.get('documents', []) if isinstance(data, dict) else data

# 2. Extract Legal Statutes from the Data
def extract_legal_statutes(legal_data):
    """
    Extract legal statutes from the legal documents.
    This function assumes that the legal documents are stored in 'legal_statute' type.
    """
    statutes = []
    for document in legal_data:
        if isinstance(document, dict) and document.get('content_type') == 'legal_statute':
            statutes.append(document)
        elif isinstance(document, dict) and document.get('content_type') == 'legal_document':
            # Also include legal_document type as fallback
            statutes.append(document)
    return statutes

# 3. Create Prompts for LangChain
def create_compliance_prompt(feature_description, statute_content):
    """
    This function creates a prompt for LangChain based on the feature description and the legal statute content.
    """
    prompt = f"""
    Feature Description: {feature_description}

    Legal Regulation Content:
    {statute_content}

    Based on the legal content above, does this feature require specific compliance logic related to the law? 
    Please flag the feature with the appropriate compliance requirements and explain.
    """
    return prompt

# 4. Set Up OpenRouter (KIMI v2) configuration
if not ComplianceConfig.OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not set. The script will use mock responses instead of calling OpenRouter.")


def call_openrouter(prompt, model=ComplianceConfig.OPENROUTER_MODEL, api_key=ComplianceConfig.OPENROUTER_API_KEY, timeout=30):
    """
    Call the OpenRouter API /v1/chat/completions with a simple user message.
    Returns the assistant text on success, or raises an exception on failure.
    """
    if not api_key:
        raise RuntimeError("OpenRouter API key not configured")

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
1. Whether this feature requires compliance measures (YES/NO)
2. Specific legal requirements that apply
3. Risk level (HIGH/MEDIUM/LOW)
4. Recommended implementation steps

Be specific and actionable in your response.
"""
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": enhanced_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        # Try to extract assistant content from common OpenAI-style response
        choices = data.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            content = message.get("content") or choices[0].get("text")
            return content or ""
        # Fallback to other possible fields
        return data.get("text", "")
    except Exception as e:
        raise RuntimeError(f"OpenRouter request failed: {e}")

# 5. Enhanced Flag Compliance Logic for Features
def flag_feature_for_compliance(feature_description: str, relevant_statutes: List[Dict], cache: Optional[ComplianceCache] = None) -> List[Dict]:
    """
    Enhanced function that flags features for compliance using vector search results and caching.
    """
    compliance_flags = []

    for i, statute_data in enumerate(relevant_statutes):
        # Handle both vector store results and direct statute objects
        if isinstance(statute_data, dict) and 'content' in statute_data:
            # Direct statute object
            statute_content = statute_data['content']
            statute_title = statute_data.get('title', 'Unknown Document')
        else:
            # Vector store result format
            statute_content = statute_data if isinstance(statute_data, str) else str(statute_data)
            statute_title = f"Document {i+1}"

        if not statute_content.strip():
            continue

        # Check cache first
        if cache and ComplianceConfig.ENABLE_CACHE:
            cached_result = cache.get_cached_result(feature_description, statute_content)
            if cached_result:
                compliance_flags.append({
                    'statute': statute_title,
                    'compliance_flag': cached_result,
                    'cached': True
                })
                continue

        # Create the prompt for analysis
        prompt = create_compliance_prompt(feature_description, statute_content)

        # Try OpenRouter API if key is present
        if ComplianceConfig.OPENROUTER_API_KEY:
            try:
                result = call_openrouter(prompt)
                
                # Cache the result
                if cache and ComplianceConfig.ENABLE_CACHE:
                    cache.cache_result(feature_description, statute_content, result)
                    
            except Exception as e:
                result = f"Error processing with OpenRouter: {str(e)}"
        else:
            # Enhanced mock response with more realistic analysis
            result = (
                f"COMPLIANCE ANALYSIS for {statute_title}:\n"
                f"1. Compliance Required: YES\n"
                f"2. Key Requirements:\n"
                f"   - User age verification and parental consent mechanisms\n"
                f"   - Geographic restriction implementation\n"
                f"   - Data protection and privacy controls\n"
                f"   - Content filtering and time-based restrictions\n"
                f"3. Risk Level: MEDIUM\n"
                f"4. Implementation Steps:\n"
                f"   - Implement robust age verification system\n"
                f"   - Design parental consent workflow\n"
                f"   - Add geographic location detection\n"
                f"   - Create minor-specific user interface controls\n"
                f"5. Legal Considerations: Review state-specific requirements for minors' digital privacy"
            )

        # Collect the compliance flag and reasoning
        compliance_flags.append({
            'statute': statute_title,
            'compliance_flag': result,
            'cached': False
        })
    
    return compliance_flags

# 6. Enhanced Processing with Vector Search and Structured Output
def process_compliance_analysis(legal_docs_path: str, features: List[Dict], use_cache: bool = True) -> Dict:
    """Enhanced processing pipeline with vector search and structured output"""
    
    print("🚀 Starting enhanced compliance analysis...")
    
    # Initialize components
    print("📊 Initializing vector store...")
    try:
        vector_store = LegalDocumentVectorStore()
        print("✅ Vector store initialized")
    except Exception as e:
        # Fall back to the SimpleFallbackStore from vector_store module
        print(f"❌ Vector store failed to initialize: {e}")
        try:
            from vector_store import SimpleFallbackStore
            vector_store = SimpleFallbackStore()
            print("ℹ️ Falling back to SimpleFallbackStore (keyword search)")
        except Exception as e2:
            print(f"❌ Failed to initialize fallback store as well: {e2}")
            # Return an empty but well-formed report to avoid KeyError in downstream code
            empty_report = {
                'summary': {
                    'total_features': 0,
                    'high_risk_features': 0,
                    'medium_risk_features': 0,
                    'low_risk_features': 0,
                    'applicable_regulations': [],
                    'generated_at': datetime.now().isoformat()
                },
                'features': [],
                'error': f'Failed to initialize any document store: {e} | {e2}'
            }
            return empty_report
    
    cache = ComplianceCache() if use_cache else None
    if cache and use_cache:
        cache.clear_expired()
        print("🗄️ Cache initialized and cleaned")
    
    # Load and index documents
    print("📚 Loading legal documents...")
    legal_data = load_legal_documents(legal_docs_path)
    legal_statutes = extract_legal_statutes(legal_data)
    print(f"📖 Loaded {len(legal_data)} total documents, {len(legal_statutes)} legal statutes")
    
    # Check if documents need indexing
    if vector_store.needs_reindexing(legal_statutes):
        print("🔄 Indexing documents in vector store...")
        vector_store.add_documents(legal_statutes)
        print("✅ Document indexing complete")
    else:
        print("✅ Documents already indexed")
    
    # Process features
    results = []
    
    for i, feature in enumerate(features, 1):
        print(f"\n🔍 Processing Feature {i}/{len(features)}: {feature['feature_name']}")
        
        # Find relevant statutes using vector search
        print("   🎯 Finding relevant statutes...")
        search_results = vector_store.search_relevant_statutes(
            feature['feature_description'],
            n_results=ComplianceConfig.MAX_STATUTES_PER_FEATURE
        )
        
        # Process search results
        relevant_statutes = []
        if search_results['documents'] and search_results['documents'][0]:
            for j, (doc, metadata) in enumerate(zip(search_results['documents'][0], search_results['metadatas'][0])):
                # Calculate relevance score
                score = calculate_relevance_score(
                    feature['feature_description'],
                    doc,
                    metadata
                )
                
                if score >= ComplianceConfig.RELEVANCE_THRESHOLD:
                    relevant_statutes.append({
                        'content': doc,
                        'title': metadata.get('title', f'Document {j+1}'),
                        'metadata': metadata,
                        'relevance_score': score
                    })
        
        print(f"   📋 Found {len(relevant_statutes)} relevant statutes (score >= {ComplianceConfig.RELEVANCE_THRESHOLD})")
        
        # Process compliance for relevant statutes only
        if relevant_statutes:
            print("   🤖 Analyzing compliance requirements...")
            compliance_flags = flag_feature_for_compliance(
                feature['feature_description'],
                relevant_statutes,
                cache
            )
        else:
            print("   ⚠️ No relevant statutes found")
            compliance_flags = []
        
        # Create feature results
        feature_results = {
            'feature': feature,
            'compliance_flags': compliance_flags,
            'relevant_statutes_count': len(relevant_statutes),
            'processed_at': datetime.now().isoformat()
        }
        results.append(feature_results)
    
    print(f"\n🎉 Analysis complete! Processed {len(features)} features")
    return generate_structured_compliance_report(results)


def generate_structured_compliance_report(results: List[Dict]) -> Dict:
    """Generate a structured and actionable compliance report"""
    print("📊 Generating structured compliance report...")
    
    report = {
        'summary': {
            'total_features': len(results),
            'high_risk_features': 0,
            'medium_risk_features': 0,
            'low_risk_features': 0,
            'applicable_regulations': set(),
            'generated_at': datetime.now().isoformat()
        },
        'features': []
    }
    
    for result in results:
        feature_report = {
            'feature_name': result['feature']['feature_name'],
            'description': result['feature']['feature_description'],
            'compliance_requirements': [],
            'risk_level': 'low',
            'action_items': [],
            'relevant_statutes_count': result.get('relevant_statutes_count', 0),
            'processed_at': result.get('processed_at', '')
        }
        
        # Process compliance flags
        for flag in result['compliance_flags']:
            if is_relevant_compliance(flag):
                compliance_req = parse_compliance_requirements(flag)
                feature_report['compliance_requirements'].append(compliance_req)
                
                # Track applicable regulations
                report['summary']['applicable_regulations'].add(compliance_req['statute'])
                
                # Update risk level
                if compliance_req['severity'] == 'high':
                    feature_report['risk_level'] = 'high'
                elif compliance_req['severity'] == 'medium' and feature_report['risk_level'] != 'high':
                    feature_report['risk_level'] = 'medium'
                
                # Add action items
                feature_report['action_items'].extend(
                    generate_action_items(compliance_req)
                )
        
        # Remove duplicate action items
        feature_report['action_items'] = list(set(feature_report['action_items']))
        
        # Update summary counts
        if feature_report['risk_level'] == 'high':
            report['summary']['high_risk_features'] += 1
        elif feature_report['risk_level'] == 'medium':
            report['summary']['medium_risk_features'] += 1
        else:
            report['summary']['low_risk_features'] += 1
        
        report['features'].append(feature_report)
    
    # Convert set to list for JSON serialization
    report['summary']['applicable_regulations'] = list(report['summary']['applicable_regulations'])
    
    print(f"✅ Report generated: {report['summary']['high_risk_features']} high-risk, "
          f"{report['summary']['medium_risk_features']} medium-risk, "
          f"{report['summary']['low_risk_features']} low-risk features")
    
    return report

# 7. Output Writing Functions
def write_detailed_output(report: Dict):
    """Write detailed human-readable output"""
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("🏛️  ENHANCED LEGAL COMPLIANCE ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # Summary
        summary = report['summary']
        f.write("📊 EXECUTIVE SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Features Analyzed: {summary['total_features']}\n")
        f.write(f"🔴 High Risk Features: {summary['high_risk_features']}\n")
        f.write(f"🟡 Medium Risk Features: {summary['medium_risk_features']}\n")
        f.write(f"🟢 Low Risk Features: {summary['low_risk_features']}\n")
        f.write(f"📋 Applicable Regulations: {len(summary['applicable_regulations'])}\n")
        f.write(f"⏰ Generated: {summary['generated_at']}\n\n")
        
        # Feature details
        for i, feature in enumerate(report['features'], 1):
            risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            f.write(f"{risk_emoji.get(feature['risk_level'], '⚪')} FEATURE {i}: {feature['feature_name']}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Description: {feature['description']}\n\n")
            f.write(f"Risk Level: {feature['risk_level'].upper()}\n")
            f.write(f"Relevant Statutes Analyzed: {feature['relevant_statutes_count']}\n\n")
            
            if feature['compliance_requirements']:
                f.write("📋 COMPLIANCE REQUIREMENTS:\n")
                for j, req in enumerate(feature['compliance_requirements'], 1):
                    f.write(f"{j}. Statute: {req['statute']}\n")
                    f.write(f"   Severity: {req['severity'].upper()}\n")
                    f.write(f"   Analysis: {req['requirements']}\n\n")
            
            if feature['action_items']:
                f.write("✅ ACTION ITEMS:\n")
                for item in feature['action_items']:
                    f.write(f"   • {item}\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n\n")

def write_json_output(report: Dict):
    """Write structured JSON output for programmatic use"""
    with open('compliance_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

def write_summary_output(report: Dict):
    """Write executive summary"""
    with open('summary.txt', 'w', encoding='utf-8') as f:
        summary = report['summary']
        f.write("COMPLIANCE ANALYSIS EXECUTIVE SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"📊 OVERVIEW\n")
        f.write(f"Features Analyzed: {summary['total_features']}\n")
        f.write(f"High Risk: {summary['high_risk_features']}\n")
        f.write(f"Medium Risk: {summary['medium_risk_features']}\n")
        f.write(f"Low Risk: {summary['low_risk_features']}\n\n")
        
        f.write("🚨 HIGH PRIORITY ACTIONS NEEDED:\n")
        high_risk_features = [f for f in report['features'] if f['risk_level'] == 'high']
        if high_risk_features:
            for feature in high_risk_features:
                f.write(f"• {feature['feature_name']}\n")
                for item in feature['action_items'][:3]:  # Top 3 action items
                    f.write(f"  - {item}\n")
                f.write("\n")
        else:
            f.write("• No high-risk features identified\n\n")
        
        f.write("📋 KEY REGULATIONS INVOLVED:\n")
        for reg in summary['applicable_regulations'][:10]:  # Top 10
            f.write(f"• {reg}\n")

# 8. Main execution function
def main():
    """Main execution function with enhanced processing"""
    
    # Define test features
    feature_samples = [
        {
            "feature_name": "Curfew login blocker with ASL and GH for Utah minors",
            "feature_description": "To comply with the Utah Social Media Regulation Act, we are implementing a curfew-based login restriction for users under 18. The system uses ASL to detect minor accounts and routes enforcement through GH to apply only within Utah boundaries."
        },
        {
            "feature_name": "PF default toggle with NR enforcement for California teens",
            "feature_description": "As part of compliance with California's SB976, the app will disable PF by default for users under 18 located in California."
        },
        {
            "feature_name": "AI-powered content recommendation engine",
            "feature_description": "Implementation of machine learning algorithms to personalize content feeds for users, including behavioral analysis and predictive modeling for engagement optimization."
        }
    ]
    
    # Run enhanced compliance analysis
    legal_documents_path = "legal_documents.json"
    
    try:
        report = process_compliance_analysis(
            legal_docs_path=legal_documents_path,
            features=feature_samples,
            use_cache=ComplianceConfig.ENABLE_CACHE
        )

        # Validate report structure before writing outputs
        if not isinstance(report, dict) or 'summary' not in report:
            raise ValueError("Enhanced analysis did not return a valid report structure")

        # Write structured results to multiple output formats
        write_detailed_output(report)
        write_json_output(report)
        write_summary_output(report)

        print(f"\n📄 Results written to:")
        print(f"   • output.txt (detailed analysis)")
        print(f"   • compliance_report.json (structured data)")
        print(f"   • summary.txt (executive summary)")

    except Exception as e:
        print(f"❌ Error during enhanced analysis: {e}")
        # Provide actionable steps for common environment errors (NumPy/transformers on Windows)
        print("\nCommon cause: missing or incompatible NumPy/transformers dependencies (often on Windows).")
        print("Recommended fix (using conda, run these in PowerShell):")
        print("  conda activate aichallenge; conda install -c conda-forge numpy pytorch -y")
        print("  pip install -U transformers sentence-transformers chromadb")
        print("Alternatively, run the simplified fallback pipeline that doesn't require heavy ML deps.")

        # Fallback: run simplified pipeline from rag_simple.py
        try:
            print("\n🔁 Running fallback simplified pipeline (rag_simple.py)...")
            import subprocess, sys
            subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'rag_simple.py')], check=True)
            print("✔️ Fallback pipeline completed. Check output.txt and compliance_report.json.")
        except Exception as fallback_err:
            print(f"Failed to run fallback pipeline: {fallback_err}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
