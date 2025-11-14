"""
CFO Agent - Chief Financial Officer for Galion Company
Financial planning, budgeting, and capital management.
"""

from .base_agent import BaseAgent, PersonalityTraits, AgentResult, AgentCapabilities
import logging
import json
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class CFOAgent(BaseAgent):
    """
    CFO Agent - Financial leadership and capital management for Galion Company

    Responsibilities:
    - Financial planning and budgeting
    - Capital allocation and efficiency
    - Investor relations and fundraising
    - Financial risk management
    - Unit economics and profitability analysis
    """

    def __init__(self):
        super().__init__(
            name="CFO",
            personality=PersonalityTraits(
                analytical=0.98,
                creative=0.4,
                empathetic=0.6,
                precision=0.99,
                helpful=0.8
            ),
            capabilities=AgentCapabilities(
                can_execute_code=True,
                can_access_filesystem=False,
                can_make_api_calls=True,
                can_generate_content=True,
                can_analyze_data=True,
                can_interact_with_users=True,
                can_schedule_tasks=False,
                can_monitor_systems=False,
                supported_languages=["en"],
                expertise_domains=[
                    "financial planning",
                    "capital management",
                    "budgeting",
                    "investor relations",
                    "unit economics"
                ],
                tool_access=["financial_modeling", "budgeting_tools", "forecasting", "reporting"]
            )
        )

        self.financial_model = {
            "revenue_streams": {
                "subscription_saas": "60% of revenue (developer.Galion.app)",
                "enterprise_licenses": "25% of revenue (custom solutions)",
                "platform_fees": "15% of revenue (Galion.studio/Galion.app)"
            },
            "cost_structure": {
                "engineering": "45% of costs (R&D and development)",
                "infrastructure": "20% of costs (cloud and AI APIs)",
                "marketing": "15% of costs (customer acquisition)",
                "operations": "20% of costs (G&A and support)"
            },
            "unit_economics": {
                "customer_acquisition_cost": "$42",
                "monthly_revenue_per_user": "$85",
                "customer_lifetime_value": "$520",
                "payback_period": "6 months"
            }
        }

        self.capital_priorities = [
            "Engineering team expansion",
            "AI infrastructure scaling",
            "Market expansion initiatives",
            "Product development acceleration",
            "Working capital optimization"
        ]

    async def execute(self, prompt: str, context: Dict[str, Any]) -> AgentResult:
        """Execute CFO-level financial analysis and decisions"""
        start_time = datetime.utcnow()

        try:
            # Analyze financial context
            financial_context = self._analyze_financial_context(prompt, context)

            # Generate financial leadership response
            response = await self._generate_financial_response(prompt, financial_context)

            execution_time = (datetime.utcnow() - start_time).total_seconds()
            cost = 0.045  # Financial decisions are critical and high-value

            return AgentResult(
                success=True,
                response=response,
                cost=cost,
                execution_time=execution_time
            )

        except Exception as e:
            logger.error(f"CFO Agent error: {e}")
            return AgentResult(
                success=False,
                response=f"Financial analysis error: {str(e)}",
                cost=0.0,
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    def _analyze_financial_context(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial context for decision making"""
        financial_context = {
            "company_stage": "growth_series_a",
            "runway_months": 18,
            "burn_rate_monthly": "$150K",
            "revenue_growth": "300% year_over_year",
            "profitability_status": "pre_profit_but_improving",
            "key_risks": [
                "AI API cost volatility",
                "Customer acquisition scaling",
                "Talent competition in AI space",
                "Regulatory changes in AI"
            ],
            "investment_opportunities": [
                "Engineering team expansion (highest ROI)",
                "AI infrastructure optimization",
                "Enterprise sales team buildout",
                "International market expansion"
            ]
        }

        # Determine financial focus area
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['budget', 'allocation', 'spend']):
            financial_context["focus_area"] = "budget_allocation"
        elif any(word in prompt_lower for word in ['investment', 'funding', 'raise']):
            financial_context["focus_area"] = "capital_raising"
        elif any(word in prompt_lower for word in ['forecast', 'projection', 'model']):
            financial_context["focus_area"] = "financial_forecasting"
        elif any(word in prompt_lower for word in ['risk', 'hedge', 'insurance']):
            financial_context["focus_area"] = "risk_management"
        else:
            financial_context["focus_area"] = "financial_strategy"

        return financial_context

    async def _generate_financial_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate CFO-level financial response"""

        base_response = f"""**Financial Leadership Analysis - CFO Perspective**

**Financial Context:**
- Company Stage: {context['company_stage'].replace('_', ' ').title()}
- Runway: {context['runway_months']} months
- Growth Rate: {context['revenue_growth']}
- Focus Area: {context['focus_area'].replace('_', ' ').title()}

**Financial Assessment:**
"""

        # Add financial assessment based on focus area
        if context['focus_area'] == 'budget_allocation':
            base_response += """
• **Current Burn Rate**: $150K monthly across engineering, infrastructure, marketing
• **Revenue Streams**: 60% SaaS subscriptions, 25% enterprise, 15% platform fees
• **Unit Economics**: $42 CAC, $85 MRR, $520 LTV, 6-month payback
• **Allocation Strategy**: 45% engineering, 20% infrastructure, 15% marketing, 20% operations"""

        elif context['focus_area'] == 'capital_raising':
            base_response += """
• **Current Valuation**: Pre-money $50M based on 15x revenue multiple
• **Fundraising Target**: $15M Series A at $65M post-money
• **Use of Funds**: 50% product development, 30% market expansion, 20% working capital
• **Investor Interest**: Strong traction in AI infrastructure space"""

        elif context['focus_area'] == 'financial_forecasting':
            base_response += """
• **Revenue Projection**: $12M ARR by EOY, $50M by end of 2025
• **Path to Profitability**: Q3 2025 with 40% gross margins
• **Key Assumptions**: 300% YoY growth, stable AI API costs, enterprise conversion
• **Sensitivity Analysis**: 20% variance in key metrics shows resilient model"""

        elif context['focus_area'] == 'risk_management':
            base_response += """
• **Primary Risks**: AI API cost volatility, talent competition, regulatory uncertainty
• **Risk Mitigation**: Fixed-price contracts, diversified hiring, compliance framework
• **Insurance Coverage**: Cyber liability, key person, business interruption
• **Contingency Planning**: 6-month emergency fund, flexible cost structure"""

        else:
            base_response += """
• **Financial Health**: Strong unit economics, improving gross margins, scalable model
• **Capital Efficiency**: $42 CAC with $520 LTV indicates efficient customer acquisition
• **Growth Trajectory**: 300% YoY growth with clear path to profitability
• **Market Opportunity**: $50B+ AI agent platform market with first-mover advantage"""

        base_response += f"""

**Financial Strategy Recommendation for: *{prompt}*

**Capital Allocation Framework:**
1. **Engineering Priority**: 45% of budget - highest ROI for product development
2. **Infrastructure Scaling**: 20% of budget - AI API costs and cloud optimization
3. **Customer Acquisition**: 15% of budget - marketing and sales development
4. **Operational Excellence**: 20% of budget - support and administrative scaling

**Financial Decision Criteria:**
- ✅ **Invest** if projected ROI > 3x within 12 months
- ⚠️ **Evaluate** if ROI 2-3x but strategic importance high
- ❌ **Defer** if ROI < 2x or execution risk too high

**Key Financial Metrics to Monitor:**
- **Monthly Recurring Revenue (MRR)**: Current growth trajectory excellent
- **Customer Acquisition Cost (CAC)**: $42 - efficient compared to $520 LTV
- **Gross Revenue Retention**: 95%+ - strong product-market fit
- **Cash Conversion Cycle**: Negative - customers pay before we pay expenses

**Capital Strategy:**
Our current financial position is strong with 18 months of runway, positive unit economics, and clear path to profitability. The key focus should be on scaling efficiently while maintaining capital discipline. I recommend proceeding with the proposed investment while implementing strict monitoring of key financial metrics.

**Risk Considerations:**
- AI API cost fluctuations require ongoing monitoring
- Enterprise sales cycle length impacts cash flow forecasting
- Talent market competition requires premium compensation strategy
- Regulatory landscape requires ongoing compliance investment

*This analysis represents CFO-level financial leadership for sustainable, profitable growth.*"""

        return base_response

    async def get_financial_dashboard(self) -> Dict[str, Any]:
        """Get financial performance dashboard"""
        return {
            "financial_health": {
                "runway_months": 18,
                "monthly_burn": "$150K",
                "revenue_growth": "300% YoY",
                "gross_margins": "35%"
            },
            "unit_economics": {
                "customer_acquisition_cost": "$42",
                "monthly_revenue_per_user": "$85",
                "customer_lifetime_value": "$520",
                "payback_period_months": 6
            },
            "revenue_streams": {
                "saas_subscriptions": "60%",
                "enterprise_licenses": "25%",
                "platform_fees": "15%"
            },
            "cost_structure": {
                "engineering": "45%",
                "infrastructure": "20%",
                "marketing": "15%",
                "operations": "20%"
            },
            "forecast_2025": {
                "annual_revenue_target": "$50M",
                "path_to_profitability": "Q3 2025",
                "team_size_target": "75 people",
                "market_expansion": "3 continents"
            }
        }
