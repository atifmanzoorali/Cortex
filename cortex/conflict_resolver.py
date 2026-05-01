import json
from datetime import datetime
from typing import List, Dict, Optional

LOG_PATH = "cortex/cortex_logs.txt"
HEALING_LOG_PATH = "cortex/healing_events.log"

def detect_conflict(existing_row, new_node: 'KnowledgeNode') -> Dict[str, any]:
    """
    Detect conflicts between existing and new node.
    Returns dict with conflict info including timeline reasoning.
    """
    conflicts = {
        'has_conflict': False,
        'fields': [],
        'old_values': {},
        'new_values': {},
        'reasoning': ''
    }
    
    # Get timestamps for timeline reasoning
    existing_timestamp = existing_row[9] if len(existing_row) > 9 else None  # timestamp column
    new_timestamp = new_node.timestamp
    
    # Check revenue conflict (>10% difference)
    if existing_row[5] and new_node.revenue_amount:
        old_rev = existing_row[5]
        new_rev = new_node.revenue_amount
        if abs(old_rev - new_rev) / old_rev > 0.1:
            conflicts['has_conflict'] = True
            conflicts['fields'].append('revenue')
            conflicts['old_values']['revenue'] = old_rev
            conflicts['new_values']['revenue'] = new_rev
            
            # Timeline reasoning
            if existing_timestamp and new_timestamp:
                if new_timestamp > existing_timestamp:
                    conflicts['reasoning'] += "New data (" + str(new_timestamp) + ") is newer than existing (" + str(existing_timestamp) + "). "
                    conflicts['reasoning'] += "Revenue changed from $" + format(old_rev, ',.0f') + " to $" + format(new_rev, ',.0f') + ". "
                else:
                    conflicts['reasoning'] += "Existing data (" + str(existing_timestamp) + ") is newer than new (" + str(new_timestamp) + "). "
    
    # Check tech stack changes
    old_tech = json.loads(existing_row[4]) if existing_row[4] else []
    if set(old_tech) != set(new_node.tech_stack):
        conflicts['has_conflict'] = True
        conflicts['fields'].append('tech_stack')
        conflicts['old_values']['tech_stack'] = old_tech
        conflicts['new_values']['tech_stack'] = new_node.tech_stack
        
        # Check for migrations (e.g., AWS to Vercel)
        if existing_timestamp and new_timestamp:
            if new_timestamp > existing_timestamp:
                conflicts['reasoning'] += "Tech stack evolved from " + str(old_tech) + " to " + str(new_node.tech_stack) + ". "
    
    return conflicts

def log_conflict(existing_row, new_node: 'KnowledgeNode', conflict_info: Dict):
    """Log conflict to cortex_logs.txt with timeline reasoning."""
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write("[" + datetime.now().isoformat() + "] CONFLICT DETECTED\n")
        f.write("  Founder: " + str(new_node.founder_name) + "\n")
        f.write("  Startup: " + str(new_node.startup_name) + "\n")
        f.write("  Existing Node: " + str(existing_row[0]) + "\n")
        f.write("  New Node: " + str(new_node.node_id) + "\n")
        f.write("  Conflicting Fields: " + str(conflict_info['fields']) + "\n")
        f.write("  Old Values: " + str(conflict_info['old_values']) + "\n")
        f.write("  New Values: " + str(conflict_info['new_values']) + "\n")
        f.write("  Timeline Reasoning: " + str(conflict_info['reasoning']) + "\n")
        f.write("  Action: Flagged both nodes, kept both records\n")
        f.write("-" * 50 + "\n")

def log_healing_event(founder_name: str, startup_name: str, field: str, 
                      old_value: any, new_value: any, reason: str):
    """Log self-healing events to healing_events.log."""
    with open(HEALING_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write("[" + datetime.now().isoformat() + "] HEALING EVENT\n")
        f.write("  Founder: " + str(founder_name) + "\n")
        f.write("  Startup: " + str(startup_name) + "\n")
        f.write("  Field: " + str(field) + "\n")
        f.write("  Old Value: " + str(old_value) + "\n")
        f.write("  New Value: " + str(new_value) + "\n")
        f.write("  Reason: " + str(reason) + "\n")
        f.write("-" * 50 + "\n")

def should_auto_heal(conflict_info: Dict, time_threshold_days: int = 365) -> bool:
    """
    Determine if we should automatically update the primary node.
    Auto-heal if new data is significantly newer (>1 year).
    """
    # Simple heuristic: if new data is much newer, it's likely more accurate
    # In production, this would use actual date parsing
    return len(conflict_info['fields']) > 0 and 'newer' in conflict_info['reasoning'].lower()
