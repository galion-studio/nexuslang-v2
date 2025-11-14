"""
Customer Support Agent for Galion Platform v2.2
Provides voice-to-voice customer support with intent recognition and knowledge base integration.

"Your imagination is the end."
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .base_agent import BaseAgent, AgentResult, AgentContext, PersonalityTraits, AgentCapabilities

logger = logging.getLogger(__name__)

class CustomerSupportAgent(BaseAgent):
    """
    AI Customer Support Agent

    Specializes in:
    - Voice-to-voice customer interactions
    - Intent recognition and classification
    - Knowledge base integration
    - Ticket creation and management
    - Issue resolution workflows
    - Customer satisfaction tracking
    """

    def __init__(self):
        personality = PersonalityTraits(
            analytical=0.7,      # Analytical for problem diagnosis
            creative=0.6,        # Creative problem solving
            empathetic=0.95,     # Highly empathetic for customer support
            precision=0.8,       # Precise in understanding and solutions
            helpful=0.98,        # Exceptionally helpful and supportive
            humor=0.4,           # Light humor when appropriate
            directness=0.7,      # Direct but not blunt
            curiosity=0.8        # Curious about customer needs and experiences
        )

        capabilities = AgentCapabilities(
            can_execute_code=False,      # No code execution needed
            can_access_filesystem=False, # No direct file access
            can_make_api_calls=True,     # Can call support APIs
            can_generate_content=True,   # Generates responses and solutions
            can_analyze_data=False,      # Limited data analysis
            can_interact_with_users=True, # Direct user interaction
            can_schedule_tasks=True,     # Can schedule follow-ups
            can_monitor_systems=False,   # No system monitoring
            supported_languages=["en"],  # English primary
            expertise_domains=[
                "customer_support",
                "technical_support",
                "issue_resolution",
                "product_guidance",
                "account_management",
                "billing_support"
            ],
            tool_access=["knowledge_base", "ticket_system", "user_database"]
        )

        super().__init__(
            name="Customer Support",
            personality=personality,
            capabilities=capabilities,
            description="Empathetic customer support specialist providing voice-based assistance",
            version="2.0.0"
        )

        # Support knowledge base
        self.knowledge_base = {
            "account_issues": {
                "login_problems": "Check email/password, try password reset, clear browser cache",
                "account_locked": "Contact support for account unlock, verify identity",
                "billing_issues": "Check payment method, update billing info, contact billing team"
            },
            "technical_issues": {
                "voice_not_working": "Check microphone permissions, test audio settings, try different browser",
                "app_crashes": "Clear cache, update browser, check system requirements",
                "slow_performance": "Close other tabs, check internet connection, clear browser data"
            },
            "feature_questions": {
                "how_to_use_voice": "Click microphone button, grant permissions, speak clearly",
                "file_uploads": "Drag and drop files or click upload button",
                "sharing_projects": "Use share button, enter email addresses"
            }
        }

        # Common support phrases and responses
        self.support_responses = {
            "greeting": "Hello! I'm here to help you with any questions or issues you might have. How can I assist you today?",
            "empathy": "I understand this can be frustrating. Let me help you resolve this issue.",
            "escalation": "I'll need to escalate this to our technical team. They'll follow up with you shortly.",
            "follow_up": "Is there anything else I can help you with today?",
            "resolution": "Great! I'm glad I could help resolve your issue. Please don't hesitate to reach out if you need anything else."
        }

    async def execute(
        self,
        prompt: str,
        context: Optional[AgentContext] = None,
        **kwargs
    ) -> AgentResult:
        """
        Execute customer support request.

        Analyzes customer queries and provides appropriate support.
        """
        start_time = datetime.now()

        try:
            # Analyze the customer query
            query_analysis = await self.analyze_customer_query(prompt)

            # Route to appropriate support workflow
            if query_analysis["intent"] == "technical_issue":
                response = await self.handle_technical_issue(prompt, query_analysis, context)
            elif query_analysis["intent"] == "account_issue":
                response = await self.handle_account_issue(prompt, query_analysis, context)
            elif query_analysis["intent"] == "billing_issue":
                response = await self.handle_billing_issue(prompt, query_analysis, context)
            elif query_analysis["intent"] == "feature_question":
                response = await self.handle_feature_question(prompt, query_analysis, context)
            elif query_analysis["intent"] == "general_inquiry":
                response = await self.handle_general_inquiry(prompt, query_analysis, context)
            else:
                response = await self.handle_unknown_query(prompt, context)

            # Add support metadata
            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentResult(
                success=True,
                response=response,
                cost=0.02,  # Lower cost for support interactions
                execution_time=execution_time,
                metadata={
                    "intent": query_analysis["intent"],
                    "confidence": query_analysis["confidence"],
                    "urgency": query_analysis["urgency"],
                    "needs_escalation": query_analysis["needs_escalation"],
                    "suggested_actions": query_analysis["suggested_actions"]
                }
            )

        except Exception as e:
            logger.error(f"Customer support execution failed: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentResult(
                success=False,
                response="I apologize, but I'm experiencing technical difficulties. Please try again in a moment, or contact our human support team for immediate assistance.",
                cost=0.01,
                execution_time=execution_time,
                error=str(e)
            )

    async def analyze_customer_query(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze customer query to determine intent and support needs.
        """
        prompt_lower = prompt.lower()

        analysis = {
            "intent": "general_inquiry",
            "confidence": 0.7,
            "urgency": "normal",
            "needs_escalation": False,
            "suggested_actions": [],
            "sentiment": "neutral"
        }

        # Check for urgency indicators
        urgent_words = ["urgent", "emergency", "immediately", "asap", "broken", "can't access", "stuck"]
        if any(word in prompt_lower for word in urgent_words):
            analysis["urgency"] = "high"

        # Analyze intent
        if any(word in prompt_lower for word in ["login", "password", "account", "access", "sign in"]):
            analysis["intent"] = "account_issue"
            analysis["confidence"] = 0.9
            analysis["suggested_actions"] = ["check_credentials", "password_reset"]

        elif any(word in prompt_lower for word in ["billing", "payment", "charge", "invoice", "refund"]):
            analysis["intent"] = "billing_issue"
            analysis["confidence"] = 0.9
            analysis["suggested_actions"] = ["check_payment_method", "contact_billing"]

        elif any(word in prompt_lower for word in ["crash", "error", "not working", "bug", "slow", "freeze"]):
            analysis["intent"] = "technical_issue"
            analysis["confidence"] = 0.85
            analysis["suggested_actions"] = ["troubleshooting_steps", "check_requirements"]

        elif any(word in prompt_lower for word in ["how to", "how do", "feature", "function", "tutorial"]):
            analysis["intent"] = "feature_question"
            analysis["confidence"] = 0.8
            analysis["suggested_actions"] = ["provide_guidance", "suggest_resources"]

        # Check for frustration indicators
        frustration_words = ["frustrated", "angry", "upset", "disappointed", "terrible", "worst"]
        if any(word in prompt_lower for word in frustration_words):
            analysis["sentiment"] = "negative"
            analysis["needs_escalation"] = True

        return analysis

    async def handle_technical_issue(self, prompt: str, analysis: Dict[str, Any], context: Optional[AgentContext] = None) -> str:
        """Handle technical support issues"""
        response = "I understand you're experiencing a technical issue. Let me help you troubleshoot this.\n\n"

        # Provide specific troubleshooting based on issue type
        if "voice" in prompt.lower() or "microphone" in prompt.lower():
            response += "## Voice/Audio Troubleshooting:\n\n"
            response += "1. **Check Permissions**: Ensure the browser has microphone access\n"
            response += "2. **Test Audio**: Try the voice test in settings\n"
            response += "3. **Browser Check**: Use Chrome or Firefox for best results\n"
            response += "4. **Restart**: Refresh the page and try again\n\n"

        elif "slow" in prompt.lower() or "performance" in prompt.lower():
            response += "## Performance Issues:\n\n"
            response += "1. **Close Other Tabs**: Free up browser resources\n"
            response += "2. **Check Internet**: Ensure stable connection\n"
            response += "3. **Clear Cache**: Clear browser cache and cookies\n"
            response += "4. **Update Browser**: Use latest browser version\n\n"

        elif "crash" in prompt.lower() or "error" in prompt.lower():
            response += "## Application Crashes:\n\n"
            response += "1. **Refresh Page**: Try reloading the application\n"
            response += "2. **Clear Data**: Clear browser data for this site\n"
            response += "3. **Different Browser**: Try accessing from another browser\n"
            response += "4. **System Requirements**: Verify your system meets requirements\n\n"

        # Add escalation if needed
        if analysis["urgency"] == "high" or analysis["sentiment"] == "negative":
            response += "**If these steps don't resolve your issue, I'll escalate this to our technical team for immediate attention.**\n\n"

        response += "Would you like me to walk you through any of these steps, or do you have additional details about the issue?"

        return response

    async def handle_account_issue(self, prompt: str, analysis: Dict[str, Any], context: Optional[AgentContext] = None) -> str:
        """Handle account-related issues"""
        response = "I'll help you resolve this account issue. Let's work through this step by step.\n\n"

        if "login" in prompt.lower() or "password" in prompt.lower():
            response += "## Password/Login Issues:\n\n"
            response += "1. **Check Credentials**: Verify email and password are correct\n"
            response += "2. **Password Reset**: Use 'Forgot Password' link on login page\n"
            response += "3. **Browser Cache**: Clear browser cache and try again\n"
            response += "4. **Two-Factor Auth**: Check if 2FA code is required\n\n"

            if "locked" in prompt.lower():
                response += "**Account Lock**: If your account is locked, please contact support@galion.app for immediate unlock.\n\n"

        elif "access" in prompt.lower():
            response += "## Access Issues:\n\n"
            response += "1. **Verify Permissions**: Check if your account has necessary permissions\n"
            response += "2. **Session Timeout**: Try logging out and back in\n"
            response += "3. **Browser Issues**: Try incognito/private browsing mode\n\n"

        response += "Are you able to try these steps, or would you like me to guide you through the process?"

        return response

    async def handle_billing_issue(self, prompt: str, analysis: Dict[str, Any], context: Optional[AgentContext] = None) -> str:
        """Handle billing and payment issues"""
        response = "I'll help you with your billing inquiry. Our billing team handles all payment-related matters.\n\n"

        response += "## Billing Support:\n\n"
        response += "For immediate assistance with:\n"
        response += "• Payment processing issues\n"
        response += "• Subscription changes\n"
        response += "• Refunds or credits\n"
        response += "• Invoice questions\n\n"

        response += "**Please contact our billing team at billing@galion.app or call 1-800-GALION-1**\n\n"

        response += "They'll be able to access your account details and resolve your billing question directly."

        return response

    async def handle_feature_question(self, prompt: str, analysis: Dict[str, Any], context: Optional[AgentContext] = None) -> str:
        """Handle questions about platform features"""
        response = "I'd be happy to help you understand how to use our platform features!\n\n"

        # Provide feature-specific guidance
        if "voice" in prompt.lower():
            response += "## Using Voice Features:\n\n"
            response += "1. **Enable Voice**: Click the microphone icon to start voice interaction\n"
            response += "2. **Grant Permissions**: Allow microphone access when prompted\n"
            response += "3. **Speak Clearly**: Use a quiet environment and speak naturally\n"
            response += "4. **Voice Commands**: Try saying 'Help' or 'Show me the dashboard'\n\n"

        elif "project" in prompt.lower() or "file" in prompt.lower():
            response += "## Managing Projects & Files:\n\n"
            response += "1. **Create Project**: Use the 'New Project' button\n"
            response += "2. **Upload Files**: Drag and drop or click the upload area\n"
            response += "3. **Share Projects**: Click 'Share' and enter email addresses\n"
            response += "4. **Version Control**: All changes are automatically saved\n\n"

        elif "ide" in prompt.lower() or "code" in prompt.lower():
            response += "## Using the IDE:\n\n"
            response += "1. **Open IDE**: Navigate to developer.Galion.app\n"
            response += "2. **Create Files**: Right-click in file explorer to create\n"
            response += "3. **AI Assistance**: Use the AI prompt bar for code generation\n"
            response += "4. **Run Code**: Use the terminal panel to execute code\n\n"

        response += "Would you like me to elaborate on any of these features or show you how to get started?"

        return response

    async def handle_general_inquiry(self, prompt: str, analysis: Dict[str, Any], context: Optional[AgentContext] = None) -> str:
        """Handle general customer inquiries"""
        response = "Thank you for reaching out! I'm here to help with any questions about Galion.\n\n"

        response += "## How Can I Help?\n\n"
        response += "I can assist you with:\n\n"
        response += "• **Getting Started**: Platform tutorials and onboarding\n"
        response += "• **Account Management**: Profile settings and preferences\n"
        response += "• **Technical Support**: Troubleshooting and bug reports\n"
        response += "• **Feature Guidance**: How to use platform capabilities\n"
        response += "• **Billing Questions**: Subscription and payment information\n"
        response += "• **Best Practices**: Tips for getting the most out of Galion\n\n"

        response += "Could you please tell me more specifically what you'd like help with today?"

        return response

    async def handle_unknown_query(self, prompt: str, context: Optional[AgentContext] = None) -> str:
        """Handle queries that don't fit standard categories"""
        response = "I want to make sure I understand your question correctly. Let me rephrase what I think you're asking...\n\n"

        response += f"**Your question**: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n\n"

        response += "Could you please clarify or provide more details so I can give you the most helpful response possible?"

        return response

