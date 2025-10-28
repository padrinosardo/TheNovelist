#!/usr/bin/env python3
"""
Test script for Project model language support
"""
import sys
from models.project import Project


def test_create_new_with_language():
    """Test creating a new project with language parameter"""
    print("=" * 60)
    print("TEST 1: Create new project with language")
    print("=" * 60)

    # Test with Italian (default)
    project_it = Project.create_new("Il mio romanzo", "Mario Rossi")
    assert project_it.language == "it", f"Expected 'it', got '{project_it.language}'"
    print("✓ Default language (Italian): PASSED")

    # Test with English
    project_en = Project.create_new("My Novel", "John Doe", language="en")
    assert project_en.language == "en", f"Expected 'en', got '{project_en.language}'"
    print("✓ English language: PASSED")

    # Test with Spanish
    project_es = Project.create_new("Mi Novela", "Juan Pérez", language="es")
    assert project_es.language == "es", f"Expected 'es', got '{project_es.language}'"
    print("✓ Spanish language: PASSED")

    # Test with French
    project_fr = Project.create_new("Mon Roman", "Pierre Dupont", language="fr")
    assert project_fr.language == "fr", f"Expected 'fr', got '{project_fr.language}'"
    print("✓ French language: PASSED")

    # Test with German
    project_de = Project.create_new("Mein Roman", "Hans Schmidt", language="de")
    assert project_de.language == "de", f"Expected 'de', got '{project_de.language}'"
    print("✓ German language: PASSED")

    print("\n✅ TEST 1 PASSED\n")


def test_serialization():
    """Test to_dict() includes language"""
    print("=" * 60)
    print("TEST 2: Serialization (to_dict)")
    print("=" * 60)

    project = Project.create_new("Test Project", "Test Author", language="en")
    project_dict = project.to_dict()

    assert 'language' in project_dict, "Language field missing in serialization"
    assert project_dict['language'] == "en", f"Expected 'en', got '{project_dict['language']}'"

    print(f"Serialized data: {project_dict}")
    print("\n✅ TEST 2 PASSED\n")


def test_deserialization():
    """Test from_dict() correctly loads language"""
    print("=" * 60)
    print("TEST 3: Deserialization (from_dict)")
    print("=" * 60)

    # Test with language field present
    data_with_lang = {
        'title': 'English Novel',
        'author': 'John Doe',
        'language': 'en',
        'created_date': '2025-01-01T10:00:00',
        'modified_date': '2025-01-01T10:00:00'
    }

    project = Project.from_dict(data_with_lang)
    assert project.language == "en", f"Expected 'en', got '{project.language}'"
    print("✓ Deserialization with language field: PASSED")

    # Test backward compatibility (no language field)
    data_without_lang = {
        'title': 'Old Project',
        'author': 'Old Author',
        'created_date': '2024-01-01T10:00:00',
        'modified_date': '2024-01-01T10:00:00'
    }

    project_old = Project.from_dict(data_without_lang)
    assert project_old.language == "it", f"Expected 'it' (default), got '{project_old.language}'"
    print("✓ Backward compatibility (defaults to 'it'): PASSED")

    print("\n✅ TEST 3 PASSED\n")


def test_round_trip():
    """Test complete serialization/deserialization cycle"""
    print("=" * 60)
    print("TEST 4: Round-trip (create -> serialize -> deserialize)")
    print("=" * 60)

    # Create project
    original = Project.create_new("Test Novel", "Test Author", language="fr")
    original.manuscript_text = "Sample text content"

    # Serialize
    serialized = original.to_dict()

    # Deserialize
    restored = Project.from_dict(serialized, manuscript_text=original.manuscript_text)

    # Verify all fields
    assert restored.title == original.title, "Title mismatch"
    assert restored.author == original.author, "Author mismatch"
    assert restored.language == original.language, f"Language mismatch: expected '{original.language}', got '{restored.language}'"
    assert restored.created_date == original.created_date, "Created date mismatch"
    assert restored.modified_date == original.modified_date, "Modified date mismatch"
    assert restored.manuscript_text == original.manuscript_text, "Manuscript text mismatch"

    print("✓ All fields preserved in round-trip: PASSED")
    print("\n✅ TEST 4 PASSED\n")


def test_direct_instantiation():
    """Test creating Project directly with dataclass"""
    print("=" * 60)
    print("TEST 5: Direct instantiation")
    print("=" * 60)

    # Test with all parameters
    project = Project(
        title="Direct Project",
        author="Direct Author",
        language="es",
        created_date="2025-01-01T00:00:00",
        modified_date="2025-01-01T00:00:00",
        manuscript_text="Content"
    )

    assert project.language == "es", f"Expected 'es', got '{project.language}'"
    print("✓ Direct instantiation with language: PASSED")

    # Test with minimal parameters (using defaults)
    project_minimal = Project(
        title="Minimal Project",
        author="Minimal Author"
    )

    assert project_minimal.language == "it", f"Expected 'it' (default), got '{project_minimal.language}'"
    print("✓ Direct instantiation with defaults: PASSED")

    print("\n✅ TEST 5 PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING PROJECT LANGUAGE SUPPORT TESTS")
    print("=" * 60 + "\n")

    try:
        test_create_new_with_language()
        test_serialization()
        test_deserialization()
        test_round_trip()
        test_direct_instantiation()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n✅ Project model now supports multi-language:")
        print("   - Italian (it)")
        print("   - English (en)")
        print("   - Spanish (es)")
        print("   - French (fr)")
        print("   - German (de)")
        print("\n✅ Backward compatibility maintained:")
        print("   - Old projects without 'language' field default to 'it'")
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
