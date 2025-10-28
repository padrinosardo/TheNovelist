#!/usr/bin/env python3
"""
Test script for ProjectManager Integration (Feature 4.1)
"""
import sys
import os
import tempfile
import shutil
from pathlib import Path

from managers.project_manager import ProjectManager
from models.project_type import ProjectType
from models.container_type import ContainerType


def test_create_project_with_containers():
    """Test creating a new project with container support"""
    print("=" * 60)
    print("TEST 1: Create Project with Containers")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        pm = ProjectManager()

        # Create project filepath
        project_file = os.path.join(temp_dir, "test_novel.tnp")

        # Create novel project
        success = pm.create_new_project(
            title="Il Mio Romanzo",
            author="Test Author",
            filepath=project_file,
            language="it",
            project_type=ProjectType.NOVEL,
            genre="Fantasy",
            target_word_count=80000,
            tags=["epic", "magic"]
        )

        assert success == True
        print(f"✓ Created project: {project_file}")

        # Verify file exists
        assert os.path.exists(project_file)
        print("✓ Project file exists")

        # Open and verify
        import zipfile
        with zipfile.ZipFile(project_file, 'r') as zipf:
            file_list = zipf.namelist()
            print(f"\n✓ Files in ZIP ({len(file_list)}):")

            # Check required files
            assert 'manifest.json' in file_list
            print("  - manifest.json")
            assert 'manuscript_structure.json' in file_list
            print("  - manuscript_structure.json")
            assert 'characters.json' in file_list
            print("  - characters.json")

            # Check container files (should include locations, research, timeline, etc.)
            expected_containers = [
                'locations.json',
                'research.json',
                'timeline.json',
                'worldbuilding.json',
                'notes.json'
            ]

            for container_file in expected_containers:
                if container_file in file_list:
                    print(f"  - {container_file}")

            # Check manifest content
            import json
            manifest_data = json.loads(zipf.read('manifest.json'))
            assert manifest_data['title'] == "Il Mio Romanzo"
            assert manifest_data['author'] == "Test Author"
            assert manifest_data['language'] == "it"
            assert manifest_data['project_type'] == "novel"
            assert manifest_data['genre'] == "Fantasy"
            assert manifest_data['target_word_count'] == 80000
            assert manifest_data['tags'] == ["epic", "magic"]
            print("\n✓ Manifest contains all new fields")

    print("\n✅ TEST 1 PASSED\n")


def test_open_project_with_containers():
    """Test opening a project and using container managers"""
    print("=" * 60)
    print("TEST 2: Open Project and Use Container Managers")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        pm = ProjectManager()

        # Create project
        project_file = os.path.join(temp_dir, "test_project.tnp")
        pm.create_new_project(
            title="Test Project",
            author="Test",
            filepath=project_file,
            project_type=ProjectType.NOVEL
        )
        print("✓ Created test project")

        # Close and reopen
        pm.close_project()
        project, manuscript, characters = pm.open_project(project_file)

        assert project is not None
        assert project.title == "Test Project"
        assert project.project_type == ProjectType.NOVEL
        print(f"✓ Opened project: {project.title}")

        # Verify container managers are initialized
        assert pm.container_manager is not None
        assert pm.location_manager is not None
        assert pm.research_manager is not None
        assert pm.timeline_manager is not None
        assert pm.source_manager is not None
        assert pm.note_manager is not None
        print("✓ All container managers initialized")

        # Test adding content to containers
        loc_id = pm.location_manager.add_location(
            name="Castle of Doom",
            description="A dark fortress",
            location_type="castle"
        )
        print(f"✓ Added location: {loc_id[:8]}...")

        note_id = pm.research_manager.add_research_note(
            title="Medieval Weapons",
            content="Research about swords...",
            category="history"
        )
        print(f"✓ Added research note: {note_id[:8]}...")

        event_id = pm.timeline_manager.add_timeline_event(
            title="The Great Battle",
            date="Year 1250",
            sort_order=10
        )
        print(f"✓ Added timeline event: {event_id[:8]}...")

        # Save project
        pm.save_project()
        print("✓ Saved project with containers")

        # Reopen and verify data persisted
        pm.close_project()
        project2, _, _ = pm.open_project(project_file)

        locations = pm.location_manager.get_all_locations()
        assert len(locations) == 1
        assert locations[0].name == "Castle of Doom"
        print(f"✓ Location persisted: {locations[0].name}")

        notes = pm.research_manager.get_all_research_notes()
        assert len(notes) == 1
        assert notes[0].title == "Medieval Weapons"
        print(f"✓ Research note persisted: {notes[0].title}")

        events = pm.timeline_manager.get_all_timeline_events()
        assert len(events) == 1
        assert events[0].title == "The Great Battle"
        print(f"✓ Timeline event persisted: {events[0].title}")

    print("\n✅ TEST 2 PASSED\n")


def test_migration_old_project():
    """Test that old projects are migrated correctly"""
    print("=" * 60)
    print("TEST 3: Migration of Old Project Format")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a fake old project (without project_type, genre, etc.)
        import zipfile
        import json

        project_file = os.path.join(temp_dir, "old_project.tnp")

        # Old manifest format (without new fields)
        old_manifest = {
            'title': 'Old Project',
            'author': 'Old Author',
            'language': 'it',
            'created_date': '2024-01-01T00:00:00',
            'modified_date': '2024-01-01T00:00:00'
            # Missing: project_type, genre, target_word_count, tags
        }

        # Create minimal old project structure
        temp_project_dir = os.path.join(temp_dir, 'old_temp')
        os.makedirs(temp_project_dir)

        with open(os.path.join(temp_project_dir, 'manifest.json'), 'w') as f:
            json.dump(old_manifest, f)

        with open(os.path.join(temp_project_dir, 'manuscript_structure.json'), 'w') as f:
            json.dump({
                'chapters': [],
                'current_scene_id': None
            }, f)

        with open(os.path.join(temp_project_dir, 'characters.json'), 'w') as f:
            json.dump({'characters': []}, f)

        os.makedirs(os.path.join(temp_project_dir, 'images'))

        # Create ZIP
        with zipfile.ZipFile(project_file, 'w') as zipf:
            zipf.write(os.path.join(temp_project_dir, 'manifest.json'), 'manifest.json')
            zipf.write(os.path.join(temp_project_dir, 'manuscript_structure.json'), 'manuscript_structure.json')
            zipf.write(os.path.join(temp_project_dir, 'characters.json'), 'characters.json')
            zipf.writestr('images/', '')

        shutil.rmtree(temp_project_dir)
        print("✓ Created fake old project")

        # Open with new ProjectManager
        pm = ProjectManager()
        project, _, _ = pm.open_project(project_file)

        assert project is not None
        assert project.title == "Old Project"
        assert project.project_type == ProjectType.NOVEL  # Should default to NOVEL
        assert project.genre == ""  # Should default to empty
        assert project.target_word_count == 0  # Should default to 0
        assert project.tags == []  # Should default to empty list
        print("✓ Old project migrated successfully")
        print(f"  - project_type: {project.project_type.value}")
        print(f"  - genre: '{project.genre}'")
        print(f"  - target_word_count: {project.target_word_count}")
        print(f"  - tags: {project.tags}")

        # Verify container managers are still initialized (even for migrated project)
        assert pm.container_manager is not None
        print("✓ Container managers initialized for migrated project")

    print("\n✅ TEST 3 PASSED\n")


def test_different_project_types():
    """Test creating different project types with appropriate containers"""
    print("=" * 60)
    print("TEST 4: Different Project Types with Appropriate Containers")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        pm = ProjectManager()

        # Test Novel (should have locations, research, timeline, etc.)
        novel_file = os.path.join(temp_dir, "novel.tnp")
        pm.create_new_project(
            title="Novel Project",
            author="Author",
            filepath=novel_file,
            project_type=ProjectType.NOVEL
        )

        import zipfile
        with zipfile.ZipFile(novel_file, 'r') as zipf:
            file_list = zipf.namelist()
            assert 'locations.json' in file_list
            assert 'research.json' in file_list
            assert 'timeline.json' in file_list
            print("✓ Novel has narrative containers (locations, research, timeline)")

        pm.close_project()

        # Test Article (should have sources, keywords)
        article_file = os.path.join(temp_dir, "article.tnp")
        pm.create_new_project(
            title="Article Project",
            author="Author",
            filepath=article_file,
            project_type=ProjectType.ARTICLE_MAGAZINE
        )

        with zipfile.ZipFile(article_file, 'r') as zipf:
            file_list = zipf.namelist()
            assert 'sources.json' in file_list
            assert 'keywords.json' in file_list
            print("✓ Article has journalism containers (sources, keywords)")

    print("\n✅ TEST 4 PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING PROJECT MANAGER INTEGRATION TESTS (Feature 4.1)")
    print("=" * 60 + "\n")

    try:
        test_create_project_with_containers()
        test_open_project_with_containers()
        test_migration_old_project()
        test_different_project_types()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n✅ Feature 4.1 - ProjectManager Integration:")
        print("   - Projects created with project_type, genre, tags")
        print("   - Container files automatically created based on type")
        print("   - All container managers initialized on project open")
        print("   - Data persists across save/load cycles")
        print("   - Old projects migrate seamlessly")
        print("   - Different project types get appropriate containers")
        print("\n✅ Extended .tnp format includes:")
        print("   - manifest.json (with new fields)")
        print("   - locations.json, research.json, timeline.json")
        print("   - sources.json, notes.json, etc.")
        print("   - All containers based on project_type")
        print("\n✅ Ready for Feature 4.2 (Migration System)!")
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
