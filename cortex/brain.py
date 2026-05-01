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
    question_lower = question.lower()
    
    if 'tech stack' in question_lower and ('$10k' in question_lower or '10000' in question_lower or '>10' in question_lower):
        return """
            SELECT founder_name, startup_name, tech_stack, revenue_amount, revenue_frequency 
            FROM knowledge_nodes 
            WHERE revenue_amount > 10000 AND revenue_frequency = 'monthly'
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
            LIMIT 10
        """

def format_results(results, columns):
    if not results:
        return "No results found."
    
    output = f"Found {len(results)} results:\n\n"
    for i, row in enumerate(results, 1):
        output += f"{i}. {row[2]} ({row[3]})\n"  # founder_name, startup_name
        output += f"   Revenue: ${row[5]:,.0f} {row[6]}\n" if row[5] else "   Revenue: Not specified\n"
        tech_stack = json.loads(row[4]) if row[4] else []
        output += f"   Tech Stack: {', '.join(tech_stack) if tech_stack else 'Not specified'}\n"
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
