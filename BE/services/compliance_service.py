"""
Compliance Service - Business logic layer
"""
from typing import Dict, Any
from core.analyzer import UnifiedComplianceAnalyzer

class ComplianceService:
    """Service layer for compliance analysis operations"""
    
    def __init__(self):
        self.analyzer = UnifiedComplianceAnalyzer()
    
    async def analyze_feature(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a feature for compliance
        
        Args:
            feature_data: Dictionary containing feature information
            
        Returns:
            Analysis results
        """
        return await self.analyzer.analyze_feature(feature_data)
