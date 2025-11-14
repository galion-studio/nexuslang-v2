"""
User Acceptance Testing framework for Deep Search.
Manages beta testing, user feedback collection, and acceptance validation.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import random
from collections import defaultdict

from ...core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class UserFeedback:
    """Represents user feedback and ratings."""
    feedback_id: str
    user_id: str
    session_id: Optional[str] = None
    feature_name: str = ""
    rating: int = 0  # 1-5 scale
    feedback_text: str = ""
    feedback_type: str = "general"  # general, bug_report, feature_request, usability_issue
    user_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "new"  # new, reviewed, addressed, closed
    priority: str = "medium"  # low, medium, high, critical
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    resolution_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class BetaTestProgram:
    """Represents a beta testing program."""
    program_id: str
    name: str
    description: str
    version: str
    start_date: datetime
    end_date: Optional[datetime] = None
    target_users: int = 100
    enrolled_users: List[str] = field(default_factory=list)
    status: str = "planning"  # planning, active, paused, completed
    acceptance_criteria: List[str] = field(default_factory=list)
    test_scenarios: List[Dict[str, Any]] = field(default_factory=list)
    success_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserSession:
    """Represents a user testing session."""
    session_id: str
    user_id: str
    program_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration: float = 0.0
    actions_performed: List[Dict[str, Any]] = field(default_factory=list)
    features_tested: List[str] = field(default_factory=list)
    feedback_provided: bool = False
    completion_status: str = "in_progress"  # in_progress, completed, abandoned
    satisfaction_score: Optional[int] = None
    notes: str = ""


@dataclass
class AcceptanceTestResult:
    """Results of acceptance testing."""
    test_id: str
    program_id: str
    test_date: datetime
    tester_count: int = 0
    completion_rate: float = 0.0
    average_satisfaction: float = 0.0
    acceptance_criteria_met: Dict[str, bool] = field(default_factory=dict)
    overall_passed: bool = False
    recommendations: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    go_no_go_recommendation: str = "pending"  # go, no_go, conditional_go, pending


class UserAcceptanceTester:
    """
    Comprehensive User Acceptance Testing framework for Deep Search.

    Features:
    - Beta program management
    - User feedback collection and analysis
    - Session tracking and user journey analysis
    - Acceptance criteria validation
    - Go/no-go decision support
    - Automated survey distribution
    - Feature adoption tracking
    """

    def __init__(self):
        self.beta_programs = {}
        self.user_feedback = {}
        self.user_sessions = {}
        self.feedback_categories = {}
        self.acceptance_tests = {}

        # Initialize default survey templates
        self.survey_templates = self._initialize_survey_templates()

        # Initialize acceptance criteria templates
        self.acceptance_criteria_templates = self._initialize_acceptance_criteria()

    def _initialize_survey_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize survey templates for different testing phases."""
        return {
            "post_session_feedback": {
                "name": "Post-Session Feedback Survey",
                "description": "Collect feedback immediately after user testing sessions",
                "questions": [
                    {
                        "id": "overall_satisfaction",
                        "type": "rating",
                        "question": "How satisfied are you with your overall experience?",
                        "scale": "1-5",
                        "required": True
                    },
                    {
                        "id": "ease_of_use",
                        "type": "rating",
                        "question": "How easy was it to use the system?",
                        "scale": "1-5",
                        "required": True
                    },
                    {
                        "id": "feature_completeness",
                        "type": "rating",
                        "question": "Did the system provide all the features you expected?",
                        "scale": "1-5",
                        "required": True
                    },
                    {
                        "id": "performance_satisfaction",
                        "type": "rating",
                        "question": "How satisfied are you with the system performance?",
                        "scale": "1-5",
                        "required": True
                    },
                    {
                        "id": "recommendation_likelihood",
                        "type": "rating",
                        "question": "How likely are you to recommend this system to others?",
                        "scale": "1-10",
                        "required": True
                    },
                    {
                        "id": "open_feedback",
                        "type": "text",
                        "question": "Please provide any additional feedback or suggestions:",
                        "required": False
                    },
                    {
                        "id": "issues_encountered",
                        "type": "text",
                        "question": "Did you encounter any issues or problems? Please describe:",
                        "required": False
                    }
                ]
            },

            "feature_specific_feedback": {
                "name": "Feature-Specific Feedback Survey",
                "description": "Detailed feedback on specific features",
                "questions": [
                    {
                        "id": "feature_understanding",
                        "type": "rating",
                        "question": "How well did you understand this feature?",
                        "scale": "1-5",
                        "required": True
                    },
                    {
                        "id": "feature_usefulness",
                        "type": "rating",
                        "question": "How useful do you find this feature?",
                        "scale": "1-5",
                        "required": True
                    },
                    {
                        "id": "feature_ease_of_use",
                        "type": "rating",
                        "question": "How easy was this feature to use?",
                        "scale": "1-5",
                        "required": True
                    },
                    {
                        "id": "feature_improvements",
                        "type": "text",
                        "question": "What improvements would you suggest for this feature?",
                        "required": False
                    }
                ]
            },

            "usability_testing": {
                "name": "Usability Testing Survey",
                "description": "Comprehensive usability assessment",
                "questions": [
                    {
                        "id": "task_completion",
                        "type": "multiple_choice",
                        "question": "Were you able to complete the assigned tasks?",
                        "options": ["Yes, easily", "Yes, with some difficulty", "No, could not complete"],
                        "required": True
                    },
                    {
                        "id": "navigation_difficulty",
                        "type": "rating",
                        "question": "How difficult was it to navigate through the system?",
                        "scale": "1-5 (1=Very Easy, 5=Very Difficult)",
                        "required": True
                    },
                    {
                        "id": "interface_intuitiveness",
                        "type": "rating",
                        "question": "How intuitive did you find the user interface?",
                        "scale": "1-5 (1=Not Intuitive, 5=Very Intuitive)",
                        "required": True
                    },
                    {
                        "id": "error_messages",
                        "type": "text",
                        "question": "How clear and helpful were error messages when they appeared?",
                        "required": False
                    },
                    {
                        "id": "learning_curve",
                        "type": "rating",
                        "question": "How steep was the learning curve?",
                        "scale": "1-5 (1=Very Gentle, 5=Very Steep)",
                        "required": True
                    }
                ]
            }
        }

    def _initialize_acceptance_criteria(self) -> Dict[str, List[str]]:
        """Initialize acceptance criteria templates."""
        return {
            "minimum_viable_product": [
                "System must be accessible and functional for all target users",
                "Core research functionality must work without critical errors",
                "User interface must be responsive and usable",
                "Data must be properly saved and retrievable",
                "System must handle basic error scenarios gracefully"
            ],

            "feature_complete": [
                "All planned features must be implemented and functional",
                "Integration between components must work correctly",
                "Performance must meet established benchmarks",
                "Security requirements must be satisfied",
                "Documentation must be complete and accurate"
            ],

            "production_ready": [
                "System must pass all integration and load tests",
                "User acceptance rate must be above 80%",
                "Critical bugs must be resolved",
                "Monitoring and alerting must be operational",
                "Backup and recovery procedures must be tested",
                "User training materials must be available"
            ],

            "research_platform": [
                "Deep research functionality must work reliably",
                "Citation management must be accurate",
                "Multi-language support must function properly",
                "Collaborative features must work for multiple users",
                "Voice features must be functional and accurate"
            ]
        }

    async def create_beta_program(self, program_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new beta testing program.

        Args:
            program_data: Program configuration data

        Returns:
            Program creation result
        """
        try:
            program_id = f"beta_{int(datetime.utcnow().timestamp())}_{program_data['name'].replace(' ', '_').lower()}"

            program = BetaTestProgram(
                program_id=program_id,
                name=program_data["name"],
                description=program_data.get("description", ""),
                version=program_data.get("version", "1.0.0"),
                start_date=datetime.utcnow(),
                target_users=program_data.get("target_users", 100),
                acceptance_criteria=program_data.get("acceptance_criteria", []),
                test_scenarios=program_data.get("test_scenarios", []),
                success_metrics=program_data.get("success_metrics", {})
            )

            # Set acceptance criteria if template specified
            if "criteria_template" in program_data:
                template_name = program_data["criteria_template"]
                if template_name in self.acceptance_criteria_templates:
                    program.acceptance_criteria = self.acceptance_criteria_templates[template_name]

            self.beta_programs[program_id] = program

            logger.info(f"Created beta program: {program.name} (ID: {program_id})")

            return {
                "success": True,
                "program_id": program_id,
                "name": program.name,
                "status": program.status,
                "start_date": program.start_date.isoformat(),
                "acceptance_criteria_count": len(program.acceptance_criteria)
            }

        except Exception as e:
            logger.error(f"Beta program creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def start_beta_program(self, program_id: str) -> Dict[str, Any]:
        """
        Start a beta testing program.

        Args:
            program_id: Program ID to start

        Returns:
            Program start result
        """
        try:
            if program_id not in self.beta_programs:
                return {"success": False, "error": "Program not found"}

            program = self.beta_programs[program_id]

            if program.status != "planning":
                return {"success": False, "error": f"Program is already {program.status}"}

            program.status = "active"
            program.start_date = datetime.utcnow()

            logger.info(f"Started beta program: {program.name} (ID: {program_id})")

            return {
                "success": True,
                "program_id": program_id,
                "status": "active",
                "start_date": program.start_date.isoformat(),
                "target_users": program.target_users
            }

        except Exception as e:
            logger.error(f"Beta program start failed: {e}")
            return {"success": False, "error": str(e)}

    async def enroll_user_in_program(self, program_id: str, user_id: str, user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enroll a user in a beta testing program.

        Args:
            program_id: Program ID
            user_id: User ID to enroll
            user_profile: Optional user profile information

        Returns:
            Enrollment result
        """
        try:
            if program_id not in self.beta_programs:
                return {"success": False, "error": "Program not found"}

            program = self.beta_programs[program_id]

            if program.status != "active":
                return {"success": False, "error": f"Program is {program.status}, not accepting enrollments"}

            if user_id in program.enrolled_users:
                return {"success": False, "error": "User already enrolled in this program"}

            program.enrolled_users.append(user_id)

            # Create initial user session
            session_id = await self.start_user_session(user_id, program_id)

            logger.info(f"Enrolled user {user_id} in beta program: {program.name}")

            return {
                "success": True,
                "program_id": program_id,
                "user_id": user_id,
                "session_id": session_id,
                "enrollment_date": datetime.utcnow().isoformat(),
                "total_enrolled": len(program.enrolled_users)
            }

        except Exception as e:
            logger.error(f"User enrollment failed: {e}")
            return {"success": False, "error": str(e)}

    async def start_user_session(self, user_id: str, program_id: Optional[str] = None) -> str:
        """
        Start a user testing session.

        Args:
            user_id: User ID
            program_id: Optional program ID

        Returns:
            Session ID
        """
        session_id = f"session_{int(datetime.utcnow().timestamp())}_{user_id}"

        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            program_id=program_id
        )

        self.user_sessions[session_id] = session

        logger.info(f"Started user session: {session_id} for user {user_id}")

        return session_id

    async def record_user_action(self, session_id: str, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a user action during testing.

        Args:
            session_id: Session ID
            action_data: Action details

        Returns:
            Recording result
        """
        try:
            if session_id not in self.user_sessions:
                return {"success": False, "error": "Session not found"}

            session = self.user_sessions[session_id]

            action_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "action_type": action_data.get("action_type", "unknown"),
                "feature": action_data.get("feature", ""),
                "details": action_data.get("details", {}),
                "duration": action_data.get("duration", 0.0),
                "success": action_data.get("success", True)
            }

            session.actions_performed.append(action_record)

            # Track features tested
            if action_data.get("feature"):
                feature = action_data["feature"]
                if feature not in session.features_tested:
                    session.features_tested.append(feature)

            return {
                "success": True,
                "session_id": session_id,
                "action_recorded": action_record["action_type"],
                "total_actions": len(session.actions_performed)
            }

        except Exception as e:
            logger.error(f"Action recording failed: {e}")
            return {"success": False, "error": str(e)}

    async def submit_user_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit user feedback.

        Args:
            feedback_data: Feedback details

        Returns:
            Submission result
        """
        try:
            feedback_id = f"feedback_{int(datetime.utcnow().timestamp())}_{feedback_data['user_id']}"

            feedback = UserFeedback(
                feedback_id=feedback_id,
                user_id=feedback_data["user_id"],
                session_id=feedback_data.get("session_id"),
                feature_name=feedback_data.get("feature_name", ""),
                rating=feedback_data.get("rating", 0),
                feedback_text=feedback_data.get("feedback_text", ""),
                feedback_type=feedback_data.get("feedback_type", "general"),
                user_context=feedback_data.get("user_context", {}),
                tags=feedback_data.get("tags", [])
            )

            self.user_feedback[feedback_id] = feedback

            # Update session if provided
            if feedback.session_id and feedback.session_id in self.user_sessions:
                session = self.user_sessions[feedback.session_id]
                session.feedback_provided = True
                if feedback.rating > 0:
                    session.satisfaction_score = feedback.rating

            # Categorize feedback
            self._categorize_feedback(feedback)

            logger.info(f"Submitted feedback: {feedback_id} from user {feedback.user_id}")

            return {
                "success": True,
                "feedback_id": feedback_id,
                "rating": feedback.rating,
                "type": feedback.feedback_type,
                "status": feedback.status
            }

        except Exception as e:
            logger.error(f"Feedback submission failed: {e}")
            return {"success": False, "error": str(e)}

    def _categorize_feedback(self, feedback: UserFeedback):
        """Categorize feedback for analysis."""
        category = feedback.feedback_type

        if category not in self.feedback_categories:
            self.feedback_categories[category] = {
                "count": 0,
                "total_rating": 0,
                "feedback_items": []
            }

        cat_data = self.feedback_categories[category]
        cat_data["count"] += 1
        cat_data["total_rating"] += feedback.rating

        # Keep recent feedback items (limit to 50 per category)
        cat_data["feedback_items"].append({
            "id": feedback.feedback_id,
            "rating": feedback.rating,
            "text": feedback.feedback_text[:200],  # Truncate
            "timestamp": feedback.timestamp.isoformat()
        })

        if len(cat_data["feedback_items"]) > 50:
            cat_data["feedback_items"] = cat_data["feedback_items"][-50:]

    async def end_user_session(self, session_id: str, completion_status: str = "completed",
                             final_notes: str = "") -> Dict[str, Any]:
        """
        End a user testing session.

        Args:
            session_id: Session ID
            completion_status: Completion status
            final_notes: Final session notes

        Returns:
            Session end result
        """
        try:
            if session_id not in self.user_sessions:
                return {"success": False, "error": "Session not found"}

            session = self.user_sessions[session_id]
            session.end_time = datetime.utcnow()
            session.duration = (session.end_time - session.start_time).total_seconds()
            session.completion_status = completion_status
            session.notes = final_notes

            logger.info(f"Ended user session: {session_id} - {completion_status}")

            return {
                "success": True,
                "session_id": session_id,
                "duration": session.duration,
                "completion_status": completion_status,
                "actions_performed": len(session.actions_performed),
                "features_tested": len(session.features_tested)
            }

        except Exception as e:
            logger.error(f"Session end failed: {e}")
            return {"success": False, "error": str(e)}

    async def run_acceptance_test(self, program_id: str) -> Dict[str, Any]:
        """
        Run acceptance testing for a beta program.

        Args:
            program_id: Program ID

        Returns:
            Acceptance test results
        """
        try:
            if program_id not in self.beta_programs:
                return {"success": False, "error": "Program not found"}

            program = self.beta_programs[program_id]

            if program.status != "active":
                return {"success": False, "error": f"Program is {program.status}"}

            # Analyze user sessions and feedback
            test_result = await self._analyze_acceptance_criteria(program)

            # Store test result
            test_id = f"acceptance_test_{int(datetime.utcnow().timestamp())}_{program_id}"
            self.acceptance_tests[test_id] = test_result

            # Update program status based on results
            if test_result.overall_passed:
                program.status = "completed"
                program.end_date = datetime.utcnow()
            else:
                # Check if there are critical issues
                if test_result.critical_issues:
                    program.status = "paused"  # Pause for fixes
                else:
                    program.status = "completed"  # Allow conditional release

            logger.info(f"Acceptance test completed for program: {program.name}")

            return {
                "success": True,
                "test_id": test_id,
                "program_id": program_id,
                "overall_passed": test_result.overall_passed,
                "completion_rate": test_result.completion_rate,
                "average_satisfaction": test_result.average_satisfaction,
                "go_no_go_recommendation": test_result.go_no_go_recommendation,
                "critical_issues_count": len(test_result.critical_issues)
            }

        except Exception as e:
            logger.error(f"Acceptance test failed: {e}")
            return {"success": False, "error": str(e)}

    async def _analyze_acceptance_criteria(self, program: BetaTestProgram) -> AcceptanceTestResult:
        """Analyze acceptance criteria for a beta program."""
        result = AcceptanceTestResult(
            test_id=f"analysis_{int(datetime.utcnow().timestamp())}",
            program_id=program.program_id,
            test_date=datetime.utcnow()
        )

        # Get all sessions for this program
        program_sessions = [s for s in self.user_sessions.values() if s.program_id == program.program_id]

        if not program_sessions:
            result.critical_issues.append("No user sessions found for acceptance testing")
            result.go_no_go_recommendation = "no_go"
            return result

        result.tester_count = len(set(s.user_id for s in program_sessions))

        # Calculate completion rate
        completed_sessions = [s for s in program_sessions if s.completion_status == "completed"]
        result.completion_rate = len(completed_sessions) / len(program_sessions) if program_sessions else 0

        # Calculate average satisfaction
        satisfaction_scores = [s.satisfaction_score for s in program_sessions if s.satisfaction_score]
        if satisfaction_scores:
            result.average_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)

        # Evaluate acceptance criteria
        criteria_met = {}

        for criterion in program.acceptance_criteria:
            if "user acceptance rate" in criterion.lower():
                criteria_met[criterion] = result.completion_rate >= 0.8
            elif "satisfaction" in criterion.lower():
                criteria_met[criterion] = result.average_satisfaction >= 3.5 if result.average_satisfaction else False
            elif "functional" in criterion.lower():
                # Check for critical feedback
                critical_feedback = [f for f in self.user_feedback.values()
                                   if f.feedback_type == "bug_report" and f.priority == "critical"]
                criteria_met[criterion] = len(critical_feedback) == 0
            elif "performance" in criterion.lower():
                # This would integrate with performance monitoring
                criteria_met[criterion] = True  # Placeholder
            else:
                # Default: assume met unless critical issues found
                criteria_met[criterion] = len(result.critical_issues) == 0

        result.acceptance_criteria_met = criteria_met

        # Determine overall pass/fail
        result.overall_passed = all(criteria_met.values())

        # Generate recommendations
        result.recommendations = self._generate_acceptance_recommendations(result, program)

        # Determine go/no-go recommendation
        if result.overall_passed and result.completion_rate >= 0.8 and result.average_satisfaction >= 3.5:
            result.go_no_go_recommendation = "go"
        elif result.completion_rate >= 0.6 and result.average_satisfaction >= 3.0 and not result.critical_issues:
            result.go_no_go_recommendation = "conditional_go"
        else:
            result.go_no_go_recommendation = "no_go"

        return result

    def _generate_acceptance_recommendations(self, result: AcceptanceTestResult, program: BetaTestProgram) -> List[str]:
        """Generate recommendations based on acceptance test results."""
        recommendations = []

        if result.completion_rate < 0.7:
            recommendations.append("Improve user onboarding and task completion rates")

        if result.average_satisfaction < 3.5:
            recommendations.append("Address user satisfaction issues identified in feedback")

        if not result.overall_passed:
            failed_criteria = [k for k, v in result.acceptance_criteria_met.items() if not v]
            recommendations.append(f"Address failed acceptance criteria: {', '.join(failed_criteria[:3])}")

        if result.critical_issues:
            recommendations.append(f"Resolve {len(result.critical_issues)} critical issues before release")

        if result.tester_count < program.target_users * 0.5:
            recommendations.append("Consider extending beta testing to gather more user feedback")

        return recommendations

    def get_program_status(self, program_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a beta program."""
        if program_id not in self.beta_programs:
            return None

        program = self.beta_programs[program_id]

        return {
            "program_id": program.program_id,
            "name": program.name,
            "status": program.status,
            "version": program.version,
            "enrolled_users": len(program.enrolled_users),
            "target_users": program.target_users,
            "start_date": program.start_date.isoformat(),
            "acceptance_criteria_count": len(program.acceptance_criteria),
            "progress_percentage": (len(program.enrolled_users) / program.target_users) * 100
        }

    def get_feedback_summary(self, program_id: Optional[str] = None) -> Dict[str, Any]:
        """Get feedback summary for a program or all programs."""
        feedback_items = list(self.user_feedback.values())

        if program_id:
            # Filter feedback by program
            program_sessions = [s.session_id for s in self.user_sessions.values() if s.program_id == program_id]
            feedback_items = [f for f in feedback_items if f.session_id in program_sessions]

        if not feedback_items:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "categories": {},
                "recent_feedback": []
            }

        # Calculate statistics
        total_feedback = len(feedback_items)
        ratings = [f.rating for f in feedback_items if f.rating > 0]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0

        # Category breakdown
        categories = {}
        for category, data in self.feedback_categories.items():
            categories[category] = {
                "count": data["count"],
                "average_rating": data["total_rating"] / data["count"] if data["count"] > 0 else 0.0
            }

        # Recent feedback (last 10)
        recent_feedback = sorted(feedback_items, key=lambda x: x.timestamp, reverse=True)[:10]
        recent_feedback_data = [
            {
                "id": f.feedback_id,
                "rating": f.rating,
                "type": f.feedback_type,
                "text": f.feedback_text[:100],  # Truncate
                "timestamp": f.timestamp.isoformat()
            }
            for f in recent_feedback
        ]

        return {
            "total_feedback": total_feedback,
            "average_rating": round(average_rating, 2),
            "categories": categories,
            "recent_feedback": recent_feedback_data
        }

    def get_survey_templates(self) -> Dict[str, Any]:
        """Get available survey templates."""
        return {
            "templates": self.survey_templates,
            "total_templates": len(self.survey_templates),
            "categories": ["post_session", "feature_specific", "usability"]
        }

    def get_acceptance_criteria_templates(self) -> Dict[str, Any]:
        """Get acceptance criteria templates."""
        return {
            "templates": self.acceptance_criteria_templates,
            "total_templates": len(self.acceptance_criteria_templates),
            "categories": ["development_stage", "readiness_level", "feature_focus"]
        }

    def get_user_session_summary(self, program_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of user sessions."""
        sessions = list(self.user_sessions.values())

        if program_id:
            sessions = [s for s in sessions if s.program_id == program_id]

        if not sessions:
            return {
                "total_sessions": 0,
                "completed_sessions": 0,
                "average_duration": 0.0,
                "average_satisfaction": 0.0,
                "completion_rate": 0.0
            }

        completed_sessions = [s for s in sessions if s.completion_status == "completed"]
        satisfaction_scores = [s.satisfaction_score for s in sessions if s.satisfaction_score]

        return {
            "total_sessions": len(sessions),
            "completed_sessions": len(completed_sessions),
            "average_duration": sum(s.duration for s in sessions) / len(sessions),
            "average_satisfaction": sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0.0,
            "completion_rate": len(completed_sessions) / len(sessions) if sessions else 0.0
        }
