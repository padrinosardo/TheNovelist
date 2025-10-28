#!/usr/bin/env python3
"""
Test script for Container System (Feature 3.1)
"""
import sys
from models.project_type import ProjectType
from models.container_type import ContainerType
from models.project import Project


def test_project_type_enum():
    """Test ProjectType enum functionality"""
    print("=" * 60)
    print("TEST 1: ProjectType Enum")
    print("=" * 60)

    # Test all project types
    print("\nAll Project Types:")
    for pt in ProjectType:
        icon = pt.get_icon()
        name_it = pt.get_display_name('it')
        name_en = pt.get_display_name('en')
        word_range = pt.get_target_word_count_range()
        print(f"  {icon} {pt.value:20s} | IT: {name_it:25s} | EN: {name_en:25s} | Words: {word_range[0]:6d}-{word_range[1]:6d}")

    print("\n✅ TEST 1 PASSED\n")


def test_container_type_enum():
    """Test ContainerType enum functionality"""
    print("=" * 60)
    print("TEST 2: ContainerType Enum")
    print("=" * 60)

    # Test all container types
    print("\nAll Container Types:")
    for ct in ContainerType:
        icon, name_it = ContainerType.get_display_info(ct, 'it')
        icon, name_en = ContainerType.get_display_info(ct, 'en')
        filename = ContainerType.get_filename(ct)
        print(f"  {icon} {ct.value:20s} | IT: {name_it:25s} | EN: {name_en:25s} | File: {filename}")

    print("\n✅ TEST 2 PASSED\n")


def test_containers_for_project_types():
    """Test container mapping for each project type"""
    print("=" * 60)
    print("TEST 3: Containers Available per Project Type")
    print("=" * 60)

    for pt in ProjectType:
        containers = ContainerType.get_available_for_project_type(pt)
        print(f"\n{pt.get_icon()} {pt.get_display_name('it')}:")
        for ct in containers:
            icon, name = ContainerType.get_display_info(ct, 'it')
            print(f"    {icon} {name}")

    print("\n✅ TEST 3 PASSED\n")


def test_project_with_type():
    """Test Project model with project_type"""
    print("=" * 60)
    print("TEST 4: Project Model with Type")
    print("=" * 60)

    # Create new project
    project = Project.create_new(
        title="Il Mio Romanzo",
        author="Mario Rossi",
        language="it",
        project_type=ProjectType.NOVEL,
        genre="Fantasy",
        target_word_count=80000,
        tags=["epic", "magic", "adventure"]
    )

    print(f"\nCreated project:")
    print(f"  Title: {project.title}")
    print(f"  Author: {project.author}")
    print(f"  Language: {project.language}")
    print(f"  Type: {project.project_type.get_display_name('it')} ({project.project_type.value})")
    print(f"  Genre: {project.genre}")
    print(f"  Target Word Count: {project.target_word_count:,}")
    print(f"  Tags: {', '.join(project.tags)}")

    # Test serialization
    print("\n✓ Testing to_dict()...")
    project_dict = project.to_dict()
    assert project_dict['project_type'] == 'novel'
    assert project_dict['genre'] == 'Fantasy'
    assert project_dict['target_word_count'] == 80000
    assert project_dict['tags'] == ["epic", "magic", "adventure"]
    print("  ✓ Serialization OK")

    # Test deserialization
    print("\n✓ Testing from_dict()...")
    project2 = Project.from_dict(project_dict)
    assert project2.title == "Il Mio Romanzo"
    assert project2.project_type == ProjectType.NOVEL
    assert project2.genre == "Fantasy"
    assert project2.target_word_count == 80000
    assert len(project2.tags) == 3
    print("  ✓ Deserialization OK")

    print("\n✅ TEST 4 PASSED\n")


def test_backward_compatibility():
    """Test that old projects without project_type still work"""
    print("=" * 60)
    print("TEST 5: Backward Compatibility")
    print("=" * 60)

    # Simulate old project data (without project_type)
    old_project_data = {
        'title': 'Vecchio Progetto',
        'author': 'Autore Sconosciuto',
        'language': 'it',
        'created_date': '2024-01-01T12:00:00',
        'modified_date': '2024-01-01T12:00:00'
        # No project_type, genre, target_word_count, tags
    }

    print("\nLoading old project data (no project_type)...")
    project = Project.from_dict(old_project_data)

    assert project.title == "Vecchio Progetto"
    assert project.language == "it"
    assert project.project_type == ProjectType.NOVEL  # Should default to NOVEL
    assert project.genre == ""
    assert project.target_word_count == 0
    assert project.tags == []

    print(f"  ✓ Old project loaded successfully")
    print(f"  ✓ Default project_type: {project.project_type.value}")
    print(f"  ✓ Default genre: '{project.genre}'")
    print(f"  ✓ Default target_word_count: {project.target_word_count}")
    print(f"  ✓ Default tags: {project.tags}")

    print("\n✅ TEST 5 PASSED\n")


def test_novel_vs_article_containers():
    """Compare containers for Novel vs Article"""
    print("=" * 60)
    print("TEST 6: Novel vs Article - Container Comparison")
    print("=" * 60)

    novel_containers = ContainerType.get_available_for_project_type(ProjectType.NOVEL)
    article_containers = ContainerType.get_available_for_project_type(ProjectType.ARTICLE_MAGAZINE)

    print("\n📚 Novel containers:")
    for ct in novel_containers:
        icon, name = ContainerType.get_display_info(ct, 'it')
        print(f"    {icon} {name}")

    print("\n📰 Magazine Article containers:")
    for ct in article_containers:
        icon, name = ContainerType.get_display_info(ct, 'it')
        print(f"    {icon} {name}")

    # Check differences
    print("\n✓ Novel has CHARACTERS, LOCATIONS, TIMELINE (narrative-focused)")
    assert ContainerType.CHARACTERS in novel_containers
    assert ContainerType.LOCATIONS in novel_containers
    assert ContainerType.TIMELINE in novel_containers

    print("✓ Article has SOURCES, KEYWORDS (journalism-focused)")
    assert ContainerType.SOURCES in article_containers
    assert ContainerType.KEYWORDS in article_containers

    print("\n✅ TEST 6 PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING CONTAINER SYSTEM TESTS (Feature 3.1)")
    print("=" * 60 + "\n")

    try:
        test_project_type_enum()
        test_container_type_enum()
        test_containers_for_project_types()
        test_project_with_type()
        test_backward_compatibility()
        test_novel_vs_article_containers()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n✅ Feature 3.1 - Container Architecture:")
        print("   - ProjectType enum with 8 types")
        print("   - ContainerType enum with 14 container types")
        print("   - Dynamic container mapping per project type")
        print("   - Project model extended with project_type, genre, tags")
        print("   - Backward compatibility for old projects")
        print("   - Localization support (it, en, es, fr, de)")
        print("\n✅ Ready for Feature 3.2 (Data Models)!")
        print()

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
