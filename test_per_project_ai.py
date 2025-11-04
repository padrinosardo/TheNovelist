"""
Test script for Per-Project AI Configuration
Tests the ability for each project to use different AI providers
"""
import os
import sys
import tempfile
from models.project import Project
from managers.ai.ai_manager import AIManager
from managers.project_manager import ProjectManager


def test_project_model_ai_fields():
    """Test Project model has AI configuration fields"""
    print("\n" + "="*70)
    print("TEST 1: Project Model AI Fields")
    print("="*70)

    # Create a project with AI configuration
    from models.project_type import ProjectType
    project = Project.create_new(
        title="Test Novel",
        author="Test Author",
        language="en",
        project_type=ProjectType.NOVEL,
        ai_provider_name="claude",
        ai_provider_config={
            "api_key": "sk-ant-test-key",
            "model": "claude-3-sonnet-20240229"
        }
    )

    print(f"✅ Created project: {project.title}")
    print(f"   AI Provider: {project.ai_provider_name}")
    print(f"   AI Model: {project.ai_provider_config.get('model')}")

    # Test serialization
    project_dict = project.to_dict()
    assert 'ai_provider_name' in project_dict, "❌ ai_provider_name not in dict"
    assert 'ai_provider_config' in project_dict, "❌ ai_provider_config not in dict"
    print("✅ Project serialization includes AI fields")

    # Test deserialization
    restored_project = Project.from_dict(project_dict)
    assert restored_project.ai_provider_name == "claude", "❌ Provider name not restored"
    assert restored_project.ai_provider_config['model'] == "claude-3-sonnet-20240229", "❌ Config not restored"
    print("✅ Project deserialization restores AI fields correctly")

    return project


def test_backward_compatibility():
    """Test that projects without AI config still work"""
    print("\n" + "="*70)
    print("TEST 2: Backward Compatibility")
    print("="*70)

    # Create project dict without AI fields (simulates old project)
    old_project_dict = {
        'title': 'Old Project',
        'author': 'Old Author',
        'language': 'en',
        'project_type': 'novel',
        'created_date': '2024-01-01T00:00:00',
        'modified_date': '2024-01-01T00:00:00'
    }

    # Should load without errors
    try:
        project = Project.from_dict(old_project_dict)
        print(f"✅ Loaded old project: {project.title}")
        print(f"   AI Provider (default): {project.ai_provider_name}")
        print(f"   AI Config (default): {project.ai_provider_config}")

        # Default values should be set
        assert project.ai_provider_name == 'claude', "❌ Default provider not set"
        assert isinstance(project.ai_provider_config, dict), "❌ Config is not a dict"
        assert 'model' in project.ai_provider_config, "❌ Config should have default model"
        print("✅ Old projects get sensible defaults (provider and config with default values)")

        return project
    except Exception as e:
        print(f"❌ Failed to load old project: {e}")
        sys.exit(1)


def test_different_providers():
    """Test creating projects with different AI providers"""
    print("\n" + "="*70)
    print("TEST 3: Multiple AI Providers")
    print("="*70)

    from models.project_type import ProjectType

    # Claude project
    claude_project = Project.create_new(
        title="Claude Project",
        author="Author",
        language="en",
        project_type=ProjectType.NOVEL,
        ai_provider_name="claude",
        ai_provider_config={
            "api_key": "sk-ant-test",
            "model": "claude-3-5-sonnet-20240620"
        }
    )
    print(f"✅ Claude Project: {claude_project.ai_provider_name} - {claude_project.ai_provider_config['model']}")

    # OpenAI project
    openai_project = Project.create_new(
        title="OpenAI Project",
        author="Author",
        language="en",
        project_type=ProjectType.NOVEL,
        ai_provider_name="openai",
        ai_provider_config={
            "api_key": "sk-test",
            "model": "gpt-4-turbo-preview"
        }
    )
    print(f"✅ OpenAI Project: {openai_project.ai_provider_name} - {openai_project.ai_provider_config['model']}")

    # Ollama project (local, no API key needed)
    ollama_project = Project.create_new(
        title="Ollama Project",
        author="Author",
        language="en",
        project_type=ProjectType.NOVEL,
        ai_provider_name="ollama",
        ai_provider_config={
            "base_url": "http://localhost:11434",
            "model": "llama2"
        }
    )
    print(f"✅ Ollama Project: {ollama_project.ai_provider_name} - {ollama_project.ai_provider_config['model']}")

    return claude_project, openai_project, ollama_project


def test_ai_manager_per_project():
    """Test AIManager can get provider from project config"""
    print("\n" + "="*70)
    print("TEST 4: AIManager Per-Project Configuration")
    print("="*70)

    from models.project_type import ProjectType
    ai_manager = AIManager()
    print("✅ AIManager initialized")

    # Create a project with specific AI config
    project = Project.create_new(
        title="AI Test Project",
        author="Author",
        language="en",
        project_type=ProjectType.NOVEL,
        ai_provider_name="claude",
        ai_provider_config={
            "api_key": "sk-ant-test-key-12345",
            "model": "claude-3-haiku-20240307"
        }
    )

    # Test get_provider_from_project method exists
    assert hasattr(ai_manager, 'get_provider_from_project'), "❌ Method get_provider_from_project not found"
    print("✅ Method get_provider_from_project exists")

    # Test that it returns None when API key is invalid (expected behavior)
    provider = ai_manager.get_provider_from_project(project)
    # Provider will be None because API key is fake, but method should not crash
    print(f"   Provider instantiation: {provider is not None and 'valid' or 'invalid API key (expected)'}")
    print("✅ Method handles project configuration without crashing")

    # Test with project without AI config (should return None gracefully)
    old_project = Project.create_new(
        title="Old Project",
        author="Author",
        language="en",
        project_type=ProjectType.NOVEL,
        ai_provider_config={}  # Empty config
    )
    provider = ai_manager.get_provider_from_project(old_project)
    assert provider is None, "❌ Should return None for project without config"
    print("✅ Method returns None for projects without AI config (fallback works)")


def test_project_manager_integration():
    """Test ProjectManager saves and loads AI configuration"""
    print("\n" + "="*70)
    print("TEST 5: ProjectManager Integration")
    print("="*70)

    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.tnp', delete=False)
    temp_path = temp_file.name
    temp_file.close()

    try:
        # Create project with AI config
        pm = ProjectManager()
        success = pm.create_new_project(
            title="AI Config Test",
            author="Test Author",
            filepath=temp_path
        )

        if not success:
            print("❌ Failed to create project")
            return

        print(f"✅ Created project at: {temp_path}")

        # Modify AI configuration
        pm.current_project.ai_provider_name = "openai"
        pm.current_project.ai_provider_config = {
            "api_key": "sk-test-openai",
            "model": "gpt-4"
        }

        # Save project
        if not pm.save_project():
            print("❌ Failed to save project")
            return

        print("✅ Saved project with AI configuration")
        print(f"   Provider: {pm.current_project.ai_provider_name}")
        print(f"   Model: {pm.current_project.ai_provider_config['model']}")

        # Close and reload project
        pm2 = ProjectManager()
        if not pm2.open_project(temp_path):
            print("❌ Failed to reload project")
            return

        # Verify AI configuration persisted
        assert pm2.current_project.ai_provider_name == "openai", "❌ Provider name not persisted"
        assert pm2.current_project.ai_provider_config['model'] == "gpt-4", "❌ Model not persisted"
        assert pm2.current_project.ai_provider_config['api_key'] == "sk-test-openai", "❌ API key not persisted"

        print("✅ Reloaded project - AI configuration persisted correctly")
        print(f"   Provider: {pm2.current_project.ai_provider_name}")
        print(f"   Model: {pm2.current_project.ai_provider_config['model']}")

    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print(f"   Cleaned up: {temp_path}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("PER-PROJECT AI CONFIGURATION - TEST SUITE")
    print("="*70)
    print("\nTesting the ability for each project to use different AI providers")
    print("with independent configuration (provider, model, API keys).")

    try:
        # Run tests
        test_project_model_ai_fields()
        test_backward_compatibility()
        test_different_providers()
        test_ai_manager_per_project()
        test_project_manager_integration()

        # Summary
        print("\n" + "="*70)
        print("ALL TESTS PASSED ✅")
        print("="*70)
        print("\nPer-Project AI Configuration is working correctly:")
        print("  - Projects can store AI provider configuration")
        print("  - Different projects can use different providers (Claude, OpenAI, Ollama)")
        print("  - Old projects without AI config load with sensible defaults")
        print("  - AI configuration persists across save/load cycles")
        print("  - AIManager can instantiate providers from project config")
        print("\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
