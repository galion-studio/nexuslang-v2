"""
Business Analyst Agent - Specialized in Business Analysis and Requirements

This agent handles:
- Requirements gathering and analysis
- Business process modeling
- Stakeholder management
- Use case development
- Functional specification writing
- Business case development
- Gap analysis and solution assessment
"""

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent


class BusinessAnalystAgent(BaseAgent):
    """Specialized business analyst agent for requirements and analysis tasks."""

    def __init__(self, name: str = "business_analyst_agent", **kwargs):
        super().__init__(
            name=name,
            description="Specialized in business analysis, requirements engineering, and stakeholder management",
            capabilities=[
                "requirements_analysis", "stakeholder_management", "business_process_modeling",
                "use_case_development", "functional_specifications", "business_case_analysis",
                "gap_analysis", "solution_assessment", "change_management"
            ],
            personality={
                "expertise_level": "expert",
                "communication_style": "structured",
                "specialties": ["business_analysis", "requirements", "stakeholder_management"]
            },
            **kwargs
        )

        # Business analysis knowledge base
        self.requirements_frameworks = self._get_requirements_frameworks()
        self.business_analysis_techniques = self._get_business_analysis_techniques()
        self.stakeholder_management = self._get_stakeholder_management()
        self.business_case_templates = self._get_business_case_templates()

    def _get_requirements_frameworks(self) -> Dict[str, Any]:
        """Get requirements engineering frameworks and methodologies."""
        return {
            "babok": {
                "name": "Business Analysis Body of Knowledge (BABoK)",
                "areas": [
                    "Business Analysis Planning and Monitoring",
                    "Elicitation and Collaboration",
                    "Requirements Life Cycle Management",
                    "Strategy Analysis",
                    "Requirements Analysis and Design Definition",
                    "Solution Evaluation"
                ],
                "techniques": [
                    "Brainstorming", "Document Analysis", "Business Rules Analysis",
                    "Data Mining", "Decision Analysis", "Financial Analysis",
                    "Functional Decomposition", "Interface Analysis", "Metrics and KPIs",
                    "Non-Functional Requirements Analysis", "Organization Modeling",
                    "Prioritization", "Process Modeling", "Prototyping", "Requirements Traceability",
                    "Risk Analysis", "Root Cause Analysis", "Scope Modeling", "Sequence Diagrams",
                    "Stakeholder Analysis", "Surveys", "SWOT Analysis", "Use Cases and Scenarios",
                    "User Stories", "Vendor Assessment", "Workshops"
                ]
            },
            "agile_requirements": {
                "methodologies": [
                    {
                        "name": "User Stories",
                        "format": "As a [type of user], I want [some goal] so that [some reason]",
                        "benefits": ["Simple", "Conversational", "Testable"],
                        "considerations": ["INVEST criteria", "Acceptance criteria"]
                    },
                    {
                        "name": "Use Cases",
                        "structure": ["Actor", "Goal", "Preconditions", "Main Success Scenario", "Alternative Flows"],
                        "benefits": ["Comprehensive", "Structured", "Traceable"],
                        "considerations": ["Level of detail", "Maintainability"]
                    },
                    {
                        "name": "Job Stories",
                        "format": "When [situation], I want to [motivation], so I can [expected outcome]",
                        "benefits": ["Context-focused", "Motivation-driven", "User-centric"],
                        "considerations": ["Situation analysis", "Motivation understanding"]
                    }
                ]
            },
            "requirements_types": {
                "functional": [
                    "Business rules", "Data requirements", "External interface requirements",
                    "Functional requirements", "Reporting requirements"
                ],
                "non_functional": [
                    "Performance requirements", "Security requirements", "Usability requirements",
                    "Reliability requirements", "Scalability requirements", "Compatibility requirements"
                ],
                "transition": [
                    "Data migration requirements", "Training requirements",
                    "Organizational change requirements", "Operational requirements"
                ]
            }
        }

    def _get_business_analysis_techniques(self) -> Dict[str, Any]:
        """Get business analysis techniques and tools."""
        return {
            "elicitation_techniques": [
                {
                    "name": "Interviews",
                    "description": "One-on-one or small group discussions",
                    "best_for": ["Detailed information", "Complex topics"],
                    "considerations": ["Time intensive", "Interviewer skill dependent"]
                },
                {
                    "name": "Workshops",
                    "description": "Facilitated group sessions",
                    "best_for": ["Brainstorming", "Consensus building", "Cross-functional input"],
                    "considerations": ["Group dynamics", "Time management", "Facilitation skills"]
                },
                {
                    "name": "Surveys",
                    "description": "Structured questionnaires",
                    "best_for": ["Large audiences", "Quantitative data", "Geographically dispersed"],
                    "considerations": ["Response rates", "Question design", "Analysis complexity"]
                },
                {
                    "name": "Observation",
                    "description": "Watching users in their environment",
                    "best_for": ["Understanding actual behavior", "Identifying workarounds"],
                    "considerations": ["Observer effect", "Time intensive", "Access requirements"]
                },
                {
                    "name": "Document Analysis",
                    "description": "Reviewing existing documentation",
                    "best_for": ["Understanding current state", "Regulatory requirements"],
                    "considerations": ["Document availability", "Currency of information"]
                }
            ],
            "analysis_techniques": [
                {
                    "name": "SWOT Analysis",
                    "description": "Strengths, Weaknesses, Opportunities, Threats",
                    "best_for": ["Strategic planning", "Opportunity identification"],
                    "output": ["Actionable insights", "Risk mitigation strategies"]
                },
                {
                    "name": "Root Cause Analysis",
                    "description": "5 Whys, Fishbone diagrams",
                    "best_for": ["Problem solving", "Process improvement"],
                    "output": ["Root causes", "Corrective actions"]
                },
                {
                    "name": "Gap Analysis",
                    "description": "Current vs. desired state comparison",
                    "best_for": ["Requirements identification", "Solution scoping"],
                    "output": ["Requirements list", "Solution scope"]
                },
                {
                    "name": "Business Process Modeling",
                    "description": "As-is and to-be process mapping",
                    "best_for": ["Process optimization", "Requirements gathering"],
                    "output": ["Process maps", "Improvement opportunities"]
                }
            ]
        }

    def _get_stakeholder_management(self) -> Dict[str, Any]:
        """Get stakeholder management frameworks and techniques."""
        return {
            "stakeholder_analysis": {
                "identification": [
                    "Power/Interest Grid",
                    "Power/Influence Grid",
                    "Impact/Influence Grid",
                    "Stakeholder Mapping"
                ],
                "engagement_levels": [
                    {"level": "Unaware", "strategy": "Inform"},
                    {"level": "Resistant", "strategy": "Persuade"},
                    {"level": "Neutral", "strategy": "Consult"},
                    {"level": "Supportive", "strategy": "Involve"},
                    {"level": "Leading", "strategy": "Empower"}
                ]
            },
            "communication_planning": {
                "audiences": ["Executives", "Business Users", "IT Team", "Vendors"],
                "methods": ["Presentations", "Emails", "Workshops", "Status Reports"],
                "frequency": ["Weekly", "Bi-weekly", "Monthly", "As needed"],
                "artifacts": ["Requirements Document", "Business Case", "Status Reports", "User Acceptance Tests"]
            },
            "change_management": {
                "kotter_model": [
                    "Create urgency",
                    "Form powerful coalition",
                    "Create vision for change",
                    "Communicate vision",
                    "Remove obstacles",
                    "Create short-term wins",
                    "Build on change",
                    "Anchor change in culture"
                ],
                "adkar_model": [
                    "Awareness of need for change",
                    "Desire to participate",
                    "Knowledge of how to change",
                    "Ability to implement change",
                    "Reinforcement to sustain change"
                ]
            }
        }

    def _get_business_case_templates(self) -> Dict[str, Any]:
        """Get business case development templates."""
        return {
            "executive_summary": {
                "sections": [
                    "Business problem/opportunity",
                    "Proposed solution",
                    "Benefits and costs",
                    "Recommendation"
                ]
            },
            "financial_analysis": {
                "metrics": [
                    "Net Present Value (NPV)",
                    "Return on Investment (ROI)",
                    "Payback Period",
                    "Break-even Analysis",
                    "Total Cost of Ownership (TCO)"
                ],
                "cost_categories": [
                    "Development costs",
                    "Implementation costs",
                    "Operational costs",
                    "Maintenance costs",
                    "Training costs"
                ],
                "benefit_categories": [
                    "Cost savings",
                    "Revenue increases",
                    "Productivity improvements",
                    "Risk reductions",
                    "Strategic advantages"
                ]
            },
            "risk_assessment": {
                "risk_categories": [
                    "Technical risks",
                    "Business risks",
                    "Financial risks",
                    "Operational risks",
                    "Compliance risks"
                ],
                "mitigation_strategies": [
                    "Risk avoidance",
                    "Risk transfer",
                    "Risk mitigation",
                    "Risk acceptance"
                ]
            }
        }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute business analysis-related tasks."""
        task_type = task.get("type", "")
        operation = task.get("operation", "")

        if task_type == "requirements":
            return await self._handle_requirements_task(task)
        elif task_type == "stakeholder":
            return await self._handle_stakeholder_task(task)
        elif task_type == "business_case":
            return await self._handle_business_case_task(task)
        elif task_type == "process_analysis":
            return await self._handle_process_analysis_task(task)
        else:
            # Use general task execution for other business analysis tasks
            return await super().execute_task(task)

    async def _handle_requirements_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requirements-related tasks."""
        operation = task.get("operation", "")

        if operation == "gather_requirements":
            return await self._gather_requirements(task)
        elif operation == "analyze_requirements":
            return await self._analyze_requirements(task)
        elif operation == "write_specifications":
            return await self._write_specifications(task)
        elif operation == "validate_requirements":
            return await self._validate_requirements(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown requirements operation: {operation}"
            }

    async def _handle_stakeholder_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stakeholder-related tasks."""
        operation = task.get("operation", "")

        if operation == "identify_stakeholders":
            return await self._identify_stakeholders(task)
        elif operation == "analyze_stakeholders":
            return await self._analyze_stakeholders(task)
        elif operation == "develop_communication_plan":
            return await self._develop_communication_plan(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown stakeholder operation: {operation}"
            }

    async def _handle_business_case_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle business case-related tasks."""
        operation = task.get("operation", "")

        if operation == "develop_business_case":
            return await self._develop_business_case(task)
        elif operation == "financial_analysis":
            return await self._perform_financial_analysis(task)
        elif operation == "risk_assessment":
            return await self._assess_risks(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown business case operation: {operation}"
            }

    async def _handle_process_analysis_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle process analysis tasks."""
        operation = task.get("operation", "")

        if operation == "map_business_process":
            return await self._map_business_process(task)
        elif operation == "perform_gap_analysis":
            return await self._perform_gap_analysis(task)
        elif operation == "optimize_process":
            return await self._optimize_process(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown process analysis operation: {operation}"
            }

    async def _gather_requirements(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Gather requirements from stakeholders."""
        stakeholders = task.get("stakeholders", [])
        project_scope = task.get("project_scope", "")
        elicitation_methods = task.get("elicitation_methods", ["interviews", "workshops"])

        try:
            # Plan elicitation activities
            elicitation_plan = self._plan_elicitation_activities(stakeholders, elicitation_methods)

            # Prepare interview questions
            interview_questions = self._prepare_interview_questions(project_scope)

            # Create requirements template
            requirements_template = self._create_requirements_template()

            return {
                "status": "completed",
                "result": {
                    "elicitation_plan": elicitation_plan,
                    "interview_questions": interview_questions,
                    "requirements_template": requirements_template,
                    "timeline": self._estimate_elicitation_timeline(stakeholders, elicitation_methods),
                    "deliverables": [
                        "Requirements gathering plan",
                        "Interview guides",
                        "Workshop agendas",
                        "Initial requirements document"
                    ]
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Requirements gathering failed: {str(e)}"
            }

    def _plan_elicitation_activities(self, stakeholders: List[Dict[str, Any]], methods: List[str]) -> List[Dict[str, Any]]:
        """Plan requirements elicitation activities."""
        activities = []

        for stakeholder in stakeholders:
            stakeholder_name = stakeholder.get("name", "")
            role = stakeholder.get("role", "")
            priority = stakeholder.get("priority", "medium")

            for method in methods:
                if method == "interviews" and priority in ["high", "critical"]:
                    activities.append({
                        "stakeholder": stakeholder_name,
                        "method": "interview",
                        "duration": "60 minutes",
                        "preparation": ["Review background materials", "Prepare questions"],
                        "follow_up": ["Send meeting notes", "Schedule clarification calls"]
                    })
                elif method == "workshops":
                    activities.append({
                        "stakeholder": f"{stakeholder_name} and team",
                        "method": "workshop",
                        "duration": "120 minutes",
                        "preparation": ["Define objectives", "Prepare materials"],
                        "follow_up": ["Document decisions", "Assign action items"]
                    })

        return activities

    def _prepare_interview_questions(self, project_scope: str) -> Dict[str, Any]:
        """Prepare interview questions for requirements gathering."""
        return {
            "opening_questions": [
                "Can you describe your current role and responsibilities?",
                "What are your main challenges in your current work?",
                "What are your expectations for this project?"
            ],
            "functional_questions": [
                "What tasks do you perform regularly?",
                "What information do you need to do your job effectively?",
                "What are the steps in your key processes?",
                "What decisions do you make, and what information do you need?"
            ],
            "non_functional_questions": [
                "How quickly do processes need to happen?",
                "What volume of work do you handle?",
                "What are your availability requirements?",
                "What are your security and compliance needs?"
            ],
            "pain_points_questions": [
                "What frustrates you about your current processes?",
                "What workarounds do you currently use?",
                "What would make your job easier?",
                "What have you tried to solve these problems?"
            ],
            "future_vision_questions": [
                "Where do you see your role going in the future?",
                "What capabilities would help you be more effective?",
                "How do you measure success in your role?",
                "What trends are affecting your work?"
            ]
        }

    def _create_requirements_template(self) -> Dict[str, Any]:
        """Create a requirements document template."""
        return {
            "executive_summary": {
                "purpose": "",
                "scope": "",
                "assumptions": [],
                "constraints": []
            },
            "functional_requirements": {
                "business_rules": [],
                "data_requirements": [],
                "interface_requirements": [],
                "reporting_requirements": []
            },
            "non_functional_requirements": {
                "performance": [],
                "security": [],
                "usability": [],
                "reliability": [],
                "scalability": [],
                "compatibility": []
            },
            "business_rules": [],
            "data_model": {
                "entities": [],
                "relationships": [],
                "attributes": []
            },
            "use_cases": [],
            "user_stories": [],
            "acceptance_criteria": [],
            "traceability_matrix": []
        }

    def _estimate_elicitation_timeline(self, stakeholders: List[Dict[str, Any]], methods: List[str]) -> Dict[str, Any]:
        """Estimate timeline for requirements elicitation."""
        # Rough estimation: 2 weeks for small projects, 4-6 weeks for large projects
        stakeholder_count = len(stakeholders)
        method_count = len(methods)

        base_weeks = 2
        stakeholder_factor = stakeholder_count * 0.5
        method_factor = method_count * 0.5

        total_weeks = base_weeks + stakeholder_factor + method_factor

        return {
            "estimated_weeks": round(total_weeks, 1),
            "milestones": [
                {"week": 1, "activities": ["Planning and preparation", "Stakeholder identification"]},
                {"week": 2, "activities": ["Initial interviews", "Workshop planning"]},
                {"week": 3, "activities": ["Requirements workshops", "Document analysis"]},
                {"week": 4, "activities": ["Requirements validation", "Specification writing"]}
            ],
            "critical_path": ["Stakeholder analysis", "Requirements gathering", "Validation"]
        }

    async def _analyze_requirements(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze gathered requirements."""
        raw_requirements = task.get("raw_requirements", [])
        project_context = task.get("project_context", {})

        try:
            # Categorize requirements
            categorized_requirements = self._categorize_requirements(raw_requirements)

            # Identify dependencies
            dependencies = self._identify_dependencies(categorized_requirements)

            # Prioritize requirements
            prioritized_requirements = self._prioritize_requirements(categorized_requirements, project_context)

            # Identify gaps and conflicts
            gaps_and_conflicts = self._analyze_gaps_and_conflicts(categorized_requirements)

            return {
                "status": "completed",
                "result": {
                    "categorized_requirements": categorized_requirements,
                    "dependencies": dependencies,
                    "prioritized_requirements": prioritized_requirements,
                    "gaps_and_conflicts": gaps_and_conflicts,
                    "analysis_summary": self._generate_requirements_summary(categorized_requirements),
                    "recommendations": self._generate_requirements_recommendations(gaps_and_conflicts)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Requirements analysis failed: {str(e)}"
            }

    def _categorize_requirements(self, requirements: List[str]) -> Dict[str, List[str]]:
        """Categorize requirements by type."""
        categories = {
            "functional": [],
            "non_functional": [],
            "business_rules": [],
            "data": [],
            "interface": [],
            "reporting": []
        }

        functional_keywords = ["shall", "will", "must", "should", "can", "user can", "system shall"]
        non_functional_keywords = ["performance", "security", "usability", "reliability", "scalability"]
        data_keywords = ["data", "database", "store", "retrieve", "information"]
        interface_keywords = ["api", "interface", "integration", "external system"]

        for req in requirements:
            req_lower = req.lower()

            if any(keyword in req_lower for keyword in functional_keywords):
                categories["functional"].append(req)
            elif any(keyword in req_lower for keyword in non_functional_keywords):
                categories["non_functional"].append(req)
            elif any(keyword in req_lower for keyword in data_keywords):
                categories["data"].append(req)
            elif any(keyword in req_lower for keyword in interface_keywords):
                categories["interface"].append(req)
            elif "report" in req_lower or "dashboard" in req_lower:
                categories["reporting"].append(req)
            else:
                categories["business_rules"].append(req)

        return categories

    def _identify_dependencies(self, categorized_requirements: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Identify dependencies between requirements."""
        dependencies = []

        # Simple dependency identification based on keywords
        functional_reqs = categorized_requirements.get("functional", [])
        data_reqs = categorized_requirements.get("data", [])
        interface_reqs = categorized_requirements.get("interface", [])

        for i, req in enumerate(functional_reqs):
            if any(keyword in req.lower() for keyword in ["data", "store", "retrieve"]):
                for data_req in data_reqs:
                    dependencies.append({
                        "from": f"F{i+1}",
                        "to": f"D{data_reqs.index(data_req)+1}",
                        "type": "depends_on",
                        "description": f"Functional requirement depends on data requirement"
                    })

        return dependencies

    def _prioritize_requirements(self, categorized_requirements: Dict[str, List[str]], context: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Prioritize requirements based on business value and feasibility."""
        prioritized = {"must_have": [], "should_have": [], "could_have": [], "won't_have": []}

        all_requirements = []
        for category, reqs in categorized_requirements.items():
            for req in reqs:
                all_requirements.append({
                    "requirement": req,
                    "category": category,
                    "business_value": self._assess_business_value(req, context),
                    "feasibility": self._assess_feasibility(req),
                    "priority": self._calculate_priority(req, context)
                })

        # Sort by priority score
        sorted_reqs = sorted(all_requirements, key=lambda x: x["priority"], reverse=True)

        # Assign to MoSCoW categories
        for req in sorted_reqs:
            if req["priority"] >= 0.8:
                prioritized["must_have"].append(req)
            elif req["priority"] >= 0.6:
                prioritized["should_have"].append(req)
            elif req["priority"] >= 0.4:
                prioritized["could_have"].append(req)
            else:
                prioritized["won't_have"].append(req)

        return prioritized

    def _assess_business_value(self, requirement: str, context: Dict[str, Any]) -> float:
        """Assess business value of a requirement."""
        # Simple keyword-based assessment
        high_value_keywords = ["revenue", "customer", "sales", "efficiency", "productivity"]
        medium_value_keywords = ["reporting", "analytics", "automation", "integration"]

        req_lower = requirement.lower()
        if any(keyword in req_lower for keyword in high_value_keywords):
            return 0.9
        elif any(keyword in req_lower for keyword in medium_value_keywords):
            return 0.6
        else:
            return 0.4

    def _assess_feasibility(self, requirement: str) -> float:
        """Assess technical feasibility of a requirement."""
        # Simple assessment based on complexity keywords
        complex_keywords = ["real-time", "ai", "machine learning", "blockchain", "complex algorithm"]
        medium_keywords = ["integration", "api", "database", "reporting"]

        req_lower = requirement.lower()
        if any(keyword in req_lower for keyword in complex_keywords):
            return 0.3
        elif any(keyword in req_lower for keyword in medium_keywords):
            return 0.6
        else:
            return 0.8

    def _calculate_priority(self, requirement: str, context: Dict[str, Any]) -> float:
        """Calculate priority score for a requirement."""
        business_value = self._assess_business_value(requirement, context)
        feasibility = self._assess_feasibility(requirement)

        # Weighted average favoring business value
        return (business_value * 0.7) + (feasibility * 0.3)

    def _analyze_gaps_and_conflicts(self, categorized_requirements: Dict[str, List[str]]) -> Dict[str, Any]:
        """Analyze gaps and conflicts in requirements."""
        gaps = []
        conflicts = []

        # Check for common gaps
        functional_reqs = categorized_requirements.get("functional", [])
        non_functional_reqs = categorized_requirements.get("non_functional", [])

        if len(functional_reqs) == 0:
            gaps.append("No functional requirements identified")

        if len(non_functional_reqs) == 0:
            gaps.append("No non-functional requirements specified")

        # Check for conflicts (simplified)
        for req1 in functional_reqs:
            for req2 in functional_reqs:
                if req1 != req2 and self._requirements_conflict(req1, req2):
                    conflicts.append({
                        "requirement1": req1,
                        "requirement2": req2,
                        "conflict_type": "logical_conflict",
                        "resolution": "Clarify requirements with stakeholders"
                    })

        return {
            "gaps": gaps,
            "conflicts": conflicts,
            "gap_count": len(gaps),
            "conflict_count": len(conflicts)
        }

    def _requirements_conflict(self, req1: str, req2: str) -> bool:
        """Check if two requirements conflict (simplified)."""
        # Simple conflict detection - in reality, this would be more sophisticated
        contradictory_terms = [
            ("must", "must not"),
            ("shall", "shall not"),
            ("required", "not required")
        ]

        req1_lower = req1.lower()
        req2_lower = req2.lower()

        for term1, term2 in contradictory_terms:
            if (term1 in req1_lower and term2 in req2_lower) or \
               (term2 in req1_lower and term1 in req2_lower):
                return True

        return False

    def _generate_requirements_summary(self, categorized_requirements: Dict[str, List[str]]) -> Dict[str, Any]:
        """Generate a summary of requirements analysis."""
        total_requirements = sum(len(reqs) for reqs in categorized_requirements.values())

        return {
            "total_requirements": total_requirements,
            "categories": {cat: len(reqs) for cat, reqs in categorized_requirements.items()},
            "most_common_category": max(categorized_requirements.keys(),
                                      key=lambda k: len(categorized_requirements[k])),
            "complexity_assessment": "high" if total_requirements > 50 else "medium" if total_requirements > 20 else "low"
        }

    def _generate_requirements_recommendations(self, gaps_and_conflicts: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on gaps and conflicts."""
        recommendations = []

        if gaps_and_conflicts["gap_count"] > 0:
            recommendations.append("Address identified gaps through additional stakeholder interviews")

        if gaps_and_conflicts["conflict_count"] > 0:
            recommendations.append("Resolve requirement conflicts through stakeholder workshops")

        recommendations.extend([
            "Create detailed acceptance criteria for each requirement",
            "Establish requirements traceability matrix",
            "Conduct requirements validation sessions with stakeholders",
            "Consider prototyping high-risk requirements"
        ])

        return recommendations

    async def _identify_stakeholders(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Identify project stakeholders."""
        project_description = task.get("project_description", "")
        organization_context = task.get("organization_context", {})

        try:
            # Identify stakeholders using standard categories
            stakeholders = self._identify_stakeholder_categories(project_description, organization_context)

            # Assess stakeholder influence and interest
            assessed_stakeholders = self._assess_stakeholder_power(stakeholders)

            # Create stakeholder map
            stakeholder_map = self._create_stakeholder_map(assessed_stakeholders)

            return {
                "status": "completed",
                "result": {
                    "identified_stakeholders": assessed_stakeholders,
                    "stakeholder_map": stakeholder_map,
                    "total_stakeholders": len(assessed_stakeholders),
                    "key_stakeholders": [s for s in assessed_stakeholders if s.get("power", 0) >= 7],
                    "engagement_strategy": self._create_engagement_strategy(assessed_stakeholders)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Stakeholder identification failed: {str(e)}"
            }

    def _identify_stakeholder_categories(self, project_desc: str, org_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify stakeholders by category."""
        stakeholders = []

        # Standard stakeholder categories
        categories = {
            "executive_sponsor": {
                "role": "Executive Sponsor",
                "responsibility": "Project funding and strategic alignment",
                "interest_level": "high",
                "influence_level": "high"
            },
            "project_manager": {
                "role": "Project Manager",
                "responsibility": "Project execution and delivery",
                "interest_level": "high",
                "influence_level": "medium"
            },
            "business_users": {
                "role": "Business Users",
                "responsibility": "Day-to-day system usage",
                "interest_level": "high",
                "influence_level": "medium"
            },
            "it_team": {
                "role": "IT/Development Team",
                "responsibility": "System implementation and maintenance",
                "interest_level": "high",
                "influence_level": "medium"
            },
            "quality_assurance": {
                "role": "QA/Testing Team",
                "responsibility": "Quality assurance and testing",
                "interest_level": "medium",
                "influence_level": "low"
            },
            "operations": {
                "role": "Operations Team",
                "responsibility": "System deployment and monitoring",
                "interest_level": "medium",
                "influence_level": "medium"
            },
            "security": {
                "role": "Security Team",
                "responsibility": "Information security and compliance",
                "interest_level": "medium",
                "influence_level": "high"
            },
            "compliance": {
                "role": "Compliance Officer",
                "responsibility": "Regulatory compliance",
                "interest_level": "medium",
                "influence_level": "high"
            },
            "vendors": {
                "role": "External Vendors",
                "responsibility": "Third-party services and integrations",
                "interest_level": "low",
                "influence_level": "low"
            },
            "customers": {
                "role": "End Customers",
                "responsibility": "System beneficiaries",
                "interest_level": "medium",
                "influence_level": "low"
            }
        }

        # Add all categories as potential stakeholders
        for category, details in categories.items():
            stakeholders.append({
                "category": category,
                "role": details["role"],
                "responsibility": details["responsibility"],
                "interest_level": details["interest_level"],
                "influence_level": details["influence_level"],
                "identified": True,
                "specific_people": []
            })

        return stakeholders

    def _assess_stakeholder_power(self, stakeholders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess stakeholder power and interest levels."""
        assessed = []

        for stakeholder in stakeholders:
            # Convert qualitative levels to numerical scores
            interest_score = {"low": 3, "medium": 5, "high": 8}[stakeholder.get("interest_level", "medium")]
            influence_score = {"low": 3, "medium": 5, "high": 8}[stakeholder.get("influence_level", "medium")]

            # Calculate power score as combination of interest and influence
            power_score = (interest_score + influence_score) / 2

            assessed.append({
                **stakeholder,
                "interest_score": interest_score,
                "influence_score": influence_score,
                "power_score": power_score,
                "engagement_level": self._determine_engagement_level(interest_score, influence_score)
            })

        return assessed

    def _determine_engagement_level(self, interest: int, influence: int) -> str:
        """Determine appropriate engagement level based on power/interest matrix."""
        if interest >= 7 and influence >= 7:
            return "manage_closely"
        elif interest >= 7 and influence < 7:
            return "keep_satisfied"
        elif interest < 7 and influence >= 7:
            return "keep_informed"
        else:
            return "monitor_minimally"

    def _create_stakeholder_map(self, stakeholders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a stakeholder power/interest map."""
        stakeholder_map = {
            "manage_closely": [],
            "keep_satisfied": [],
            "keep_informed": [],
            "monitor_minimally": []
        }

        for stakeholder in stakeholders:
            engagement = stakeholder.get("engagement_level", "monitor_minimally")
            stakeholder_map[engagement].append({
                "role": stakeholder.get("role"),
                "power_score": stakeholder.get("power_score"),
                "interest_score": stakeholder.get("interest_score")
            })

        return stakeholder_map

    def _create_engagement_strategy(self, stakeholders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create stakeholder engagement strategy."""
        strategy = {}

        for stakeholder in stakeholders:
            engagement_level = stakeholder.get("engagement_level")
            role = stakeholder.get("role")

            if engagement_level == "manage_closely":
                strategy[role] = {
                    "communication_frequency": "weekly",
                    "communication_method": "face-to-face meetings",
                    "involvement_level": "active_participation",
                    "decision_rights": "approval_required"
                }
            elif engagement_level == "keep_satisfied":
                strategy[role] = {
                    "communication_frequency": "bi-weekly",
                    "communication_method": "email_updates",
                    "involvement_level": "regular_updates",
                    "decision_rights": "consultation"
                }
            elif engagement_level == "keep_informed":
                strategy[role] = {
                    "communication_frequency": "monthly",
                    "communication_method": "newsletter",
                    "involvement_level": "status_updates",
                    "decision_rights": "information_only"
                }
            else:  # monitor_minimally
                strategy[role] = {
                    "communication_frequency": "quarterly",
                    "communication_method": "annual_updates",
                    "involvement_level": "minimal",
                    "decision_rights": "information_only"
                }

        return strategy

    async def _develop_business_case(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Develop a business case for a project or initiative."""
        project_description = task.get("project_description", "")
        proposed_solution = task.get("proposed_solution", "")
        cost_estimates = task.get("cost_estimates", {})
        benefit_estimates = task.get("benefit_estimates", {})

        try:
            # Executive summary
            executive_summary = self._create_executive_summary(project_description, proposed_solution)

            # Financial analysis
            financial_analysis = self._perform_financial_analysis_internal(cost_estimates, benefit_estimates)

            # Risk assessment
            risk_assessment = self._assess_project_risks(project_description, proposed_solution)

            # Implementation plan
            implementation_plan = self._create_implementation_plan(project_description)

            # Recommendation
            recommendation = self._create_recommendation(financial_analysis, risk_assessment)

            return {
                "status": "completed",
                "result": {
                    "executive_summary": executive_summary,
                    "financial_analysis": financial_analysis,
                    "risk_assessment": risk_assessment,
                    "implementation_plan": implementation_plan,
                    "recommendation": recommendation,
                    "business_case_score": self._calculate_business_case_score(financial_analysis, risk_assessment)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Business case development failed: {str(e)}"
            }

    def _create_executive_summary(self, project_desc: str, solution: str) -> Dict[str, Any]:
        """Create executive summary for business case."""
        return {
            "problem_statement": f"The organization faces challenges with: {project_desc}",
            "proposed_solution": f"Implement {solution} to address these challenges",
            "expected_benefits": [
                "Improved operational efficiency",
                "Cost savings through automation",
                "Enhanced decision-making capabilities",
                "Competitive advantage"
            ],
            "investment_required": "To be determined through detailed analysis",
            "timeline": "12-18 months implementation",
            "success_criteria": [
                "ROI of 150% within 3 years",
                "User adoption rate of 80%",
                "Reduction in operational costs by 25%"
            ]
        }

    def _perform_financial_analysis_internal(self, costs: Dict[str, Any], benefits: Dict[str, Any]) -> Dict[str, Any]:
        """Perform financial analysis for business case."""
        # Mock financial calculations
        total_costs = sum(costs.values()) if costs else 500000
        total_benefits = sum(benefits.values()) if benefits else 750000

        npv = total_benefits - total_costs
        roi = (npv / total_costs) * 100 if total_costs > 0 else 0
        payback_period = 2.5  # years

        return {
            "total_costs": total_costs,
            "total_benefits": total_benefits,
            "net_present_value": npv,
            "return_on_investment": roi,
            "payback_period_years": payback_period,
            "break_even_point": total_costs / (total_benefits / 5) if total_benefits > 0 else 0,
            "cost_benefit_ratio": total_benefits / total_costs if total_costs > 0 else 0
        }

    def _assess_project_risks(self, project_desc: str, solution: str) -> Dict[str, Any]:
        """Assess project risks."""
        risks = [
            {
                "category": "technical",
                "description": "Technical implementation challenges",
                "probability": 0.3,
                "impact": 0.6,
                "mitigation": "Conduct technical feasibility study and prototype"
            },
            {
                "category": "business",
                "description": "Changes in business requirements",
                "probability": 0.4,
                "impact": 0.5,
                "mitigation": "Implement agile development with regular feedback"
            },
            {
                "category": "operational",
                "description": "Integration with existing systems",
                "probability": 0.5,
                "impact": 0.4,
                "mitigation": "Perform integration testing and have rollback plan"
            },
            {
                "category": "financial",
                "description": "Cost overruns",
                "probability": 0.3,
                "impact": 0.7,
                "mitigation": "Detailed cost estimation and change control process"
            }
        ]

        overall_risk_score = sum((r["probability"] * r["impact"]) for r in risks)

        return {
            "identified_risks": risks,
            "overall_risk_score": overall_risk_score,
            "risk_level": "high" if overall_risk_score > 0.5 else "medium" if overall_risk_score > 0.3 else "low",
            "mitigation_strategy": "Comprehensive risk management plan with regular monitoring"
        }

    def _create_implementation_plan(self, project_desc: str) -> Dict[str, Any]:
        """Create implementation plan."""
        return {
            "phases": [
                {
                    "name": "Planning and Analysis",
                    "duration": "4 weeks",
                    "deliverables": ["Project plan", "Requirements document", "Technical design"]
                },
                {
                    "name": "Development",
                    "duration": "12 weeks",
                    "deliverables": ["Working software", "Unit tests", "Documentation"]
                },
                {
                    "name": "Testing and Quality Assurance",
                    "duration": "4 weeks",
                    "deliverables": ["Test results", "Quality metrics", "User acceptance"]
                },
                {
                    "name": "Deployment and Training",
                    "duration": "4 weeks",
                    "deliverables": ["Deployed system", "User training", "Go-live support"]
                }
            ],
            "total_duration": "24 weeks",
            "critical_success_factors": [
                "Stakeholder engagement",
                "Technical expertise availability",
                "Change management",
                "Quality assurance"
            ],
            "resource_requirements": {
                "team_members": ["Project Manager", "Business Analyst", "Developers", "QA Testers"],
                "external_resources": ["Infrastructure", "Third-party services"],
                "budget": "TBD based on detailed estimates"
            }
        }

    def _create_recommendation(self, financial: Dict[str, Any], risk: Dict[str, Any]) -> Dict[str, Any]:
        """Create final recommendation."""
        roi = financial.get("return_on_investment", 0)
        risk_score = risk.get("overall_risk_score", 1)

        if roi > 100 and risk_score < 0.4:
            recommendation = "Strongly recommend proceeding"
            confidence = "high"
        elif roi > 50 and risk_score < 0.6:
            recommendation = "Recommend proceeding with mitigation"
            confidence = "medium"
        elif roi > 25:
            recommendation = "Proceed with caution"
            confidence = "low"
        else:
            recommendation = "Do not recommend proceeding"
            confidence = "low"

        return {
            "recommendation": recommendation,
            "confidence_level": confidence,
            "decision_criteria": [
                f"ROI of {roi:.1f}% meets organizational threshold",
                f"Risk score of {risk_score:.2f} is acceptable",
                "Strategic alignment with business objectives",
                "Technical feasibility confirmed"
            ],
            "next_steps": [
                "Present business case to executive committee",
                "Secure project funding and resources",
                "Initiate detailed project planning",
                "Begin stakeholder engagement"
            ]
        }

    def _calculate_business_case_score(self, financial: Dict[str, Any], risk: Dict[str, Any]) -> float:
        """Calculate overall business case score."""
        roi_score = min(financial.get("return_on_investment", 0) / 100, 1.0)
        risk_penalty = risk.get("overall_risk_score", 0)

        return max(0, roi_score - risk_penalty)
