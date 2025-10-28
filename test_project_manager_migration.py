#!/usr/bin/env python3
"""
Test script for ProjectManager language support and migration
"""
import sys
import os
import tempfile
import json
import zipfile
import shutil
from managers.project_manager import ProjectManager
from models.project import Project


def test_create_project_with_language():
    """Test creating a new project with language parameter"""
    print("=" * 60)
    print("TEST 1: Create New Project with Language")
    print("=" * 60)

    manager = ProjectManager()

    # Create temp file for testing
    temp_file = tempfile.NamedTemporaryFile(suffix='.tnp', delete=False)
    temp_file.close()

    try:
        # Test creating project with English
        success = manager.create_new_project(
            title="English Novel",
            author="Test Author",
            filepath=temp_file.name,
            language='en'
        )

        assert success, "Project creation should succeed"
        assert manager.current_project is not None, "Current project should be set"
        assert manager.current_project.language == 'en', f"Language should be 'en', got '{manager.current_project.language}'"

        print(f"✓ Project created with language: {manager.current_project.language}")

        # Verify the ZIP file contains correct language in manifest
        with zipfile.ZipFile(temp_file.name, 'r') as zipf:
            with zipf.open('manifest.json') as f:
                manifest_data = json.load(f)
                assert 'language' in manifest_data, "Manifest should contain language field"
                assert manifest_data['language'] == 'en', f"Manifest language should be 'en', got '{manifest_data['language']}'"

        print("✓ Manifest contains correct language field")

        manager.close_project()

        # Test creating project with default language (Italian)
        temp_file2 = tempfile.NamedTemporaryFile(suffix='.tnp', delete=False)
        temp_file2.close()

        success = manager.create_new_project(
            title="Romanzo Italiano",
            author="Autore Test",
            filepath=temp_file2.name
            # language not specified, should default to 'it'
        )

        assert success, "Project creation with default language should succeed"
        assert manager.current_project.language == 'it', f"Default language should be 'it', got '{manager.current_project.language}'"
        print("✓ Project created with default language: it")

        manager.close_project()
        os.unlink(temp_file2.name)

    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    print("\n✅ TEST 1 PASSED\n")


def test_migration_old_project():
    """Test migration of old project without language field"""
    print("=" * 60)
    print("TEST 2: Migration of Old Project Format")
    print("=" * 60)

    # Create a fake old project without language field
    temp_file = tempfile.NamedTemporaryFile(suffix='.tnp', delete=False)
    temp_file.close()

    try:
        # Create temp directory with old project structure
        temp_dir = tempfile.mkdtemp()

        # Create old-style manifest without language field
        old_manifest = {
            'title': 'Old Project',
            'author': 'Old Author',
            'created_date': '2024-01-01T00:00:00',
            'modified_date': '2024-01-01T00:00:00'
            # Note: no 'language' field
        }

        manifest_path = os.path.join(temp_dir, 'manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(old_manifest, f, indent=2)

        # Create minimal manuscript structure
        from models.manuscript_structure import ManuscriptStructure
        structure = ManuscriptStructure.create_default()
        structure_path = os.path.join(temp_dir, 'manuscript_structure.json')
        with open(structure_path, 'w', encoding='utf-8') as f:
            json.dump(structure.to_dict(), f, indent=2)

        # Create empty characters
        characters_path = os.path.join(temp_dir, 'characters.json')
        with open(characters_path, 'w', encoding='utf-8') as f:
            json.dump({'characters': []}, f, indent=2)

        # Create images directory
        images_dir = os.path.join(temp_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)

        # Create ZIP file
        with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(manifest_path, 'manifest.json')
            zipf.write(structure_path, 'manuscript_structure.json')
            zipf.write(characters_path, 'characters.json')
            zipf.writestr('images/', '')

        # Clean up temp directory
        shutil.rmtree(temp_dir)

        print("✓ Created old-format project file (without language)")

        # Now open it with ProjectManager
        manager = ProjectManager()
        project, manuscript_text, characters = manager.open_project(temp_file.name)

        assert project is not None, "Project should open successfully"
        assert hasattr(project, 'language'), "Project should have language attribute"
        assert project.language == 'it', f"Migrated language should be 'it', got '{project.language}'"

        print(f"✓ Old project migrated successfully")
        print(f"  - Title: {project.title}")
        print(f"  - Language: {project.language} (auto-migrated)")

        # Verify manifest was updated in temp directory
        temp_manifest_path = os.path.join(manager._temp_dir, 'manifest.json')
        with open(temp_manifest_path, 'r', encoding='utf-8') as f:
            migrated_manifest = json.load(f)
            assert 'language' in migrated_manifest, "Migrated manifest should contain language"
            assert migrated_manifest['language'] == 'it', "Migrated language should be 'it'"

        print("✓ Manifest updated with language field")

        manager.close_project()

    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    print("\n✅ TEST 2 PASSED\n")


def test_nlp_integration():
    """Test that NLP manager is configured when project is opened/created"""
    print("=" * 60)
    print("TEST 3: NLP Manager Integration")
    print("=" * 60)

    from analysis.nlp_manager import nlp_manager

    manager = ProjectManager()
    temp_file = tempfile.NamedTemporaryFile(suffix='.tnp', delete=False)
    temp_file.close()

    try:
        # Create project with Spanish language
        success = manager.create_new_project(
            title="Novela en Español",
            author="Autor",
            filepath=temp_file.name,
            language='es'
        )

        assert success, "Project creation should succeed"

        # Check that NLP manager has the correct language set
        current_lang = nlp_manager.get_current_language()
        assert current_lang == 'es', f"NLP language should be 'es', got '{current_lang}'"
        print(f"✓ NLP manager language set to: {current_lang}")

        manager.close_project()

        # Now open the same project
        project, _, _ = manager.open_project(temp_file.name)
        assert project is not None, "Project should open successfully"

        # Check that NLP manager language was set again
        current_lang = nlp_manager.get_current_language()
        assert current_lang == 'es', f"NLP language should be 'es' after opening, got '{current_lang}'"
        print(f"✓ NLP manager language maintained after reopening: {current_lang}")

        manager.close_project()

    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    print("\n✅ TEST 3 PASSED\n")


def test_save_preserves_language():
    """Test that saving a project preserves the language field"""
    print("=" * 60)
    print("TEST 4: Save Project Preserves Language")
    print("=" * 60)

    manager = ProjectManager()
    temp_file = tempfile.NamedTemporaryFile(suffix='.tnp', delete=False)
    temp_file.close()

    try:
        # Create project with French
        manager.create_new_project(
            title="Roman Français",
            author="Auteur",
            filepath=temp_file.name,
            language='fr'
        )

        # Modify project slightly
        manager.current_project.title = "Roman Français Modifié"

        # Save project
        success = manager.save_project()
        assert success, "Project save should succeed"
        print("✓ Project saved")

        manager.close_project()

        # Reopen and verify language is preserved
        project, _, _ = manager.open_project(temp_file.name)
        assert project is not None, "Project should reopen successfully"
        assert project.language == 'fr', f"Language should be preserved as 'fr', got '{project.language}'"
        assert project.title == "Roman Français Modifié", "Title modification should be preserved"
        print("✓ Language preserved after save/reload cycle")

        manager.close_project()

    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    print("\n✅ TEST 4 PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING PROJECT MANAGER MIGRATION TESTS")
    print("=" * 60 + "\n")

    try:
        test_create_project_with_language()
        test_migration_old_project()
        test_nlp_integration()
        test_save_preserves_language()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n✅ ProjectManager Multi-Language Support:")
        print("   - New projects support language parameter")
        print("   - Old projects migrate automatically to 'it'")
        print("   - NLP manager is configured on project open/create")
        print("   - Language is preserved through save/load cycles")
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
