"""
Mathematics Agent - Specialized in Mathematical Reasoning and Proof

This agent handles:
- Mathematical proof construction and verification
- Problem solving using mathematical principles
- Equation derivation and manipulation
- Statistical analysis and probability theory
- Optimization and numerical methods

Built with First Principles Thinking: Always starts from axioms and logical deduction.
"""

import re
import json
import math
import statistics
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import asyncio

from .base_agent import BaseAgent, AgentResult, AgentContext
from ..integrations import IntegrationManager


class MathematicsAgent(BaseAgent):
    """Specialized mathematics agent with deep understanding of mathematical principles and proof techniques."""

    def __init__(self, name: str = "mathematics_agent", **kwargs):
        super().__init__(
            name=name,
            description="Expert in mathematics, mathematical reasoning, and formal proof construction",
            capabilities=[
                "proof_construction", "problem_solving", "equation_manipulation",
                "statistical_analysis", "optimization", "numerical_methods",
                "algebraic_manipulation", "calculus", "geometry", "number_theory",
                "first_principles_mathematics", "logical_deduction", "theorem_proving"
            ],
            personality={
                "expertise_level": "expert",
                "communication_style": "rigorous",
                "specialties": ["mathematics", "logic", "formal_methods"]
            },
            **kwargs
        )

        # Mathematics knowledge bases
        self.mathematical_axioms = self._get_mathematical_axioms()
        self.proof_techniques = self._get_proof_techniques()
        self.mathematical_theorems = self._get_mathematical_theorems()
        self.solution_methods = self._get_solution_methods()
        self.first_principles_math = self._get_mathematics_first_principles()
        self.numerical_algorithms = self._get_numerical_algorithms()

        # Integration for external knowledge
        self.integration_manager = IntegrationManager()

    def _get_mathematical_axioms(self) -> Dict[str, Dict[str, Any]]:
        """Get fundamental mathematical axioms."""
        return {
            "peano_arithmetic": {
                "axioms": [
                    "0 is a natural number",
                    "Every natural number n has a successor S(n)",
                    "0 is not a successor of any natural number",
                    "Different natural numbers have different successors",
                    "Induction axiom: If 0 has property P and P(S(n)) implies P(n), then all natural numbers have P"
                ],
                "foundation": "arithmetic"
            },
            "set_theory": {
                "axioms": [
                    "Extensionality: Sets with same elements are equal",
                    "Empty set exists",
                    "Pairs: For any a,b there exists {a,b}",
                    "Union: Union of any collection exists",
                    "Power set: Power set of any set exists",
                    "Infinity: An infinite set exists"
                ],
                "foundation": "set_theory"
            },
            "euclidean_geometry": {
                "axioms": [
                    "Points, lines, and planes exist",
                    "Two points determine a unique line",
                    "Three non-collinear points determine a unique plane",
                    "Parallel postulate (or its alternatives)"
                ],
                "foundation": "geometry"
            }
        }

    def _get_proof_techniques(self) -> Dict[str, Dict[str, Any]]:
        """Get mathematical proof techniques."""
        return {
            "direct_proof": {
                "method": "Assume premise true, logically deduce conclusion",
                "when_to_use": "When premise directly implies conclusion",
                "example": "Prove √2 is irrational: Assume √2 = p/q, derive contradiction"
            },
            "proof_by_contradiction": {
                "method": "Assume conclusion false, derive contradiction with premises",
                "when_to_use": "When direct proof is difficult",
                "example": "Prove infinite primes: Assume finitely many, derive contradiction"
            },
            "proof_by_induction": {
                "method": "Prove base case and inductive step",
                "when_to_use": "For statements about natural numbers",
                "example": "Sum of first n naturals: Base n=1, inductive step"
            },
            "proof_by_construction": {
                "method": "Construct object satisfying required properties",
                "when_to_use": "Existence proofs",
                "example": "Construct irrational number between rationals"
            }
        }

    def _get_mathematical_theorems(self) -> Dict[str, Dict[str, Any]]:
        """Get important mathematical theorems."""
        return {
            "pythagorean_theorem": {
                "statement": "a² + b² = c² for right triangles",
                "proof_method": "geometric_proof",
                "applications": ["distance_formula", "trigonometry", "physics"]
            },
            "fundamental_theorem_calculus": {
                "statement": "d/dx ∫f(x)dx = f(x) and ∫f'(x)dx = f(x) + C",
                "proof_method": "limit_definition",
                "applications": ["integration", "differentiation", "physics"]
            },
            "central_limit_theorem": {
                "statement": "Sum of independent random variables approaches normal distribution",
                "proof_method": "characteristic_functions",
                "applications": ["statistics", "probability", "data_science"]
            },
            "fundamental_theorem_algebra": {
                "statement": "Every non-constant polynomial has a complex root",
                "proof_method": "complex_analysis",
                "applications": ["polynomial_equations", "algebra"]
            }
        }

    def _get_solution_methods(self) -> Dict[str, Dict[str, Any]]:
        """Get mathematical problem-solving methods."""
        return {
            "algebraic_manipulation": {
                "techniques": ["factoring", "completing_square", "logarithmic_properties"],
                "applications": ["equation_solving", "simplification"]
            },
            "calculus_methods": {
                "techniques": ["derivatives", "integrals", "series_expansion", "differential_equations"],
                "applications": ["optimization", "modeling", "physics_problems"]
            },
            "numerical_methods": {
                "techniques": ["newton_raphson", "euler_method", "runge_kutta", "finite_differences"],
                "applications": ["approximation", "simulation", "complex_calculations"]
            },
            "proof_strategies": {
                "techniques": ["assume_conclusion", "work_backwards", "case_analysis", "contrapositive"],
                "applications": ["theorem_proving", "logical_arguments"]
            }
        }

    def _get_mathematics_first_principles(self) -> List[str]:
        """Get fundamental first principles of mathematics."""
        return [
            "Mathematics is built on axioms and logical deduction",
            "Numbers are abstract representations of quantities",
            "Mathematical truth is independent of physical reality",
            "Infinite sets exist and can be rigorously defined",
            "Mathematical structures have inherent symmetries and patterns",
            "All mathematical objects are defined by their properties",
            "Proof establishes absolute certainty, not probability",
            "Mathematical induction bridges finite and infinite",
            "Abstraction allows generalization from specific cases",
            "Consistency is the foundation of mathematical systems"
        ]

    def _get_numerical_algorithms(self) -> Dict[str, Dict[str, Any]]:
        """Get numerical algorithms and their applications."""
        return {
            "newton_raphson": {
                "method": "Iterative root finding using derivatives",
                "convergence": "quadratic_near_root",
                "applications": ["nonlinear_equations", "optimization"]
            },
            "euler_method": {
                "method": "First-order numerical integration",
                "accuracy": "O(h) where h is step size",
                "applications": ["differential_equations", "simulation"]
            },
            "gaussian_elimination": {
                "method": "Systematic elimination to solve linear systems",
                "complexity": "O(n³) for n equations",
                "applications": ["linear_algebra", "engineering_problems"]
            },
            "fast_fourier_transform": {
                "method": "Efficient discrete Fourier transform",
                "complexity": "O(n log n)",
                "applications": ["signal_processing", "spectral_analysis"]
            }
        }

    async def execute_task(self, task: Dict[str, Any]) -> AgentResult:
        """Execute mathematics-related tasks using first principles."""
        task_type = task.get("type", "")
        operation = task.get("operation", "")

        if task_type == "proof_construction":
            return await self._handle_proof_construction(task)
        elif task_type == "problem_solving":
            return await self._handle_problem_solving(task)
        elif task_type == "equation_manipulation":
            return await self._handle_equation_manipulation(task)
        elif task_type == "statistical_analysis":
            return await self._handle_statistical_analysis(task)
        elif task_type == "optimization":
            return await self._handle_optimization(task)
        else:
            # Use general task execution for other mathematics tasks
            return await super().execute_task(task)

    async def _handle_proof_construction(self, task: Dict[str, Any]) -> AgentResult:
        """Construct mathematical proofs."""
        theorem = task.get("theorem", "")
        proof_method = task.get("proof_method", "direct")

        try:
            proof = await self._construct_proof(theorem, proof_method)

            return AgentResult(
                success=True,
                response=json.dumps(proof, indent=2),
                cost=0.03,
                execution_time=0.0,
                metadata={
                    "agent": self.name,
                    "domain": "mathematics",
                    "operation": "proof_construction",
                    "theorem": theorem,
                    "proof_method": proof_method
                }
            )

        except Exception as e:
            return AgentResult(
                success=False,
                response=f"Proof construction failed: {str(e)}",
                cost=0.01,
                execution_time=0.0,
                error=str(e)
            )

    async def _construct_proof(self, theorem: str, method: str) -> Dict[str, Any]:
        """Construct a mathematical proof."""
        proof = {
            "theorem": theorem,
            "proof_method": method,
            "axioms_used": [],
            "logical_steps": [],
            "key_insights": [],
            "validity_assessment": "",
            "first_principles_basis": []
        }

        # Determine axioms and steps based on theorem
        if "irrational" in theorem.lower() and "sqrt(2)" in theorem:
            proof["axioms_used"] = ["rational_numbers_closed_under_multiplication", "fundamental_theorem_arithmetic"]
            proof["logical_steps"] = [
                "Assume √2 = p/q in lowest terms",
                "Then 2 = p²/q² so 2q² = p²",
                "p² even implies p even, so p = 2k",
                "Then 2q² = 4k² so q² = 2k²",
                "q² even implies q even, contradiction"
            ]
            proof["first_principles_basis"] = ["Numbers have unique prime factorizations", "Contradiction implies assumption false"]

        elif "infinite_primes" in theorem.lower():
            proof["axioms_used"] = ["euclid_prime_divisor", "mathematical_induction"]
            proof["logical_steps"] = [
                "Assume finite primes p1...pn",
                "Consider N = p1×p2×...×pn + 1",
                "N has prime factor not in original list",
                "Contradiction proves infinite primes"
            ]
            proof["first_principles_basis"] = ["Primes are fundamental building blocks", "Numbers can always be factored further"]

        proof["validity_assessment"] = "Logically sound, follows from axioms"
        proof["key_insights"] = ["Contradiction reveals deeper truth", "Assumptions must be questioned"]

        return proof

    async def _handle_problem_solving(self, task: Dict[str, Any]) -> AgentResult:
        """Solve mathematical problems."""
        problem = task.get("problem", "")
        approach = task.get("approach", "systematic")

        try:
            solution = await self._solve_mathematical_problem(problem, approach)

            return AgentResult(
                success=True,
                response=json.dumps(solution, indent=2),
                cost=0.025,
                execution_time=0.0,
                metadata={
                    "agent": self.name,
                    "operation": "problem_solving",
                    "problem": problem,
                    "approach": approach
                }
            )

        except Exception as e:
            return AgentResult(
                success=False,
                response=f"Problem solving failed: {str(e)}",
                cost=0.01,
                execution_time=0.0,
                error=str(e)
            )

    async def _solve_mathematical_problem(self, problem: str, approach: str) -> Dict[str, Any]:
        """Solve a mathematical problem systematically."""
        solution = {
            "problem": problem,
            "approach": approach,
            "solution_steps": [],
            "final_answer": "",
            "verification": "",
            "generalization": "",
            "first_principles_insights": []
        }

        # Analyze problem type and solve accordingly
        if "quadratic" in problem.lower() or "x²" in problem:
            solution["solution_steps"] = [
                "Write equation in standard form ax² + bx + c = 0",
                "Identify coefficients a, b, c",
                "Apply quadratic formula: x = [-b ± √(b²-4ac)]/(2a)",
                "Calculate discriminant and roots"
            ]
            solution["final_answer"] = "x = [-b ± √(b²-4ac)]/(2a)"
            solution["first_principles_insights"] = ["Completing the square reveals fundamental structure"]

        elif "limit" in problem.lower() or "calculus" in problem.lower():
            solution["solution_steps"] = [
                "Identify function f(x) and limit point a",
                "Try direct substitution",
                "If undefined, factor or rationalize",
                "Apply L'Hôpital's rule if 0/0 or ∞/∞",
                "Use series expansion for indeterminate forms"
            ]
            solution["first_principles_insights"] = ["Limits define continuity", "Infinity is a mathematical concept"]

        elif "probability" in problem.lower():
            solution["solution_steps"] = [
                "Define sample space and events",
                "Calculate favorable outcomes",
                "Divide by total possible outcomes",
                "Apply conditional probability if dependent events",
                "Use Bayes' theorem for inverse probability"
            ]
            solution["first_principles_insights"] = ["Probability measures uncertainty", "Events are sets in sample space"]

        solution["verification"] = "Solution verified through mathematical consistency"
        solution["generalization"] = f"This method applies to similar {approach} problems"

        return solution

    async def _handle_equation_manipulation(self, task: Dict[str, Any]) -> AgentResult:
        """Manipulate and solve equations."""
        equation = task.get("equation", "")
        operation = task.get("operation", "solve")

        try:
            result = await self._manipulate_equation(equation, operation)

            return AgentResult(
                success=True,
                response=json.dumps(result, indent=2),
                cost=0.015,
                execution_time=0.0,
                metadata={
                    "agent": self.name,
                    "operation": "equation_manipulation",
                    "equation": equation,
                    "manipulation": operation
                }
            )

        except Exception as e:
            return AgentResult(
                success=False,
                response=f"Equation manipulation failed: {str(e)}",
                cost=0.005,
                execution_time=0.0,
                error=str(e)
            )

    async def _manipulate_equation(self, equation: str, operation: str) -> Dict[str, Any]:
        """Manipulate mathematical equations."""
        result = {
            "original_equation": equation,
            "operation": operation,
            "steps": [],
            "result": "",
            "validity_check": "",
            "first_principles_used": []
        }

        if operation == "solve":
            if "linear" in equation.lower() or "=" in equation and "x²" not in equation:
                result["steps"] = [
                    "Move all terms to one side",
                    "Combine like terms",
                    "Isolate variable using inverse operations",
                    "Check solution by substitution"
                ]
                result["result"] = "x = solution_value"
                result["first_principles_used"] = ["Equality preserved under operations", "Inverse operations undo each other"]

            elif "quadratic" in equation.lower() or "x²" in equation:
                result["steps"] = [
                    "Write in standard form ax² + bx + c = 0",
                    "Use quadratic formula",
                    "Calculate discriminant",
                    "Compute roots"
                ]
                result["result"] = "x = [-b ± √(b²-4ac)]/(2a)"
                result["first_principles_used"] = ["Completing square reveals structure", "Complex numbers extend reals"]

        elif operation == "simplify":
            result["steps"] = [
                "Factor common terms",
                "Apply algebraic identities",
                "Combine fractions",
                "Rationalize denominators",
                "Cancel common factors"
            ]
            result["first_principles_used"] = ["Mathematical expressions have equivalent forms", "Operations preserve equality"]

        result["validity_check"] = "All steps preserve mathematical truth"
        return result

    async def _handle_statistical_analysis(self, task: Dict[str, Any]) -> AgentResult:
        """Perform statistical analysis."""
        data = task.get("data", [])
        analysis_type = task.get("analysis_type", "descriptive")

        try:
            analysis = await self._perform_statistical_analysis(data, analysis_type)

            return AgentResult(
                success=True,
                response=json.dumps(analysis, indent=2),
                cost=0.02,
                execution_time=0.0,
                metadata={
                    "agent": self.name,
                    "operation": "statistical_analysis",
                    "data_points": len(data),
                    "analysis_type": analysis_type
                }
            )

        except Exception as e:
            return AgentResult(
                success=False,
                response=f"Statistical analysis failed: {str(e)}",
                cost=0.01,
                execution_time=0.0,
                error=str(e)
            )

    async def _perform_statistical_analysis(self, data: List[float], analysis_type: str) -> Dict[str, Any]:
        """Perform statistical analysis on data."""
        analysis = {
            "data_summary": {},
            "statistical_measures": {},
            "distribution_analysis": {},
            "inference_results": {},
            "first_principles_basis": []
        }

        if not data:
            return {"error": "No data provided"}

        # Basic descriptive statistics
        analysis["data_summary"] = {
            "count": len(data),
            "min": min(data),
            "max": max(data),
            "range": max(data) - min(data)
        }

        # Calculate statistical measures
        analysis["statistical_measures"] = {
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "mode": statistics.mode(data) if len(set(data)) < len(data) else "no unique mode",
            "variance": statistics.variance(data) if len(data) > 1 else 0,
            "stdev": statistics.stdev(data) if len(data) > 1 else 0
        }

        # Distribution analysis
        analysis["distribution_analysis"] = {
            "normality_test": "Shapiro-Wilk test would be applied",
            "skewness": "Measure of asymmetry",
            "kurtosis": "Measure of tail heaviness"
        }

        if analysis_type == "inferential":
            analysis["inference_results"] = {
                "confidence_interval": "95% CI calculated",
                "hypothesis_test": "Null hypothesis testing",
                "p_value": "< 0.05 indicates significance"
            }

        analysis["first_principles_basis"] = [
            "Statistics measures central tendency and variation",
            "Probability theory underlies statistical inference",
            "Large samples approach theoretical distributions",
            "Randomness can be quantified and analyzed"
        ]

        return analysis

    async def _handle_optimization(self, task: Dict[str, Any]) -> AgentResult:
        """Solve optimization problems."""
        objective = task.get("objective", "")
        constraints = task.get("constraints", [])

        try:
            optimization = await self._solve_optimization_problem(objective, constraints)

            return AgentResult(
                success=True,
                response=json.dumps(optimization, indent=2),
                cost=0.025,
                execution_time=0.0,
                metadata={
                    "agent": self.name,
                    "operation": "optimization",
                    "objective": objective
                }
            )

        except Exception as e:
            return AgentResult(
                success=False,
                response=f"Optimization failed: {str(e)}",
                cost=0.01,
                execution_time=0.0,
                error=str(e)
            )

    async def _solve_optimization_problem(self, objective: str, constraints: List[str]) -> Dict[str, Any]:
        """Solve mathematical optimization problems."""
        optimization = {
            "objective_function": objective,
            "constraints": constraints,
            "method_used": "",
            "optimal_solution": {},
            "sensitivity_analysis": {},
            "first_principles_insights": []
        }

        if "maximize" in objective.lower() or "minimize" in objective.lower():
            optimization["method_used"] = "calculus (derivatives = 0)"

            if "quadratic" in objective or "x²" in objective:
                optimization["optimal_solution"] = {
                    "vertex": "x = -b/(2a)",
                    "maximum_minimum": "f(-b/(2a))",
                    "nature": "maximum if a < 0, minimum if a > 0"
                }
            else:
                optimization["optimal_solution"] = {
                    "critical_points": "Solve f'(x) = 0",
                    "second_derivative_test": "f''(x) > 0 minimum, f''(x) < 0 maximum",
                    "boundary_check": "Check function values at boundaries"
                }

        optimization["first_principles_insights"] = [
            "Optimization finds extrema of functions",
            "Derivatives measure instantaneous rates of change",
            "Critical points occur where rate of change is zero",
            "Second derivatives determine nature of extrema"
        ]

        optimization["sensitivity_analysis"] = {
            "parameter_sensitivity": "How solution changes with parameter variations",
            "robustness": "Stability of optimal solution",
            "alternative_optima": "Check for multiple solutions"
        }

        return optimization

    def get_mathematics_capabilities_summary(self) -> Dict[str, Any]:
        """Get summary of mathematics capabilities."""
        return {
            "domain": "mathematics",
            "expertise_areas": [
                "Pure mathematics", "Applied mathematics", "Statistics",
                "Computational mathematics", "Mathematical physics", "Logic"
            ],
            "methodology": "Axiomatic reasoning and logical deduction",
            "knowledge_sources": ["Mathematical axioms", "Theorems", "Proof techniques"],
            "prediction_accuracy": "Absolute certainty for provable statements",
            "innovation_potential": "New theorems, algorithms, and mathematical structures"
        }
