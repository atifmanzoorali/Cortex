"""
Phase 3: Self-Healing Protocol
Detects conflicts and auto-heals using timeline reasoning.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from cortex.db import get_all_nodes, execute_query
from cortex.conflict_resolver import log_healing_event, should_auto_heal
from cortex.schema import KnowledgeNode

class HealthChecker:
    """Performs health checks and self-healing on the knowledge base."""
    
    def __init__(self):
        self.issues_found = 0
        self.issues_fixed = 0
        self.log_path = "cortex/healing_events.log"
    
    def run_full_check(self) -> dict:
        """
        Run comprehensive health check on all nodes.
        Returns health report.
        """
        print("[Health Check] Starting full system scan...\n")
        
        rows, columns = get_all_nodes()
        col_idx = {col: idx for idx, col in enumerate(columns)}
        
        report = {
            'total_nodes': len(rows),
            'conflicts_detected': 0,
            'auto_healed': 0,
            'manual_review_needed': 0,
            'details': []
        }
        
        # Group nodes by founder+startup to find conflicts
        node_groups = self._group_nodes(rows, col_idx)
        
        for (founder, startup), nodes in node_groups.items():
            if len(nodes) <= 1:
                continue
            
            # Check for conflicts within group
            conflicts = self._detect_group_conflicts(nodes, col_idx)
            if conflicts:
                report['conflicts_detected'] += len(conflicts)
                report['details'].extend(conflicts)
                
                # Try to auto-heal
                for conflict in conflicts:
                    if self._try_auto_heal(conflict, nodes, col_idx):
                        report['auto_healed'] += 1
                    else:
                        report['manual_review_needed'] += 1
        
        self._print_report(report)
        return report
    
    def _group_nodes(self, rows, col_idx) -> dict:
        """Group nodes by founder and startup name."""
        groups = {}
        for row in rows:
            founder = row[col_idx.get('founder_name', 0)] or 'Unknown'
            startup = row[col_idx.get('startup_name', 1)] or 'Unknown'
            key = (founder, startup)
            if key not in groups:
                groups[key] = []
            groups[key].append(row)
        return groups
    
    def _detect_group_conflicts(self, nodes, col_idx) -> list:
        """Detect conflicts within a group of nodes for same founder/startup."""
        conflicts = []
        
        # Compare each pair
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                conflict = self._compare_nodes(nodes[i], nodes[j], col_idx)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _compare_nodes(self, node1, node2, col_idx) -> dict:
        """Compare two nodes and return conflict info if found."""
        conflict = None
        
        # Compare revenue
        rev1 = node1[col_idx.get('revenue_amount', 5)]
        rev2 = node2[col_idx.get('revenue_amount', 5)]
        
        if rev1 and rev2 and abs(rev1 - rev2) / max(rev1, rev2) > 0.1:
            conflict = {
                'type': 'revenue_conflict',
                'node1_id': node1[0],
                'node2_id': node2[0],
                'field': 'revenue_amount',
                'value1': rev1,
                'value2': rev2,
                'timestamp1': node1[col_idx.get('timestamp', 9)] if col_idx.get('timestamp', 9) < len(node1) else None,
                'timestamp2': node2[col_idx.get('timestamp', 9)] if col_idx.get('timestamp', 9) < len(node2) else None
            }
        
        # Compare tech stacks
        tech1 = json.loads(node1[col_idx.get('tech_stack', 4)]) if node1[col_idx.get('tech_stack', 4)] else []
        tech2 = json.loads(node2[col_idx.get('tech_stack', 4)]) if node2[col_idx.get('tech_stack', 4)] else []
        
        if set(tech1) != set(tech2):
            if conflict is None:
                conflict = {
                    'type': 'tech_stack_conflict',
                    'node1_id': node1[0],
                    'node2_id': node2[0],
                    'field': 'tech_stack',
                    'value1': tech1,
                    'value2': tech2,
                    'timestamp1': node1[col_idx.get('timestamp', 9)],
                    'timestamp2': node2[col_idx.get('timestamp', 9)]
                }
            else:
                conflict['field'] = 'revenue_amount, tech_stack'
        
        return conflict
    
    def _try_auto_heal(self, conflict: dict, nodes: list, col_idx) -> bool:
        """
        Attempt to auto-heal a conflict using timeline reasoning.
        Returns True if healed, False if needs manual review.
        """
        # Simple heuristic: if one node is much newer, use that
        ts1 = conflict.get('timestamp1')
        ts2 = conflict.get('timestamp2')
        
        if ts1 and ts2:
            # Try to parse dates (format: YYYYMMDD)
            try:
                date1 = datetime.strptime(ts1, '%Y%m%d')
                date2 = datetime.strptime(ts2, '%Y%m%d')
                
                # If date2 is newer by >1 year, auto-update
                if (date2 - date1).days > 365:
                    self._heal_conflict(conflict, newer_node_id=conflict['node2_id'], 
                                       older_node_id=conflict['node1_id'])
                    return True
                elif (date1 - date2).days > 365:
                    self._heal_conflict(conflict, newer_node_id=conflict['node1_id'],
                                       older_node_id=conflict['node2_id'])
                    return True
            except:
                pass
        
        # Can't auto-heal, needs manual review
        return False
    
    def _heal_conflict(self, conflict: dict, newer_node_id: str, older_node_id: str):
        """Log a healing event."""
        field = conflict['field']
        newer_value = conflict.get('value2') if newer_node_id == conflict['node2_id'] else conflict.get('value1')
        older_value = conflict.get('value1') if newer_node_id == conflict['node2_id'] else conflict.get('value2')
        
        log_healing_event(
            founder_name="Unknown",  # Would get from node
            startup_name="Unknown",
            field=field,
            old_value=older_value,
            new_value=newer_value,
            reason=f"Newer node {newer_node_id} is >1 year newer than {older_node_id}"
        )
        
        print(f"  [Healed] {field}: {older_value} -> {newer_value} (timeline reasoning)")
    
    def _print_report(self, report: dict):
        """Print a formatted health report."""
        print("\n" + "=" * 50)
        print("HEALTH REPORT")
        print("=" * 50)
        print(f"Total Nodes: {report['total_nodes']}")
        print(f"Conflicts Detected: {report['conflicts_detected']}")
        print(f"Auto-Healed: {report['auto_healed']}")
        print(f"Needs Manual Review: {report['manual_review_needed']}")
        print("=" * 50)
        
        if report['details']:
            print("\nConflict Details:")
            for i, conflict in enumerate(report['details'][:5], 1):  # Show first 5
                print(f"\n{i}. {conflict['type']}")
                print(f"   Field: {conflict['field']}")
                print(f"   Nodes: {conflict['node1_id'][:8]}... vs {conflict['node2_id'][:8]}...")
        
        if report['auto_healed'] > 0:
            print("\n[Done] " + str(report['auto_healed']) + " conflict(s) auto-healed using timeline reasoning")
            print("  See cortex/healing_events.log for details")
        
        if report['manual_review_needed'] > 0:
            print("\n[Review] " + str(report['manual_review_needed']) + " conflict(s) need manual review")
    
    def check_specific_conflict(self, founder_name: str, startup_name: str) -> dict:
        """Check for conflicts for a specific founder/startup."""
        rows, columns = get_all_nodes()
        col_idx = {col: idx for idx, col in enumerate(columns)}
        
        # Filter nodes
        matching = []
        for row in rows:
            fn = row[col_idx.get('founder_name', 0)] or ''
            sn = row[col_idx.get('startup_name', 1)] or ''
            if fn == founder_name and sn == startup_name:
                matching.append(row)
        
        if len(matching) <= 1:
            return {'status': 'no_conflict', 'nodes': len(matching)}
        
        conflicts = self._detect_group_conflicts(matching, col_idx)
        return {'status': 'conflicts_found', 'count': len(conflicts), 'conflicts': conflicts}


def run_health_check():
    """Entry point for CLI --health command."""
    checker = HealthChecker()
    return checker.run_full_check()


if __name__ == "__main__":
    run_health_check()
