# Agents package
from pydantic import BaseModel, Field
from enum import Enum
from typing import Any

# --- Task & Plan Models ---
class TaskType(str, Enum):
    WEB_SEARCH = "web_search"
    DATA_EXTRACTION = "data_extraction"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    SYNTHESIS = "synthesis"
    REPORT_GENERATION = "report_generation"
    FACT_CHECK = "fact_check"

class SubTask(BaseModel):
    id: str = ""
    name: str = ""
    type: str = ""
    agent: str = ""
    description: str = ""
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)
    estimated_duration: str = ""
    dependencies: list[str] = Field(default_factory=list)

class ResearchPlan(BaseModel):
    plan_id: str = ""
    query: str = ""
    reasoning: str = ""
    tasks: list[SubTask] = Field(default_factory=list)
    estimated_total_duration: str = ""
    confidence_score: float = 1.0
    output: str = ""

# --- Researcher Models ---
class SearchResult(BaseModel):
    """Represents a single search result from web research."""
    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the source")
    snippet: str = Field(..., description="Brief excerpt from the source")
    source_name: str = Field(..., description="Name of the source website")
    published_date: str | None = Field(None, description="Publication date if available")
    relevance_score: float = Field(..., description="Relevance to query (0-1)")
    authority_score: float = Field(..., description="Source authority (0-1)")
    raw_data: dict[str, Any] = Field(default_factory=dict, description="Raw data from search API")

class ResearchResults(BaseModel):
    """Complete research results from a search session."""
    query: str = Field(..., description="The search query")
    timestamp: str = Field(..., description="When the research was conducted")
    total_sources: int = Field(..., description="Total number of sources found")
    high_confidence_sources: list[SearchResult] = Field(..., description="High relevance sources")
    medium_confidence_sources: list[SearchResult] = Field(..., description="Medium relevance sources")
    sources_used: list[str] = Field(..., description="URLs of all sources consulted")
    search_metadata: dict[str, Any] = Field(default_factory=dict, description="Search execution metadata")
    confidence_score: float = Field(..., description="Overall confidence in results (0-1)")
    gaps_identified: list[str] = Field(default_factory=list, description="Information gaps found")

# --- Analyst Models ---
class EvidenceStrength(str, Enum):
    STRONG = "strong"
    MEDIUM = "medium"
    WEAK = "weak"

class AnalysisInsight(BaseModel):
    category: str = ""
    statement: str = ""
    confidence: float = 0.0
    evidence: str = ""
    evidence_strength: EvidenceStrength = EvidenceStrength.MEDIUM
    source_count: int = 0

class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RiskAssessment(BaseModel):
    risk_id: str = ""
    title: str = ""
    description: str = ""
    level: RiskLevel = RiskLevel.MEDIUM
    probability: float = 0.0
    impact: float = 0.0
    risk_score: float = 0.0
    mitigation: str = ""
    confidence: float = 0.0

class AnalysisResults(BaseModel):
    query: str = ""
    key_findings: list[AnalysisInsight] = Field(default_factory=list)
    risks_identified: list[RiskAssessment] = Field(default_factory=list)
    patterns_detected: list[str] = Field(default_factory=list)
    reasoning_chain: list[str] = Field(default_factory=list)
    overall_confidence: float = 0.0
    data_sources_analyzed: list[str] = Field(default_factory=list)

# --- Competitive Analysis Models ---
class CompetitorInsight(BaseModel):
    """A single competitive insight from the landscape analysis."""
    competitor_name: str = Field(default="", description="Name of the competitor or market player")
    insight: str = Field(..., description="Key competitive insight")
    category: str = Field(default="general", description="Category: market_share, technology, pricing, strategy")
    confidence: float = Field(default=0.5, description="Confidence in this insight (0-1)")
    source: str = Field(default="", description="Source of the insight")

class CompetitiveAnalysisResult(BaseModel):
    """Complete competitive landscape analysis result."""
    query: str = Field(..., description="Original analysis query")
    analysis_id: str = Field(..., description="Unique analysis identifier")
    timestamp: str = Field(..., description="When the analysis was performed")
    market_overview: str = Field(default="", description="High-level market overview")
    key_competitors: list[CompetitorInsight] = Field(default_factory=list, description="Key competitor insights")
    market_trends: list[str] = Field(default_factory=list, description="Identified market trends")
    strategic_recommendations: list[str] = Field(default_factory=list, description="Strategic recommendations")
    swot_analysis: dict[str, list[str]] = Field(
        default_factory=lambda: {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
        description="SWOT analysis"
    )
    confidence_score: float = Field(default=0.5, description="Overall confidence (0-1)")
    raw_response: str = Field(default="", description="Raw response from the agent")

# --- Writer Models ---
class ReportFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"

class ReportMetadata(BaseModel):
    title: str = ""
    report_id: str = ""
    confidence_score: float = 0.0
    processing_time_seconds: float = 0.0
    generated_at: str = ""

class ReportSection(BaseModel):
    title: str = ""
    content: str = ""

class GeneratedReport(BaseModel):
    metadata: ReportMetadata = Field(default_factory=ReportMetadata)
    executive_summary: str = ""
    sections: list[ReportSection] = Field(default_factory=list)
    conclusions: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    citations: list[dict[str, Any]] = Field(default_factory=list)

# --- Dummy fallback Agent classes ---
class PlannerAgent:
    async def decompose_task(self, query: str) -> ResearchPlan:
        return ResearchPlan(query=query)
    async def validate_plan(self, plan: ResearchPlan) -> dict:
        return {"can_proceed": True, "is_valid": True}

class ResearcherAgent:
    async def search(self, query: str, max_results: int = 10) -> ResearchResults:
        return ResearchResults(query=query)

class AnalystAgent:
    async def analyze(self, query: str, research_data: dict) -> AnalysisResults:
        return AnalysisResults(query=query)

class WriterAgent:
    async def generate_report(self, query: str, analysis_results: dict) -> GeneratedReport:
        return GeneratedReport()

class CompetitiveLandscapeAgent:
    async def analyze_competitive_landscape(self, query: str, industry: str = "", region: str = "") -> CompetitiveAnalysisResult:
        return CompetitiveAnalysisResult(query=query, analysis_id="dummy", timestamp="")

__all__ = [
    "PlannerAgent",
    "ResearcherAgent",
    "AnalystAgent",
    "WriterAgent",
    "CompetitiveLandscapeAgent",
    "ResearchPlan",
    "SubTask",
    "TaskType",
    "SearchResult",
    "ResearchResults",
    "EvidenceStrength",
    "AnalysisInsight",
    "RiskLevel",
    "RiskAssessment",
    "AnalysisResults",
    "CompetitorInsight",
    "CompetitiveAnalysisResult",
    "ReportFormat",
    "ReportMetadata",
    "ReportSection",
    "GeneratedReport",
]