"""
LLM Client for OpenRouter API integration
"""
import requests
import asyncio
from typing import Dict, Any
from config import ComplianceConfig

class LLMClient:
    """Client for LLM API calls"""
    
    def __init__(self):
        self.api_key = ComplianceConfig.OPENROUTER_API_KEY
        self.model = ComplianceConfig.OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def analyze(self, prompt: str, timeout: int = 30, static_analysis: Dict = None, retrieved_docs: Dict = None) -> str:
        """
        Enhanced LLM analysis with RAG support (matching code_analyzer_llm_clean format)
        
        Args:
            prompt: The prompt to analyze
            timeout: Request timeout in seconds
            static_analysis: Static analysis results for context
            retrieved_docs: Retrieved documents from vector store
            
        Returns:
            LLM response text
        """
        if not self.api_key:
            return f"Mock LLM Response: Analysis of '{prompt[:100]}...' - This is a simulated response as no API key is configured."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/JovianSanjaya/TechJam2025",
            "X-Title": "TikTok Compliance Analyzer"
        }
        
        # Build RAG context section (force RAG usage)
        rag_context = ""
        if retrieved_docs and retrieved_docs.get('documents') and retrieved_docs['documents'][0]:
            rag_context = "\n**📚 RELEVANT LEGAL DOCUMENTS:**\n"
            documents = retrieved_docs['documents'][0]
            metadatas = retrieved_docs.get('metadatas', [[]])[0]
            
            for i, (doc, meta) in enumerate(zip(documents[:3], metadatas[:3] if metadatas else [{}]*3)):
                title = meta.get('title', f'Document {i+1}') if meta else f'Document {i+1}'
                rag_context += f"\n**{title}:**\n{doc[:800]}...\n"
            
            rag_context += "\n**Use these legal documents to inform your analysis.**\n"
        else:
            rag_context = "\n**📚 LEGAL CONTEXT:** Using fallback RAG store - general compliance knowledge enhanced with keyword matching.\n"
        
        # Enhanced prompt matching code_analyzer_llm_clean format
        enhanced_prompt = f"""
You are an expert compliance analyst specializing in social media platforms like TikTok. 
Analyze the following feature for regulatory compliance issues, particularly focusing on:

1. **COPPA (Children's Online Privacy Protection Act)** - Age verification, parental consent
2. **GDPR/Privacy Laws** - Data collection, consent, user rights  
3. **Content Moderation** - Age-appropriate content, harmful content filtering
4. **Geolocation Privacy** - Location tracking, data localization
5. **Platform-specific regulations** - Youth protection, algorithmic transparency

{rag_context}

**Feature to analyze:**
{prompt}

**Static Analysis Context:**
{f"- Patterns Found: {len(static_analysis.get('patterns', []))}" if static_analysis else "- No static analysis provided"}
{f"- Categories: {', '.join([k for k, v in static_analysis.items() if isinstance(v, list) and v])}" if static_analysis else ""}

**Please provide a JSON response with:**
{{
  "enhanced_patterns": [
    {{
      "pattern_type": "category",
      "pattern_name": "specific_pattern",
      "confidence": 0.0-1.0,
      "location": "description",
      "code_snippet": "relevant_code",
      "description": "detailed_explanation",
      "regulation_hints": ["COPPA", "GDPR", etc.],
      "llm_analysis": "your_detailed_reasoning",
      "severity": "low|medium|high|critical",
      "legal_basis": "reference_to_retrieved_documents_if_applicable"
    }}
  ],
  "compliance_insights": {{
    "overall_assessment": "summary",
    "key_risks": ["risk1", "risk2"],
    "regulatory_gaps": ["gap1", "gap2"],
    "implementation_suggestions": ["suggestion1", "suggestion2"],
    "legal_references": ["references_from_retrieved_docs"]
  }},
  "enhanced_recommendations": [
    "actionable_recommendation_1",
    "actionable_recommendation_2"
  ],
  "confidence_adjustments": {{
    "reasoning": "why_adjustments_made",
    "adjusted_risk_score": 0.0-1.0,
    "rag_influence": "how_retrieved_documents_influenced_analysis"
  }}
}}

Focus on practical, actionable insights that developers can implement immediately.
"""
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert legal compliance analyst for social media platforms. Provide detailed, accurate analysis in valid JSON format."
                },
                {"role": "user", "content": enhanced_prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.3,  # Lower temperature for more consistent analysis
            "top_p": 0.9
        }
        
        try:
            print(f"🌐 Calling OpenRouter API...")
            print(f"   Model: {self.model}")
            print(f"   RAG Context: {'✅ Documents provided' if retrieved_docs else '⚠️ Using fallback context'}")
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.post(self.base_url, headers=headers, json=payload, timeout=timeout)
            )
            
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
