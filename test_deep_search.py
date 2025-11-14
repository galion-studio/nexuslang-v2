#!/usr/bin/env python3
"""
Test script for Deep Search integration
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'v2', 'backend'))

def test_deep_search():
    """Test the deep search system integration"""
    try:
        print("Testing Deep Search System Integration")
        print("=" * 50)

        # Test 1: Import components (basic structure)
        print("Testing basic imports...")
        from services.deep_search.agents import PlannerAgent, SearcherAgent, AnalyzerAgent
        from services.deep_search.workflow import StateMachine
        from services.deep_search.validation import FactChecker
        from services.deep_search.personas import PersonaManager
        print("[OK] Core components imported successfully")

        # Test 2: Test personas (doesn't require external deps)
        print("\nTesting Persona System...")
        persona_manager = PersonaManager()
        personas = persona_manager.get_available_personas()
        print(f"[OK] Persona manager initialized with {len(personas)} personas:")
        for name, info in personas.items():
            print(f"   - {name}: {info['description']}")

        # Test 3: Test workflow state machine
        print("\nTesting State Machine...")
        state_machine = StateMachine()
        status = state_machine.get_workflow_stats()
        print(f"[OK] State machine initialized: {status['current_state']}")

        # Test 4: Test fact checker
        print("\nTesting Fact Checker...")
        fact_checker = FactChecker()
        print("[OK] Fact checker initialized")

        # Test 5: Test agent classes (basic structure)
        print("\nTesting Agent Classes...")
        planner = PlannerAgent()
        print(f"[OK] Planner agent initialized: {planner.name}")

        searcher = SearcherAgent()
        print(f"[OK] Searcher agent initialized: {searcher.name}")

        analyzer = AnalyzerAgent()
        print(f"[OK] Analyzer agent initialized: {analyzer.name}")

        # Note: Semantic memory and orchestrator require additional dependencies
        print("\nNote: Semantic memory and full orchestrator require sentence-transformers dependency")

        # Note: AgentOrchestrator requires async initialization, so we'll skip it for now
        print("\nNote: AgentOrchestrator requires async setup - will be tested in full integration")

        print("\nSUCCESS: All Deep Search components initialized successfully!")
        print("=" * 50)
        print("Deep Search system is ready for integration testing!")
        return True

    except Exception as e:
        print(f"\nFAILED: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_deep_search()
    sys.exit(0 if success else 1)
