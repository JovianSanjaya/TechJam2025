"""
Core type definitions for compliance analysis
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class AnalysisStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class CompliancePattern:
    """Represents a compliance pattern found in code"""
    pattern_type: str
    pattern_name: str
    confidence: float
    location: str
    code_snippet: str
    description: str
    regulation_hints: List[str]
    llm_analysis: Optional[str] = None
    severity: Optional[str] = None
    legal_basis: Optional[str] = None


@dataclass
class LLMResponse:
    """Response from LLM analysis"""
    enhanced_patterns: List[Dict]
    compliance_insights: Dict
    enhanced_recommendations: List[str]
    confidence_adjustments: Dict
    raw_response: str


@dataclass
class ComplianceResult:
    """Final compliance analysis result"""
    feature_name: str
    needs_compliance_logic: bool
    confidence: float
    reasoning: List[str]
    applicable_regulations: List[Dict]
    action_required: str
    human_review_needed: bool
    risk_level: str
    implementation_notes: List[str]
    patterns: List[CompliancePattern]
    llm_analysis: Optional[LLMResponse] = None
    timestamp: Optional[str] = None


@dataclass 
class AnalysisConfig:
    """Configuration for analysis"""
    use_llm: bool = True
    force_llm: bool = False
    use_rag: bool = True
    max_patterns: int = 20
    confidence_threshold: float = 0.5
