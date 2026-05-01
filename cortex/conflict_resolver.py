import json
from datetime import datetime

LOG_PATH = "cortex/cortex_logs.txt"

def detect_conflict(existing_row, new_node: 'KnowledgeNode') -> bool:
    # Check revenue conflict (>10% difference)
    if existing_row[5] and new_node.revenue_amount:
        old_rev = existing_row[5]
        new_rev = new_node.revenue_amount
        if abs(old_rev - new_rev) / old_rev > 0.1:
            return True
    
    # Check tech stack changes
    old_tech = json.loads(existing_row[4]) if existing_row[4] else []
    if set(old_tech) != set(new_node.tech_stack):
        return True
    
    return False

def log_conflict(existing_row, new_node: 'KnowledgeNode', conflict_fields: list):
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] CONFLICT DETECTED\n")
        f.write(f"  Founder: {new_node.founder_name}\n")
        f.write(f"  Startup: {new_node.startup_name}\n")
        f.write(f"  Existing Node: {existing_row[0]}\n")
        f.write(f"  New Node: {new_node.node_id}\n")
        f.write(f"  Conflicting Fields: {conflict_fields}\n")
        f.write(f"  Action: Flagged both nodes, kept both records\n")
        f.write("-" * 50 + "\n")
