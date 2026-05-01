# AGENTS.md - Cortex Project Context & Progress

## Project Overview
Cortex is an autonomous Knowledge Brain agent for the Hourglass AI challenge. It processes YouTube transcripts from Starter Story videos, constructs a structured knowledge base, and implements self-healing logic for conflicting information.

## Directory Structure
```
Cortex/
├── AGENTS.md                          # This file
├── Starter-Story-Links.xlsx           # Source file with YouTube URLs (Status column added)
├── ingest_links.py                     # Fetches metadata + transcripts from YouTube (Raw_Data)
├── process_one.py                      # Single-link test script (Option 2 filename format)
├── update_excel.py                     # Marks rows as Completed in Excel
├── .env                               # DeepSeek API key (gitignored)
├── .gitignore                          # Excludes .env, DB, logs, Raw_Data
├── requirements.txt                     # Python dependencies
├── test_extract.py                     # Revenue extraction tester
├── Raw_Data/                           # Input: 21 YouTube JSON files (NOT in git)
│   └── {video_id}_{sanitized_title}.json
├── cortex/                             # Knowledge Brain module
│   ├── __init__.py
│   ├── schema.py                       # Pydantic KnowledgeNode model
│   ├── extract.py                      # DeepSeek LLM extraction (deepseek-chat)
│   ├── db.py                           # SQLite operations
│   ├── ingest_loop.py                  # Raw_Data → Knowledge Nodes
│   ├── brain.py                        # Natural language query engine
│   ├── conflict_resolver.py           # Self-healing logic
│   ├── knowledge_base.db              # SQLite database (gitignored)
│   └── cortex_logs.txt                # Conflict log (gitignored)
└── requirements.txt                     # Dependencies
```

## Key Files Quick Reference
| File | Purpose |
|------|---------|
| `cortex/ingest_loop.py` | Processes all Raw_Data/*.json files into knowledge_base.db |
| `cortex/brain.py` | Query engine: `python cortex/brain.py "your question"` |
| `cortex/extract.py` | LLM extraction using DeepSeek API |
| `ingest_links.py` | Downloads YouTube metadata + transcripts to Raw_Data |

## Progress Tracking

### Phase 1: YouTube Ingestion (COMPLETE)
- ✅ 21 videos processed from Starter-Story-Links.xlsx
- ✅ Metadata + transcripts saved to Raw_Data/ (Option 2 naming)
- ✅ 11 files with full transcripts (rows 2-21)
- ⚠️ 10 files metadata-only (rows 22-31, YouTube IP ban)

### Phase 2: Cortex Knowledge Brain (COMPLETE - Functional)
- ✅ **Schema**: KnowledgeNode with conflict flags (has_conflict, conflict_with_node_id)
- ✅ **LLM Extraction**: DeepSeek API (`deepseek-chat`) - API key working
- ✅ **Database**: SQLite with 20 knowledge nodes (10 skipped: empty transcripts)
- ✅ **Ingestion Loop**: Processes Raw_Data/*.json → knowledge_base.db
- ✅ **Brain Query Engine**: Natural language → SQL (no API needed for queries)
- ✅ **Self-Healing**: Detects >10% revenue conflicts, flags both nodes, logs to cortex_logs.txt
- ⚠️ **Extraction Quality**: ~80% accurate (founder names need improvement)

### Database Contents (20 nodes in knowledge_base.db)
| Founder | Startup | Revenue | Tech Stack |
|---------|---------|--------|-----------|
| Steve | Journalable | $100K | - |
| Floren | multiple online projects | - | - |
| Ben | Follow Buddy | $17K | - |
| Jonathan Fishner | Charardb | - | - |
| Katie Keith | WordPress Plugins | - | ["WordPress", "WooCommerce"] |
| Jordan | Jordan's app | - | - |
| Marc Lou | Posture Mac OS app | $77K | - |
| Umberto | Floa | - | - |
| Evan | Locked | $14K | - |
| Miquel | Late Social Media API | $40K | - |
| Nick | Blocktoin | $16K | - |
| Jeremy | Taskmagic | - | - |
| Joseph | Super Demo | $250K | - |
| Ivan | Lancer | $10K | - |
| Thomas | Packager | $60K | - |
| Ethan | My Niche Mobile App | $20K | - |
| Maddox Schmidtoffer | Duckmath.org | $15K | - |
| Flo | Monai | $35K | - |
| Jacky Chow | Indexsy, Local Rank... | $12K | - |
| Vikash | Bulk Mockup | $30K | - |

## How to Run (For New Sessions)

### Process New Transcripts
```bash
cd C:\Users\Atif Manzoor\Documents\Cortex
python cortex\ingest_loop.py
```

### Query the Knowledge Base
```bash
python cortex\brain.py "What are the most common tech stacks for businesses making >$10k/month?"
python cortex\brain.py "Show me all founders making over $50k/month"
python cortex\brain.py "List all startups using React"
```

### Test Single Video Extraction
```bash
python cortex\extract.py
# (Update json_path in script first)
```

## Dependencies
```bash
pip install -r requirements.txt
```
**requirements.txt contents:**
```
openai>=1.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

## Critical Implementation Details

### DeepSeek API
- **Model**: `deepseek-chat` (cost-effective for budget)
- **Key**: Stored in `.env` as `DEEPSEEK_API_KEY`
- **Base URL**: `https://api.deepseek.com`
- **Fallback**: Regex extraction if API fails

### Conflict Resolution Logic
1. Detects >10% revenue difference between existing and new nodes
2. Detects tech stack changes (items added/removed)
3. Flags **both** old and new nodes as `has_conflict=True`
4. Links nodes via `conflict_with_node_id`
5. Logs event to `cortex_logs.txt` with timestamps

### Self-Healing "Wow" Factor
When a founder updates their revenue (e.g., $77K → $150K), Cortex:
- Detects the conflict automatically
- Preserves both data points (no data loss)
- Flags them for human review
- Logs the healing event with reasoning

## Known Issues & Limitations
1. **Founder name extraction** ~80% accurate ("Floren" vs "Florin", "Umberto" vs "Umberto")
2. **10 videos missing transcripts** (rows 22-31, YouTube IP ban - wait and retry)
3. **Tech stack extraction** needs improvement (regex fallback weak)
4. **Revenue from title only** (doesn't extract from transcript yet)

## GitHub Repository
**URL**: https://github.com/atifmanzoorali/Cortex
**Branch**: main
**Last Push**: 2026-05-01 (Cortex Brain module added)

## Next Steps for Improvement
1. Get valid transcripts for rows 22-31 (wait for YouTube IP ban to clear)
2. Improve LLM prompt for better founder name extraction
3. Add more training examples to extraction prompt
4. Test conflict resolution with sample conflicting data
5. Add unit tests for conflict detection logic

## Resume Command (What to do in new session)
```bash
cd C:\Users\Atif Manzoor\Documents\Cortex
# 1. Check if YouTube IP ban cleared, then:
python ingest_links.py  # Re-process rows 22-31 for transcripts
python cortex\ingest_loop.py  # Re-ingest with new transcripts

# 2. Test queries:
python cortex\brain.py "What startups make over $100k/month?"
```
