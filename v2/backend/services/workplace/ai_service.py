"""
AI Service
AI-powered workplace features and automation using OpenRouter.

Features:
- Task assignment optimization
- Time log analysis and categorization
- Project risk analysis
- Resource allocation optimization
- Predictive analytics
- Code review assistance
- Workflow optimization
"""

import logging
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class AIService:
    """AI-powered workplace automation and insights using OpenRouter"""

    def __init__(self):
        # Import the existing AI router
        try:
            from ..ai.ai_router import AIRouter, AIModel
            self.ai_router = AIRouter()
            self.ai_model = AIModel
            logger.info("✅ Workplace AI Service initialized with OpenRouter")
        except ImportError:
            logger.warning("⚠️  AI Router not available, using mock responses")
            self.ai_router = None

    async def analyze_time_log_description(self, description: str) -> Dict[str, Any]:
        """Analyze time log description for categorization using OpenRouter"""
        try:
            if not self.ai_router:
                # Fallback to simple keyword analysis
                return await self._fallback_time_analysis(description)

            # Use OpenRouter for intelligent analysis
            prompt = f"""
            Analyze this time log description and categorize the work:

            Description: "{description}"

            Please respond with a JSON object containing:
            - category: (development, meetings, design, testing, research, documentation, planning, etc.)
            - confidence: (0.0-1.0)
            - billable: (true/false)
            - tags: array of relevant tags
            - estimated_complexity: (simple, medium, complex)

            Be specific and accurate in your categorization.
            """

            messages = [
                {"role": "system", "content": "You are an expert at categorizing work activities for time tracking. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            response = await self.ai_router.chat_completion(
                messages=messages,
                model=self.ai_model.CLAUDE_SONNET,
                temperature=0.3,
                max_tokens=300
            )

            if response and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                # Try to parse JSON response
                try:
                    analysis = json.loads(content.strip())
                    return analysis
                except json.JSONDecodeError:
                    # Extract JSON from markdown code blocks if present
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group(1))
                        return analysis

            # If AI response parsing fails, use fallback
            return await self._fallback_time_analysis(description)

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return await self._fallback_time_analysis(description)

    async def _fallback_time_analysis(self, description: str) -> Dict[str, Any]:
        """Fallback keyword-based time log analysis"""
        analysis = {
            "category": "development",
            "confidence": 0.7,
            "suggested_task": None,
            "billable": True,
            "tags": ["coding"],
            "estimated_complexity": "medium"
        }

        desc_lower = description.lower()

        if any(word in desc_lower for word in ["meeting", "standup", "review", "retrospective", "grooming"]):
            analysis.update({
                "category": "meetings",
                "billable": False,
                "tags": ["meeting", "collaboration"],
                "confidence": 0.9
            })
        elif any(word in desc_lower for word in ["design", "ui", "ux", "mockup", "wireframe", "figma"]):
            analysis.update({
                "category": "design",
                "tags": ["design", "ui/ux"],
                "confidence": 0.85
            })
        elif any(word in desc_lower for word in ["testing", "qa", "debug", "fix", "bug"]):
            analysis.update({
                "category": "testing",
                "tags": ["testing", "qa"],
                "confidence": 0.85
            })
        elif any(word in desc_lower for word in ["research", "investigation", "analysis", "spike"]):
            analysis.update({
                "category": "research",
                "tags": ["research", "analysis"],
                "confidence": 0.8
            })
        elif any(word in desc_lower for word in ["documentation", "docs", "readme", "wiki"]):
            analysis.update({
                "category": "documentation",
                "billable": False,
                "tags": ["documentation"],
                "confidence": 0.9
            })
        elif any(word in desc_lower for word in ["planning", "roadmap", "strategy", "architecture"]):
            analysis.update({
                "category": "planning",
                "tags": ["planning", "strategy"],
                "confidence": 0.8
            })

        return analysis

    async def analyze_task_assignment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered task assignment analysis using OpenRouter"""
        try:
            if not self.ai_router:
                return await self._fallback_task_assignment(data)

            task = data["task"]
            team = data["team"]
            criteria = data.get("assignment_criteria", {})

            # Create a detailed prompt for AI analysis
            team_summary = "\n".join([
                f"- {member['name']} (ID: {member['user_id']}): Skills: {', '.join(member.get('skills', []))}, "
                f"Workload: {member.get('current_workload', 0)}/{member.get('workload_capacity', 40)}, "
                f"Performance: {member.get('performance_score', 5.0)}/10, "
                f"Availability: {member.get('availability', 'available')}"
                for member in team
            ])

            prompt = f"""
            Analyze this task and recommend the best team member for assignment:

            TASK DETAILS:
            - Title: {task.get('title', 'N/A')}
            - Description: {task.get('description', 'N/A')}
            - Priority: {task.get('priority', 'medium')}
            - Required Skills: {', '.join(task.get('required_skills', []))}
            - Complexity: {task.get('complexity', 'medium')}
            - Hours Estimate: {task.get('hours_estimate', 'N/A')}

            TEAM MEMBERS:
            {team_summary}

            ADDITIONAL CRITERIA:
            {json.dumps(criteria) if criteria else 'None specified'}

            Please respond with a JSON object containing:
            - recommended_assignee: {{user_id, name, score (0-100)}}
            - confidence: (0.0-1.0)
            - alternatives: array of top 3 alternatives with scores
            - reasoning: array of strings explaining the recommendation
            - assignment_factors: object with weights for different factors

            Consider skills match, current workload, performance history, and availability.
            """

            messages = [
                {"role": "system", "content": "You are an expert project manager skilled at task assignment optimization. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            response = await self.ai_router.chat_completion(
                messages=messages,
                model=self.ai_model.CLAUDE_SONNET,
                temperature=0.2,
                max_tokens=800
            )

            if response and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                try:
                    result = json.loads(content.strip())
                    return result
                except json.JSONDecodeError:
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group(1))
                        return result

            # If AI response parsing fails, use fallback
            return await self._fallback_task_assignment(data)

        except Exception as e:
            logger.error(f"Task assignment analysis failed: {e}")
            return await self._fallback_task_assignment(data)

    async def _fallback_task_assignment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback algorithm for task assignment"""
        try:
            task = data["task"]
            team = data["team"]

            scores = []
            for member in team:
                score = 0
                reasoning = []

                # Skill matching (30 points max)
                member_skills = set(member.get("skills", []))
                required_skills = set(task.get("required_skills", []))
                if required_skills:
                    skill_match = len(member_skills & required_skills) / len(required_skills)
                    score += skill_match * 30
                    reasoning.append(f"Skill match: {skill_match:.1%}")

                # Workload consideration (25 points max)
                current_workload = member.get("current_workload", 0)
                capacity = member.get("workload_capacity", 40)
                workload_ratio = current_workload / capacity if capacity > 0 else 0
                workload_score = max(0, 1 - workload_ratio) * 25
                score += workload_score
                reasoning.append(f"Workload capacity: {workload_score:.1f}/25")

                # Performance score (20 points max)
                perf_score = member.get("performance_score", 5.0) / 10 * 20
                score += perf_score
                reasoning.append(f"Performance: {perf_score:.1f}/20")

                # Availability bonus (15 points)
                if member.get("availability") == "available":
                    score += 15
                    reasoning.append("Available: +15")
                elif member.get("availability") == "busy":
                    score -= 10
                    reasoning.append("Busy: -10")

                # Priority consideration for urgent tasks
                if task.get("priority") == "urgent":
                    score += (member.get("performance_score", 5.0) - 5.0) * 2

                scores.append({
                    "user_id": member["user_id"],
                    "name": member["name"],
                    "score": score,
                    "reasoning": reasoning,
                    "total_score": score
                })

            # Sort by score
            scores.sort(key=lambda x: x["total_score"], reverse=True)
            best_candidate = scores[0] if scores else None

            return {
                "recommended_assignee": {
                    "user_id": best_candidate["user_id"],
                    "name": best_candidate["name"],
                    "score": best_candidate["total_score"]
                } if best_candidate else None,
                "confidence": min(best_candidate["total_score"] / 100, 0.95) if best_candidate else 0,
                "alternatives": scores[1:4],
                "reasoning": best_candidate["reasoning"] if best_candidate else [],
                "assignment_factors": {
                    "skills_weight": 0.3,
                    "workload_weight": 0.25,
                    "performance_weight": 0.2,
                    "availability_weight": 0.15,
                    "priority_weight": 0.1
                }
            }

        except Exception as e:
            logger.error(f"Fallback task assignment failed: {e}")
            return {
                "error": str(e),
                "recommended_assignee": None,
                "confidence": 0
            }

    async def analyze_project_risks(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project risks"""
        try:
            # Simple risk analysis based on project data
            risks = []

            # Timeline risk
            tasks = project_data.get("tasks", [])
            overdue_tasks = [t for t in tasks if t.get("status") == "overdue"]
            if overdue_tasks:
                risks.append({
                    "type": "timeline",
                    "severity": "high",
                    "description": f"{len(overdue_tasks)} tasks are overdue",
                    "recommendation": "Reassign resources or extend timeline"
                })

            # Resource risk
            team = project_data.get("team", [])
            overloaded_members = [m for m in team if m.get("current_workload", 0) > m.get("workload_capacity", 40) * 0.9]
            if overloaded_members:
                risks.append({
                    "type": "resource",
                    "severity": "medium",
                    "description": f"{len(overloaded_members)} team members are overloaded",
                    "recommendation": "Redistribute tasks or hire additional resources"
                })

            # Budget risk
            budget = project_data.get("project", {}).get("budget")
            if budget:
                # Calculate projected spend
                time_logs = project_data.get("time_logs", [])
                total_logged = sum(log.get("hours", 0) for log in time_logs)
                avg_hourly_rate = 50  # Assume default rate
                projected_spend = total_logged * avg_hourly_rate

                if projected_spend > budget * 0.9:
                    risks.append({
                        "type": "budget",
                        "severity": "high",
                        "description": f"Projected spend (${projected_spend:.2f}) exceeds 90% of budget (${budget:.2f})",
                        "recommendation": "Reduce scope or increase budget"
                    })

            return {
                "risks": risks,
                "overall_risk_level": "high" if any(r["severity"] == "high" for r in risks) else "medium" if risks else "low",
                "recommendations": [r["recommendation"] for r in risks]
            }

        except Exception as e:
            logger.error(f"Risk analysis failed: {e}")
            return {"error": str(e)}

    async def optimize_resource_allocation(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource allocation"""
        try:
            # Simple resource optimization
            team = project_data.get("team", [])
            tasks = project_data.get("tasks", [])

            # Calculate current utilization
            utilization = {}
            for member in team:
                user_id = member["user_id"]
                current_load = member.get("current_tasks", 0)
                capacity = member.get("workload_capacity", 40)
                utilization[user_id] = {
                    "current_load": current_load,
                    "capacity": capacity,
                    "utilization_rate": current_load / capacity if capacity > 0 else 0
                }

            # Identify bottlenecks
            bottlenecks = [uid for uid, data in utilization.items() if data["utilization_rate"] > 0.8]
            underutilized = [uid for uid, data in utilization.items() if data["utilization_rate"] < 0.5]

            recommendations = []

            if bottlenecks:
                recommendations.append(f"Redistribute work from {len(bottlenecks)} overloaded team members")

            if underutilized:
                recommendations.append(f"Assign more tasks to {len(underutilized)} underutilized team members")

            return {
                "current_utilization": utilization,
                "bottlenecks": bottlenecks,
                "underutilized": underutilized,
                "recommendations": recommendations,
                "optimization_score": 0.75  # Mock score
            }

        except Exception as e:
            logger.error(f"Resource optimization failed: {e}")
            return {"error": str(e)}

    async def predict_project_timeline(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict project completion timeline"""
        try:
            tasks = project_data.get("tasks", [])
            completed_tasks = [t for t in tasks if t.get("status") == "done"]
            total_tasks = len(tasks)

            if total_tasks == 0:
                return {"error": "No tasks found"}

            completion_rate = len(completed_tasks) / total_tasks

            # Simple velocity calculation
            time_logs = project_data.get("time_logs", [])
            total_hours_logged = sum(log.get("hours", 0) for log in time_logs)

            if completion_rate > 0:
                avg_hours_per_task = total_hours_logged / len(completed_tasks) if completed_tasks else 8
                remaining_tasks = total_tasks - len(completed_tasks)
                estimated_remaining_hours = remaining_tasks * avg_hours_per_task
                estimated_completion_days = estimated_remaining_hours / 8  # 8 hours per day

                return {
                    "completion_percentage": completion_rate * 100,
                    "estimated_completion_days": estimated_completion_days,
                    "remaining_tasks": remaining_tasks,
                    "avg_velocity": len(completed_tasks) / max(1, total_hours_logged / 8),  # tasks per day
                    "confidence": 0.7
                }
            else:
                return {
                    "completion_percentage": 0,
                    "estimated_completion_days": None,
                    "remaining_tasks": total_tasks,
                    "confidence": 0.3
                }

        except Exception as e:
            logger.error(f"Timeline prediction failed: {e}")
            return {"error": str(e)}

    async def generate_project_insights(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general project insights"""
        try:
            # Combine various analyses
            risk_analysis = await self.analyze_project_risks(project_data)
            resource_analysis = await self.optimize_resource_allocation(project_data)
            timeline_analysis = await self.predict_project_timeline(project_data)

            return {
                "risk_analysis": risk_analysis,
                "resource_analysis": resource_analysis,
                "timeline_analysis": timeline_analysis,
                "overall_health_score": 0.75,  # Mock score
                "key_insights": [
                    "Project is on track with current velocity",
                    "Monitor resource utilization closely",
                    "Consider timeline adjustments if scope changes"
                ]
            }

        except Exception as e:
            logger.error(f"Project insights generation failed: {e}")
            return {"error": str(e)}

    async def predict_project_completion(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict project completion dates"""
        try:
            projects = analytics_data.get("projects", [])

            predictions = {}
            for project in projects:
                project_id = project["id"]

                # Mock prediction - production would use ML model
                completion_pct = project.get("completion_percentage", 0)
                remaining_pct = 100 - completion_pct

                # Assume 10% completion per week velocity
                weeks_remaining = remaining_pct / 10

                predictions[str(project_id)] = {
                    "predicted_completion_date": (datetime.utcnow() + timedelta(weeks=weeks_remaining)).isoformat(),
                    "confidence": 0.75,
                    "factors": ["historical_velocity", "team_capacity", "task_complexity"]
                }

            return {
                "predictions": predictions,
                "methodology": "velocity_based_forecasting",
                "confidence_levels": {"overall": 0.75}
            }

        except Exception as e:
            logger.error(f"Project completion prediction failed: {e}")
            return {"error": str(e)}

    async def predict_team_performance(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict team performance metrics"""
        try:
            team = analytics_data.get("team", [])
            tasks = analytics_data.get("tasks", [])
            time_logs = analytics_data.get("time_logs", [])

            # Calculate current metrics
            completed_tasks = [t for t in tasks if t.get("status") == "done"]
            total_tasks = len(tasks)
            completion_rate = len(completed_tasks) / total_tasks if total_tasks > 0 else 0

            # Predict future performance
            predictions = {
                "productivity_trend": "increasing" if completion_rate > 0.7 else "stable",
                "team_velocity": len(completed_tasks) / max(1, len(team)),  # tasks per member
                "estimated_completion_rate": min(completion_rate + 0.1, 1.0),  # Assume 10% improvement
                "risk_factors": ["resource_constraints", "task_complexity"] if completion_rate < 0.5 else []
            }

            return {
                "predictions": predictions,
                "confidence_levels": {"productivity": 0.8, "velocity": 0.7},
                "recommendations": [
                    "Increase team capacity for faster delivery" if completion_rate < 0.6 else
                    "Maintain current velocity and quality standards"
                ]
            }

        except Exception as e:
            logger.error(f"Team performance prediction failed: {e}")
            return {"error": str(e)}

    async def predict_resource_needs(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict future resource needs"""
        try:
            current_team_size = len(analytics_data.get("team", []))
            projects = analytics_data.get("projects", [])
            active_projects = [p for p in projects if p.get("status") == "active"]

            # Simple resource prediction
            resource_needs = {
                "additional_developers": max(0, len(active_projects) - current_team_size),
                "additional_designers": 1 if any(p.get("name", "").lower().find("design") >= 0 for p in active_projects) else 0,
                "timeline": "3_months",
                "priority": "medium" if len(active_projects) > current_team_size else "low"
            }

            return {
                "resource_needs": resource_needs,
                "confidence_levels": {"quantity": 0.7, "timeline": 0.6},
                "recommendations": [
                    f"Hire {resource_needs['additional_developers']} additional developers" if resource_needs['additional_developers'] > 0 else
                    "Current team size is adequate for planned projects"
                ]
            }

        except Exception as e:
            logger.error(f"Resource needs prediction failed: {e}")
            return {"error": str(e)}

    async def generate_general_predictions(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general workspace predictions"""
        try:
            # Combine all prediction types
            completion = await self.predict_project_completion(analytics_data)
            performance = await self.predict_team_performance(analytics_data)
            resources = await self.predict_resource_needs(analytics_data)

            return {
                "project_completion": completion,
                "team_performance": performance,
                "resource_needs": resources,
                "overall_workspace_health": 0.8,
                "recommendations": [
                    "Focus on completing high-priority projects",
                    "Monitor team workload and redistribute if needed",
                    "Plan for future hiring based on project pipeline"
                ]
            }

        except Exception as e:
            logger.error(f"General predictions failed: {e}")
            return {"error": str(e)}

    async def optimize_billing_structure(self, billing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize billing structure for better cash flow"""
        try:
            billing_items = billing_data.get("billing_items", [])

            # Simple optimization: group small invoices, optimize timing
            optimized_items = []
            small_invoices = []
            large_invoices = []

            for item in billing_items:
                if item.get("amount", 0) < 100:
                    small_invoices.append(item)
                else:
                    large_invoices.append(item)

            # Group small invoices
            if small_invoices:
                combined = {
                    "user_id": small_invoices[0]["user_id"],
                    "user_name": small_invoices[0]["user_name"],
                    "project_name": "Multiple Projects",
                    "hours": sum(item.get("hours", 0) for item in small_invoices),
                    "tasks": [task for item in small_invoices for task in item.get("tasks", [])],
                    "optimized_amount": sum(item.get("amount", 0) for item in small_invoices),
                    "billing_group": "consolidated_small_invoices"
                }
                optimized_items.append(combined)

            # Keep large invoices as-is but optimize amounts
            for item in large_invoices:
                # Apply small discount for early payment
                discount = item.get("amount", 0) * 0.02  # 2% discount
                optimized = item.copy()
                optimized["optimized_amount"] = item.get("amount", 0) - discount
                optimized["discount_applied"] = discount
                optimized_items.append(optimized)

            return {
                "optimized_items": optimized_items,
                "total_savings": sum(item.get("discount_applied", 0) for item in optimized_items),
                "insights": {
                    "consolidated_invoices": len(small_invoices) if small_invoices else 0,
                    "optimization_strategy": "group_small_consolidate_large",
                    "expected_cash_flow_improvement": "15%"
                }
            }

        except Exception as e:
            logger.error(f"Billing optimization failed: {e}")
            return {"error": str(e)}

    async def optimize_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize workspace workflow"""
        try:
            projects = workflow_data.get("projects", [])
            tasks = workflow_data.get("tasks", [])
            team = workflow_data.get("team", [])
            focus_areas = workflow_data.get("optimization_focus", [])

            recommendations = []
            expected_improvements = {}

            # Analyze bottlenecks
            if "bottlenecks" in focus_areas:
                blocked_tasks = [t for t in tasks if t.get("blockers")]
                if blocked_tasks:
                    recommendations.append({
                        "type": "bottleneck_resolution",
                        "description": f"Resolve blockers for {len(blocked_tasks)} tasks",
                        "impact": "high",
                        "effort": "medium"
                    })
                    expected_improvements["throughput"] = "+25%"

            # Resource allocation
            if "resource_allocation" in focus_areas:
                overloaded = [m for m in team if m.get("current_tasks", 0) > 3]
                if overloaded:
                    recommendations.append({
                        "type": "resource_redistribution",
                        "description": f"Redistribute tasks from {len(overloaded)} overloaded members",
                        "impact": "high",
                        "effort": "low"
                    })
                    expected_improvements["utilization"] = "+30%"

            # Timeline optimization
            if "timeline" in focus_areas:
                overdue_tasks = [t for t in tasks if t.get("status") == "overdue"]
                if overdue_tasks:
                    recommendations.append({
                        "type": "timeline_acceleration",
                        "description": f"Fast-track {len(overdue_tasks)} overdue tasks",
                        "impact": "critical",
                        "effort": "high"
                    })
                    expected_improvements["on_time_delivery"] = "+40%"

            return {
                "recommendations": recommendations,
                "expected_improvements": expected_improvements,
                "implementation_plan": {
                    "phase_1": "Identify and resolve critical blockers",
                    "phase_2": "Optimize resource allocation",
                    "phase_3": "Implement workflow improvements"
                },
                "estimated_completion_time": "2_weeks",
                "success_probability": 0.85
            }

        except Exception as e:
            logger.error(f"Workflow optimization failed: {e}")
            return {"error": str(e)}

    async def analyze_code(self, code_content: str, language: str, context: str) -> Dict[str, Any]:
        """Analyze code for review using OpenRouter"""
        try:
            if not self.ai_router:
                return await self._fallback_code_analysis(code_content, language, context)

            # Use OpenRouter for code analysis
            prompt = f"""
            Analyze this {language} code and provide a comprehensive review:

            CONTEXT: {context}

            CODE TO ANALYZE:
            ```{language}
            {code_content}
            ```

            Please respond with a JSON object containing:
            - language: programming language
            - lines_of_code: total lines
            - complexity_score: (0.0-1.0, where 1.0 is most complex)
            - maintainability_index: (0-100, higher is better)
            - potential_issues: array of {{type, severity, description}}
            - code_quality_score: (0.0-1.0, higher is better)
            - security_concerns: array of potential security issues
            - performance_suggestions: array of performance improvements
            - best_practice_violations: array of coding standard violations

            Focus on actual code quality issues, not style preferences.
            """

            messages = [
                {"role": "system", "content": f"You are an expert {language} code reviewer with years of experience. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            response = await self.ai_router.chat_completion(
                messages=messages,
                model=self.ai_model.CLAUDE_SONNET,
                temperature=0.1,
                max_tokens=1200
            )

            if response and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                try:
                    analysis = json.loads(content.strip())
                    return analysis
                except json.JSONDecodeError:
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group(1))
                        return analysis

            # If AI response parsing fails, use fallback
            return await self._fallback_code_analysis(code_content, language, context)

        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            return await self._fallback_code_analysis(code_content, language, context)

    async def _fallback_code_analysis(self, code_content: str, language: str, context: str) -> Dict[str, Any]:
        """Fallback code analysis"""
        lines_of_code = len(code_content.split('\n'))

        # Basic heuristics
        complexity_score = min(lines_of_code / 100, 1.0)  # Rough complexity estimate
        maintainability_index = max(0, 100 - (lines_of_code / 10))  # Rough maintainability

        potential_issues = []

        # Check for common issues
        if "TODO" in code_content.upper():
            potential_issues.append({"type": "documentation", "severity": "low", "description": "TODO comments found"})
        if "FIXME" in code_content.upper():
            potential_issues.append({"type": "maintenance", "severity": "medium", "description": "FIXME comments indicate known issues"})
        if "print(" in code_content and language.lower() in ["python", "javascript", "typescript"]:
            potential_issues.append({"type": "debugging", "severity": "low", "description": "Debug print statements left in code"})

        return {
            "language": language,
            "lines_of_code": lines_of_code,
            "complexity_score": complexity_score,
            "maintainability_index": maintainability_index,
            "potential_issues": potential_issues,
            "code_quality_score": 0.7,
            "security_concerns": [],
            "performance_suggestions": [],
            "best_practice_violations": []
        }

    async def generate_code_review(self, analysis: Dict[str, Any], review_type: str, severity_level: str) -> Dict[str, Any]:
        """Generate code review feedback using OpenRouter"""
        try:
            if not self.ai_router:
                return await self._fallback_code_review(analysis, review_type, severity_level)

            # Filter issues by severity level
            severity_map = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            min_severity = severity_map.get(severity_level, 0)

            filtered_issues = [
                issue for issue in analysis.get("potential_issues", [])
                if severity_map.get(issue.get("severity", "low"), 0) >= min_severity
            ]

            prompt = f"""
            Generate a comprehensive code review based on this analysis:

            ANALYSIS RESULTS:
            - Language: {analysis.get('language', 'unknown')}
            - Lines of code: {analysis.get('lines_of_code', 0)}
            - Complexity score: {analysis.get('complexity_score', 0):.2f}
            - Maintainability index: {analysis.get('maintainability_index', 50)}
            - Code quality score: {analysis.get('code_quality_score', 0.5):.2f}

            FILTERED ISSUES (severity >= {severity_level}):
            {json.dumps(filtered_issues, indent=2)}

            REVIEW TYPE: {review_type}
            SEVERITY LEVEL: {severity_level}

            Please respond with a JSON object containing:
            - overall_score: (0.0-1.0)
            - recommendations: array of specific improvement suggestions
            - severity_breakdown: {{critical, high, medium, low}} counts
            - estimated_fix_effort: time estimate string (e.g., "2-3 hours")
            - review_type: the review type requested
            - severity_filter: the severity level used
            - prioritized_fixes: array of most critical issues to address first
            - code_improvements: specific code change suggestions

            Focus on actionable feedback for the {review_type} review type.
            """

            messages = [
                {"role": "system", "content": "You are a senior software engineer providing constructive code review feedback. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            response = await self.ai_router.chat_completion(
                messages=messages,
                model=self.ai_model.CLAUDE_SONNET,
                temperature=0.2,
                max_tokens=1000
            )

            if response and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                try:
                    feedback = json.loads(content.strip())
                    return feedback
                except json.JSONDecodeError:
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        feedback = json.loads(json_match.group(1))
                        return feedback

            # If AI response parsing fails, use fallback
            return await self._fallback_code_review(analysis, review_type, severity_level)

        except Exception as e:
            logger.error(f"Code review generation failed: {e}")
            return await self._fallback_code_review(analysis, review_type, severity_level)

    async def _fallback_code_review(self, analysis: Dict[str, Any], review_type: str, severity_level: str) -> Dict[str, Any]:
        """Fallback code review generation"""
        issues = analysis.get("potential_issues", [])

        # Count issues by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity in severity_counts:
                severity_counts[severity] += 1

        recommendations = []
        if severity_counts["critical"] > 0:
            recommendations.append("Address critical issues immediately")
        if severity_counts["high"] > 0:
            recommendations.append("Fix high-severity issues before deployment")
        if analysis.get("code_quality_score", 0.5) < 0.7:
            recommendations.append("Consider refactoring for better maintainability")
        if not recommendations:
            recommendations.append("Code looks good, consider adding more comprehensive tests")

        total_issues = sum(severity_counts.values())
        estimated_effort = "1-2 hours" if total_issues <= 2 else "2-4 hours" if total_issues <= 5 else "4+ hours"

        return {
            "overall_score": analysis.get("code_quality_score", 0.7),
            "recommendations": recommendations,
            "severity_breakdown": severity_counts,
            "estimated_fix_effort": estimated_effort,
            "review_type": review_type,
            "severity_filter": severity_level,
            "prioritized_fixes": issues[:3],  # Top 3 issues
            "code_improvements": ["Add input validation", "Improve error handling", "Add unit tests"]
        }


# Global instance
ai_service = AIService()
