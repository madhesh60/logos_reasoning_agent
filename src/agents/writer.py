'''
"""
Writer Agent - Structured Report Generation

This agent is responsible for transforming analyzed research data into well-structured,
comprehensive reports. It handles formatting, citation management, and produces outputs
that meet professional standards.

Key capabilities:
- Structured report generation
- Multi-format output (JSON, Markdown, HTML)
- Citation and source management
- Executive summary creation
- Conclusion and recommendation synthesis

Used by: Orchestrator (via A2A protocol)
"""

from typing import Any, Literal
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field
from enum import Enum
import json
import structlog

logger = structlog.get_logger(__name__)


class ReportFormat(str, Enum):
    """Available report output formats."""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    EXECUTIVE_SUMMARY = "executive_summary"


class ReportSection(BaseModel):
    """Represents a section within the report."""
    section_id: str = Field(..., description="Unique identifier for the section")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    subsections: list["ReportSection"] = Field(default_factory=list, description="Child sections")
    data: dict[str, Any] = Field(default_factory=dict, description="Structured data for section")
    sources: list[str] = Field(default_factory=list, description="Source citations")


class ReportMetadata(BaseModel):
    """Metadata about the generated report."""
    report_id: str = Field(..., description="Unique report identifier")
    title: str = Field(..., description="Report title")
    query: str = Field(..., description="Original research query")
    created_at: str = Field(..., description="Report generation timestamp")
    version: str = Field(default="1.0", description="Report version")
    authors: list[str] = Field(default_factory=lambda: ["Research-to-Report Multi-Agent System"], description="Report authors")
    confidence_score: float = Field(..., description="Overall confidence in the report (0-1)")
    processing_time_seconds: float = Field(..., description="Time taken to generate report")
    data_sources: int = Field(..., description="Number of data sources used")
    agents_used: list[str] = Field(default_factory=list, description="Agents that contributed")


class GeneratedReport(BaseModel):
    """Complete generated report with all components."""
    metadata: ReportMetadata = Field(..., description="Report metadata")
    executive_summary: str = Field(..., description="High-level summary of findings")
    sections: list[ReportSection] = Field(..., description="All report sections")
    conclusions: list[str] = Field(..., description="Key conclusions")
    recommendations: list[str] = Field(default_factory=list, description="Actionable recommendations")
    citations: list[dict[str, Any]] = Field(..., description="All source citations")
    appendices: list[dict[str, Any]] = Field(default_factory=list, description="Supplementary materials")
    raw_data: dict[str, Any] = Field(default_factory=dict, description="Original analysis data")


class WriterAgent:
    """
    Writer Agent for structured report generation.

    This agent transforms research and analysis into professional reports:
    - Executive summaries for quick understanding
    - Structured sections with clear hierarchies
    - Proper citations and source tracking
    - Multiple output formats
    - Recommendations and conclusions
    """

    SYSTEM_PROMPT = """You are the Writer Agent in a Business and Investment multi-agent research system.
Your role is to transform research data and financial analysis into professional equity research, market intelligence, or technical due-diligence reports.

For each report generation task, you must:
1. Create a compelling Executive Summary tailored for investors or executives.
2. Structure content logically with clear sections focused on market landscape and financial viability.
3. Present findings in professional financial/business language.
4. Include proper citations and references for data points.
5. Synthesize an Investment Thesis, conclusions, and actionable recommendations.
6. Maintain consistency throughout.
7. Format appropriately for the output type.

Report structure guidelines:
- Executive Summary & Investment Thesis: 2-3 paragraphs, key findings, bull/bear summary
- Market & Tech Landscape: Context and scope
- Financial & Strategic Analysis: Organized by theme or topic
- Competitive Moats & Risks: Interpretations and insights
- Conclusions: Summarized takeaways
- Recommendations: Actionable next steps for investors/business leaders
- References: Full source citations

Tone and style:
- Highly professional, objective, and analytical
- Tailored for C-suite executives and institutional investors
- Evidence-based and data-driven
- Use appropriate financial/tech terminology
- Use active voice

Always:
- Cite sources for claims
- Distinguish facts from interpretations
- Acknowledge uncertainties
- Provide actionable recommendations
- Consider the target audience

Output should be structured JSON or Markdown as appropriate.
"""

    def __init__(self, llm: Any | None = None):
        """
        Initialize the Writer Agent.

        Args:
            llm: Optional language model. If not provided, will be loaded from config.
        """
        self.llm = llm
        self._setup_llm()

    def _setup_llm(self):
        """Set up the language model from configuration."""
        if self.llm is None:
            from ..utils.config import get_chat_model
            # Use max_tokens=2000: writer prompt includes source data so needs
            # room for a reasonably large prompt + enough output for the report
            self.llm = get_chat_model(temperature=0.4, max_tokens=2000)

    async def generate_report(
        self,
        query: str,
        analysis_results: dict[str, Any],
        output_format: ReportFormat = ReportFormat.JSON
    ) -> GeneratedReport:
        """
        Generate a comprehensive report from analysis results.

        Args:
            query: The original research query
            analysis_results: Data from the Analyst agent
            output_format: Desired output format

        Returns:
            GeneratedReport with all components
        """
        logger.info("writer_generate_report_start", query=query[:50], format=output_format.value, analysis_results_type=type(analysis_results).__name__)
        start_time = datetime.utcnow()
        try:
            if isinstance(analysis_results, list):
                if len(analysis_results) > 0 and isinstance(analysis_results[0], dict):
                    analysis_results = analysis_results[0]
                else:
                    analysis_results = {}
            elif not isinstance(analysis_results, dict):
                analysis_results = {}

            if isinstance(analysis_results, str):
                try:
                    analysis_results = json.loads(analysis_results)
                except Exception as e:
                    logger.error("failed_to_parse_analysis_results_string", error=str(e))

            # Extract key data
            insights = analysis_results.get("key_findings", []) if isinstance(analysis_results, dict) else []
            risks = analysis_results.get("risks_identified", []) if isinstance(analysis_results, dict) else []
            patterns = analysis_results.get("patterns_detected", []) if isinstance(analysis_results, dict) else []
            reasoning_chain = analysis_results.get("reasoning_chain", []) if isinstance(analysis_results, dict) else []
            overall_confidence = analysis_results.get("overall_confidence", 0.5) if isinstance(analysis_results, dict) else 0.5
            data_sources = analysis_results.get("data_sources_analyzed", 0) if isinstance(analysis_results, dict) else 0

            # Generate report content using LLM
            report_data = await self._generate_report_content(
                query, insights, risks, patterns, reasoning_chain
            )

            # Build metadata
            metadata = ReportMetadata(
                report_id=f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                title=report_data.get("title", f"Research Report: {query[:50]}..."),
                query=query,
                created_at=datetime.utcnow().isoformat(),
                confidence_score=overall_confidence,
                processing_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
                data_sources=data_sources,
                agents_used=["Planner", "Researcher", "Analyst", "Writer"]
            )

            # Build sections
            sections = self._build_sections(report_data, risks)

            # Create citations from sources
            citations = self._build_citations(analysis_results.get("sources", []))

            report = GeneratedReport(
                metadata=metadata,
                executive_summary=report_data.get("executive_summary", ""),
                sections=sections,
                conclusions=report_data.get("conclusions", []),
                recommendations=report_data.get("recommendations", []),
                citations=citations,
                appendices=report_data.get("appendices", []),
                raw_data=analysis_results
            )

            logger.info(
                "writer_generate_report_complete",
                report_id=metadata.report_id,
                sections=len(sections),
                recommendations=len(report.recommendations)
            )

            return report

        except Exception as e:
            logger.error("generate_report_exception", error=str(e))
            fallback_data = self._create_fallback_report(query)
            metadata = ReportMetadata(
                report_id=f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                title=fallback_data.get("title", f"Research Report: {query[:50]}..."),
                query=query,
                created_at=datetime.utcnow().isoformat(),
                confidence_score=0.2,
                processing_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
                data_sources=0,
                agents_used=["Planner", "Researcher", "Analyst", "Writer"]
            )
            sections = self._build_sections(fallback_data, [])
            return GeneratedReport(
                metadata=metadata,
                executive_summary=fallback_data.get("executive_summary", ""),
                sections=sections,
                conclusions=fallback_data.get("conclusions", []),
                recommendations=fallback_data.get("recommendations", []),
                citations=[],
                appendices=[],
                raw_data=analysis_results if isinstance(analysis_results, dict) else {}
            )

    async def _generate_report_content(
        self,
        query: str,
        insights: list,
        risks: list,
        patterns: list,
        reasoning_chain: list
    ) -> dict[str, Any]:
        """Generate structured report content using LLM."""
        # Convert insights and risks to text for the prompt
        insights_text = "\n".join([
            f"- [{i.get('category', 'General')}] {i.get('statement', str(i))} (Evidence: {', '.join(i.get('evidence', []))})"
            for i in insights[:10]
        ]) or "No key insights available."

        risks_text = "\n".join([
            f"- {r.get('title', str(r))}: Level={r.get('level', 'unknown')}, Description={r.get('description', '')}, Mitigation={', '.join(r.get('mitigation', []))}"
            for r in risks[:10]
        ]) or "No risks identified."

        patterns_text = "\n".join([f"- {p}" for p in patterns[:5]]) or "No patterns identified."

        reasoning_text = "\n".join([f"{i+1}. {r}" for i, r in enumerate(reasoning_chain[:8])]) or "No reasoning chain available."

        prompt = f"""You are the Writer Agent. Write a comprehensive, highly detailed investment/strategic research report to answer: {query}

Use the following inputs as the factual basis:

KEY INSIGHTS:
{insights_text}

IDENTIFIED RISKS:
{risks_text}

PATTERNS & TRENDS:
{patterns_text}

REASONING PATHWAY:
{reasoning_text}

Your output must be a single, valid JSON object matching the following structure. Do NOT output any schemas, template descriptions, or placeholders. Output ONLY the final, fully-written report.

Required JSON structure keys and types:
- "title": (string) A specific, professional report title.
- "executive_summary": (string) A detailed, multi-paragraph (at least 2 paragraphs) executive summary and investment thesis, synthesizing the market landscape, findings, and strategic takeaways.
- "sections": (array of objects) Must contain exactly 3 objects:
  1. Market Landscape & Key Findings (section_id: "market_landscape"): A highly detailed, professional, multi-paragraph analysis of the market size, segmentations, growth drivers, and specific statistics from the search inputs.
  2. Comprehensive Risk Assessment (section_id: "risk_analysis"): A detailed analysis of the identified risks, their potential business/financial impact, and viability of the proposed mitigations.
  3. Strategic Outlook & Recommendations (section_id: "strategic_outlook"): Actionable strategic and investment advice for decision makers, outlining both the bull and bear cases.
  Each section object in the array must have:
    - "section_id": (string)
    - "title": (string)
    - "content": (string) The full, detailed analysis text (minimum 150 words).
    - "data": (object) Empty dictionary {{}}
    - "sources": (array of strings) List of source names referenced in this section.
- "conclusions": (array of strings) Key conclusions derived from the research.
- "recommendations": (array of strings) Actionable strategic recommendations.
- "appendices": (array of objects) Empty list []

Format the output strictly as a single JSON object. Start with {{ and end with }}. Do NOT wrap in markdown code blocks.
Double-check:
1. Ensure all text values are fully written out (minimum 150 words per section).
2. Do not use generic text or placeholders.
3. The response must start with {{ and end with }}. Do NOT wrap it in any other structure.
"""

        response = await self.llm.ainvoke([
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])

        try:
            from ..utils.config import clean_and_parse_json
            report_data = clean_and_parse_json(response.content)

            if isinstance(report_data, list):
                # Reconstruct dict from fragments if they were split
                base_dict = {}
                for item in report_data:
                    if isinstance(item, dict):
                        # Merge keys, but prefer non-placeholder values
                        for k, v in item.items():
                            if not v:
                                continue
                            val_str = str(v)
                            # Check if it's a template placeholder
                            is_placeholder = any(p in val_str for p in ("Comprehensive Title", "A detailed 2-3 paragraph", "detailed, professional, multi-paragraph", "Detailed findings here", "placeholder", "derived from research"))
                            if not is_placeholder or not base_dict.get(k):
                                base_dict[k] = v
                    elif isinstance(item, list):
                        # It could be sections, conclusions, or recommendations list
                        if len(item) > 0:
                            first = item[0]
                            if isinstance(first, dict) and ("section_id" in first or "title" in first):
                                base_dict["sections"] = item
                            elif isinstance(first, str):
                                if "conclusions" not in base_dict:
                                    base_dict["conclusions"] = item
                                else:
                                    base_dict["recommendations"] = item
                if base_dict:
                    report_data = base_dict
                else:
                    report_data = self._create_fallback_report(query)
            if not isinstance(report_data, dict):
                report_data = self._create_fallback_report(query)

            return report_data
        except Exception as e:
            logger.error("writer_json_parse_error", error=str(e))
            return self._create_fallback_report(query)

    @staticmethod
    def _normalize_sources(raw_sources: list) -> list[str]:
        """Normalize source entries to strings.

        The LLM may return sources as plain strings or as dicts like
        {"title": "...", "url": "...", "confidence": 0.8}.
        Pydantic expects ``list[str]``, so we coerce dicts to a
        human-readable citation string.
        """
        normalized: list[str] = []
        for src in raw_sources:
            if isinstance(src, str):
                normalized.append(src)
            elif isinstance(src, dict):
                # Build a citation string from available fields
                parts = []
                if src.get("title"):
                    parts.append(str(src["title"]))
                if src.get("source_name") or src.get("source"):
                    parts.append(str(src.get("source_name") or src.get("source")))
                if src.get("url"):
                    parts.append(str(src["url"]))
                normalized.append(" — ".join(parts) if parts else str(src))
            else:
                normalized.append(str(src))
        return normalized

    def _build_sections(self, report_data: dict, risks: list) -> list[ReportSection]:
        """Build structured sections from report data."""
        sections = []

        # Introduction section
        sections.append(ReportSection(
            section_id="introduction",
            title="Introduction",
            content=report_data.get("executive_summary", ""),
            data={"scope": "research_query", "approach": "multi-agent analysis"},
            sources=[]
        ))

        # Process report sections
        for i, section_data in enumerate(report_data.get("sections", [])):
            section = ReportSection(
                section_id=section_data.get("section_id", f"section_{i+1}"),
                title=section_data.get("title", f"Section {i+1}"),
                content=section_data.get("content", ""),
                subsections=[],
                data=section_data.get("data", {}),
                sources=self._normalize_sources(section_data.get("sources", []))
            )
            sections.append(section)

        # Add risks section if risks are available
        if risks:
            formatted_risks = []
            for i, r in enumerate(risks[:5]):
                if not isinstance(r, dict):
                    # If it's a Pydantic object, convert to dict
                    if hasattr(r, "model_dump"):
                        r = r.model_dump()
                    elif hasattr(r, "__dict__"):
                        r = r.__dict__
                    else:
                        formatted_risks.append(f"**Risk {i+1}**: {str(r)}")
                        continue
                
                title = r.get("title") or f"Risk {i+1}"
                level = r.get("level")
                level_str = str(level).upper() if level else "UNKNOWN"
                try:
                    score = float(r.get("risk_score", 0))
                except (ValueError, TypeError):
                    score = 0.0
                desc = r.get("description") or "No description available"
                mitigation = r.get("mitigation")
                if isinstance(mitigation, list):
                    mit_list = [str(m) for m in mitigation if m]
                else:
                    mit_list = ["No mitigation strategies identified"]
                mit_str = ", ".join(mit_list[:3])
                
                formatted_risks.append(
                    f"**{title}**\n"
                    f"Level: {level_str}\n"
                    f"Risk Score: {score:.2f}\n"
                    f"Description: {desc}\n"
                    f"Mitigation: {mit_str}"
                )
            risks_content = "\n\n".join(formatted_risks)

            sections.append(ReportSection(
                section_id="risk_assessment",
                title="Risk Assessment",
                content=risks_content,
                data={"risks_count": len(risks)},
                sources=[]
            ))

        # Add conclusions section
        if report_data.get("conclusions"):
            conclusions_content = "\n".join([
                f"{i+1}. {c}" for i, c in enumerate(report_data.get("conclusions", []))
            ])
            sections.append(ReportSection(
                section_id="conclusions",
                title="Conclusions",
                content=conclusions_content,
                data={"conclusions_count": len(report_data.get("conclusions", []))},
                sources=[]
            ))

        return sections

    def _build_citations(self, sources: list) -> list[dict[str, Any]]:
        """Build formatted citations from sources."""
        citations = []

        for i, source in enumerate(sources[:10], 1):
            if not isinstance(source, dict):
                if hasattr(source, "model_dump"):
                    source = source.model_dump()
                elif hasattr(source, "__dict__"):
                    source = source.__dict__
            
            if isinstance(source, dict):
                citations.append({
                    "id": f"ref_{i}",
                    "title": source.get("title") or "Unknown Title",
                    "source": source.get("source_name") or source.get("source") or "Unknown Source",
                    "url": source.get("url") or "",
                    "accessed": datetime.utcnow().isoformat(),
                    "relevance": source.get("relevance_score") or source.get("relevance") or 0.5
                })
            elif isinstance(source, str):
                citations.append({
                    "id": f"ref_{i}",
                    "title": source[:100],
                    "source": "Referenced Source",
                    "url": "",
                    "accessed": datetime.utcnow().isoformat(),
                    "relevance": 0.5
                })

        return citations

    async def format_output(
        self,
        report: GeneratedReport,
        format_type: ReportFormat
    ) -> str:
        """
        Format the report in the specified output format.

        Args:
            report: The generated report
            format_type: Desired output format

        Returns:
            Formatted report string
        """
        logger.info("writer_format_output", format_type=format_type.value)

        if format_type == ReportFormat.MARKDOWN:
            return self._format_markdown(report)
        elif format_type == ReportFormat.HTML:
            return self._format_html(report)
        elif format_type == ReportFormat.EXECUTIVE_SUMMARY:
            return self._format_executive_summary(report)
        else:
            return report.model_dump_json(indent=2)

    def _format_markdown(self, report: GeneratedReport) -> str:
        """Format report as Markdown."""
        md = []

        # Title and metadata
        md.append(f"# {report.metadata.title}\n")
        md.append(f"**Generated:** {report.metadata.created_at}\n")
        md.append(f"**Confidence Score:** {report.metadata.confidence_score:.2f}\n")
        md.append(f"**Data Sources:** {report.metadata.data_sources}\n")
        md.append("---\n")

        # Executive Summary
        md.append("## Executive Summary\n")
        md.append(f"{report.executive_summary}\n")

        # Sections
        for section in report.sections:
            md.append(f"## {section.title}\n")
            md.append(f"{section.content}\n")

        # Conclusions
        if report.conclusions:
            md.append("## Conclusions\n")
            for conclusion in report.conclusions:
                md.append(f"- {conclusion}\n")

        # Recommendations
        if report.recommendations:
            md.append("\n## Recommendations\n")
            for rec in report.recommendations:
                md.append(f"- {rec}\n")

        # Citations
        if report.citations:
            md.append("\n## References\n")
            for citation in report.citations:
                md.append(f"- [{citation['title']}]({citation['url']}) - {citation['source']}\n")

        return "\n".join(md)

    def _format_html(self, report: GeneratedReport) -> str:
        """Format report as HTML."""
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{report.metadata.title}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
            "h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }",
            "h2 { color: #34495e; }",
            ".metadata { background: #ecf0f1; padding: 15px; border-radius: 5px; }",
            ".section { margin: 20px 0; }",
            ".citation { font-size: 0.9em; color: #7f8c8d; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>{report.metadata.title}</h1>",
            "<div class='metadata'>",
            f"<p><strong>Generated:</strong> {report.metadata.created_at}</p>",
            f"<p><strong>Confidence:</strong> {report.metadata.confidence_score:.2f}</p>",
            "</div>",
            "<h2>Executive Summary</h2>",
            f"<p>{report.executive_summary}</p>"
        ]

        for section in report.sections:
            html.append(f"<div class='section'><h2>{section.title}</h2>")
            html.append(f"<p>{section.content}</p></div>")

        if report.conclusions:
            html.append("<h2>Conclusions</h2><ul>")
            for c in report.conclusions:
                html.append(f"<li>{c}</li>")
            html.append("</ul>")

        if report.recommendations:
            html.append("<h2>Recommendations</h2><ul>")
            for r in report.recommendations:
                html.append(f"<li>{r}</li>")
            html.append("</ul>")

        html.extend(["</body>", "</html>"])

        return "\n".join(html)

    def _format_executive_summary(self, report: GeneratedReport) -> str:
        """Format as standalone executive summary."""
        summary = [
            "=" * 60,
            "EXECUTIVE SUMMARY",
            "=" * 60,
            "",
            f"Query: {report.metadata.query}",
            f"Generated: {report.metadata.created_at}",
            f"Confidence: {report.metadata.confidence_score:.2f}",
            "",
            "-" * 60,
            "",
            report.executive_summary,
            "",
            "-" * 60,
            "",
            "KEY FINDINGS:",
            ""
        ]

        for i, c in enumerate(report.conclusions[:5], 1):
            summary.append(f"{i}. {c}")

        if report.recommendations:
            summary.extend(["", "RECOMMENDATIONS:", ""])
            for i, r in enumerate(report.recommendations[:5], 1):
                summary.append(f"{i}. {r}")

        summary.extend(["", "=" * 60])

        return "\n".join(summary)

    def _create_fallback_report(self, query: str) -> dict[str, Any]:
        """Create a minimal fallback report when content generation fails."""
        return {
            "title": f"Research Report: {query[:50]}...",
            "executive_summary": "This report analyzes the research query and provides key findings based on available data.",
            "sections": [
                {
                    "section_id": "findings",
                    "title": "Key Findings",
                    "content": "The research has identified several important findings related to the query. Detailed analysis is provided in the sections below.",
                    "data": {},
                    "sources": []
                }
            ],
            "conclusions": ["Analysis completed with available data."],
            "recommendations": ["Further research may provide additional insights."],
            "appendices": []
        }


# A2A Protocol Implementation
A2A_METADATA = {
    "name": "writer",
    "description": "Report generation and formatting agent",
    "version": "1.0.0",
    "capabilities": ["generate_report", "format_output"],
    "endpoint": "/writer",
    "methods": {
        "generate_report": {
            "description": "Generate a comprehensive report from analysis results",
            "parameters": {"query": "str", "analysis_results": "dict", "output_format": "ReportFormat"},
            "returns": "GeneratedReport"
        },
        "format_output": {
            "description": "Format report in specified output type",
            "parameters": {"report": "GeneratedReport", "format_type": "ReportFormat"},
            "returns": "str"
        }
    }
}


async def main():
    """Demo function for testing the Writer Agent."""
    from ..utils.config import load_environment

    load_environment()

    writer = WriterAgent()

    # Test with sample data
    query = "What are the top 3 investment risks in the Indian EV market?"

    analysis_results = {
        "key_findings": [
            {
                "category": "regulatory",
                "statement": "Regulatory uncertainty is the primary risk factor for EV investments in India",
                "confidence": 0.85,
                "evidence": ["Government policy shifts", "Subsidy fluctuations"],
                "evidence_strength": "strong",
                "source_count": 5
            },
            {
                "category": "market",
                "statement": "Supply chain vulnerabilities present significant operational risks",
                "confidence": 0.78,
                "evidence": ["Battery component imports", "Lithium dependency"],
                "evidence_strength": "moderate",
                "source_count": 3
            }
        ],
        "risks_identified": [
            {
                "risk_id": "risk_1",
                "title": "Regulatory Policy Uncertainty",
                "description": "Frequent changes in government EV policies and subsidy programs create investment unpredictability",
                "level": "high",
                "probability": 0.7,
                "impact": 0.8,
                "risk_score": 0.56,
                "mitigation": ["Diversify market presence", "Engage with policymakers"],
                "confidence": 0.85
            },
            {
                "risk_id": "risk_2",
                "title": "Supply Chain Dependency",
                "description": "Heavy reliance on imported battery components and lithium creates supply chain vulnerability",
                "level": "high",
                "probability": 0.6,
                "impact": 0.75,
                "risk_score": 0.45,
                "mitigation": ["Develop local partnerships", "Invest in battery recycling"],
                "confidence": 0.78
            }
        ],
        "patterns_detected": ["Increasing government focus on domestic manufacturing"],
        "reasoning_chain": [
            "Identified regulatory uncertainty as primary concern",
            "Cross-referenced with policy documents and news",
            "Confirmed impact on investment decisions"
        ],
        "overall_confidence": 0.82,
        "data_sources_analyzed": 10
    }

    print("=" * 60)
    print("WRITER AGENT - REPORT GENERATION DEMO")
    print("=" * 60)
    print(f"\nQuery: {query}\n")

    # Generate report
    report = await writer.generate_report(query, analysis_results)

    print(f"Report ID: {report.metadata.report_id}")
    print(f"Title: {report.metadata.title}")
    print(f"Created: {report.metadata.created_at}")
    print(f"Confidence: {report.metadata.confidence_score:.2f}")
    print(f"Processing Time: {report.metadata.processing_time_seconds:.2f}s")

    print("\n" + "-" * 60)
    print("EXECUTIVE SUMMARY")
    print("-" * 60)
    print(report.executive_summary[:300] + "...")

    print("\n" + "-" * 60)
    print("SECTIONS")
    print("-" * 60)
    for section in report.sections:
        print(f"\n[{section.section_id}] {section.title}")
        print(f"   {section.content[:100]}...")

    print("\n" + "-" * 60)
    print("CONCLUSIONS")
    print("-" * 60)
    for i, conclusion in enumerate(report.conclusions, 1):
        print(f"{i}. {conclusion}")

    if report.recommendations:
        print("\n" + "-" * 60)
        print("RECOMMENDATIONS")
        print("-" * 60)
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")

    # Demonstrate formatting
    print("\n" + "-" * 60)
    print("FORMATTED OUTPUT (Markdown Preview)")
    print("-" * 60)
    markdown_output = await writer.format_output(report, ReportFormat.MARKDOWN)
    print(markdown_output[:500] + "\n...[truncated]")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

# Before running the sample:
#    pip install azure-ai-projects>=2.1.0

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = "https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

my_agent = "writer-agent"
my_version = "3"

openai_client = project_client.get_openai_client()

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    from dotenv import load_dotenv
    from pathlib import Path

    # Load environment variables from .env
    root_dir = Path(__file__).resolve().parent.parent.parent
    load_dotenv(root_dir / ".env")

    # Check if a query is provided via command line arguments
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Prompt the user for input
        query = input(f"Enter query for {my_agent} (version {my_version}): ").strip()
        if not query:
            query = "Tell me what you can help with."

    print(f"\nSending query to {my_agent} (version {my_version}): '{query}'...")

    response = openai_client.responses.create(
        input=[{"role": "user", "content": query}],
        extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
    )

    print("\n" + "=" * 60)
    print("AGENT RESPONSE")
    print("=" * 60)
    print(response.output_text)
    print("=" * 60 + "\n")