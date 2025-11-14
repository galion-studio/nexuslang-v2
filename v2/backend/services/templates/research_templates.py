"""
Research templates for Deep Search.
Provides pre-built workflows and configurations for common research tasks.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ...models.research import ResearchTemplate

logger = logging.getLogger(__name__)


class ResearchTemplateManager:
    """
    Manages research templates and pre-built workflows.

    Provides standardized approaches for common research scenarios:
    - Academic research papers
    - Technical documentation
    - Comparative analysis
    - Quick fact-checking
    - Industry analysis
    - Trend research
    """

    def __init__(self):
        # Built-in templates
        self.built_in_templates = {
            "academic_research": {
                "name": "Academic Research Paper",
                "description": "Comprehensive research methodology for academic papers with proper citations",
                "category": "academic",
                "default_persona": "isaac",
                "default_depth": "exhaustive",
                "workflow_steps": {
                    "objectives": [
                        "Define research question and hypothesis",
                        "Review existing literature",
                        "Identify research gaps",
                        "Design methodology"
                    ],
                    "research_phases": [
                        "Literature review (30% of effort)",
                        "Data collection and analysis (40% of effort)",
                        "Findings synthesis (20% of effort)",
                        "Conclusion and implications (10% of effort)"
                    ],
                    "quality_checks": [
                        "Peer review validation",
                        "Citation verification",
                        "Methodological rigor",
                        "Original contribution assessment"
                    ]
                },
                "suggested_tags": ["academic", "research", "methodology", "citations"],
                "estimated_time": "2-4 weeks",
                "difficulty": "expert"
            },

            "technical_documentation": {
                "name": "Technical Documentation",
                "description": "Create comprehensive technical documentation with code examples",
                "category": "technical",
                "default_persona": "technical",
                "default_depth": "comprehensive",
                "workflow_steps": {
                    "structure": [
                        "Overview and introduction",
                        "Architecture and design",
                        "Implementation details",
                        "API documentation",
                        "Troubleshooting guide",
                        "Best practices"
                    ],
                    "validation_steps": [
                        "Code example verification",
                        "Cross-reference checking",
                        "Technical accuracy review",
                        "Clarity and readability assessment"
                    ]
                },
                "suggested_tags": ["technical", "documentation", "api", "implementation"],
                "estimated_time": "1-2 weeks",
                "difficulty": "intermediate"
            },

            "comparative_analysis": {
                "name": "Comparative Analysis",
                "description": "Compare multiple options, technologies, or approaches",
                "category": "analysis",
                "default_persona": "default",
                "default_depth": "comprehensive",
                "workflow_steps": {
                    "comparison_framework": [
                        "Define comparison criteria",
                        "Identify alternatives to compare",
                        "Establish evaluation metrics",
                        "Create comparison matrix"
                    ],
                    "analysis_phases": [
                        "Feature comparison",
                        "Performance benchmarking",
                        "Cost-benefit analysis",
                        "Risk assessment",
                        "Recommendation synthesis"
                    ]
                },
                "suggested_tags": ["comparison", "analysis", "evaluation", "recommendations"],
                "estimated_time": "3-7 days",
                "difficulty": "intermediate"
            },

            "fact_checking": {
                "name": "Quick Fact Checking",
                "description": "Rapid verification of claims, statistics, and information",
                "category": "verification",
                "default_persona": "isaac",
                "default_depth": "quick",
                "workflow_steps": {
                    "verification_steps": [
                        "Identify claim to verify",
                        "Find original source",
                        "Cross-reference multiple sources",
                        "Check publication date and context",
                        "Assess source credibility"
                    ],
                    "output_format": [
                        "Verdict (True/False/Partially True/Misleading)",
                        "Supporting evidence",
                        "Source citations",
                        "Confidence level"
                    ]
                },
                "suggested_tags": ["fact-check", "verification", "credibility", "sources"],
                "estimated_time": "1-2 hours",
                "difficulty": "beginner"
            },

            "industry_analysis": {
                "name": "Industry Analysis",
                "description": "Analyze industry trends, market dynamics, and competitive landscape",
                "category": "business",
                "default_persona": "default",
                "default_depth": "comprehensive",
                "workflow_steps": {
                    "analysis_framework": [
                        "Industry overview and definition",
                        "Market size and growth trends",
                        "Competitive landscape analysis",
                        "Key player identification",
                        "Technology trends and innovations",
                        "Regulatory environment",
                        "Future outlook and predictions"
                    ],
                    "data_sources": [
                        "Industry reports (Gartner, Forrester, McKinsey)",
                        "Financial reports and earnings calls",
                        "Trade publications and news sources",
                        "Government statistics and regulations",
                        "Academic research and white papers"
                    ]
                },
                "suggested_tags": ["industry", "market", "trends", "competition", "analysis"],
                "estimated_time": "1-2 weeks",
                "difficulty": "advanced"
            },

            "trend_research": {
                "name": "Trend Research",
                "description": "Identify and analyze emerging trends in technology, society, or business",
                "category": "trends",
                "default_persona": "creative",
                "default_depth": "comprehensive",
                "workflow_steps": {
                    "trend_identification": [
                        "Monitor industry publications and news",
                        "Track social media conversations",
                        "Analyze patent filings and research papers",
                        "Follow thought leaders and influencers",
                        "Review startup funding and investments"
                    ],
                    "trend_analysis": [
                        "Assess trend maturity (emerging vs. established)",
                        "Evaluate potential impact and disruption",
                        "Identify key drivers and indicators",
                        "Forecast timeline and adoption curve",
                        "Analyze stakeholder implications"
                    ],
                    "reporting": [
                        "Trend summary and key insights",
                        "Supporting data and evidence",
                        "Timeline projections",
                        "Strategic recommendations"
                    ]
                },
                "suggested_tags": ["trends", "emerging", "innovation", "forecasting", "analysis"],
                "estimated_time": "1 week",
                "difficulty": "intermediate"
            },

            "user_research": {
                "name": "User Research Synthesis",
                "description": "Synthesize user feedback, interviews, and usability testing data",
                "category": "ux",
                "default_persona": "isaac",
                "default_depth": "comprehensive",
                "workflow_steps": {
                    "data_collection": [
                        "User interviews and transcripts",
                        "Survey responses and analytics",
                        "Usability testing observations",
                        "Support ticket analysis",
                        "Feedback forum reviews"
                    ],
                    "synthesis_process": [
                        "Identify common themes and patterns",
                        "Categorize feedback by user type",
                        "Prioritize issues by frequency and impact",
                        "Create user personas and journey maps",
                        "Develop actionable recommendations"
                    ],
                    "deliverables": [
                        "User insights report",
                        "Persona definitions",
                        "Usability recommendations",
                        "Design implications",
                        "Follow-up research suggestions"
                    ]
                },
                "suggested_tags": ["user-research", "ux", "feedback", "personas", "insights"],
                "estimated_time": "3-5 days",
                "difficulty": "intermediate"
            },

            "literature_review": {
                "name": "Literature Review",
                "description": "Comprehensive review and synthesis of existing research literature",
                "category": "academic",
                "default_persona": "isaac",
                "default_depth": "exhaustive",
                "workflow_steps": {
                    "search_strategy": [
                        "Define search terms and databases",
                        "Set inclusion/exclusion criteria",
                        "Execute systematic search",
                        "Remove duplicates and screen abstracts"
                    ],
                    "review_process": [
                        "Full-text review of selected papers",
                        "Data extraction and coding",
                        "Quality assessment of studies",
                        "Thematic analysis and synthesis",
                        "Identify research gaps"
                    ],
                    "reporting": [
                        "Search methodology description",
                        "Study characteristics summary",
                        "Findings synthesis and themes",
                        "Quality assessment results",
                        "Implications and future research directions"
                    ]
                },
                "suggested_tags": ["literature-review", "systematic", "synthesis", "research-gaps"],
                "estimated_time": "2-3 weeks",
                "difficulty": "expert"
            }
        }

    async def get_available_templates(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all available research templates.

        Args:
            category: Optional category filter

        Returns:
            Available templates
        """
        templates = {}

        # Add built-in templates
        for template_id, template_data in self.built_in_templates.items():
            if not category or template_data["category"] == category:
                templates[template_id] = {
                    "id": template_id,
                    "name": template_data["name"],
                    "description": template_data["description"],
                    "category": template_data["category"],
                    "is_builtin": True,
                    "usage_count": 0,  # Would be tracked in database
                    "estimated_time": template_data.get("estimated_time"),
                    "difficulty": template_data.get("difficulty"),
                    "suggested_tags": template_data.get("suggested_tags", [])
                }

        # TODO: Add user-created templates from database
        # This would query ResearchTemplate table for user-created templates

        return {
            "success": True,
            "templates": templates,
            "total": len(templates),
            "categories": list(set(t["category"] for t in templates.values()))
        }

    async def get_template_details(self, template_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific template.

        Args:
            template_id: Template identifier

        Returns:
            Template details
        """
        if template_id in self.built_in_templates:
            template_data = self.built_in_templates[template_id]
            return {
                "success": True,
                "template": {
                    "id": template_id,
                    **template_data
                }
            }

        # TODO: Check for user-created templates in database
        return {
            "success": False,
            "error": f"Template '{template_id}' not found"
        }

    async def apply_template_to_research(self, template_id: str, research_query: str) -> Dict[str, Any]:
        """
        Apply a template configuration to a research query.

        Args:
            template_id: Template to apply
            research_query: Research query to enhance

        Returns:
            Enhanced research configuration
        """
        template_result = await self.get_template_details(template_id)
        if not template_result["success"]:
            return template_result

        template = template_result["template"]

        # Create enhanced research configuration
        research_config = {
            "query": research_query,
            "persona": template["default_persona"],
            "depth": template["default_depth"],
            "template_applied": template_id,
            "workflow_guidance": template["workflow_steps"],
            "suggested_tags": template.get("suggested_tags", []),
            "estimated_time": template.get("estimated_time"),
            "difficulty": template.get("difficulty"),
            "template_metadata": {
                "name": template["name"],
                "description": template["description"],
                "category": template["category"]
            }
        }

        return {
            "success": True,
            "research_config": research_config,
            "template_info": template
        }

    async def create_custom_template(self, user_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a custom research template.

        Args:
            user_id: User creating the template
            template_data: Template configuration

        Returns:
            Creation result
        """
        try:
            # Validate template data
            validation = self._validate_template_data(template_data)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid template data: {', '.join(validation['errors'])}"
                }

            # Create template record
            custom_template = ResearchTemplate(
                name=template_data["name"],
                description=template_data.get("description", ""),
                category=template_data.get("category", "custom"),
                default_persona=template_data.get("default_persona", "default"),
                workflow_steps=json.dumps(template_data.get("workflow_steps", {})),
                created_by=user_id
            )

            # Add additional metadata
            metadata = {
                "suggested_tags": template_data.get("suggested_tags", []),
                "estimated_time": template_data.get("estimated_time"),
                "difficulty": template_data.get("difficulty"),
                "is_public": template_data.get("is_public", False)
            }

            # Store metadata in a separate field or extend workflow_steps
            custom_template.workflow_steps = json.dumps({
                **json.loads(custom_template.workflow_steps),
                "metadata": metadata
            })

            # TODO: Save to database
            # session.add(custom_template)
            # await session.commit()

            logger.info(f"Created custom template '{template_data['name']}' for user {user_id}")

            return {
                "success": True,
                "template_id": "custom_" + str(hash(template_data["name"]))[:8],  # Temporary ID
                "name": custom_template.name,
                "created_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to create custom template: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _validate_template_data(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate custom template data.

        Args:
            template_data: Template data to validate

        Returns:
            Validation result
        """
        errors = []

        # Required fields
        required_fields = ["name", "workflow_steps"]
        for field in required_fields:
            if field not in template_data or not template_data[field]:
                errors.append(f"Missing required field: {field}")

        # Name validation
        if "name" in template_data:
            name = template_data["name"].strip()
            if len(name) < 3 or len(name) > 100:
                errors.append("Name must be between 3 and 100 characters")

        # Persona validation
        if "default_persona" in template_data:
            valid_personas = ["default", "isaac", "technical", "creative"]
            if template_data["default_persona"] not in valid_personas:
                errors.append(f"Default persona must be one of: {', '.join(valid_personas)}")

        # Depth validation
        if "default_depth" in template_data:
            valid_depths = ["quick", "comprehensive", "exhaustive"]
            if template_data["default_depth"] not in valid_depths:
                errors.append(f"Default depth must be one of: {', '.join(valid_depths)}")

        # Workflow steps validation
        if "workflow_steps" in template_data:
            if not isinstance(template_data["workflow_steps"], dict):
                errors.append("Workflow steps must be a dictionary")

        # Difficulty validation
        if "difficulty" in template_data:
            valid_difficulties = ["beginner", "intermediate", "advanced", "expert"]
            if template_data["difficulty"] not in valid_difficulties:
                errors.append(f"Difficulty must be one of: {', '.join(valid_difficulties)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    async def get_template_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for research templates.

        Returns:
            Template usage statistics
        """
        # This would aggregate usage data from research sessions
        # For now, return mock data
        stats = {
            "total_usage": 0,
            "popular_templates": [
                {"template_id": "academic_research", "usage_count": 45, "avg_rating": 4.8},
                {"template_id": "technical_documentation", "usage_count": 38, "avg_rating": 4.6},
                {"template_id": "comparative_analysis", "usage_count": 32, "avg_rating": 4.4},
                {"template_id": "fact_checking", "usage_count": 67, "avg_rating": 4.2}
            ],
            "category_breakdown": {
                "academic": 45,
                "technical": 38,
                "analysis": 32,
                "verification": 67,
                "business": 28,
                "trends": 19,
                "ux": 15
            },
            "generated_at": datetime.utcnow().isoformat()
        }

        return stats

    def generate_research_plan_from_template(self, template_id: str, research_query: str) -> Dict[str, Any]:
        """
        Generate a detailed research plan from a template.

        Args:
            template_id: Template to use
            research_query: Research query

        Returns:
            Detailed research plan
        """
        if template_id not in self.built_in_templates:
            return {"error": f"Template '{template_id}' not found"}

        template = self.built_in_templates[template_id]

        # Generate research phases based on template
        workflow_steps = template["workflow_steps"]

        research_plan = {
            "query": research_query,
            "template": template_id,
            "phases": [],
            "estimated_timeline": template.get("estimated_time", "1 week"),
            "difficulty": template.get("difficulty", "intermediate"),
            "required_expertise": self._get_expertise_requirements(template),
            "success_criteria": self._get_success_criteria(template)
        }

        # Convert workflow steps to research phases
        phase_counter = 1
        for section_name, steps in workflow_steps.items():
            if isinstance(steps, list):
                for step in steps:
                    research_plan["phases"].append({
                        "phase_number": phase_counter,
                        "name": step,
                        "section": section_name,
                        "estimated_time": self._estimate_phase_time(step, template),
                        "deliverables": self._get_phase_deliverables(step, template)
                    })
                    phase_counter += 1

        return research_plan

    def _get_expertise_requirements(self, template: Dict[str, Any]) -> List[str]:
        """Get expertise requirements for a template."""
        difficulty = template.get("difficulty", "intermediate")

        requirements = {
            "beginner": ["Basic research skills", "Internet search proficiency"],
            "intermediate": ["Research methodology knowledge", "Data analysis skills", "Critical thinking"],
            "advanced": ["Domain expertise", "Advanced research methods", "Statistical analysis"],
            "expert": ["Academic research experience", "Publication background", "Peer review experience"]
        }

        return requirements.get(difficulty, requirements["intermediate"])

    def _get_success_criteria(self, template: Dict[str, Any]) -> List[str]:
        """Get success criteria for a template."""
        category = template.get("category", "general")

        criteria = {
            "academic": [
                "Comprehensive literature review completed",
                "Original contribution identified",
                "Methodology clearly defined",
                "Findings properly validated",
                "Conclusions well-supported"
            ],
            "technical": [
                "Documentation is complete and accurate",
                "Code examples functional",
                "Technical concepts clearly explained",
                "Best practices identified",
                "Troubleshooting guide comprehensive"
            ],
            "analysis": [
                "Comparison criteria well-defined",
                "All alternatives thoroughly evaluated",
                "Recommendations data-driven",
                "Risks and limitations identified",
                "Actionable insights provided"
            ],
            "verification": [
                "All claims verified against sources",
                "Source credibility assessed",
                "Context and limitations explained",
                "Clear verdict provided",
                "Evidence well-documented"
            ]
        }

        return criteria.get(category, [
            "Research objectives met",
            "Sources credible and relevant",
            "Analysis comprehensive",
            "Conclusions well-supported",
            "Deliverables meet requirements"
        ])

    def _estimate_phase_time(self, step: str, template: Dict[str, Any]) -> str:
        """Estimate time required for a research phase."""
        # Simple estimation based on keywords
        step_lower = step.lower()

        if any(word in step_lower for word in ["review", "analysis", "synthesis"]):
            return "2-4 hours"
        elif any(word in step_lower for word in ["research", "investigation", "collection"]):
            return "4-8 hours"
        elif any(word in step_lower for word in ["writing", "documentation", "reporting"]):
            return "3-6 hours"
        elif any(word in step_lower for word in ["validation", "verification", "testing"]):
            return "1-3 hours"
        else:
            return "1-2 hours"

    def _get_phase_deliverables(self, step: str, template: Dict[str, Any]) -> List[str]:
        """Get deliverables for a research phase."""
        step_lower = step.lower()

        if "literature" in step_lower and "review" in step_lower:
            return ["Annotated bibliography", "Literature summary", "Research gaps identified"]
        elif "methodology" in step_lower:
            return ["Research design document", "Data collection plan", "Analysis framework"]
        elif "data" in step_lower and "collection" in step_lower:
            return ["Raw data files", "Data collection log", "Quality assessment report"]
        elif "analysis" in step_lower:
            return ["Analysis results", "Data visualizations", "Statistical reports"]
        elif "synthesis" in step_lower:
            return ["Findings summary", "Integrated analysis", "Key insights document"]
        elif "validation" in step_lower:
            return ["Validation report", "Quality assurance checklist", "Error log"]
        elif "writing" in step_lower or "documentation" in step_lower:
            return ["Draft document", "Reference list", "Style guide compliance"]
        else:
            return ["Phase deliverables", "Progress documentation", "Quality checklist"]

    async def get_recommended_templates(self, research_query: str) -> List[Dict[str, Any]]:
        """
        Recommend templates based on research query analysis.

        Args:
            research_query: Research query to analyze

        Returns:
            Recommended templates with relevance scores
        """
        query_lower = research_query.lower()

        # Keyword-based template recommendations
        recommendations = []

        # Academic research indicators
        if any(word in query_lower for word in ["research", "study", "analysis", "literature", "methodology"]):
            recommendations.append({
                "template_id": "academic_research",
                "relevance_score": 0.9,
                "reason": "Query indicates academic research methodology"
            })

        # Technical documentation indicators
        if any(word in query_lower for word in ["api", "documentation", "implementation", "code", "technical"]):
            recommendations.append({
                "template_id": "technical_documentation",
                "relevance_score": 0.8,
                "reason": "Query focuses on technical implementation and documentation"
            })

        # Comparative analysis indicators
        if any(word in query_lower for word in ["compare", "versus", "vs", "better", "alternative"]):
            recommendations.append({
                "template_id": "comparative_analysis",
                "relevance_score": 0.8,
                "reason": "Query involves comparing multiple options"
            })

        # Fact checking indicators
        if any(word in query_lower for word in ["fact", "check", "verify", "true", "false", "claim"]):
            recommendations.append({
                "template_id": "fact_checking",
                "relevance_score": 0.7,
                "reason": "Query focuses on verification and fact checking"
            })

        # Industry analysis indicators
        if any(word in query_lower for word in ["industry", "market", "trend", "business", "company"]):
            recommendations.append({
                "template_id": "industry_analysis",
                "relevance_score": 0.7,
                "reason": "Query involves industry and market analysis"
            })

        # Default recommendations if no specific matches
        if not recommendations:
            recommendations = [
                {
                    "template_id": "fact_checking",
                    "relevance_score": 0.5,
                    "reason": "General research template suitable for most queries"
                },
                {
                    "template_id": "comparative_analysis",
                    "relevance_score": 0.4,
                    "reason": "Flexible analysis framework"
                }
            ]

        # Sort by relevance score
        recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)

        return recommendations[:3]  # Return top 3 recommendations
