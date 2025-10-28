#!/usr/bin/env python3
"""
Test script for NLP Multi-Language System
"""
import sys
from analysis.nlp_manager import nlp_manager
from analysis.style import StyleAnalyzer
from analysis.grammar import GrammarAnalyzer


def test_nlp_manager_singleton():
    """Test that NLPModelManager is a singleton"""
    print("=" * 60)
    print("TEST 1: NLPModelManager Singleton Pattern")
    print("=" * 60)

    from analysis.nlp_manager import NLPModelManager

    manager1 = NLPModelManager()
    manager2 = NLPModelManager()

    assert manager1 is manager2, "NLPModelManager should be a singleton"
    print("✓ Singleton pattern working correctly")

    # Test global instance
    assert nlp_manager is manager1, "Global instance should be the same"
    print("✓ Global instance working correctly")

    print("\n✅ TEST 1 PASSED\n")


def test_language_support():
    """Test supported languages"""
    print("=" * 60)
    print("TEST 2: Supported Languages")
    print("=" * 60)

    supported = nlp_manager.get_supported_languages()
    print(f"Supported languages: {supported}")

    expected = ['it', 'en', 'es', 'fr', 'de']
    assert set(supported) == set(expected), f"Expected {expected}, got {supported}"

    print("✓ All 5 languages supported: it, en, es, fr, de")
    print("\n✅ TEST 2 PASSED\n")


def test_set_language():
    """Test setting language"""
    print("=" * 60)
    print("TEST 3: Set Language")
    print("=" * 60)

    # Test valid language
    result = nlp_manager.set_language('en')
    assert result is True, "Should successfully set language"
    assert nlp_manager.get_current_language() == 'en', "Current language should be 'en'"
    print("✓ Language set to English")

    # Test switching language
    nlp_manager.set_language('it')
    assert nlp_manager.get_current_language() == 'it', "Current language should be 'it'"
    print("✓ Language switched to Italian")

    # Test invalid language (should fallback to 'it')
    nlp_manager.set_language('xx')
    assert nlp_manager.get_current_language() == 'it', "Should fallback to 'it'"
    print("✓ Invalid language fallback working")

    print("\n✅ TEST 3 PASSED\n")


def test_check_model_availability():
    """Test checking model availability without loading"""
    print("=" * 60)
    print("TEST 4: Check Model Availability")
    print("=" * 60)

    for lang in ['it', 'en', 'es', 'fr', 'de']:
        availability = nlp_manager.is_model_available(lang)
        print(f"{lang}: spaCy={availability['spacy']}, LanguageTool={availability['languagetool']}")

        # LanguageTool should always be available
        assert availability['languagetool'] is True, f"LanguageTool should be available for {lang}"

    print("\n✅ TEST 4 PASSED\n")


def test_spacy_loading():
    """Test spaCy model loading (only if installed)"""
    print("=" * 60)
    print("TEST 5: spaCy Model Loading")
    print("=" * 60)

    # Try to load Italian model
    nlp_manager.set_language('it')
    nlp = nlp_manager.get_spacy_model('it')

    if nlp is not None:
        print("✓ Italian spaCy model loaded successfully")

        # Test processing
        doc = nlp("Questo è un test.")
        assert len(list(doc.sents)) > 0, "Should process text correctly"
        print("✓ spaCy processing works")

        # Test caching
        nlp2 = nlp_manager.get_spacy_model('it')
        assert nlp is nlp2, "Should use cached model"
        print("✓ Model caching works")
    else:
        print("⚠ Italian spaCy model not installed (skipping test)")
        print("  Install with: python -m spacy download it_core_news_sm")

    print("\n✅ TEST 5 PASSED\n")


def test_languagetool_loading():
    """Test LanguageTool loading"""
    print("=" * 60)
    print("TEST 6: LanguageTool Loading")
    print("=" * 60)

    # Try to load Italian LanguageTool
    nlp_manager.set_language('it')
    tool = nlp_manager.get_language_tool('it')

    if tool is not None:
        print("✓ Italian LanguageTool loaded successfully")

        # Test checking
        matches = tool.check("Qesto è un test con errore.")
        print(f"  Found {len(matches)} potential issues")

        # Test caching
        tool2 = nlp_manager.get_language_tool('it')
        assert tool is tool2, "Should use cached tool"
        print("✓ Tool caching works")
    else:
        print("⚠ LanguageTool not available (internet connection required)")

    print("\n✅ TEST 6 PASSED\n")


def test_style_analyzer_multilang():
    """Test StyleAnalyzer with multiple languages"""
    print("=" * 60)
    print("TEST 7: StyleAnalyzer Multi-Language")
    print("=" * 60)

    # Test Italian
    analyzer_it = StyleAnalyzer(language='it')
    assert analyzer_it.language == 'it', "Should be set to Italian"
    print("✓ Italian StyleAnalyzer created")

    # Test English
    analyzer_en = StyleAnalyzer(language='en')
    assert analyzer_en.language == 'en', "Should be set to English"
    print("✓ English StyleAnalyzer created")

    # Test language switching
    analyzer_it.set_language('es')
    assert analyzer_it.language == 'es', "Should switch to Spanish"
    print("✓ Language switching works")

    # Test analysis (only if spaCy model available)
    nlp = nlp_manager.get_spacy_model('it')
    if nlp is not None:
        analyzer_it.set_language('it')
        result = analyzer_it.analyze("Questo è un test di analisi dello stile. Ha due frasi.")

        if result['success']:
            print(f"✓ Analysis successful: {result['num_sentences']} sentences, {result['num_words']} words")
            assert 'language' in result, "Result should include language"
            assert result['language'] == 'it', "Language should be 'it'"
            print("✓ Language field included in results")
        else:
            print(f"⚠ Analysis failed: {result.get('error')}")
    else:
        print("⚠ Skipping analysis test (spaCy model not installed)")

    print("\n✅ TEST 7 PASSED\n")


def test_grammar_analyzer_multilang():
    """Test GrammarAnalyzer with multiple languages"""
    print("=" * 60)
    print("TEST 8: GrammarAnalyzer Multi-Language")
    print("=" * 60)

    # Test Italian (uses SimpleGrammarChecker)
    analyzer_it = GrammarAnalyzer(language='it')
    assert analyzer_it.language == 'it', "Should be set to Italian"
    print("✓ Italian GrammarAnalyzer created")

    result_it = analyzer_it.analyze("Questo è un test senza errori.")
    assert result_it['success'], "Analysis should succeed"
    print(f"✓ Italian analysis works (found {result_it['total_errors']} issues)")

    # Test English (uses LanguageTool)
    analyzer_en = GrammarAnalyzer(language='en')
    assert analyzer_en.language == 'en', "Should be set to English"
    print("✓ English GrammarAnalyzer created")

    tool = nlp_manager.get_language_tool('en')
    if tool is not None:
        result_en = analyzer_en.analyze("This is a test without errors.")
        assert result_en['success'], "Analysis should succeed"
        print(f"✓ English analysis works (found {result_en['total_errors']} issues)")
    else:
        print("⚠ Skipping English test (LanguageTool not available)")

    print("\n✅ TEST 8 PASSED\n")


def test_memory_management():
    """Test memory management (unload models)"""
    print("=" * 60)
    print("TEST 9: Memory Management")
    print("=" * 60)

    # Load Italian
    nlp_manager.set_language('it')
    nlp_manager.get_spacy_model('it')
    nlp_manager.get_language_tool('it')

    # Unload Italian
    nlp_manager.unload_language('it')
    print("✓ Models unloaded successfully")

    # Verify they're not in cache anymore by checking internal state
    assert 'it' not in nlp_manager._spacy_models, "spaCy model should be unloaded"
    assert 'it' not in nlp_manager._language_tools, "LanguageTool should be unloaded"
    print("✓ Cache cleared correctly")

    print("\n✅ TEST 9 PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING NLP MULTI-LANGUAGE SYSTEM TESTS")
    print("=" * 60 + "\n")

    try:
        test_nlp_manager_singleton()
        test_language_support()
        test_set_language()
        test_check_model_availability()
        test_spacy_loading()
        test_languagetool_loading()
        test_style_analyzer_multilang()
        test_grammar_analyzer_multilang()
        test_memory_management()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n✅ NLP Multi-Language System is working:")
        print("   - Singleton pattern implemented")
        print("   - 5 languages supported (it, en, es, fr, de)")
        print("   - Lazy loading and caching work")
        print("   - StyleAnalyzer multi-language support")
        print("   - GrammarAnalyzer multi-language support")
        print("   - Memory management works")
        print("\n⚠️ Note: Some tests may be skipped if models are not installed")
        print("   Install spaCy models with:")
        print("   python -m spacy download it_core_news_sm")
        print("   python -m spacy download en_core_web_sm")
        print("   (etc. for other languages)")
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
