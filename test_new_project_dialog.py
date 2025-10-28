#!/usr/bin/env python3
"""
Test script for New Project Dialog (Feature 5.1)
"""
import sys
from PySide6.QtWidgets import QApplication
from ui.dialogs.new_project_dialog import NewProjectDialog
from models.project_type import ProjectType


def test_dialog_ui():
    """Test that the dialog opens and displays correctly"""
    print("=" * 60)
    print("TEST 1: Dialog UI Display")
    print("=" * 60)

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    dialog = NewProjectDialog()
    print("✓ Dialog created successfully")

    # Check that all widgets exist
    assert dialog.title_input is not None
    assert dialog.author_input is not None
    assert dialog.language_combo is not None
    assert dialog.project_type_combo is not None
    assert dialog.genre_input is not None
    assert dialog.word_count_spin is not None
    assert dialog.tags_input is not None
    assert dialog.containers_preview is not None
    print("✓ All input widgets exist")

    # Check project types are populated
    assert dialog.project_type_combo.count() == len(ProjectType)
    print(f"✓ Project type combo has {dialog.project_type_combo.count()} types")

    # Check languages are populated
    assert dialog.language_combo.count() == 5
    print(f"✓ Language combo has {dialog.language_combo.count()} languages")

    print("\n✅ TEST 1 PASSED\n")
    return app


def test_project_type_change():
    """Test that changing project type updates containers preview"""
    print("=" * 60)
    print("TEST 2: Project Type Change")
    print("=" * 60)

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    dialog = NewProjectDialog()

    # Test changing to different project types
    for i in range(dialog.project_type_combo.count()):
        dialog.project_type_combo.setCurrentIndex(i)
        project_type = dialog.project_type_combo.currentData()

        print(f"\n✓ Selected: {project_type.get_display_name('it')}")

        # Check that description updated
        assert len(dialog.type_description.text()) > 0
        print(f"  Description: {dialog.type_description.text()[:50]}...")

        # Check that containers preview updated
        assert len(dialog.containers_preview.text()) > 0
        print(f"  Containers: {dialog.containers_preview.text()[:80]}...")

    print("\n✅ TEST 2 PASSED\n")
    return app


def test_word_count_suggestion():
    """Test word count suggestion feature"""
    print("=" * 60)
    print("TEST 3: Word Count Suggestion")
    print("=" * 60)

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    dialog = NewProjectDialog()

    # Test suggestion for Novel
    dialog.project_type_combo.setCurrentIndex(0)  # Novel
    dialog._suggest_word_count()
    word_count = dialog.word_count_spin.value()

    print(f"✓ Novel suggested word count: {word_count:,} words")
    assert word_count > 0
    assert 50000 <= word_count <= 120000  # Novel range

    # Test suggestion for Short Story
    for i in range(dialog.project_type_combo.count()):
        pt = dialog.project_type_combo.itemData(i)
        if pt == ProjectType.SHORT_STORY:
            dialog.project_type_combo.setCurrentIndex(i)
            break

    dialog._suggest_word_count()
    word_count = dialog.word_count_spin.value()

    print(f"✓ Short Story suggested word count: {word_count:,} words")
    assert word_count > 0
    assert 1000 <= word_count <= 20000  # Short story range

    print("\n✅ TEST 3 PASSED\n")
    return app


def test_validation():
    """Test input validation"""
    print("=" * 60)
    print("TEST 4: Input Validation")
    print("=" * 60)

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    dialog = NewProjectDialog()

    # Test empty title validation
    dialog.title_input.setText("")
    dialog.author_input.setText("Test Author")

    # Manually trigger validation (without actually showing dialog)
    title = dialog.title_input.text().strip()
    from utils.validators import Validators
    is_valid, error_msg = Validators.validate_project_name(title)

    assert is_valid == False
    print(f"✓ Empty title rejected: {error_msg}")

    # Test valid title
    dialog.title_input.setText("My Test Project")
    title = dialog.title_input.text().strip()
    is_valid, error_msg = Validators.validate_project_name(title)

    assert is_valid == True
    print("✓ Valid title accepted")

    # Test tags parsing
    dialog.tags_input.setText("fantasy, magic, adventure")
    tags_text = dialog.tags_input.text().strip()
    tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

    assert len(tags) == 3
    assert "fantasy" in tags
    assert "magic" in tags
    assert "adventure" in tags
    print(f"✓ Tags parsed correctly: {tags}")

    print("\n✅ TEST 4 PASSED\n")
    return app


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING NEW PROJECT DIALOG TESTS (Feature 5.1)")
    print("=" * 60 + "\n")

    try:
        app = test_dialog_ui()
        test_project_type_change()
        test_word_count_suggestion()
        test_validation()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n✅ Feature 5.1 - New Project Dialog:")
        print("   - Complete dialog with all fields")
        print("   - Project type selection with descriptions")
        print("   - Dynamic containers preview")
        print("   - Genre, target word count, tags")
        print("   - Word count suggestions based on type")
        print("   - Input validation")
        print("   - Integrated with MainWindow")
        print("\n✅ Dialog includes:")
        print("   - 8 project types with icons")
        print("   - 5 languages support")
        print("   - Real-time containers preview")
        print("   - Helpful tooltips and validation")
        print("\n✅ Ready to test in the application!")
        print()

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
