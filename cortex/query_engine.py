"""
Phase 2: Dynamic Schema Expansion
Handles the "Infinite Question" problem by dynamically learning new fields.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
from datetime import datetime
from openai import OpenAI
from cortex.db import init_db, get_all_nodes, execute_query
from cortex.extract import extract_knowledge

API_KEY = 'sk-a3b5eb71e73f4561aa3b1d439fc4a2ed'
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

class DynamicSchemaManager:
    """Manages dynamic field expansion for Cortex."""
    
    # Core fields that are always available
    CORE_FIELDS = ['founder_name', 'startup_name', 'tech_stack', 'revenue_amount', 
                   'revenue_frequency', 'key_lessons', 'timestamp']
    
    def __init__(self):
        self.raw_data_dir = "Raw_Data"
        self.learned_fields = set()
        self._load_learned_fields()
    
    def _load_learned_fields(self):
        """Load already-learned fields from database."""
        try:
            rows, columns = get_all_nodes()
            if 'dynamic_fields' in columns:
                for row in rows:
                    col_idx = columns.index('dynamic_fields')
                    if row[col_idx]:
                        try:
                            fields = json.loads(row[col_idx])
                            self.learned_fields.update(fields.keys())
                        except:
                            pass
        except:
            pass
    
    def identify_missing_field(self, question: str) -> str:
        """
        Identify what new field the user is asking about.
        Returns the field name or None if it's a core field question.
        """
        question_lower = question.lower()
        
        # Common field mappings
        field_patterns = {
            'relationship_status': ['single', 'married', 'relationship', 'girlfriend', 'boyfriend', 'wife', 'husband'],
            'morning_routine': ['morning routine', 'wake up', 'daily routine', 'schedule'],
            'cofounder_info': ['cofounder', 'co-founder', 'partner', 'started with'],
            'pivot_reason': ['pivot', 'why did you change', 'switched from', 'originally'],
            'funding_status': ['funding', 'raised', 'investment', 'bootstrapped', 'vc'],
            'location': ['where', 'location', 'based in', 'city', 'country'],
            'age': ['old', 'age', 'how old', 'born'],
            'background': ['background', 'previous job', 'worked at', 'before starting'],
        }
        
        for field, keywords in field_patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                return field
        
        # Try to infer field name from question
        # Look for patterns like "what is their X" or "how many X"
        patterns = [
            r'what (is|are) their (.+?)\??$',
            r'how many (.+?) (are|have|is)',
            r'list all (.+?)',
            r'show me (.+?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question_lower)
            if match:
                field = match.group(2) if len(match.groups()) > 1 else match.group(1)
                field = field.strip().replace(' ', '_')
                return field
        
        return None
    
    def search_transcripts(self, field: str) -> list:
        """
        Search Raw_Data transcripts for mentions of the field topic.
        Returns list of (filename, filepath) tuples sorted by relevance.
        """
        results = []
        
        if not os.path.exists(self.raw_data_dir):
            return results
        
        # Define keyword mappings for common fields
        keyword_map = {
            'relationship_status': ['wife', 'husband', 'girlfriend', 'boyfriend', 'married', 'single', 'relationship', 'spouse', 'partner'],
            'morning_routine': ['morning', 'wake up', 'routine', 'schedule', 'daily', 'breakfast', 'start my day'],
            'cofounder_info': ['cofounder', 'co-founder', 'partner', 'started with', 'founded with', 'together with'],
            'pivot_reason': ['pivot', 'changed', 'switched', 'originally', 'started as', 'moved to', 'shifted'],
            'funding_status': ['funding', 'raised', 'investment', 'investor', 'vc', 'bootstrapped', 'self-funded'],
            'location': ['location', 'based in', 'city', 'country', 'live in', 'from', 'san francisco', 'new york'],
            'age': ['age', 'old', 'born', 'year old', 'how old'],
            'background': ['background', 'previous', 'worked at', 'before starting', 'formerly', 'previously'],
        }
        
        # Get keywords for this field
        keywords = keyword_map.get(field, field.replace('_', ' ').split())
        
        for filename in os.listdir(self.raw_data_dir):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(self.raw_data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                transcript = data.get('transcript', '').lower()
                if not transcript:
                    continue
                
                # Keyword matching for relevance
                score = 0
                for keyword in keywords:
                    score += transcript.count(keyword.lower()) * 10
                
                # Also check metadata
                metadata = data.get('metadata', {})
                title = metadata.get('title', '').lower()
                description = metadata.get('description', '').lower()
                
                for keyword in keywords:
                    score += title.count(keyword.lower()) * 50
                    score += description.count(keyword.lower()) * 30
                
                if score > 0:
                    results.append((filename, score, filepath))
            except:
                continue
        
        # Sort by relevance score
        results.sort(key=lambda x: x[1], reverse=True)
        return [(r[0], r[2]) for r in results]  # Return (filename, filepath)
    
    def extract_field_from_transcript(self, json_path: str, field: str, question: str) -> any:
        """
        Use LLM to extract the specific field from a transcript.
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            transcript = data.get('transcript', '')
            if not transcript:
                return None
            
            prompt = f"""Extract the following information from this YouTube transcript. Return ONLY valid JSON.

Question: {question}
Field to extract: {field}

Transcript excerpt (first 3000 chars):
{transcript[:3000]}

Extract the value for "{field}" and return JSON:
{{
  "{field}": "extracted value here, or null if not mentioned"
}}

JSON output:"""
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get(field)
        except:
            return None
    
    def learn_field(self, field: str, question: str, update_db: bool = True) -> dict:
        """
        Learn a new field by scanning all relevant transcripts.
        Returns a dict with extraction statistics.
        """
        print(f"\n[Learning] Cortex is learning a new field: '{field}'")
        print(f"   Searching transcripts in {self.raw_data_dir}/...")
        
        relevant_files = self.search_transcripts(field)
        
        if not relevant_files:
            print(f"   ⚠️  No relevant transcripts found for '{field}'")
            return {'field': field, 'extracted': 0, 'total': 0}
        
        print(f"   Found {len(relevant_files)} potentially relevant transcripts")
        
        extracted = 0
        total = 0
        
        for filename, filepath in relevant_files:
            total += 1
            value = self.extract_field_from_transcript(filepath, field, question)
            
            if value is not None:
                # Update database
                if update_db:
                    self._update_node_with_field(filepath, field, value)
                extracted += 1
                print(f"   [OK] Extracted '{field}' from {filename}")
            else:
                print(f"   [X] No '{field}' found in {filename}")
        
        self.learned_fields.add(field)
        
        # Log the learning event
        self._log_learning_event(field, extracted, total)
        
        print(f"\n[Done] Cortex learned '{field}': {extracted}/{total} transcripts processed")
        
        return {'field': field, 'extracted': extracted, 'total': total}
    
    def _update_node_with_field(self, json_path: str, field: str, value: any):
        """Update a node in the database with a new dynamic field."""
        import sqlite3
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            video_id = data.get('video_id', '')
            
            conn = sqlite3.connect("cortex/knowledge_base.db")
            
            # Get current dynamic_fields for this node
            cursor = conn.execute(
                "SELECT dynamic_fields FROM knowledge_nodes WHERE video_id = ?",
                (video_id,)
            )
            row = cursor.fetchone()
            
            if row and row[0]:
                dynamic_fields = json.loads(row[0])
            else:
                dynamic_fields = {}
            
            # Update the field
            dynamic_fields[field] = value
            
            # Save back to database
            conn.execute(
                "UPDATE knowledge_nodes SET dynamic_fields = ? WHERE video_id = ?",
                (json.dumps(dynamic_fields), video_id)
            )
            conn.commit()
            conn.close()
        except:
            pass
    
    def _log_learning_event(self, field: str, extracted: int, total: int):
        """Log when Cortex learns a new field."""
        log_path = "cortex/learning_events.log"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] LEARNED NEW FIELD\n")
            f.write(f"  Field: {field}\n")
            f.write(f"  Extracted from: {extracted}/{total} transcripts\n")
            f.write(f"  Status: Now available for all future queries\n")
            f.write("-" * 50 + "\n")


def query_with_dynamic_expansion(question: str) -> str:
    """
    Main query function that handles dynamic schema expansion.
    """
    manager = DynamicSchemaManager()
    
    # Check if this is asking about a non-core field
    missing_field = manager.identify_missing_field(question)
    
    if missing_field and missing_field not in manager.CORE_FIELDS:
        # This is a dynamic field question
        print(f"[Thinking] I don't have '{missing_field}' data yet. Let me learn it...")
        
        # Learn the field
        stats = manager.learn_field(missing_field, question)
        
        if stats['extracted'] == 0:
            return f"Sorry, I couldn't find any information about '{missing_field}' in the transcripts."
    
    # Now query the database
    return execute_dynamic_query(question, manager)


def execute_dynamic_query(question: str, manager: DynamicSchemaManager) -> str:
    """
    Execute a query that may involve dynamic fields.
    """
    import sqlite3
    
    conn = sqlite3.connect("cortex/knowledge_base.db")
    cursor = conn.execute("SELECT * FROM knowledge_nodes")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    
    if not rows:
        return "No data found in the knowledge base."
    
    # Build result based on question
    question_lower = question.lower()
    
    # Check if asking about dynamic fields
    for field in manager.learned_fields:
        if field.lower() in question_lower or field.lower() in manager.identify_missing_field(question).lower():
            return format_dynamic_field_results(rows, columns, field)
    
    # Fall back to basic info
    return format_basic_results(rows, columns)


def format_dynamic_field_results(rows, columns, field: str):
    """Format results for a dynamic field query."""
    col_idx = {col: idx for idx, col in enumerate(columns)}
    
    # Filter rows that have this field
    results = []
    for row in rows:
        dynamic_fields_str = row[col_idx.get('dynamic_fields', -1)]
        if dynamic_fields_str:
            try:
                dynamic_fields = json.loads(dynamic_fields_str)
                if field in dynamic_fields and dynamic_fields[field]:
                    founder = row[col_idx.get('founder_name', 0)] or 'Unknown'
                    startup = row[col_idx.get('startup_name', 1)] or 'Unknown'
                    results.append((founder, startup, dynamic_fields[field]))
            except:
                pass
    
    if not results:
        return f"No data found for '{field}'."
    
    output = f"Found {len(results)} results for '{field}':\n\n"
    for i, (founder, startup, value) in enumerate(results, 1):
        output += f"{i}. {founder} ({startup}): {value}\n"
    
    return output


def format_basic_results(rows, columns):
    """Format basic results (fallback)."""
    col_idx = {col: idx for idx, col in enumerate(columns)}
    
    output = f"Found {len(rows)} results:\n\n"
    for i, row in enumerate(rows, 1):
        founder = row[col_idx.get('founder_name', 0)] or 'Unknown'
        startup = row[col_idx.get('startup_name', 1)] or 'Unknown'
        output += f"{i}. {founder} ({startup})\n"
    
    return output


if __name__ == "__main__":
    # Test the dynamic schema manager
    manager = DynamicSchemaManager()
    
    # Test with a question
    test_question = "How many founders are single?"
    print(f"Test question: {test_question}\n")
    
    missing_field = manager.identify_missing_field(test_question)
    print(f"Identified missing field: {missing_field}\n")
    
    if missing_field:
        stats = manager.learn_field(missing_field, test_question)
        print(f"\nStats: {stats}")
