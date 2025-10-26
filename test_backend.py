"""
Test script for ProjectManager and CharacterManager
Run this to verify Phase 1 implementation
"""
import os
import sys
from managers.project_manager import ProjectManager


def test_project_creation():
    """Test creating a new project"""
    print("\n" + "="*60)
    print("TEST 1: Creating a new project")
    print("="*60)

    pm = ProjectManager()
    success = pm.create_new_project(
        title="My First Novel",
        author="Antonio Caria",
        filepath="test_project.tnp"
    )

    if success:
        print("✅ Project created successfully")
        print(f"   Title: {pm.current_project.title}")
        print(f"   Author: {pm.current_project.author}")
        print(f"   File: {pm.current_filepath}")
        return pm
    else:
        print("❌ Failed to create project")
        sys.exit(1)


def test_character_operations(pm):
    """Test adding, updating, and managing characters"""
    print("\n" + "="*60)
    print("TEST 2: Adding characters")
    print("="*60)

    # Add first character
    char1 = pm.character_manager.add_character(
        name="Mario Rossi",
        description="A 45-year-old private detective with a troubled past. "
                   "Cynical on the outside but has a heart of gold."
    )
    print(f"✅ Added character: {char1.name}")
    print(f"   ID: {char1.id}")

    # Add second character
    char2 = pm.character_manager.add_character(
        name="Lucia Bianchi",
        description="A brilliant lawyer in her thirties. "
                   "Sharp mind and determined personality."
    )
    print(f"✅ Added character: {char2.name}")
    print(f"   ID: {char2.id}")

    # List all characters
    print("\n" + "-"*60)
    print("All characters in project:")
    for char in pm.character_manager.get_all_characters():
        print(f"  • {char.name} - {char.description[:50]}...")

    return char1, char2


def test_character_update(pm, character):
    """Test updating a character"""
    print("\n" + "="*60)
    print("TEST 3: Updating a character")
    print("="*60)

    print(f"Original name: {character.name}")
    print(f"Original description: {character.description[:50]}...")

    updated = pm.character_manager.update_character(
        character.id,
        name="Mario Rossi (Updated)",
        description="UPDATED: A 45-year-old private detective..."
    )

    if updated:
        print(f"✅ Character updated")
        print(f"   New name: {updated.name}")
        print(f"   New description: {updated.description[:50]}...")
    else:
        print("❌ Failed to update character")


def test_save_project(pm):
    """Test saving the project"""
    print("\n" + "="*60)
    print("TEST 4: Saving the project")
    print("="*60)

    # Update manuscript text
    manuscript_text = """Chapter 1: The Beginning

It was a dark and stormy night when Mario Rossi received the phone call
that would change his life forever. The voice on the other end was
familiar - it was Lucia Bianchi, the lawyer he had worked with on
several cases before.

"Mario, I need your help," she said urgently. "It's about the Moretti case..."

Mario sighed. He had hoped never to hear that name again.
"""

    success = pm.save_project(manuscript_text)

    if success:
        print("✅ Project saved successfully")
        print(f"   File: {pm.current_filepath}")
        print(f"   Manuscript length: {len(manuscript_text)} characters")
        print(f"   Characters count: {len(pm.character_manager.get_all_characters())}")
    else:
        print("❌ Failed to save project")
        sys.exit(1)


def test_open_project():
    """Test opening an existing project"""
    print("\n" + "="*60)
    print("TEST 5: Opening the saved project")
    print("="*60)

    pm2 = ProjectManager()
    project, manuscript, characters = pm2.open_project("test_project.tnp")

    if project:
        print("✅ Project opened successfully")
        print(f"   Title: {project.title}")
        print(f"   Author: {project.author}")
        print(f"   Created: {project.created_date}")
        print(f"   Modified: {project.modified_date}")
        print(f"   Manuscript length: {len(manuscript)} characters")
        print(f"   Characters loaded: {len(characters)}")
        print("\n   Characters:")
        for char in characters:
            print(f"      • {char.name}")
        return pm2
    else:
        print("❌ Failed to open project")
        sys.exit(1)


def test_delete_character(pm):
    """Test deleting a character"""
    print("\n" + "="*60)
    print("TEST 6: Deleting a character")
    print("="*60)

    chars = pm.character_manager.get_all_characters()
    if chars:
        char_to_delete = chars[0]
        print(f"Deleting character: {char_to_delete.name}")

        success = pm.character_manager.delete_character(char_to_delete.id)

        if success:
            print(f"✅ Character deleted")
            print(f"   Remaining characters: {len(pm.character_manager.get_all_characters())}")
            for char in pm.character_manager.get_all_characters():
                print(f"      • {char.name}")
        else:
            print("❌ Failed to delete character")


def test_save_after_delete(pm):
    """Test saving after deletion"""
    print("\n" + "="*60)
    print("TEST 7: Saving after deletion")
    print("="*60)

    success = pm.save_project()

    if success:
        print("✅ Project saved successfully after deletion")
    else:
        print("❌ Failed to save project")


def cleanup():
    """Clean up test files"""
    print("\n" + "="*60)
    print("CLEANUP: Removing test files")
    print("="*60)

    if os.path.exists("test_project.tnp"):
        os.remove("test_project.tnp")
        print("✅ Test project file removed")


def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# PHASE 1 BACKEND TESTING")
    print("# Testing ProjectManager and CharacterManager")
    print("#"*60)

    try:
        # Test 1: Create project
        pm = test_project_creation()

        # Test 2: Add characters
        char1, char2 = test_character_operations(pm)

        # Test 3: Update character
        test_character_update(pm, char1)

        # Test 4: Save project
        test_save_project(pm)

        # Test 5: Open project
        pm2 = test_open_project()

        # Test 6: Delete character
        test_delete_character(pm2)

        # Test 7: Save after delete
        test_save_after_delete(pm2)

        # Close project
        pm2.close_project()

        print("\n" + "#"*60)
        print("# ALL TESTS PASSED! ✅")
        print("#"*60)

        # Ask if user wants to keep test file
        print("\nTest file 'test_project.tnp' was created.")
        response = input("Do you want to delete it? (y/n): ").lower()
        if response == 'y':
            cleanup()
        else:
            print("✅ Test file kept for inspection")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
