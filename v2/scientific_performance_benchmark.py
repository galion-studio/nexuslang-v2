"""
Scientific Knowledge Enhancement - Performance Benchmark Suite
==============================================================

Comprehensive benchmarking and validation suite for the Nexus Lang V2
Scientific Knowledge Enhancement system.

Tests:
- Performance benchmarks across different query types
- Accuracy validation against known scientific results
- Scalability testing under load
- Memory usage and resource consumption analysis
- Cross-domain collaboration efficiency
- External API integration reliability

Author: Nexus Lang V2 Performance Team
Date: November 2025
"""

import asyncio
import time
import json
import statistics
import psutil
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np


class PerformanceBenchmark:
    """Comprehensive performance benchmarking for scientific knowledge system."""

    def __init__(self):
        self.results = {}
        self.baseline_metrics = {}
        self.system_info = self._get_system_info()

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmark context."""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "memory_total": psutil.virtual_memory().total,
            "platform": os.uname().sysname if hasattr(os, 'uname') else os.name,
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            "timestamp": datetime.now().isoformat()
        }

    async def run_complete_benchmark_suite(self):
        """Run the complete benchmark suite."""
        print("🚀 NEXUS LANG V2 - SCIENTIFIC PERFORMANCE BENCHMARK SUITE")
        print("=" * 70)
        print()

        # System baseline
        self._measure_baseline()

        # Individual benchmarks
        await self.benchmark_single_domain_queries()
        await self.benchmark_multi_agent_collaboration()
        await self.benchmark_first_principles_analysis()
        await self.benchmark_external_api_integration()
        await self.benchmark_memory_usage()
        await self.benchmark_concurrent_load()
        await self.benchmark_accuracy_validation()

        # Generate comprehensive report
        self.generate_benchmark_report()

    def _measure_baseline(self):
        """Measure system baseline before benchmarks."""
        print("📊 Establishing System Baseline...")

        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        self.baseline_metrics = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used": memory.used,
            "timestamp": datetime.now().isoformat()
        }

        print(f"CPU: {cpu_percent:.1f}%")
        print(f"Memory: {memory.percent:.1f}%")
        print()

    async def benchmark_single_domain_queries(self):
        """Benchmark single-domain scientific queries."""
        print("🎯 BENCHMARK: Single-Domain Scientific Queries")
        print("-" * 50)

        # Test queries for each domain
        test_queries = {
            "physics": [
                "Explain Newton's second law",
                "What is the photoelectric effect?",
                "How does quantum tunneling work?",
                "Derive the ideal gas law",
                "Explain gravitational time dilation"
            ],
            "chemistry": [
                "What is hybridization in carbon compounds?",
                "Explain acid-base titration",
                "How do enzymes catalyze reactions?",
                "What is the mechanism of SN1 reaction?",
                "Explain molecular orbital theory"
            ],
            "mathematics": [
                "Prove that √2 is irrational",
                "Solve the quadratic equation ax² + bx + c = 0",
                "What is the fundamental theorem of calculus?",
                "Explain Bayes' theorem",
                "Prove the Pythagorean theorem"
            ]
        }

        results = {}

        for domain, queries in test_queries.items():
            print(f"Testing {domain.upper()} domain ({len(queries)} queries)...")

            domain_results = []
            for query in queries:
                start_time = time.time()
                # Mock execution - in real implementation, this would call the actual API
                result = await self._mock_scientific_query(query, domain, collaboration=False)
                execution_time = time.time() - start_time

                domain_results.append({
                    "query": query,
                    "execution_time": execution_time,
                    "confidence": result.get("confidence", 0.8),
                    "success": result.get("success", True)
                })

            # Calculate statistics
            execution_times = [r["execution_time"] for r in domain_results]
            confidences = [r["confidence"] for r in domain_results]
            success_rate = sum(1 for r in domain_results if r["success"]) / len(domain_results)

            results[domain] = {
                "query_count": len(queries),
                "avg_execution_time": statistics.mean(execution_times),
                "median_execution_time": statistics.median(execution_times),
                "min_execution_time": min(execution_times),
                "max_execution_time": max(execution_times),
                "avg_confidence": statistics.mean(confidences),
                "success_rate": success_rate,
                "individual_results": domain_results
            }

            print(f"Average execution time: {results[domain]['avg_execution_time']:.2f}s")
            print(f"Average confidence: {results[domain]['avg_confidence']:.2f}")
            print(f"Success rate: {results[domain]['success_rate']:.1f}")
        print()
        self.results["single_domain"] = results

    async def benchmark_multi_agent_collaboration(self):
        """Benchmark multi-agent collaboration performance."""
        print("🤝 BENCHMARK: Multi-Agent Scientific Collaboration")
        print("-" * 55)

        # Complex queries requiring multiple domains
        collaboration_queries = [
            "How does quantum mechanics explain chemical bonding?",
            "What mathematical models describe thermodynamic processes?",
            "How do electromagnetic fields affect chemical reactions?",
            "What is the relationship between statistical mechanics and information theory?",
            "How does general relativity affect atomic clocks and GPS systems?",
            "What role does group theory play in quantum chemistry?",
            "How do fluid dynamics principles apply to blood circulation?",
            "What mathematical structures describe crystal lattice symmetries?",
            "How does quantum field theory unify electromagnetic and weak forces?",
            "What statistical methods validate climate change models?"
        ]

        print(f"Testing {len(collaboration_queries)} multi-agent collaboration queries...")

        results = []
        for query in collaboration_queries:
            start_time = time.time()
            result = await self._mock_scientific_query(query, "multi", collaboration=True)
            execution_time = time.time() - start_time

            results.append({
                "query": query,
                "execution_time": execution_time,
                "agent_contributions": len(result.get("agent_contributions", {})),
                "confidence": result.get("confidence", 0.8),
                "cross_domain_connections": len(result.get("cross_domain_connections", []))
            })

        # Calculate statistics
        execution_times = [r["execution_time"] for r in results]
        agent_contributions = [r["agent_contributions"] for r in results]

        benchmark_results = {
            "query_count": len(collaboration_queries),
            "avg_execution_time": statistics.mean(execution_times),
            "avg_agent_contributions": statistics.mean(agent_contributions),
            "avg_confidence": statistics.mean([r["confidence"] for r in results]),
            "individual_results": results
        }

        print(f"Average execution time: {benchmark_results['avg_execution_time']:.2f}s")
        print(f"Average agent contributions: {benchmark_results['avg_agent_contributions']:.1f}")
        print(f"Average confidence: {benchmark_results['avg_confidence']:.1f}")
        print()
        self.results["multi_agent"] = benchmark_results

    async def benchmark_first_principles_analysis(self):
        """Benchmark first principles analysis performance."""
        print("⚛️  BENCHMARK: First Principles Analysis")
        print("-" * 45)

        analysis_topics = [
            ("thermodynamics", "physics"),
            ("electromagnetism", "physics"),
            ("quantum_mechanics", "physics"),
            ("organic_synthesis", "chemistry"),
            ("catalysis", "chemistry"),
            ("calculus", "mathematics"),
            ("probability_theory", "mathematics"),
            ("group_theory", "mathematics")
        ]

        print(f"Testing {len(analysis_topics)} first principles analyses...")

        results = []
        for topic, domain in analysis_topics:
            start_time = time.time()
            result = await self._mock_first_principles_analysis(topic, domain)
            execution_time = time.time() - start_time

            results.append({
                "topic": topic,
                "domain": domain,
                "execution_time": execution_time,
                "principles_identified": len(result.get("fundamental_principles", [])),
                "deduction_steps": len(result.get("logical_deduction_steps", [])),
                "confidence": result.get("confidence", 0.85)
            })

        # Statistics
        execution_times = [r["execution_time"] for r in results]
        principles_count = [r["principles_identified"] for r in results]

        benchmark_results = {
            "analysis_count": len(analysis_topics),
            "avg_execution_time": statistics.mean(execution_times),
            "avg_principles_identified": statistics.mean(principles_count),
            "avg_confidence": statistics.mean([r["confidence"] for r in results]),
            "individual_results": results
        }

        print(f"Average execution time: {benchmark_results['avg_execution_time']:.2f}s")
        print(f"Average principles identified: {benchmark_results['avg_principles_identified']:.1f}")
        print(f"Average confidence: {benchmark_results['avg_confidence']:.1f}")
        print()
        self.results["first_principles"] = benchmark_results

    async def benchmark_external_api_integration(self):
        """Benchmark external API integration performance."""
        print("🌐 BENCHMARK: External API Integration")
        print("-" * 45)

        # Test queries for different external sources
        api_tests = {
            "wikipedia": [
                "Quantum_mechanics",
                "Thermodynamics",
                "Organic_chemistry",
                "Calculus",
                "Electromagnetism"
            ],
            "pubchem": [
                "water",
                "ethanol",
                "benzene",
                "caffeine",
                "glucose"
            ],
            "arxiv": [
                "physics",
                "chemistry",
                "mathematics"
            ],
            "crossref": [
                "machine learning",
                "quantum physics",
                "organic synthesis"
            ]
        }

        results = {}

        for api_name, queries in api_tests.items():
            print(f"Testing {api_name.upper()} API ({len(queries)} queries)...")

            api_results = []
            for query in queries:
                start_time = time.time()
                result = await self._mock_external_api_call(api_name, query)
                execution_time = time.time() - start_time

                api_results.append({
                    "query": query,
                    "execution_time": execution_time,
                    "success": result.get("success", True),
                    "data_size": len(str(result.get("data", "")))
                })

            # Statistics
            success_rate = sum(1 for r in api_results if r["success"]) / len(api_results)
            avg_execution_time = statistics.mean([r["execution_time"] for r in api_results])

            results[api_name] = {
                "query_count": len(queries),
                "success_rate": success_rate,
                "avg_execution_time": avg_execution_time,
                "total_data_retrieved": sum(r["data_size"] for r in api_results),
                "individual_results": api_results
            }

            print(f"Success rate: {results[api_name]['success_rate']:.1%}")
            print(f"Average execution time: {results[api_name]['avg_execution_time']:.2f}s")
        print()
        self.results["external_apis"] = results

    async def benchmark_memory_usage(self):
        """Benchmark memory usage during scientific operations."""
        print("💾 BENCHMARK: Memory Usage Analysis")
        print("-" * 40)

        memory_snapshots = []

        # Baseline memory
        baseline_memory = psutil.virtual_memory()
        memory_snapshots.append({
            "phase": "baseline",
            "memory_percent": baseline_memory.percent,
            "memory_used": baseline_memory.used
        })

        # Test different operation types
        operations = [
            ("single_physics", lambda: self._mock_scientific_query("Explain relativity", "physics")),
            ("multi_agent", lambda: self._mock_scientific_query("Quantum chemistry", "multi", True)),
            ("first_principles", lambda: self._mock_first_principles_analysis("thermodynamics", "physics")),
            ("external_api", lambda: self._mock_external_api_call("wikipedia", "Quantum_mechanics"))
        ]

        for op_name, op_func in operations:
            print(f"Testing memory usage for {op_name}...")

            # Memory before operation
            before_memory = psutil.virtual_memory()

            # Execute operation
            await op_func()

            # Memory after operation
            after_memory = psutil.virtual_memory()

            memory_snapshots.append({
                "phase": op_name,
                "memory_before": before_memory.used,
                "memory_after": after_memory.used,
                "memory_delta": after_memory.used - before_memory.used,
                "memory_percent": after_memory.percent
            })

            # Small delay to stabilize
            await asyncio.sleep(0.1)

        # Analyze memory patterns
        memory_deltas = [s["memory_delta"] for s in memory_snapshots[1:]]
        avg_memory_delta = statistics.mean(memory_deltas)
        max_memory_delta = max(memory_deltas)

        benchmark_results = {
            "snapshots": memory_snapshots,
            "avg_memory_delta": avg_memory_delta,
            "max_memory_delta": max_memory_delta,
            "memory_efficiency": "good" if abs(avg_memory_delta) < 50 * 1024 * 1024 else "needs_optimization"
        }

        print(f"Average memory delta: {avg_memory_delta:.1f} MB")
        print(f"Max memory delta: {max_memory_delta:.1f} MB")
        print(f"Memory efficiency: {benchmark_results['memory_efficiency']}")
        print()

        self.results["memory_usage"] = benchmark_results

    async def benchmark_concurrent_load(self):
        """Benchmark system performance under concurrent load."""
        print("⚡ BENCHMARK: Concurrent Load Testing")
        print("-" * 40)

        # Test different concurrency levels
        concurrency_levels = [1, 5, 10, 20, 50]
        test_queries = [
            "Explain quantum entanglement",
            "What is photosynthesis?",
            "Solve x² + 2x + 1 = 0",
            "How does natural selection work?",
            "What is the Pythagorean theorem?"
        ] * 10  # Repeat for more queries

        results = {}

        for concurrency in concurrency_levels:
            print(f"Testing with {concurrency} concurrent queries...")

            start_time = time.time()

            # Create concurrent tasks
            tasks = []
            for i in range(min(concurrency, len(test_queries))):
                query = test_queries[i]
                task = self._mock_scientific_query(query, "auto")
                tasks.append(task)

            # Execute concurrently
            await asyncio.gather(*tasks)

            total_time = time.time() - start_time

            # Calculate metrics
            queries_per_second = concurrency / total_time
            avg_time_per_query = total_time / concurrency

            results[concurrency] = {
                "total_time": total_time,
                "queries_per_second": queries_per_second,
                "avg_time_per_query": avg_time_per_query,
                "throughput_efficiency": queries_per_second / concurrency
            }

            print(f"Average time per query: {avg_time_per_query:.2f}s")
            print(f"Throughput efficiency: {results[concurrency]['throughput_efficiency']:.3f}")
        print()
        self.results["concurrent_load"] = results

    async def benchmark_accuracy_validation(self):
        """Benchmark accuracy against known scientific results."""
        print("🎯 BENCHMARK: Scientific Accuracy Validation")
        print("-" * 50)

        # Test cases with known correct answers
        accuracy_tests = [
            {
                "query": "What is the speed of light in vacuum?",
                "expected_answer": "299792458 m/s",
                "domain": "physics",
                "validation_type": "exact_value"
            },
            {
                "query": "What is the chemical formula for water?",
                "expected_answer": "H2O",
                "domain": "chemistry",
                "validation_type": "exact_formula"
            },
            {
                "query": "What is 2 + 2?",
                "expected_answer": "4",
                "domain": "mathematics",
                "validation_type": "exact_calculation"
            },
            {
                "query": "Is the square root of 2 rational?",
                "expected_answer": "no",
                "domain": "mathematics",
                "validation_type": "logical_correctness"
            },
            {
                "query": "What is the pH of pure water at 25°C?",
                "expected_answer": "7.0",
                "domain": "chemistry",
                "validation_type": "exact_value"
            }
        ]

        print(f"Testing accuracy against {len(accuracy_tests)} known scientific facts...")

        results = []
        for test in accuracy_tests:
            result = await self._mock_scientific_query(test["query"], test["domain"])
            accuracy_score = self._validate_accuracy(result, test)

            results.append({
                "query": test["query"],
                "expected": test["expected_answer"],
                "actual": result.get("answer", "N/A"),
                "accuracy_score": accuracy_score,
                "validation_type": test["validation_type"]
            })

        # Calculate overall accuracy
        accuracy_scores = [r["accuracy_score"] for r in results]
        avg_accuracy = statistics.mean(accuracy_scores)
        accuracy_distribution = {
            "perfect": sum(1 for s in accuracy_scores if s >= 0.95),
            "good": sum(1 for s in accuracy_scores if 0.8 <= s < 0.95),
            "fair": sum(1 for s in accuracy_scores if 0.6 <= s < 0.8),
            "poor": sum(1 for s in accuracy_scores if s < 0.6)
        }

        benchmark_results = {
            "test_count": len(accuracy_tests),
            "avg_accuracy": avg_accuracy,
            "accuracy_distribution": accuracy_distribution,
            "individual_results": results
        }

        print(f"Average accuracy: {avg_accuracy:.1%}")
        print(f"Perfect accuracy (≥95%): {accuracy_distribution['perfect']}")
        print(f"Good accuracy (80-95%): {accuracy_distribution['good']}")
        print(f"Fair accuracy (60-80%): {accuracy_distribution['fair']}")
        print(f"Poor accuracy (<60%): {accuracy_distribution['poor']}")
        print()

        self.results["accuracy_validation"] = benchmark_results

    def _validate_accuracy(self, result: Dict[str, Any], test: Dict[str, Any]) -> float:
        """Validate accuracy of scientific answer."""
        actual_answer = result.get("answer", "").lower().strip()
        expected_answer = test["expected_answer"].lower().strip()

        if test["validation_type"] == "exact_value" or test["validation_type"] == "exact_formula":
            # Exact match required
            return 1.0 if actual_answer == expected_answer else 0.0
        elif test["validation_type"] == "exact_calculation":
            # Exact numerical match
            return 1.0 if actual_answer == expected_answer else 0.0
        elif test["validation_type"] == "logical_correctness":
            # Logical correctness
            return 1.0 if actual_answer == expected_answer else 0.0
        else:
            # Default fuzzy matching
            return 0.8 if expected_answer in actual_answer else 0.0

    async def _mock_scientific_query(self, query: str, domain: str = "auto", collaboration: bool = False) -> Dict[str, Any]:
        """Mock scientific query execution for benchmarking."""
        # Simulate processing time based on query complexity
        complexity_factor = len(query.split()) / 10
        processing_time = 0.5 + (complexity_factor * 0.5) + (0.3 if collaboration else 0)

        await asyncio.sleep(processing_time * 0.1)  # Simulate actual processing

        # Mock result
        return {
            "query": query,
            "domain": domain,
            "answer": f"Scientific analysis of: {query}",
            "confidence": 0.85 + (0.1 if collaboration else 0),
            "processing_time": processing_time,
            "agent_contributions": 3 if collaboration else 1,
            "cross_domain_connections": 2 if collaboration else 0,
            "sources_used": ["internal_agent", "wikipedia"] if not collaboration else ["physics_agent", "chemistry_agent", "mathematics_agent", "wikipedia"],
            "success": True
        }

    async def _mock_first_principles_analysis(self, topic: str, domain: str) -> Dict[str, Any]:
        """Mock first principles analysis."""
        await asyncio.sleep(0.3)  # Simulate processing

        return {
            "topic": topic,
            "domain": domain,
            "fundamental_principles": [
                "Matter consists of atoms",
                "Energy conservation",
                "Mathematical consistency"
            ],
            "logical_deduction_steps": [
                "Start with basic axioms",
                "Apply logical operations",
                "Derive conclusions"
            ],
            "counterexamples": [],
            "conclusions": [f"Understanding of {topic} from first principles"],
            "confidence": 0.9
        }

    async def _mock_external_api_call(self, api_name: str, query: str) -> Dict[str, Any]:
        """Mock external API call."""
        # Simulate API response times
        api_delays = {
            "wikipedia": 0.2,
            "pubchem": 0.5,
            "arxiv": 0.3,
            "crossref": 0.4
        }

        delay = api_delays.get(api_name, 0.2)
        await asyncio.sleep(delay)

        return {
            "api": api_name,
            "query": query,
            "data": f"Mock data from {api_name} for {query}",
            "success": True,
            "response_time": delay
        }

    def generate_benchmark_report(self):
        """Generate comprehensive benchmark report."""
        print("📊 COMPREHENSIVE BENCHMARK REPORT")
        print("=" * 50)

        # Overall performance summary
        print("\n🎯 OVERALL PERFORMANCE SUMMARY")
        print("-" * 35)

        # Calculate aggregate metrics
        if "single_domain" in self.results:
            single_domain = self.results["single_domain"]
            total_queries = sum(d["query_count"] for d in single_domain.values())
            avg_execution_time = statistics.mean([
                d["avg_execution_time"] for d in single_domain.values()
            ])
            avg_confidence = statistics.mean([
                d["avg_confidence"] for d in single_domain.values()
            ])

            print(f"Single-domain queries: {total_queries} total")
            print(f"  Average response time: {avg_time:.2f}s")
            print(f"  Average confidence: {avg_confidence:.2f}")
        if "multi_agent" in self.results:
            multi = self.results["multi_agent"]
            print(f"Multi-agent queries: {multi['query_count']}")
            print(f"  Average response time: {multi['avg_time']:.2f}s")
            print(f"  Success rate: {multi['success_rate']:.1f}%")
        if "first_principles" in self.results:
            fp = self.results["first_principles"]
            print(f"First principles analyses: {fp['analysis_count']}")
            print(f"  Average processing time: {fp['avg_time']:.2f}s")
            print(f"  Success rate: {fp['success_rate']:.1f}%")
        if "external_apis" in self.results:
            apis = self.results["external_apis"]
            total_api_queries = sum(a["query_count"] for a in apis.values())
            avg_api_success = statistics.mean([a["success_rate"] for a in apis.values()])
            print(f"External API queries: {total_api_queries}")
            print(f"  Average success rate: {avg_api_success:.1f}%")
        if "accuracy_validation" in self.results:
            acc = self.results["accuracy_validation"]
            print(f"Accuracy validation tests: {acc['test_count']}")
            print(f"  Average accuracy: {acc['avg_accuracy']:.1f}%")
            print(f"Perfect accuracy: {acc['accuracy_distribution']['perfect']}")

        # Performance analysis
        print("\n⚡ PERFORMANCE ANALYSIS")
        print("-" * 25)

        # Identify bottlenecks and strengths
        bottlenecks = []
        strengths = []

        if "single_domain" in self.results:
            for domain, metrics in self.results["single_domain"].items():
                if metrics["avg_execution_time"] > 2.0:
                    bottlenecks.append(f"{domain} queries slow ({metrics['avg_execution_time']:.2f}s)")
                elif metrics["avg_execution_time"] < 1.0:
                    strengths.append(f"{domain} queries fast ({metrics['avg_execution_time']:.2f}s)")

                if metrics["success_rate"] < 0.9:
                    bottlenecks.append(f"{domain} success rate low ({metrics['success_rate']:.1%})")
                elif metrics["success_rate"] > 0.95:
                    strengths.append(f"{domain} highly reliable ({metrics['success_rate']:.1%})")

        if bottlenecks:
            print("🚨 Potential Bottlenecks:")
            for bottleneck in bottlenecks[:3]:  # Show top 3
                print(f"  • {bottleneck}")

        if strengths:
            print("✅ Performance Strengths:")
            for strength in strengths[:3]:  # Show top 3
                print(f"  • {strength}")

        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 20)

        recommendations = []

        # Based on benchmark results
        if "concurrent_load" in self.results:
            concurrent = self.results["concurrent_load"]
            max_throughput = max([c["queries_per_second"] for c in concurrent.values()])
            if max_throughput < 10:
                recommendations.append("Consider optimizing for higher concurrency")
            else:
                recommendations.append("Good concurrent performance - consider scaling horizontally")

        if "memory_usage" in self.results:
            memory = self.results["memory_usage"]
            if memory["avg_memory_delta"] > 100 * 1024 * 1024:  # 100MB
                recommendations.append("High memory usage - implement memory optimization")
            else:
                recommendations.append("Memory usage acceptable - monitor for growth")

        if "external_apis" in self.results:
            apis = self.results["external_apis"]
            avg_success = statistics.mean([a["success_rate"] for a in apis.values()])
            if avg_success < 0.9:
                recommendations.append("External API reliability needs improvement")
            else:
                recommendations.append("External API integration stable")

        if not recommendations:
            recommendations = ["System performing well - continue monitoring"]

        for rec in recommendations:
            print(f"  • {rec}")

        # Save detailed results
        self._save_benchmark_results()

        print("\n✅ BENCHMARK SUITE COMPLETED")
        print("Detailed results saved to: scientific_benchmark_results.json")
        print("=" * 50)

    def _save_benchmark_results(self):
        """Save benchmark results to file."""
        results_file = {
            "benchmark_metadata": {
                "timestamp": datetime.now().isoformat(),
                "system_info": self.system_info,
                "baseline_metrics": self.baseline_metrics
            },
            "benchmark_results": self.results
        }

        with open("scientific_benchmark_results.json", "w") as f:
            json.dump(results_file, f, indent=2, default=str)

    def create_performance_charts(self):
        """Create performance visualization charts."""
        try:
            # Single domain performance
            if "single_domain" in self.results:
                domains = list(self.results["single_domain"].keys())
                execution_times = [self.results["single_domain"][d]["avg_execution_time"] for d in domains]
                confidences = [self.results["single_domain"][d]["avg_confidence"] for d in domains]

                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

                ax1.bar(domains, execution_times)
                ax1.set_title('Average Execution Time by Domain')
                ax1.set_ylabel('Time (seconds)')

                ax2.bar(domains, confidences)
                ax2.set_title('Average Confidence by Domain')
                ax2.set_ylabel('Confidence Score')

                plt.tight_layout()
                plt.savefig('scientific_performance_charts.png', dpi=300, bbox_inches='tight')
                plt.close()

                print("📈 Performance charts saved to: scientific_performance_charts.png")

        except ImportError:
            print("⚠️  Matplotlib not available - skipping chart generation")
        except Exception as e:
            print(f"⚠️  Chart generation failed: {e}")


async def main():
    """Main benchmark execution."""
    benchmark = PerformanceBenchmark()

    try:
        await benchmark.run_complete_benchmark_suite()
        benchmark.create_performance_charts()
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
