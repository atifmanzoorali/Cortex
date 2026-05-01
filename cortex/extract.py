import os
import json
import re
import time
from datetime import datetime
from typing import List, Optional
from cortex.schema import KnowledgeNode
import uuid
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")


def extract_knowledge(
    json_path: str, fields_to_extract: Optional[List[str]] = None
) -> Optional[KnowledgeNode]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    transcript = data.get("transcript", "")
    metadata = data.get("metadata", {})
    video_id = data.get("video_id", "")
    title = metadata.get("title", "")
    description = metadata.get("description", "")

    if not transcript:
        raise ValueError("Empty transcript")

    # Build dynamic prompt based on fields needed
    dynamic_fields_prompt = ""
    if fields_to_extract:
        field_list = ", ".join(fields_to_extract)
        dynamic_fields_prompt = f'\n  "dynamic_fields": {{"field_name": "value"}} // Extract these fields if available: {field_list}'

    # Use LLM for everything - simpler and more reliable
    prompt = f"""Extract the following from this YouTube video data. Return ONLY valid JSON.

Video Title: {title}
Upload Date: {metadata.get('upload_date', '')}

Transcript excerpt (first 5000 chars):
{transcript[:5000]}

Extract and return JSON:
{{
  "founder_name": "Name of founder (e.g., Marc Lou, Katie Keith)",
  "startup_name": "Product/business name (e.g., Journalable, WordPress Plugins)",
  "tech_stack": ["list", "of", "technologies"],
  "revenue_amount": 77000,
  "revenue_frequency": "monthly",
  "key_lessons": ["lesson 1", "lesson 2", "lesson 3"]{dynamic_fields_prompt}
}}

JSON output:"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=1000,
            )
            content = response.choices[0].message.content
            result = json.loads(content) if content else {}

            dynamic_fields = result.get("dynamic_fields", {})

            return KnowledgeNode(
                node_id=str(uuid.uuid4()),
                video_id=video_id,
                founder_name=result.get("founder_name", ""),
                startup_name=result.get("startup_name", ""),
                tech_stack=result.get("tech_stack", []),
                revenue_amount=result.get("revenue_amount"),
                revenue_frequency=result.get("revenue_frequency", "monthly"),
                revenue_currency="USD",
                key_lessons=result.get("key_lessons", []),
                timestamp=metadata.get("upload_date", ""),
                has_conflict=False,
                conflict_with_node_id=None,
                dynamic_fields=dynamic_fields,
            )
        except Exception as e:
            if attempt == 2:
                raise e
            time.sleep(2**attempt)
    return None
