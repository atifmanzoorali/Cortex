import os
import json
import re
import time
from datetime import datetime
from cortex.schema import KnowledgeNode
import uuid

def extract_knowledge(json_path: str) -> KnowledgeNode:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    transcript = data.get('transcript', '')
    metadata = data.get('metadata', {})
    video_id = data.get('video_id', '')
    
    if not transcript:
        raise ValueError("Empty transcript")
    
    # Try DeepSeek API first
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            
            prompt = f"""
Extract founder insights from this YouTube transcript. Return ONLY valid JSON matching this schema:
{{
  "founder_name": "string",
  "startup_name": "string", 
  "tech_stack": ["string"],
  "revenue_amount": float or null,
  "revenue_frequency": "monthly|annual|one-time",
  "key_lessons": ["string"]
}}

Video Title: {metadata.get('title', '')}
Upload Date: {metadata.get('upload_date', '')}

Transcript:
{transcript[:8000]}

JSON output:
"""
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            result = json.loads(response.choices[0].message.content)
            
            return KnowledgeNode(
                node_id=str(uuid.uuid4()),
                video_id=video_id,
                founder_name=result.get('founder_name', ''),
                startup_name=result.get('startup_name', ''),
                tech_stack=result.get('tech_stack', []),
                revenue_amount=result.get('revenue_amount'),
                revenue_frequency=result.get('revenue_frequency', 'monthly'),
                revenue_currency='USD',
                key_lessons=result.get('key_lessons', []),
                timestamp=metadata.get('upload_date', ''),
                has_conflict=False,
                conflict_with_node_id=None
            )
        except Exception as e:
            print(f"  API failed, using fallback extraction: {e}")
    
    # Fallback: Rule-based extraction
    return fallback_extract(transcript, metadata, video_id)

def fallback_extract(transcript: str, metadata: dict, video_id: str) -> KnowledgeNode:
    """Extract basic info using regex patterns (for demo/fallback)"""
    title = metadata.get('title', '')
    description = metadata.get('description', '')
    full_text = f"{title} {description} {transcript}"
    
    # Extract revenue
    revenue_amount = None
    revenue_frequency = 'monthly'
    
    # Pattern: $XK/month, $XM/month, $X,000/month
    patterns = [
        r'\$(\d+)K[/\s]*(?:month|mo)',
        r'\$(\d+)M[/\s]*(?:month|mo)',
        r'\$(\d+)[,\s]*000[/\s]*(?:month|mo)',
        r'\$(\d+)k[/\s]*(?:year|annually)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            amount = float(match.group(1))
            if 'K' in pattern or 'k' in pattern:
                revenue_amount = amount * 1000
            elif 'M' in pattern:
                revenue_amount = amount * 1000000
            else:
                revenue_amount = amount * 1000
            break
    
    # Extract frequency
    if re.search(r'year|annual', full_text, re.IGNORECASE):
        revenue_frequency = 'annual'
    elif re.search(r'one.time|one-time', full_text, re.IGNORECASE):
        revenue_frequency = 'one-time'
    
    # Extract founder name (look for patterns like "Marc Lou", "I'm Marc", "founder name")
    founder_name = ""
    # Pattern: "I'm [Name]" or "My name is [Name]"
    name_match = re.search(r"(?:I'm|my name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", full_text[:1000], re.IGNORECASE)
    if name_match:
        founder_name = name_match.group(1)
    else:
        # Pattern: Title starts with "[Name] makes" or "[Name] built"
        name_match = re.search(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:makes|built|made|make|build)', title, re.IGNORECASE)
        if name_match:
            founder_name = name_match.group(1)
        else:
            # Pattern: "follow [Name]" or "@[Name]"
            name_match = re.search(r'(?:follow|@)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', full_text[:1000], re.IGNORECASE)
            if name_match:
                founder_name = name_match.group(1)
    
    # Extract startup name (after "app" or "saas" mentions)
    startup_name = ""
    startup_match = re.search(r'([\w\s]+)\s*(?:app|saas|platform|software)', full_text[:500], re.IGNORECASE)
    if startup_match:
        startup_name = startup_match.group(1).strip()
    
    # Extract tech stack
    tech_keywords = ['react', 'node', 'python', 'javascript', 'typescript', 'aws', 'docker', 'postgresql', 'mongodb', 'flutter', 'swift', 'kotlin', 'firebase']
    tech_stack = [kw for kw in tech_keywords if kw in full_text.lower()]
    
    # Extract lessons (simple: first few sentences with "tip", "advice", "lesson")
    key_lessons = []
    lesson_patterns = [r'([^.]*(?:tip|advice|lesson|learn)[^.]*\.)', r'([^.]*(?:don\'t|do not)[^.]*\.)']
    for pattern in lesson_patterns:
        matches = re.findall(pattern, full_text[:2000], re.IGNORECASE)
        key_lessons.extend(matches[:2])
    
    return KnowledgeNode(
        node_id=str(uuid.uuid4()),
        video_id=video_id,
        founder_name=founder_name,
        startup_name=startup_name,
        tech_stack=tech_stack[:5],
        revenue_amount=revenue_amount,
        revenue_frequency=revenue_frequency,
        revenue_currency='USD',
        key_lessons=key_lessons[:3],
        timestamp=metadata.get('upload_date', ''),
        has_conflict=False,
        conflict_with_node_id=None
    )
