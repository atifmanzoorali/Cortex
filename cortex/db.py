import sqlite3
import json
from cortex.schema import KnowledgeNode

DB_PATH = "cortex/knowledge_base.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_nodes (
            node_id TEXT PRIMARY KEY,
            video_id TEXT,
            founder_name TEXT,
            startup_name TEXT,
            tech_stack TEXT,
            revenue_amount REAL,
            revenue_frequency TEXT,
            revenue_currency TEXT,
            key_lessons TEXT,
            timestamp TEXT,
            has_conflict INTEGER DEFAULT 0,
            conflict_with_node_id TEXT,
            created_at TEXT,
            dynamic_fields TEXT DEFAULT '{}'
        )
    """)
    # Add dynamic_fields column if it doesn't exist (migration for existing DB)
    try:
        conn.execute(
            "ALTER TABLE knowledge_nodes ADD COLUMN dynamic_fields TEXT DEFAULT '{}'"
        )
    except:
        pass  # Column already exists
    conn.commit()
    conn.close()


def insert_node(node: KnowledgeNode):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO knowledge_nodes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,
        (
            node.node_id,
            node.video_id,
            node.founder_name,
            node.startup_name,
            json.dumps(node.tech_stack),
            node.revenue_amount,
            node.revenue_frequency,
            node.revenue_currency,
            json.dumps(node.key_lessons),
            node.timestamp,
            1 if node.has_conflict else 0,
            node.conflict_with_node_id,
            node.created_at,
            json.dumps(node.dynamic_fields),
        ),
    )
    conn.commit()
    conn.close()


def find_existing(founder_name: str, startup_name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        """
        SELECT * FROM knowledge_nodes 
        WHERE founder_name = ? AND startup_name = ? AND has_conflict = 0
    """,
        (founder_name, startup_name),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_nodes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT * FROM knowledge_nodes")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    return rows, columns


def flag_conflict(node_id: str, conflict_with_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE knowledge_nodes SET has_conflict = 1, conflict_with_node_id = ? WHERE node_id = ?",
        (conflict_with_id, node_id),
    )
    conn.execute(
        "UPDATE knowledge_nodes SET has_conflict = 1, conflict_with_node_id = ? WHERE node_id = ?",
        (node_id, conflict_with_id),
    )
    conn.commit()
    conn.close()


def execute_query(sql: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(sql)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    return results, columns
