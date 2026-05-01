"""
Cortex CLI - Developer Interface
Usage:
    python cortex.py --ingest                    # Initial build / re-ingest
    python cortex.py --ask "question"            # Query with dynamic expansion
    python cortex.py --health                    # Self-healing check (Phase 3)
    python cortex.py --status                    # Show database stats
"""

import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='Cortex Knowledge Brain CLI')
    parser.add_argument('--ingest', action='store_true', help='Ingest transcripts into knowledge base')
    parser.add_argument('--ask', type=str, help='Ask a question (triggers dynamic expansion if needed)')
    parser.add_argument('--health', action='store_true', help='Run self-healing check (Phase 3)')
    parser.add_argument('--status', action='store_true', help='Show database statistics')
    
    args = parser.parse_args()
    
    if args.ingest:
        print("[Cortex] Phase 1: Initial Build")
        print("=" * 40)
        from cortex.ingest import migrate_existing_nodes, run_ingestion
        migrate_existing_nodes()
        run_ingestion()
    
    elif args.ask:
        print("[Query] Question: " + str(args.ask) + "\n")
        from cortex.query_engine import query_with_dynamic_expansion
        result = query_with_dynamic_expansion(args.ask)
        print(result)
    
    elif args.health:
        print("[Health] Cortex Phase 3: Self-Healing Check")
        print("=" * 40)
        from cortex.health_check import run_health_check
        run_health_check()
    
    elif args.status:
        print("[Status] Cortex Database Status")
        print("=" * 40)
        from cortex.db import get_all_nodes
        try:
            rows, columns = get_all_nodes()
            print("Total nodes in database: " + str(len(rows)))
            print("Columns: " + ", ".join(columns))
            
            # Count nodes with dynamic fields
            if 'dynamic_fields' in columns:
                col_idx = columns.index('dynamic_fields')
                dynamic_count = sum(1 for row in rows if row[col_idx] and row[col_idx] != '{}')
                print("Nodes with dynamic fields: " + str(dynamic_count))
            
            # Show learned fields
            print("\nLearned dynamic fields:")
            learned = set()
            for row in rows:
                if row[col_idx] and row[col_idx] != '{}':
                    try:
                        fields = json.loads(row[col_idx])
                        learned.update(fields.keys())
                    except:
                        pass
            if learned:
                for field in sorted(learned):
                    print("  - " + field)
            else:
                print("  (none yet)")
        except Exception as e:
            print("Error: " + str(e))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
