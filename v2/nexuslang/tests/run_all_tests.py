"""
Run all NexusLang v2 tests
Comprehensive test runner for the entire system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_test_file(test_file):
    """Run a test file and return success status"""
    print(f"\n{'=' * 60}")
    print(f"Running: {test_file}")
    print('=' * 60)
    
    try:
        # Import and run the test module
        module_name = test_file.replace('.py', '').replace('/', '.')
        exec(open(os.path.join(os.path.dirname(__file__), test_file)).read())
        return True
    except Exception as e:
        print(f"\n❌ {test_file} FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all test files"""
    print("╔" + "=" * 58 + "╗")
    print("║" + "  NexusLang v2 - Comprehensive Test Suite".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    test_files = [
        'test_lexer.py',
        'test_interpreter.py',
    ]
    
    results = {}
    
    for test_file in test_files:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            results[test_file] = run_test_file(test_file)
        else:
            print(f"⚠️  Skipping {test_file} (not found)")
            results[test_file] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_file, result in results.items():
        if result is True:
            print(f"✅ {test_file}")
        elif result is False:
            print(f"❌ {test_file}")
        else:
            print(f"⏭️  {test_file} (skipped)")
    
    print("=" * 60)
    print(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("=" * 60)
    
    if failed > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        print("\n🎉 NexusLang v2 is ready for launch!")


if __name__ == "__main__":
    main()

