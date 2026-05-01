import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from openai import OpenAI
from dotenv import load_dotenv
from cortex.db import execute_query

load_dotenv()
client = OpenAI(api_key=load_dotenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def natural_language_to_sql(question: str) -> str:
    # Simple rule-based conversion for demo (no API needed)
    import re
    question_lower = question.lower()
    
    # Extract revenue threshold if present (e.g., "$50k", "$100,000", "over $50k")
    revenue_threshold = None
    # Match patterns like $50k, $50,000, 50k, 50000
    match = re.search(r'\$?(\d+,?\d*)\s*[kK]|\$(\d+,?\d*)', question)
    if match:
        amount_str = match.group(1) or match.group(2)
        amount = int(amount_str.replace(',', ''))
        if 'k' in question_lower or 'K' in question:
            amount = amount * 1000
        revenue_threshold = amount
    
    if 'tech stack' in question_lower and revenue_threshold and revenue_threshold >= 10000:
        return f"""
            SELECT founder_name, startup_name, tech_stack, revenue_amount, revenue_frequency 
            FROM knowledge_nodes 
            WHERE revenue_amount > {revenue_threshold} AND revenue_frequency = 'monthly'
            ORDER BY revenue_amount DESC
        """
    elif revenue_threshold:
        return f"""
            SELECT founder_name, startup_name, revenue_amount, revenue_frequency, tech_stack
            FROM knowledge_nodes 
            WHERE revenue_amount > {revenue_threshold} AND revenue_frequency = 'monthly'
            ORDER BY revenue_amount DESC
        """
    elif 'revenue' in question_lower and 'month' in question_lower:
        return """
            SELECT founder_name, startup_name, revenue_amount, revenue_frequency 
            FROM knowledge_nodes 
            WHERE revenue_amount IS NOT NULL AND revenue_frequency = 'monthly'
            ORDER BY revenue_amount DESC
        """
    elif 'tech stack' in question_lower:
        return """
            SELECT founder_name, startup_name, tech_stack 
            FROM knowledge_nodes 
            WHERE tech_stack != '[]'
        """
    else:
        return """
            SELECT founder_name, startup_name, revenue_amount, tech_stack 
            FROM knowledge_nodes 
            ORDER BY revenue_amount DESC
        """

def format_results(results, columns):
    if not results:
        return "No results found."
    
    # Create a mapping of column names to indices
    col_idx = {col: idx for idx, col in enumerate(columns)}
    
    output = f"Found {len(results)} results:\n\n"
    for i, row in enumerate(results, 1):
        founder = row[col_idx.get('founder_name', 0)] or 'Unknown'
        startup = row[col_idx.get('startup_name', 1)] or 'Unknown'
        output += f"{i}. {founder} ({startup})\n"
        
        revenue = row[col_idx.get('revenue_amount', -1)] if 'revenue_amount' in col_idx else None
        freq = row[col_idx.get('revenue_frequency', -1)] if 'revenue_frequency' in col_idx else ''
        if revenue:
            output += f"   Revenue: ${revenue:,.0f} {freq or ''}\n"
        else:
            output += "   Revenue: Not specified\n"
        
        tech_idx = col_idx.get('tech_stack', -1)
        if tech_idx >= 0 and row[tech_idx]:
            try:
                tech_stack = json.loads(row[tech_idx])
                output += f"   Tech Stack: {', '.join(tech_stack) if tech_stack else 'Not specified'}\n"
            except:
                pass
        output += "\n"
    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cortex/brain.py \"your question\"")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    print(f"Question: {question}\n")
    
    try:
        sql = natural_language_to_sql(question)
        print(f"SQL: {sql}\n")
        results, columns = execute_query(sql)
        print(format_results(results, columns))
    except Exception as e:
        print(f"Error: {e}")
