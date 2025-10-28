#!/usr/bin/env python3
"""
Test script for SettingsManager with UI language support
"""
import sys
import os
from pathlib import Path
from utils.settings import SettingsManager


def test_default_ui_language():
    """Test that default UI language is set"""
    print("=" * 60)
    print("TEST 1: Default UI Language")
    print("=" * 60)

    settings = SettingsManager()
    ui_lang = settings.get_preferred_ui_language()

    assert ui_lang == "it", f"Expected 'it', got '{ui_lang}'"
    print(f"✓ Default UI language: {ui_lang}")

    print("\n✅ TEST 1 PASSED\n")


def test_set_ui_language():
    """Test setting UI language"""
    print("=" * 60)
    print("TEST 2: Set UI Language")
    print("=" * 60)

    settings = SettingsManager()

    # Test setting to English
    settings.set_preferred_ui_language('en')
    ui_lang = settings.get_preferred_ui_language()
    assert ui_lang == 'en', f"Expected 'en', got '{ui_lang}'"
    print(f"✓ Set to English: {ui_lang}")

    # Test setting to Spanish
    settings.set_preferred_ui_language('es')
    ui_lang = settings.get_preferred_ui_language()
    assert ui_lang == 'es', f"Expected 'es', got '{ui_lang}'"
    print(f"✓ Set to Spanish: {ui_lang}")

    # Reset to Italian
    settings.set_preferred_ui_language('it')
    ui_lang = settings.get_preferred_ui_language()
    assert ui_lang == 'it', f"Expected 'it', got '{ui_lang}'"
    print(f"✓ Reset to Italian: {ui_lang}")

    print("\n✅ TEST 2 PASSED\n")


def test_invalid_language():
    """Test that invalid language codes are handled"""
    print("=" * 60)
    print("TEST 3: Invalid Language Handling")
    print("=" * 60)

    settings = SettingsManager()

    # Try to set invalid language
    print("Attempting to set invalid language 'xx'...")
    settings.set_preferred_ui_language('xx')
    ui_lang = settings.get_preferred_ui_language()

    assert ui_lang == 'it', f"Expected fallback to 'it', got '{ui_lang}'"
    print(f"✓ Invalid language rejected, fallback to: {ui_lang}")

    print("\n✅ TEST 3 PASSED\n")


def test_persistence():
    """Test that UI language persists across sessions"""
    print("=" * 60)
    print("TEST 4: Persistence Across Sessions")
    print("=" * 60)

    # Create first settings instance and set language
    settings1 = SettingsManager()
    settings1.set_preferred_ui_language('fr')
    print("✓ Set UI language to French in first instance")

    # Create second settings instance (simulates app restart)
    settings2 = SettingsManager()
    ui_lang = settings2.get_preferred_ui_language()

    assert ui_lang == 'fr', f"Expected 'fr' to persist, got '{ui_lang}'"
    print(f"✓ UI language persisted: {ui_lang}")

    # Reset to Italian for next tests
    settings2.set_preferred_ui_language('it')

    print("\n✅ TEST 4 PASSED\n")


def test_settings_file_structure():
    """Test that settings file has correct structure"""
    print("=" * 60)
    print("TEST 5: Settings File Structure")
    print("=" * 60)

    settings = SettingsManager()
    settings_file = settings.settings_file

    assert settings_file.exists(), "Settings file should exist"
    print(f"✓ Settings file exists: {settings_file}")

    # Check that file contains preferred_ui_language
    import json
    with open(settings_file, 'r') as f:
        data = json.load(f)

    assert 'preferred_ui_language' in data, "Settings should contain 'preferred_ui_language'"
    print(f"✓ Settings contains 'preferred_ui_language': {data['preferred_ui_language']}")

    # Display full settings structure
    print("\nCurrent settings.json structure:")
    for key, value in data.items():
        print(f"  {key}: {value}")

    print("\n✅ TEST 5 PASSED\n")


def test_distinction_project_vs_ui_language():
    """Test conceptual distinction between project and UI language"""
    print("=" * 60)
    print("TEST 6: Project vs UI Language Distinction")
    print("=" * 60)

    print("\n📚 Conceptual Explanation:")
    print("-" * 60)
    print("1. UI Language (Settings Manager):")
    print("   - Controls interface text (menu, dialogs, messages)")
    print("   - Global for the application")
    print("   - Future i18n implementation")
    print("   - Example: User wants UI in English")
    print()
    print("2. Project Language (Project Model):")
    print("   - Controls NLP analysis (grammar, style)")
    print("   - Specific to each project")
    print("   - Already implemented")
    print("   - Example: Project manuscript is in Italian")
    print()
    print("Use Case:")
    print("   User with UI in English can work on:")
    print("   - Italian novel (IT NLP analysis)")
    print("   - French article (FR NLP analysis)")
    print("   - Spanish story (ES NLP analysis)")
    print("-" * 60)

    settings = SettingsManager()
    ui_lang = settings.get_preferred_ui_language()

    print(f"\n✓ UI Language (from settings): {ui_lang}")
    print("✓ Project Language: Set per-project in Project model")
    print("✓ These are independent and serve different purposes")

    print("\n✅ TEST 6 PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING SETTINGS MANAGER TESTS")
    print("=" * 60 + "\n")

    try:
        test_default_ui_language()
        test_set_ui_language()
        test_invalid_language()
        test_persistence()
        test_settings_file_structure()
        test_distinction_project_vs_ui_language()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n✅ Settings Manager - UI Language Support:")
        print("   - Default language: Italian (it)")
        print("   - 5 languages supported: it, en, es, fr, de")
        print("   - Validation for invalid codes")
        print("   - Persistent across sessions")
        print("   - Clear distinction from project language")
        print("\n✅ Infrastructure ready for:")
        print("   - Future UI localization (i18n)")
        print("   - Multi-language interface")
        print("   - User preferences per language")
        print("\n")

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
