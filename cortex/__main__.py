"""
Test runner for Cortex modules.
Run with: python -m cortex
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_schema():
    """Test KnowledgeNode creation and dynamic fields."""
    print("Testing schema.py...")
    from cortex.schema import KnowledgeNode

    # Test basic creation
    node = KnowledgeNode(node_id="test", video_id="abc123")
    assert node.founder_name is None
    assert node.dynamic_fields == {}
    assert node.has_conflict is False
    print("  ✓ KnowledgeNode creation works")

    # Test with dynamic fields
    node_with_fields = KnowledgeNode(
        node_id="test2",
        video_id="def456",
        dynamic_fields={"pivot_reason": "market change"},
    )
    assert node_with_fields.dynamic_fields == {"pivot_reason": "market change"}
    print("  ✓ Dynamic fields work")
    print("Schema tests passed!\n")


def test_db():
    """Test database operations."""
    print("Testing db.py...")
    from cortex.db import init_db, get_all_nodes

    # Test init (should not raise)
    init_db()
    print("  ✓ init_db() works")

    # Test get_all_nodes
    rows, columns = get_all_nodes()
    assert isinstance(rows, list)
    assert isinstance(columns, list)
    print(f"  ✓ get_all_nodes() returned {len(rows)} rows, {len(columns)} columns")
    print("DB tests passed!\n")


def test_conflict_resolver():
    """Test conflict detection."""
    print("Testing conflict_resolver.py...")
    from cortex.conflict_resolver import detect_conflict, should_auto_heal

    # Create a mock existing row
    existing_row = (
        "node1",
        "vid1",
        "John",
        "Startup",
        "[]",
        100000,
        "monthly",
        "USD",
        "[]",
        "20240101",
        0,
        None,
        "2024-01-01T00:00:00",
        "{}",
    )

    from cortex.schema import KnowledgeNode

    new_node = KnowledgeNode(
        node_id="node2",
        video_id="vid2",
        founder_name="John",
        startup_name="Startup",
        revenue_amount=200000,
        timestamp="20240601",
    )

    # Test conflict detection
    result = detect_conflict(existing_row, new_node)
    assert result["has_conflict"] is True
    assert "revenue" in result["fields"]
    print("  ✓ Conflict detection works")
    print("Conflict resolver tests passed!\n")


def test_health_check():
    """Test health checker initialization."""
    print("Testing health_check.py...")
    from cortex.health_check import HealthChecker

    checker = HealthChecker()
    assert checker.issues_found == 0
    assert checker.issues_fixed == 0
    print("  ✓ HealthChecker initialization works")
    print("Health check tests passed!\n")


def test_query_engine():
    """Test query engine initialization."""
    print("Testing query_engine.py...")
    from cortex.query_engine import DynamicSchemaManager

    manager = DynamicSchemaManager()
    assert isinstance(manager.learned_fields, set)
    assert isinstance(manager.CORE_FIELDS, list)
    print("  ✓ DynamicSchemaManager initialization works")

    # Test field identification
    field = manager.identify_missing_field("What is the funding status?")
    assert field is not None
    print("  ✓ Field identification works")
    print("Query engine tests passed!\n")


def test_extract():
    """Test extract module imports."""
    print("Testing extract.py...")
    from cortex.extract import extract_knowledge

    assert callable(extract_knowledge)
    print("  ✓ extract_knowledge function imported")
    print("Extract tests passed!\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Cortex Module Tests")
    print("=" * 50 + "\n")

    try:
        test_schema()
        test_db()
        test_conflict_resolver()
        test_health_check()
        test_query_engine()
        test_extract()

        print("=" * 50)
        print("ALL TESTS PASSED! ✓")
        print("=" * 50)
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
