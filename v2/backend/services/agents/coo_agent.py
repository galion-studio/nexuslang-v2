"""
COO Agent - Chief Operating Officer for Galion Company
Operational excellence, team management, and company scaling.
"""

from .base_agent import BaseAgent, PersonalityTraits, AgentResult, AgentCapabilities
import logging
import json
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class COOAgent(BaseAgent):
    """
    COO Agent - Operations leadership and organizational management for Galion Company

    Responsibilities:
    - Operational efficiency and process optimization
    - Team management and organizational scaling
    - Cross-functional coordination
    - Performance management and KPIs
    - Operational risk management
    """

    def __init__(self):
        super().__init__(
            name="COO",
            personality=PersonalityTraits(
                analytical=0.85,
                creative=0.6,
                empathetic=0.8,
                precision=0.9,
                helpful=0.9
            ),
            capabilities=AgentCapabilities(
                can_execute_code=False,
                can_access_filesystem=False,
                can_make_api_calls=True,
                can_generate_content=True,
                can_analyze_data=True,
                can_interact_with_users=True,
                can_schedule_tasks=True,
                can_monitor_systems=True,
                supported_languages=["en"],
                expertise_domains=[
                    "operations management",
                    "team leadership",
                    "process optimization",
                    "organizational scaling",
                    "performance management"
                ],
                tool_access=["hr_systems", "performance_analytics", "process_management", "team_collaboration"]
            )
        )

        self.operational_domains = {
            "engineering": {
                "team_size": 25,
                "processes": ["Agile development", "Code reviews", "CI/CD", "Testing"],
                "metrics": ["Velocity", "Code coverage", "Deployment frequency", "MTTR"]
            },
            "product": {
                "team_size": 8,
                "processes": ["Roadmap planning", "Sprint planning", "User research", "A/B testing"],
                "metrics": ["Feature delivery", "User satisfaction", "Conversion rates", "Retention"]
            },
            "customer_success": {
                "team_size": 6,
                "processes": ["Onboarding", "Support ticketing", "Account management", "Expansion"],
                "metrics": ["Response time", "Resolution rate", "NPS", "Expansion revenue"]
            },
            "operations": {
                "team_size": 4,
                "processes": ["Finance", "Legal", "HR", "Facilities"],
                "metrics": ["Process efficiency", "Compliance", "Employee satisfaction", "Cost control"]
            }
        }

        self.scaling_priorities = [
            "Process documentation and standardization",
            "Team expansion and hiring optimization",
            "Cross-functional communication improvement",
            "Performance measurement and analytics",
            "Operational risk mitigation"
        ]

    async def execute(self, prompt: str, context: Dict[str, Any]) -> AgentResult:
        """Execute COO-level operational analysis and decisions"""
        start_time = datetime.utcnow()

        try:
            # Analyze operational context
            operational_context = self._analyze_operational_context(prompt, context)

            # Generate operations leadership response
            response = await self._generate_operational_response(prompt, operational_context)

            execution_time = (datetime.utcnow() - start_time).total_seconds()
            cost = 0.038  # Operational decisions affect company efficiency

            return AgentResult(
                success=True,
                response=response,
                cost=cost,
                execution_time=execution_time
            )

        except Exception as e:
            logger.error(f"COO Agent error: {e}")
            return AgentResult(
                success=False,
                response=f"Operational analysis error: {str(e)}",
                cost=0.0,
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    def _analyze_operational_context(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze operational context for decision making"""
        operational_context = {
            "company_size": "~45 people",
            "growth_stage": "hyper_growth",
            "operational_maturity": "scaling_startup",
            "key_challenges": [
                "Team coordination across time zones",
                "Process documentation gaps",
                "Communication scaling",
                "Performance measurement complexity"
            ],
            "operational_strengths": [
                "Strong engineering culture",
                "Product-market fit achieved",
                "Technical talent density",
                "Cross-functional collaboration"
            ]
        }

        # Determine operational focus area
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['team', 'hire', 'culture']):
            operational_context["focus_area"] = "team_management"
        elif any(word in prompt_lower for word in ['process', 'efficiency', 'workflow']):
            operational_context["focus_area"] = "process_optimization"
        elif any(word in prompt_lower for word in ['scale', 'growth', 'expansion']):
            operational_context["focus_area"] = "organizational_scaling"
        elif any(word in prompt_lower for word in ['performance', 'kpi', 'metrics']):
            operational_context["focus_area"] = "performance_management"
        else:
            operational_context["focus_area"] = "operational_strategy"

        return operational_context

    async def _generate_operational_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate COO-level operational response"""

        base_response = f"""**Operations Leadership Analysis - COO Perspective**

**Operational Context:**
- Organization Size: {context['company_size']}
- Growth Stage: {context['growth_stage'].replace('_', ' ').title()}
- Focus Area: {context['focus_area'].replace('_', ' ').title()}

**Operational Assessment:**
"""

        # Add operational assessment based on focus area
        if context['focus_area'] == 'team_management':
            base_response += """
• **Current Team**: 45 people across engineering, product, operations, customer success
• **Growth Rate**: Adding 2-3 people monthly to support scaling
• **Culture Focus**: Innovation-driven, collaborative, results-oriented
• **Development**: Regular 1:1s, quarterly reviews, professional development budgets"""

        elif context['focus_area'] == 'process_optimization':
            base_response += """
• **Methodology**: Agile/Scrum across engineering and product teams
• **Tools**: Linear for project management, Slack for communication, Notion for docs
• **Bottlenecks**: Cross-team communication, documentation maintenance
• **Improvements**: Process automation, template standardization, regular retrospectives"""

        elif context['focus_area'] == 'organizational_scaling':
            base_response += """
• **Current Structure**: Functional organization with cross-functional projects
• **Scaling Needs**: Additional layer of management for 50+ person organization
• **Communication**: Daily standups, weekly all-hands, monthly town halls
• **Integration**: New hire onboarding program, knowledge sharing initiatives"""

        elif context['focus_area'] == 'performance_management':
            base_response += """
• **Key Metrics**: Revenue growth, user acquisition, product delivery velocity
• **Team KPIs**: Individual contributor goals aligned with company objectives
• **Feedback Loops**: Regular performance reviews, 360-degree feedback
• **Recognition**: Peer recognition program, milestone celebrations, equity grants"""

        else:
            base_response += """
• **Operational Health**: Strong processes with room for scaling optimization
• **Team Productivity**: High output with good work-life balance maintenance
• **Communication**: Effective cross-functional collaboration with improvement areas
• **Scalability**: Current processes support 2x growth with minor adjustments"""

        base_response += f"""

**Operational Strategy Recommendation for: *{prompt}*

**Immediate Operational Actions:**
1. **Process Audit**: Review current workflows against scaling requirements
2. **Team Assessment**: Evaluate capacity and identify hiring needs
3. **Communication Enhancement**: Implement improved cross-team coordination
4. **Performance Framework**: Establish clear KPIs and measurement systems

**Organizational Development Roadmap:**
- **Short-term (3 months)**: Process documentation, hiring pipeline setup
- **Medium-term (6-12 months)**: Management structure evolution, performance systems
- **Long-term (12-24 months)**: Enterprise-grade operations, global expansion readiness

**Scaling Framework:**
- **People**: Hire for skill and cultural fit, focus on T-shaped capabilities
- **Process**: Document everything, standardize workflows, automate repetitive tasks
- **Technology**: Invest in tools that scale with team size and complexity
- **Culture**: Maintain startup agility while building institutional knowledge

**Risk Mitigation:**
- Regular organizational health surveys
- Cross-training programs to prevent single points of failure
- Knowledge documentation and sharing initiatives
- Scalable communication frameworks (async-first approach)

**Operational Excellence Focus:**
Our current operational foundation is solid but requires evolution to support 2-3x growth. The key is maintaining our innovative culture while building the structure needed for scale. I recommend starting with process documentation and team expansion planning while implementing regular operational health check-ins.

*This analysis represents COO-level operational leadership for sustainable scaling.*"""

        return base_response

    async def get_operations_dashboard(self) -> Dict[str, Any]:
        """Get operations performance dashboard"""
        return {
            "organizational_health": {
                "team_size": 45,
                "departments": 4,
                "growth_rate": "15% quarterly",
                "employee_satisfaction": "8.2/10"
            },
            "operational_efficiency": {
                "process_maturity": "85%",
                "automation_level": "60%",
                "documentation_coverage": "75%",
                "cross_team_collaboration": "7.8/10"
            },
            "scaling_readiness": {
                "current_capacity": "80%",
                "recommended_hiring": "12 people Q2",
                "process_scalability": "good",
                "infrastructure_scalability": "excellent"
            },
            "key_processes": {
                "engineering": "Agile/Scrum methodology",
                "product": "Dual-track development",
                "customer_success": "HubSpot-based CRM",
                "operations": "Notion-based knowledge management"
            },
            "performance_metrics": {
                "sprint_velocity": "+15% improvement",
                "customer_response_time": "< 2 hours",
                "code_deployment_frequency": "daily",
                "documentation_updates": "weekly"
            }
        }
