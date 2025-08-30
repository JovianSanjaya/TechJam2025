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
    
    async def analyze(self, prompt: str, timeout: int = 30) -> str:
        """
        Analyze prompt using LLM
        
        Args:
            prompt: The prompt to analyze
            timeout: Request timeout in seconds
            
        Returns:
            LLM response text
        """
        if not self.api_key:
            return f"Mock LLM Response: Analysis of '{prompt[:100]}...' - This is a simulated response as no API key is configured."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
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
            "model": self.model,
            "messages": [
                {"role": "user", "content": enhanced_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            print(f"🌐 Calling OpenRouter API with model: {self.model}")
            
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
