import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from cortex.extract import extract_knowledge
from cortex.db import init_db, insert_node, find_existing, flag_conflict
from cortex.conflict_resolver import detect_conflict, log_conflict
from cortex.schema import KnowledgeNode

def run_ingestion():
    init_db()
    raw_data_dir = "Raw_Data"
    processed = 0
    skipped = 0
    failed = 0
    
    for filename in os.listdir(raw_data_dir):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(raw_data_dir, filename)
        try:
            node = extract_knowledge(filepath)
        except ValueError as e:
            print(f"Skipped {filename}: {e}")
            skipped += 1
            continue
        except Exception as e:
            print(f"Failed {filename}: {e}")
            failed += 1
            continue
        
        # Check for conflicts
        existing = find_existing(node.founder_name, node.startup_name)
        if existing and detect_conflict(existing, node):
            log_conflict(existing, node, ["revenue", "tech_stack"])
            insert_node(node)
            flag_conflict(existing[0], node.node_id)
            print(f"Conflict flagged: {node.founder_name} - {node.startup_name}")
        else:
            insert_node(node)
            print(f"Inserted: {node.founder_name} - {node.startup_name}")
        
        processed += 1
    
    print(f"\nDone: {processed} processed, {skipped} skipped, {failed} failed")

if __name__ == "__main__":
    run_ingestion()
