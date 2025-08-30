"""
Core type definitions for compliance analysis.

This module defines the primary data structures used throughout the compliance
analysis system, including configuration classes, analysis results, and
response objects for different analysis components.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class AnalysisStatus(Enum):
    """Enumeration of possible analysis status values."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class RiskLevel(Enum):
    """Enumeration of risk levels for compliance assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class CompliancePattern:
    """
    Represents a compliance pattern found in code.
    
    Contains information about detected compliance patterns including
    location, confidence level, and regulatory implications.
    """
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
    """
    Response from LLM analysis.
    
    Contains structured results from Large Language Model analysis including
    enhanced patterns, compliance insights, and recommendations.
    """
    enhanced_patterns: List[Dict]
    compliance_insights: Dict
    enhanced_recommendations: List[str]
    confidence_adjustments: Dict
    raw_response: str
    problematic_code_analysis: List[Dict] = None
    compliance_gaps: List[Dict] = None
    code_quality_improvements: List[Dict] = None


@dataclass
class ComplianceResult:
    """
    Final compliance analysis result.
    
    Represents the comprehensive output of compliance analysis including
    risk assessment, applicable regulations, and implementation guidance.
    """
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
    """
    Configuration for compliance analysis.
    
    Defines settings and parameters that control the behavior of the
    compliance analysis system including service enablement and thresholds.
    """
    use_llm: bool = True
    force_llm: bool = False
    use_rag: bool = True
    max_patterns: int = 20
    confidence_threshold: float = 0.5
