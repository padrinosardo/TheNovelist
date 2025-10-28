#!/usr/bin/env python3
"""
Test script for Container Managers (Feature 3.3)
"""
import sys
import os
import tempfile
import shutil
from pathlib import Path

from managers.container_manager import ContainerManager
from managers.location_manager import LocationManager
from managers.research_manager import ResearchManager
from managers.timeline_manager import TimelineManager
from managers.source_manager import SourceManager
from managers.note_manager import NoteManager
from models.container_type import ContainerType


def test_container_manager():
    """Test ContainerManager basic functionality"""
    print("=" * 60)
    print("TEST 1: ContainerManager - Basic Operations")
    print("=" * 60)

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        container_manager = ContainerManager(temp_dir)

        # Test loading empty container
        locations = container_manager.load_container(ContainerType.LOCATIONS)
        assert len(locations) == 0
        print("✓ Load empty container: OK")

        # Test adding item
        from models.location import Location
        loc = Location(name="Test Location")
        loc_id = container_manager.add_item(ContainerType.LOCATIONS, loc)
        assert loc_id == loc.id
        print(f"✓ Add item: OK (ID: {loc_id[:8]}...)")

        # Test getting item
        retrieved = container_manager.get_item(ContainerType.LOCATIONS, loc_id)
        assert retrieved is not None
        assert retrieved.name == "Test Location"
        print("✓ Get item: OK")

        # Test get all items
        all_items = container_manager.get_all_items(ContainerType.LOCATIONS)
        assert len(all_items) == 1
        print(f"✓ Get all items: {len(all_items)} items")

        # Test save container
        success = container_manager.save_container(ContainerType.LOCATIONS)
        assert success == True
        print("✓ Save container: OK")

        # Verify file was created
        json_file = Path(temp_dir) / "locations.json"
        assert json_file.exists()
        print(f"✓ JSON file created: {json_file.name}")

        # Test reload from disk
        container_manager2 = ContainerManager(temp_dir)
        locations2 = container_manager2.load_container(ContainerType.LOCATIONS)
        assert len(locations2) == 1
        assert locations2[0].name == "Test Location"
        print("✓ Reload from disk: OK")

        # Test update item
        loc.description = "Updated description"
        success = container_manager2.update_item(ContainerType.LOCATIONS, loc_id, loc)
        assert success == True
        print("✓ Update item: OK")

        # Test delete item
        success = container_manager2.delete_item(ContainerType.LOCATIONS, loc_id)
        assert success == True
        assert len(container_manager2.get_all_items(ContainerType.LOCATIONS)) == 0
        print("✓ Delete item: OK")

    print("\n✅ TEST 1 PASSED\n")


def test_location_manager():
    """Test LocationManager"""
    print("=" * 60)
    print("TEST 2: LocationManager")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        images_dir = os.path.join(temp_dir, "images")
        container_manager = ContainerManager(temp_dir)
        location_manager = LocationManager(container_manager, images_dir)

        # Add location
        loc_id = location_manager.add_location(
            name="Castello",
            description="Un antico castello",
            location_type="fortezza"
        )
        print(f"✓ Created location: ID {loc_id[:8]}...")

        # Get location
        loc = location_manager.get_location(loc_id)
        assert loc is not None
        assert loc.name == "Castello"
        print(f"✓ Retrieved location: {loc.name}")

        # Search locations
        results = location_manager.search_locations("castello")
        assert len(results) == 1
        print(f"✓ Search: found {len(results)} result(s)")

        # Get by type
        by_type = location_manager.get_locations_by_type("fortezza")
        assert len(by_type) == 1
        print(f"✓ Get by type: {len(by_type)} location(s)")

        # Save
        location_manager.save()
        print("✓ Saved locations")

        # Delete
        location_manager.delete_location(loc_id)
        assert len(location_manager.get_all_locations()) == 0
        print("✓ Deleted location")

    print("\n✅ TEST 2 PASSED\n")


def test_research_manager():
    """Test ResearchManager"""
    print("=" * 60)
    print("TEST 3: ResearchManager")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        container_manager = ContainerManager(temp_dir)
        research_manager = ResearchManager(container_manager)

        # Add research note
        note_id = research_manager.add_research_note(
            title="Storia Medievale",
            content="Note sulla storia...",
            category="storia"
        )
        print(f"✓ Created research note: ID {note_id[:8]}...")

        # Get note
        note = research_manager.get_research_note(note_id)
        assert note is not None
        note.add_tag("medioevo")
        note.add_tag("storia")
        research_manager.update_research_note(note)
        print(f"✓ Added tags: {note.tags}")

        # Get by category
        by_category = research_manager.get_notes_by_category("storia")
        assert len(by_category) == 1
        print(f"✓ Get by category: {len(by_category)} note(s)")

        # Get by tag
        by_tag = research_manager.get_notes_by_tag("medioevo")
        assert len(by_tag) == 1
        print(f"✓ Get by tag: {len(by_tag)} note(s)")

        # Get all tags
        all_tags = research_manager.get_all_tags()
        assert len(all_tags) == 2
        print(f"✓ All tags: {all_tags}")

        # Search
        results = research_manager.search_notes("storia")
        assert len(results) == 1
        print(f"✓ Search: found {len(results)} result(s)")

    print("\n✅ TEST 3 PASSED\n")


def test_timeline_manager():
    """Test TimelineManager"""
    print("=" * 60)
    print("TEST 4: TimelineManager")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        container_manager = ContainerManager(temp_dir)
        timeline_manager = TimelineManager(container_manager)

        # Add events
        event1_id = timeline_manager.add_timeline_event(
            title="Evento 1",
            date="Anno 100",
            sort_order=10
        )
        event2_id = timeline_manager.add_timeline_event(
            title="Evento 2",
            date="Anno 200",
            sort_order=20
        )
        event3_id = timeline_manager.add_timeline_event(
            title="Evento 3",
            date="Anno 300",
            sort_order=30
        )
        print(f"✓ Created 3 timeline events")

        # Get sorted events
        sorted_events = timeline_manager.get_all_timeline_events(sorted=True)
        assert len(sorted_events) == 3
        assert sorted_events[0].title == "Evento 1"
        assert sorted_events[2].title == "Evento 3"
        print(f"✓ Sorted events: {[e.title for e in sorted_events]}")

        # Reorder event
        timeline_manager.reorder_event(event1_id, 35)
        sorted_events = timeline_manager.get_all_timeline_events(sorted=True)
        assert sorted_events[2].title == "Evento 1"
        print("✓ Reordered event 1 to position 3")

        # Auto-sort
        timeline_manager.auto_sort_events()
        sorted_events = timeline_manager.get_all_timeline_events(sorted=True)
        assert sorted_events[0].sort_order == 0
        assert sorted_events[1].sort_order == 10
        assert sorted_events[2].sort_order == 20
        print("✓ Auto-sorted events")

    print("\n✅ TEST 4 PASSED\n")


def test_source_manager():
    """Test SourceManager"""
    print("=" * 60)
    print("TEST 5: SourceManager")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        container_manager = ContainerManager(temp_dir)
        source_manager = SourceManager(container_manager)

        # Add web source
        source1_id = source_manager.add_source(
            title="Climate Change Study",
            author="Smith, J.",
            url="https://example.com/study",
            source_type="web"
        )
        print("✓ Created web source")

        # Add journal source
        source2_id = source_manager.add_source(
            title="AI Research Paper",
            author="Johnson, M.",
            source_type="journal",
            publisher="IEEE",
            doi="10.1234/example"
        )
        print("✓ Created journal source")

        # Get by type
        web_sources = source_manager.get_web_sources()
        assert len(web_sources) == 1
        print(f"✓ Web sources: {len(web_sources)}")

        academic_sources = source_manager.get_academic_sources()
        assert len(academic_sources) == 1
        print(f"✓ Academic sources: {len(academic_sources)}")

        # Generate bibliography
        bibliography = source_manager.generate_bibliography("apa")
        assert len(bibliography) > 0
        print(f"✓ Generated APA bibliography ({len(bibliography)} chars)")

        # Export BibTeX
        bibtex = source_manager.export_sources_to_bibtex()
        assert "@" in bibtex
        print(f"✓ Exported BibTeX ({len(bibtex)} chars)")

    print("\n✅ TEST 5 PASSED\n")


def test_note_manager():
    """Test NoteManager"""
    print("=" * 60)
    print("TEST 6: NoteManager")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        container_manager = ContainerManager(temp_dir)
        note_manager = NoteManager(container_manager)

        # Add notes
        note1_id = note_manager.add_note(
            title="Idea importante",
            content="Questa è un'idea...",
            color="#FFD700",
            pinned=True
        )
        note2_id = note_manager.add_note(
            title="Nota semplice",
            content="Solo una nota"
        )
        print(f"✓ Created 2 notes")

        # Get pinned notes
        pinned = note_manager.get_pinned_notes()
        assert len(pinned) == 1
        assert pinned[0].title == "Idea importante"
        print(f"✓ Pinned notes: {len(pinned)}")

        # Add tags
        note = note_manager.get_note(note1_id)
        note.add_tag("importante")
        note.add_tag("idea")
        note_manager.update_note(note)
        print(f"✓ Added tags: {note.tags}")

        # Get by tag
        by_tag = note_manager.get_notes_by_tag("importante")
        assert len(by_tag) == 1
        print(f"✓ Get by tag: {len(by_tag)} note(s)")

        # Get by color
        by_color = note_manager.get_notes_by_color("#FFD700")
        assert len(by_color) == 1
        print(f"✓ Get by color: {len(by_color)} note(s)")

        # Search
        results = note_manager.search_notes("idea")
        assert len(results) >= 1
        print(f"✓ Search: found {len(results)} result(s)")

        # Toggle pin
        note_manager.toggle_pin(note2_id)
        assert len(note_manager.get_pinned_notes()) == 2
        print("✓ Toggled pin")

        # Recently modified
        recent = note_manager.get_recently_modified_notes(limit=5)
        assert len(recent) == 2
        print(f"✓ Recently modified: {len(recent)} note(s)")

    print("\n✅ TEST 6 PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING CONTAINER MANAGERS TESTS (Feature 3.3)")
    print("=" * 60 + "\n")

    try:
        test_container_manager()
        test_location_manager()
        test_research_manager()
        test_timeline_manager()
        test_source_manager()
        test_note_manager()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n✅ Feature 3.3 - Container Managers:")
        print("   - ContainerManager: Generic CRUD operations")
        print("   - LocationManager: Locations with image handling")
        print("   - ResearchManager: Research notes with tags/categories")
        print("   - TimelineManager: Events with auto-sorting")
        print("   - SourceManager: Citations with APA/MLA/BibTeX")
        print("   - NoteManager: Generic notes with pins/links/colors")
        print("\n✅ All managers support:")
        print("   - Full CRUD operations")
        print("   - Search and filtering")
        print("   - Persistence to JSON")
        print("   - Specialized methods for each type")
        print("\n✅ Ready for Feature 4.1 (ProjectManager Integration)!")
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
