"""
Phase 1: Initial Build (Structured Extraction)
Processes transcripts into Knowledge Nodes with dynamic field support.
"""

import os
import sys
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from cortex.extract import extract_knowledge
from cortex.db import init_db, insert_node, find_existing, flag_conflict, get_all_nodes
from cortex.conflict_resolver import detect_conflict, log_conflict
from cortex.schema import KnowledgeNode


def run_ingestion(fields_to_extract: Optional[List[str]] = None) -> Tuple[int, int, int]:
    """
    Process all transcripts in Raw_Data/ folder.

    Args:
        fields_to_extract: Optional list of additional fields to extract (Phase 2 support)
    """
    init_db()
    raw_data_dir = "Raw_Data"
    processed = 0
    skipped = 0
    failed = 0

    print(f"Starting ingestion from {raw_data_dir}/")
    if fields_to_extract:
        print(f"Extracting dynamic fields: {fields_to_extract}")

    for filename in os.listdir(raw_data_dir):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(raw_data_dir, filename)
        try:
            node = extract_knowledge(filepath, fields_to_extract)
        except ValueError as e:
            print(f"Skipped {filename}: {e}")
            skipped += 1
            continue
        except Exception as e:
            print(f"Failed {filename}: {e}")
            failed += 1
            continue

        if node is None:
            skipped += 1
            continue

        # Check for conflicts with existing nodes
        existing = find_existing(node.founder_name or "", node.startup_name or "")
        if existing and detect_conflict(existing, node):
            log_conflict(existing, node, {"revenue": "revenue", "tech_stack": "tech_stack"})
            insert_node(node)
            flag_conflict(existing[0], node.node_id)
            print(f"Conflict flagged: {node.founder_name} - {node.startup_name}")
        else:
            insert_node(node)
            print(f"Inserted: {node.founder_name} - {node.startup_name}")

        processed += 1

    print(f"\nDone: {processed} processed, {skipped} skipped, {failed} failed")
    return processed, skipped, failed


def migrate_existing_nodes():
    """
    Migrate existing nodes to add dynamic_fields column support.
    This is safe to run multiple times.
    """
    init_db()
    rows, columns = get_all_nodes()

    # Check if dynamic_fields column exists in results
    if "dynamic_fields" not in columns:
        print("Migration needed: dynamic_fields column not found in query results")
        print("Please run init_db() again to add the column")
        return

    print(f"Migration check complete: {len(rows)} nodes in database")
    print("All nodes now support dynamic fields")


if __name__ == "__main__":
    print("Cortex Phase 1: Initial Build")
    print("=" * 40)
    migrate_existing_nodes()
    run_ingestion()
