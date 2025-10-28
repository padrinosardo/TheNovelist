#!/usr/bin/env python3
"""
Test script for Data Models (Feature 3.2)
"""
import sys
from models.location import Location
from models.research_note import ResearchNote
from models.timeline_event import TimelineEvent
from models.source import Source
from models.note import Note


def test_location_model():
    """Test Location data model"""
    print("=" * 60)
    print("TEST 1: Location Model")
    print("=" * 60)

    # Create location
    location = Location(
        name="Castello di Dragonstone",
        description="Un'antica fortezza sulla costa rocciosa",
        location_type="castello",
        notes="Luogo chiave per i primi capitoli"
    )

    print(f"\nCreated location:")
    print(f"  Name: {location.name}")
    print(f"  Type: {location.location_type}")
    print(f"  ID: {location.id}")
    print(f"  Created: {location.created_date[:19]}")

    # Test methods
    location.add_image("castle1.jpg")
    location.add_image("castle2.jpg")
    location.add_character("char-123")
    location.add_character("char-456")

    print(f"\n✓ Added 2 images: {location.images}")
    print(f"✓ Added 2 characters: {location.characters_present}")

    # Test serialization
    location_dict = location.to_dict()
    assert location_dict['name'] == "Castello di Dragonstone"
    assert len(location_dict['images']) == 2
    assert len(location_dict['characters_present']) == 2
    print("✓ Serialization OK")

    # Test deserialization
    location2 = Location.from_dict(location_dict)
    assert location2.name == location.name
    assert location2.images == location.images
    print("✓ Deserialization OK")

    print("\n✅ TEST 1 PASSED\n")


def test_research_note_model():
    """Test ResearchNote data model"""
    print("=" * 60)
    print("TEST 2: ResearchNote Model")
    print("=" * 60)

    # Create research note
    note = ResearchNote(
        title="Storia della Siderurgia Medievale",
        content="Nel medioevo, la produzione del ferro avveniva attraverso...",
        category="storia"
    )

    print(f"\nCreated research note:")
    print(f"  Title: {note.title}")
    print(f"  Category: {note.category}")
    print(f"  ID: {note.id}")

    # Test methods
    note.add_source("https://example.com/medieval-iron")
    note.add_source("Libro: Storia della Metallurgia")
    note.add_tag("medioevo")
    note.add_tag("tecnologia")
    note.add_tag("armi")

    print(f"\n✓ Added 2 sources: {len(note.sources)}")
    print(f"✓ Added 3 tags: {note.tags}")
    print(f"✓ Has tag 'medioevo': {note.has_tag('medioevo')}")

    # Test serialization
    note_dict = note.to_dict()
    assert note_dict['title'] == "Storia della Siderurgia Medievale"
    assert len(note_dict['sources']) == 2
    assert len(note_dict['tags']) == 3
    print("✓ Serialization OK")

    # Test deserialization
    note2 = ResearchNote.from_dict(note_dict)
    assert note2.title == note.title
    assert note2.tags == note.tags
    print("✓ Deserialization OK")

    print("\n✅ TEST 2 PASSED\n")


def test_timeline_event_model():
    """Test TimelineEvent data model"""
    print("=" * 60)
    print("TEST 3: TimelineEvent Model")
    print("=" * 60)

    # Create timeline event
    event = TimelineEvent(
        title="Battaglia di Blackwater",
        date="Anno 298 AC",
        description="Una battaglia navale decisiva per la difesa della capitale",
        sort_order=10
    )

    print(f"\nCreated timeline event:")
    print(f"  Title: {event.title}")
    print(f"  Date: {event.date}")
    print(f"  Sort Order: {event.sort_order}")
    print(f"  ID: {event.id}")

    # Test methods
    event.add_character("char-123")
    event.add_character("char-456")
    event.add_location("loc-789")

    print(f"\n✓ Added 2 characters: {event.characters}")
    print(f"✓ Added 1 location: {event.locations}")

    # Test serialization
    event_dict = event.to_dict()
    assert event_dict['title'] == "Battaglia di Blackwater"
    assert event_dict['sort_order'] == 10
    assert len(event_dict['characters']) == 2
    print("✓ Serialization OK")

    # Test deserialization
    event2 = TimelineEvent.from_dict(event_dict)
    assert event2.title == event.title
    assert event2.sort_order == event.sort_order
    print("✓ Deserialization OK")

    print("\n✅ TEST 3 PASSED\n")


def test_source_model():
    """Test Source data model"""
    print("=" * 60)
    print("TEST 4: Source Model")
    print("=" * 60)

    # Create source (web)
    source_web = Source(
        title="The Impact of Climate Change on Biodiversity",
        author="Smith, J. & Brown, A.",
        url="https://example.com/climate-biodiversity",
        source_type="web"
    )

    print(f"\nCreated web source:")
    print(f"  Title: {source_web.title}")
    print(f"  Author: {source_web.author}")
    print(f"  Type: {source_web.source_type}")
    print(f"  URL: {source_web.url}")
    print(f"  Is web source: {source_web.is_web_source()}")

    # Create source (journal)
    source_journal = Source(
        title="Neural Networks in Natural Language Processing",
        author="Johnson, M.",
        source_type="journal",
        publisher="IEEE Transactions",
        publication_date="2023",
        doi="10.1234/example.doi"
    )

    print(f"\nCreated journal source:")
    print(f"  Title: {source_journal.title}")
    print(f"  Publisher: {source_journal.publisher}")
    print(f"  DOI: {source_journal.doi}")
    print(f"  Is academic source: {source_journal.is_academic_source()}")

    # Test citation generation
    apa_citation = source_web.generate_apa_citation()
    print(f"\n✓ Generated APA citation:")
    print(f"  {apa_citation}")

    mla_citation = source_web.generate_mla_citation()
    print(f"✓ Generated MLA citation:")
    print(f"  {mla_citation}")

    # Test serialization
    source_dict = source_web.to_dict()
    assert source_dict['title'] == "The Impact of Climate Change on Biodiversity"
    assert source_dict['source_type'] == "web"
    print("✓ Serialization OK")

    # Test deserialization
    source2 = Source.from_dict(source_dict)
    assert source2.title == source_web.title
    assert source2.url == source_web.url
    print("✓ Deserialization OK")

    print("\n✅ TEST 4 PASSED\n")


def test_note_model():
    """Test Note data model"""
    print("=" * 60)
    print("TEST 5: Note Model")
    print("=" * 60)

    # Create note
    note = Note(
        title="Idea per il finale",
        content="Il protagonista scopre che l'antagonista era in realtà suo fratello...",
        color="#FFD700"
    )

    print(f"\nCreated note:")
    print(f"  Title: {note.title}")
    print(f"  Word Count: {note.get_word_count()}")
    print(f"  Color: {note.color}")
    print(f"  Pinned: {note.pinned}")
    print(f"  ID: {note.id}")

    # Test methods
    note.add_tag("plot")
    note.add_tag("twist")
    note.add_tag("finale")
    note.toggle_pin()
    note.link_to_character("char-123")

    print(f"\n✓ Added 3 tags: {note.tags}")
    print(f"✓ Pinned: {note.pinned}")
    print(f"✓ Linked to character: {note.linked_to_character}")
    print(f"✓ Has links: {note.has_links()}")

    # Test serialization
    note_dict = note.to_dict()
    assert note_dict['title'] == "Idea per il finale"
    assert note_dict['pinned'] == True
    assert len(note_dict['tags']) == 3
    assert note_dict['color'] == "#FFD700"
    print("✓ Serialization OK")

    # Test deserialization
    note2 = Note.from_dict(note_dict)
    assert note2.title == note.title
    assert note2.pinned == note.pinned
    assert note2.tags == note.tags
    print("✓ Deserialization OK")

    print("\n✅ TEST 5 PASSED\n")


def test_all_models_serialization():
    """Test that all models can be serialized and deserialized"""
    print("=" * 60)
    print("TEST 6: All Models - Round-trip Serialization")
    print("=" * 60)

    models = [
        ("Location", Location(name="Test Location")),
        ("ResearchNote", ResearchNote(title="Test Research")),
        ("TimelineEvent", TimelineEvent(title="Test Event")),
        ("Source", Source(title="Test Source")),
        ("Note", Note(title="Test Note"))
    ]

    print("\nTesting round-trip serialization for all models:")
    for model_name, model in models:
        # Serialize
        data = model.to_dict()

        # Deserialize
        model_class = type(model)
        restored = model_class.from_dict(data)

        # Verify
        assert restored.id == model.id
        assert restored.created_date == model.created_date

        print(f"  ✓ {model_name}: OK (ID: {restored.id[:8]}...)")

    print("\n✅ TEST 6 PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING DATA MODELS TESTS (Feature 3.2)")
    print("=" * 60 + "\n")

    try:
        test_location_model()
        test_research_note_model()
        test_timeline_event_model()
        test_source_model()
        test_note_model()
        test_all_models_serialization()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n✅ Feature 3.2 - Data Models:")
        print("   - Location: Places with images, characters, hierarchy")
        print("   - ResearchNote: Research with sources, tags, categories")
        print("   - TimelineEvent: Chronological events with sort order")
        print("   - Source: Citations with APA/MLA generation")
        print("   - Note: Generic notes with tags, links, colors, pinning")
        print("\n✅ All models support:")
        print("   - UUID generation")
        print("   - Automatic timestamps")
        print("   - Full serialization/deserialization")
        print("   - Helper methods for common operations")
        print("\n✅ Ready for Feature 3.3 (Container Managers)!")
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
