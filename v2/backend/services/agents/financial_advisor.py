"""
Financial Advisor Agent for Galion Platform v2.2
Provides financial analysis, investment advice, and budget planning with personality-driven responses.

"Your imagination is the end."
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .base_agent import BaseAgent, AgentResult, AgentContext, PersonalityTraits, AgentCapabilities

logger = logging.getLogger(__name__)

class FinancialAdvisorAgent(BaseAgent):
    """
    AI Financial Advisor Agent

    Specializes in:
    - Financial analysis and planning
    - Investment advice and strategy
    - Budget optimization
    - Risk assessment
    - Market insights
    - Retirement planning
    """

    def __init__(self):
        personality = PersonalityTraits(
            analytical=0.95,    # Highly analytical for financial data
            creative=0.7,       # Creative problem solving for financial strategies
            empathetic=0.85,    # Empathetic to understand financial stress
            precision=0.9,      # Precise with numbers and calculations
            helpful=0.95,       # Exceptionally helpful with financial guidance
            humor=0.2,          # Serious topic, minimal humor
            directness=0.8,     # Direct about financial realities
            curiosity=0.75      # Curious about financial goals and situations
        )

        capabilities = AgentCapabilities(
            can_execute_code=False,      # Doesn't need code execution
            can_access_filesystem=False, # No file system access needed
            can_make_api_calls=True,     # Can call financial APIs
            can_generate_content=True,   # Generates financial reports and advice
            can_analyze_data=True,       # Analyzes financial data
            can_interact_with_users=True, # Direct user interaction
            can_schedule_tasks=False,    # No scheduling needed
            can_monitor_systems=False,   # No system monitoring
            supported_languages=["en"],  # English for now
            expertise_domains=[
                "personal finance",
                "investment planning",
                "budget analysis",
                "retirement planning",
                "risk assessment",
                "market analysis"
            ],
            tool_access=["financial_calculators", "market_data", "budget_tools"]
        )

        super().__init__(
            name="Financial Advisor",
            personality=personality,
            capabilities=capabilities,
            description="Expert financial advisor providing personalized investment and budget guidance",
            version="2.0.0"
        )

        # Financial knowledge base
        self.financial_concepts = {
            "emergency_fund": "3-6 months of expenses",
            "debt_to_income": "Should be under 36%",
            "investment_allocation": "60% stocks, 40% bonds (aggressive)",
            "retirement_savings": "15% of income for 401k",
            "credit_score_ranges": {"excellent": "750+", "good": "680-749", "fair": "580-679", "poor": "<580"}
        }

    async def execute(
        self,
        prompt: str,
        context: Optional[AgentContext] = None,
        **kwargs
    ) -> AgentResult:
        """
        Execute financial advice request.

        Analyzes financial queries and provides personalized guidance.
        """
        start_time = datetime.now()

        try:
            # Analyze the financial query
            query_analysis = await self.analyze_financial_query(prompt)

            # Generate appropriate response based on query type
            if query_analysis["query_type"] == "budget_analysis":
                response = await self.analyze_budget(prompt, context)
            elif query_analysis["query_type"] == "investment_advice":
                response = await self.provide_investment_advice(prompt, context)
            elif query_analysis["query_type"] == "debt_management":
                response = await self.advise_on_debt(prompt, context)
            elif query_analysis["query_type"] == "retirement_planning":
                response = await self.plan_retirement(prompt, context)
            elif query_analysis["query_type"] == "general_financial_question":
                response = await self.answer_general_question(prompt, context)
            else:
                response = await self.provide_general_financial_guidance(prompt, context)

            # Add disclaimer
            response += "\n\n**Important Disclaimer:** This is not personalized financial advice. " \
                       "I am an AI assistant providing general educational information. " \
                       "Please consult with a qualified financial advisor or tax professional " \
                       "for advice specific to your situation."

            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentResult(
                success=True,
                response=response,
                cost=0.03,  # Cost per execution
                execution_time=execution_time,
                metadata={
                    "query_type": query_analysis["query_type"],
                    "confidence": query_analysis["confidence"],
                    "topics_covered": query_analysis["topics"]
                }
            )

        except Exception as e:
            logger.error(f"Financial advisor execution failed: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentResult(
                success=False,
                response="I apologize, but I encountered an error while analyzing your financial query. Please try rephrasing your question or consult a financial professional.",
                cost=0.01,
                execution_time=execution_time,
                error=str(e)
            )

    async def analyze_financial_query(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze the financial query to determine type and complexity.
        """
        prompt_lower = prompt.lower()

        analysis = {
            "query_type": "general_financial_question",
            "confidence": 0.8,
            "topics": [],
            "urgency": "normal",
            "requires_calculation": False
        }

        # Budget-related queries
        if any(word in prompt_lower for word in ["budget", "expenses", "income", "saving", "spending"]):
            analysis["query_type"] = "budget_analysis"
            analysis["topics"].append("budgeting")
            analysis["requires_calculation"] = True

        # Investment queries
        elif any(word in prompt_lower for word in ["invest", "stock", "bond", "portfolio", "market", "return"]):
            analysis["query_type"] = "investment_advice"
            analysis["topics"].append("investing")
            analysis["confidence"] = 0.9

        # Debt queries
        elif any(word in prompt_lower for word in ["debt", "loan", "credit", "mortgage", "payoff"]):
            analysis["query_type"] = "debt_management"
            analysis["topics"].append("debt_management")

        # Retirement queries
        elif any(word in prompt_lower for word in ["retirement", "401k", "ira", "pension", "retire"]):
            analysis["query_type"] = "retirement_planning"
            analysis["topics"].append("retirement")

        # Check for numbers (indicates calculations needed)
        if re.search(r'\d+', prompt):
            analysis["requires_calculation"] = True

        return analysis

    async def analyze_budget(self, prompt: str, context: Optional[AgentContext] = None) -> str:
        """Analyze budget and provide recommendations"""
        response = "## Budget Analysis & Recommendations\n\n"

        # Extract numbers from prompt
        numbers = re.findall(r'\d+\.?\d*', prompt)
        if numbers:
            response += f"I see you've mentioned some figures. Let me help you analyze your budget:\n\n"
            response += "### Key Budget Principles:\n"
            response += f"• **50/30/20 Rule**: 50% needs, 30% wants, 20% savings/debt payoff\n"
            response += f"• **Emergency Fund**: Aim for {self.financial_concepts['emergency_fund']}\n"
            response += f"• **Savings Rate**: Target 20% of income\n\n"
        else:
            response += "To provide specific budget advice, please share:\n"
            response += "• Monthly income\n• Major expenses\n• Current savings\n• Debt obligations\n\n"

        response += "### Budget Optimization Strategies:\n"
        response += "1. **Track Every Penny**: Use budgeting apps to monitor spending\n"
        response += "2. **Cut Unnecessary Expenses**: Review subscriptions and discretionary spending\n"
        response += "3. **Increase Income**: Consider side hustles or career advancement\n"
        response += "4. **Automate Savings**: Set up automatic transfers to savings accounts\n"
        response += "5. **Pay Yourself First**: Prioritize savings before other expenses\n\n"

        return response

    async def provide_investment_advice(self, prompt: str, context: Optional[AgentContext] = None) -> str:
        """Provide investment recommendations"""
        response = "## Investment Strategy Recommendations\n\n"

        response += "### Risk-Return Spectrum:\n"
        response += "• **Conservative**: Bonds, CDs, money market (lower risk, lower returns)\n"
        response += "• **Moderate**: Balanced portfolio (60% stocks, 40% bonds)\n"
        response += "• **Aggressive**: Mostly stocks, some alternatives (higher risk, higher potential returns)\n\n"

        response += "### Core Investment Principles:\n"
        response += "1. **Diversification**: Don't put all eggs in one basket\n"
        response += "2. **Long-term Focus**: Markets go up over time\n"
        response += "3. **Dollar-cost Averaging**: Invest regularly regardless of price\n"
        response += "4. **Tax Efficiency**: Use tax-advantaged accounts\n"
        response += "5. **Rebalancing**: Maintain target allocations\n\n"

        response += "### Recommended Asset Allocation:\n"
        response += f"**{self.financial_concepts['investment_allocation']}**\n\n"

        response += "### Getting Started:\n"
        response += "• Open a brokerage account (Fidelity, Vanguard, Charles Schwab)\n"
        response += "• Set up automatic monthly investments\n"
        response += "• Consider low-cost index funds or ETFs\n"
        response += "• Start small and increase over time\n\n"

        return response

    async def advise_on_debt(self, prompt: str, context: Optional[AgentContext] = None) -> str:
        """Provide debt management advice"""
        response = "## Debt Management Strategy\n\n"

        response += "### Debt Payoff Methods:\n"
        response += "• **Debt Snowball**: Pay minimums, focus on smallest balance first\n"
        response += "• **Debt Avalanche**: Pay minimums, focus on highest interest rate first\n"
        response += "• **Debt Consolidation**: Combine debts for lower interest\n\n"

        response += f"### Healthy Debt Ratios:\n"
        response += f"• **Debt-to-Income**: {self.financial_concepts['debt_to_income']}\n"
        response += f"• **Credit Utilization**: Keep under 30%\n\n"

        response += "### Debt Priority Order:\n"
        response += "1. **High-interest credit card debt** (>15% APR)\n"
        response += "2. **Personal loans and payday loans**\n"
        response += "3. **Low-interest student loans**\n"
        response += "4. **Mortgage and auto loans** (usually lowest interest)\n\n"

        response += "### Action Steps:\n"
        response += "• Create a debt payoff plan\n"
        response += "• Cut unnecessary spending to free up cash\n"
        response += "• Consider balance transfers for lower rates\n"
        response += "• Build emergency fund to avoid more debt\n\n"

        return response

    async def plan_retirement(self, prompt: str, context: Optional[AgentContext] = None) -> str:
        """Provide retirement planning guidance"""
        response = "## Retirement Planning Guide\n\n"

        response += f"### Savings Target:\n"
        response += f"• **401k/IRAs**: {self.financial_concepts['retirement_savings']} of income\n"
        response += f"• **Employer Match**: Maximize free money\n"
        response += f"• **Total Goal**: 25x annual expenses by retirement\n\n"

        response += "### Account Types:\n"
        response += "• **401k**: Employer-sponsored, tax-deferred\n"
        response += "• **Traditional IRA**: Tax-deductible contributions\n"
        response += "• **Roth IRA**: Tax-free withdrawals in retirement\n"
        response += "• **SEP IRA**: For self-employed\n\n"

        response += "### Investment Strategy:\n"
        response += "• **Early Career**: Aggressive allocation (90% stocks)\n"
        response += "• **Mid Career**: Moderate allocation (70% stocks)\n"
        response += "• **Late Career**: Conservative allocation (50% stocks)\n\n"

        response += "### Key Considerations:\n"
        response += "• Start early (compounding is powerful)\n"
        response += "• Increase contributions annually\n"
        response += "• Plan for healthcare costs\n"
        response += "• Consider Social Security timing\n\n"

        return response

    async def answer_general_question(self, prompt: str, context: Optional[AgentContext] = None) -> str:
        """Answer general financial questions"""
        # This would integrate with actual financial knowledge base
        # For now, provide structured general advice

        response = "## Financial Guidance\n\n"

        response += "Based on your question, here are some key principles:\n\n"

        response += "### General Financial Rules:\n"
        response += "• **Live below your means**\n"
        response += "• **Save before spending**\n"
        response += "• **Invest for the long term**\n"
        response += "• **Diversify your investments**\n"
        response += "• **Educate yourself continuously**\n\n"

        response += "### Recommended Resources:\n"
        response += "• Books: 'The Intelligent Investor', 'Your Money or Your Life'\n"
        response += "• Websites: NerdWallet, Investopedia, Morningstar\n"
        response += "• Apps: Mint, YNAB, Personal Capital\n\n"

        return response

    async def provide_general_financial_guidance(self, prompt: str, context: Optional[AgentContext] = None) -> str:
        """Provide general financial guidance when query type is unclear"""
        response = "## Comprehensive Financial Planning\n\n"

        response += "### The Financial Planning Pyramid:\n\n"
        response += "1. **Emergency Fund** - 3-6 months of expenses\n"
        response += "2. **Debt Elimination** - Pay off high-interest debt\n"
        response += "3. **Retirement Savings** - Max out tax-advantaged accounts\n"
        response += "4. **Insurance Coverage** - Protect against major risks\n"
        response += "5. **Investment Growth** - Build wealth through markets\n"
        response += "6. **Tax Optimization** - Minimize tax burden legally\n"
        response += "7. **Estate Planning** - Protect your legacy\n\n"

        response += "### Immediate Action Items:\n"
        response += "• Assess your current financial situation\n"
        response += "• Create a budget and track spending\n"
        response += "• Build an emergency fund\n"
        response += "• Start retirement savings\n"
        response += "• Review insurance coverage\n\n"

        response += "Would you like me to dive deeper into any of these areas?"

        return response

