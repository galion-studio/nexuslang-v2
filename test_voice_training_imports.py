#!/usr/bin/env python3
"""
Test script for Voice-to-Voice AI Training System imports and basic functionality
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all voice training components can be imported"""
    print("🧪 Testing Voice-to-Voice AI Training System imports...")

    tests = [
        ("Voice Training Pipeline", "ai.training.voice_training_pipeline", "VoiceTrainingPipeline"),
        ("Voice Data Collector", "ai.training.voice_data_collector", "VoiceDataCollector"),
        ("Custom Voice Model", "ai.training.custom_voice_model", "CustomVoiceModelTrainer"),
        ("Voice Synthesis", "ai.training.voice_synthesis", "VoiceSynthesizer"),
        ("Voice Agent Orchestrator", "ai.training.voice_agent_orchestrator", "VoiceAgentOrchestrator"),
        ("Video Voice Pipeline", "ai.training.video_voice_pipeline", "VideoVoicePipeline"),
        ("Platform Integration", "ai.training.voice_platform_integration", "VoicePlatformIntegration"),
        ("Voice Training API", "v2.backend.api.voice_training_api", "router"),
    ]

    passed = 0
    failed = 0

    for test_name, module_name, class_name in tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            obj = getattr(module, class_name)
            print(f"✅ {test_name}: Imported successfully")
            passed += 1
        except ImportError as e:
            print(f"❌ {test_name}: Import failed - {e}")
            failed += 1
        except AttributeError as e:
            print(f"❌ {test_name}: Attribute not found - {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error - {e}")
            failed += 1

    print(f"\n📊 Import Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All voice training components imported successfully!")
        return True
    else:
        print("⚠️  Some components failed to import. Check dependencies.")
        return False

def test_basic_functionality():
    """Test basic functionality of voice training components"""
    print("\n🧪 Testing basic functionality...")

    try:
        # Test VoiceDataCollector initialization
        from ai.training.voice_data_collector import VoiceDataCollector

        config = {
            'data_directory': '/tmp/voice_test',
            'max_sessions': 10
        }

        collector = VoiceDataCollector(config)
        print("✅ VoiceDataCollector initialized successfully")

        # Test VoiceSynthesizer initialization
        from ai.training.voice_synthesis import VoiceSynthesizer

        synth_config = {
            'voices_directory': '/tmp/voices_test'
        }

        synthesizer = VoiceSynthesizer(synth_config)
        print("✅ VoiceSynthesizer initialized successfully")

        # Test VoiceAgentOrchestrator initialization
        from ai.training.voice_agent_orchestrator import VoiceAgentOrchestrator

        agent_config = {
            'agent_orchestration': {}
        }

        orchestrator = VoiceAgentOrchestrator(agent_config)
        print("✅ VoiceAgentOrchestrator initialized successfully")

        print("🎉 Basic functionality tests passed!")
        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_platform_integration():
    """Test platform integration components"""
    print("\n🧪 Testing platform integration...")

    try:
        from ai.training.voice_platform_integration import VoicePlatformIntegration

        integration = VoicePlatformIntegration({
            'voice_training': {},
            'data_collection': {},
            'model_training': {},
            'voice_synthesis': {},
            'agent_orchestration': {},
            'video_processing': {}
        })

        print("✅ VoicePlatformIntegration initialized successfully")

        # Test getting platform configs
        galion_app_config = integration.get_platform_voice_config("galion_app")
        print("✅ Galion App config retrieved")

        developer_config = integration.get_platform_voice_config("developer_platform")
        print("✅ Developer Platform config retrieved")

        studio_config = integration.get_platform_voice_config("galion_studio")
        print("✅ Galion Studio config retrieved")

        print("🎉 Platform integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Platform integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎤 Voice-to-Voice AI Training System - Test Suite")
    print("=" * 60)

    # Test imports
    imports_ok = test_imports()

    if not imports_ok:
        print("\n❌ Import tests failed. Cannot continue with functionality tests.")
        return False

    # Test basic functionality
    functionality_ok = test_basic_functionality()

    # Test platform integration
    integration_ok = test_platform_integration()

    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")

    all_passed = imports_ok and functionality_ok and integration_ok

    if all_passed:
        print("🎉 ALL TESTS PASSED! Voice training system is ready!")
        print("\n🚀 Next steps:")
        print("1. Deploy with: docker-compose up -d")
        print("2. Test API: curl http://localhost:8010/api/voice-training/health")
        print("3. Start collecting voice data")
        print("4. Train your first custom voice model!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
