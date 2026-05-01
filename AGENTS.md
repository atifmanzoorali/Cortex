# AGENTS.md - Cortex Project Context & Progress

## Project Overview
Cortex is an autonomous Knowledge Brain agent for the Hourglass AI challenge. It processes YouTube transcripts from Starter Story videos, constructs a structured knowledge base with **dynamic schema expansion** and **self-healing logic** for conflicting information.

## Architecture Decision: Hybrid SQLite + JSON
- **SQLite**: Fast SQL queries on structured data
- **JSON column (`dynamic_fields`)**: Infinite schema flexibility for new fields
- **Why not pure JSON/SQLite?**: Need both speed and flexibility

## Directory Structure
```
Cortex/
├── AGENTS.md                          # This file
├── Improve.md                         # Implementation plan & progress tracking
├── Starter-Story-Links.xlsx           # Source file with YouTube URLs
├── cortex.py                          # CLI entry point (Phase 4)
├── ingest_links.py                     # Fetches metadata + transcripts from YouTube
├── process_one.py                      # Single-link test script
├── update_excel.py                     # Marks rows as Completed in Excel
├── .env                               # DeepSeek API key (gitignored)
├── .gitignore                          # Excludes .env, DB, logs, Raw_Data
├── requirements.txt                     # Python dependencies
├── test_extract.py                     # Revenue extraction tester
├── Raw_Data/                           # Input: YouTube JSON files (NOT in git)
│   └── {video_id}_{sanitized_title}.json
├── cortex/                             # Knowledge Brain module
│   ├── __init__.py
│   ├── schema.py                       # KnowledgeNode with dynamic_fields support
│   ├── extract.py                      # DeepSeek LLM extraction (supports dynamic fields)
│   ├── db.py                           # SQLite operations (updated for dynamic_fields)
│   ├── ingest.py                       # Phase 1: Initial build module
│   ├── query_engine.py                # Phase 2: DynamicSchemaManager
│   ├── health_check.py                # Phase 3: Self-healing health checker
│   ├── conflict_resolver.py           # Enhanced with timeline reasoning
│   ├── brain.py                        # Legacy query engine (superseded by query_engine.py)
│   ├── knowledge_base.db              # SQLite database (gitignored)
│   ├── cortex_logs.txt                # Conflict logs (gitignored)
│   ├── healing_events.log             # Self-healing events (gitignored)
│   └── learning_events.log            # Dynamic field learning (gitignored)
└── requirements.txt                     # Dependencies
```

## Key Files Quick Reference
| File | Purpose |
|------|---------|
| `cortex.py --ingest` | Process transcripts into knowledge base (Phase 1) |
| `cortex.py --ask "question"` | Query with dynamic expansion (Phase 2) |
| `cortex.py --health` | Self-healing check (Phase 3) |
| `cortex.py --status` | Show database stats and learned fields |
| `cortex/query_engine.py` | DynamicSchemaManager: learns new fields on-demand |
| `cortex/health_check.py` | HealthChecker: detects conflicts, auto-heals |
| `cortex/conflict_resolver.py` | Timeline-based conflict resolution |

## Progress Tracking

### Phase 1: Initial Build (COMPLETE) ✅
- ✅ Schema updated with `dynamic_fields = {}` (JSON dict) in KnowledgeNode
- ✅ Database migrated: added `dynamic_fields` column to SQLite
- ✅ `ingest.py` created for structured extraction
- ✅ `extract.py` updated to support dynamic field extraction
- ✅ **Tested**: 19 nodes processed successfully from 11 transcripts
- ⚠️ 10 transcripts still missing (YouTube IP ban)

### Phase 2: Dynamic Schema Expansion (COMPLETE) ✅
- ✅ `query_engine.py` with `DynamicSchemaManager` class
- ✅ Keyword-based transcript search (fast, free)
- ✅ LLM-powered field extraction from matching transcripts
- ✅ Auto-saves to `dynamic_fields` column in SQLite
- ✅ Logs learning events to `learning_events.log`
- ✅ **Tested**:
  - "What is the pivot reason?" → Learned `pivot_reason` (2 extracted)
  - "What are morning routines?" → Learned `morning_routine` (1 extracted)
  - "What is funding status?" → Learned `funding_status` (2 extracted)

### Phase 3: Self-Healing Protocol (COMPLETE) ✅
- ✅ `conflict_resolver.py` enhanced with timeline reasoning
  - Uses `video_upload_date` to determine "current truth" (newer = truer)
  - Logs healing events with reasoning to `healing_events.log`
  - Auto-updates primary node when timeline clearly shows update
- ✅ `health_check.py` with `HealthChecker` class
  - CLI command: `python cortex.py --health`
  - Detects revenue contradictions across time
  - Detects tech stack migrations (e.g., AWS → Vercel)
  - Generates health report with auto-healing stats
- ✅ **Tested**: Health check runs successfully on 38 nodes, 0 conflicts detected

### Phase 4: CLI Interface (COMPLETE) ✅
- ✅ `cortex.py` CLI entry point
  - `--ingest`: Initial build / re-ingest transcripts
  - `--ask "question"`: Query with dynamic expansion (triggers learning if needed)
  - `--health`: Run self-healing check
  - `--status`: Show database stats and learned fields
- ✅ Windows-compatible (no emoji/unicode issues)
- ✅ Clear error handling and user feedback
- ✅ **Tested**: All commands working, 38 nodes in database

### Phase E: Code Quality Fixes (COMPLETE) ✅ *[2026-05-01]*
- ✅ **Fixed hardcoded API keys** - Moved to `.env` file using `python-dotenv`
  - Updated `query_engine.py` and `extract.py` to use `os.getenv('DEEPSEEK_API_KEY')`
- ✅ **Fixed syntax errors** - All files pass `py_compile` check
- ✅ **Fixed typos/naming** - Verified `founder_name` and `learned_fields` consistency
- ✅ **Ran black formatter** - All 9 Python files reformatted (0 formatting issues)
- ✅ **Added module tests** - Created `cortex/__main__.py` with tests for all core modules
  - Run with: `python -m cortex`

### Phase A: Code Quality Audit (COMPLETE) ✅ *[2026-05-01]*
- ✅ **Pylint: 9.82/10** (Target: >8.0/10) - Exceeded
- ✅ **Black: 0 formatting issues** (Target: 0) - Passed
- ✅ **Mypy: 0 type errors** (Target: 0) - Passed
- ✅ **Bandit: 0 high-severity issues** (Target: 0) - Passed
- ✅ **Fixes applied**:
  - Added type annotations to fix 28 mypy errors
  - Created `pyproject.toml` with pylint/mypy configuration
  - Fixed `load_dotenv()` usage and added missing imports
  - Fixed `Optional` type hints and return types throughout codebase

### Phase 2: Dynamic Schema Expansion (COMPLETE) ✅
- ✅ `query_engine.py` with `DynamicSchemaManager` class
- ✅ Keyword-based transcript search (fast, free)
- ✅ LLM-powered field extraction from matching transcripts
- ✅ Auto-saves to `dynamic_fields` column in SQLite
- ✅ Logs learning events to `learning_events.log`
- ✅ **Tested**:
  - "What is the pivot reason?" → Learned `pivot_reason` (2 extracted)
  - "What are morning routines?" → Learned `morning_routine` (1 extracted)
  - "What is funding status?" → Learned `funding_status` (2 extracted)

### Phase 3: Self-Healing Protocol (COMPLETE) ✅
- ✅ `conflict_resolver.py` enhanced with timeline reasoning
  - Uses `video_upload_date` to determine "current truth" (newer = truer)
  - Logs healing events with reasoning to `healing_events.log`
  - Auto-updates primary node when timeline clearly shows update
- ✅ `health_check.py` with `HealthChecker` class
  - CLI command: `python cortex.py --health`
  - Detects revenue contradictions across time
  - Detects tech stack migrations (e.g., AWS → Vercel)
  - Generates health report with auto-healing stats
- ✅ **Tested**: Health check runs successfully on 38 nodes, 0 conflicts detected

### Phase 4: CLI Interface (COMPLETE) ✅
- ✅ `cortex.py` CLI entry point
  - `--ingest`: Initial build / re-ingest transcripts
  - `--ask "question"`: Query with dynamic expansion (triggers learning if needed)
  - `--health`: Run self-healing check
  - `--status`: Show database stats and learned fields
- ✅ Windows-compatible (no emoji/unicode issues)
- ✅ Clear error handling and user feedback
- ✅ **Tested**: All commands working, 38 nodes in database

## Database Contents (38 nodes in knowledge_base.db)
| Founder | Startup | Revenue | Tech Stack | Dynamic Fields |
|---------|---------|--------|-----------|----------------|
| Steve | Journalable | $100K | - | funding_status: bootstrapped |
| Jordan | Jordan's app | $300K | TypeScript, React, Postgres... | funding_status: bootstrapped |
| Marc Lou | Posture Mac OS app | $77K | Electron, Mac OS | morning_routine: [extracted] |
| Jeremy | Taskmagic | $3M | Zapier, no code tools | - |
| ... | ... | ... | ... | ... |

**Dynamic Fields Learned:**
- `pivot_reason` (2 extracted)
- `morning_routine` (1 extracted)
- `funding_status` (2 extracted)

## How to Run (For New Sessions)

### Check Database Status
```bash
cd C:\Users\Atif Manzoor\Documents\Cortex
python cortex.py --status
```

### Process New Transcripts
```bash
python cortex.py --ingest
```

### Query with Dynamic Expansion
```bash
python cortex.py --ask "What is the most common pivot reason?"
python cortex.py --ask "What are the morning routines of founders?"
python cortex.py --ask "What is the funding status of these startups?"
# Automatically learns new fields if not already known
```

### Self-Healing Health Check
```bash
python cortex.py --health
# Scans all nodes, detects conflicts, auto-heals using timeline reasoning
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
- **Usage**: 
  - Phase 1: Extract core fields from transcripts
  - Phase 2: Extract dynamic fields on-demand (1 call per field, not per query)

### Conflict Resolution Logic (Enhanced)
1. Detects >10% revenue difference between existing and new nodes
2. Detects tech stack changes (items added/removed)
3. Uses **timeline reasoning** (video upload dates) to determine "current truth"
4. Flags **both** old and new nodes as `has_conflict=True`
5. **Auto-heals** if newer data is >1 year older
6. Logs events to `cortex_logs.txt` and `healing_events.log`

### Dynamic Schema Expansion (Phase 2 "Wow" Factor)
When a user asks about a field NOT in the schema (e.g., "Are they single?"):
1. **Identifies missing field** from the question
2. **Searches transcripts** using keyword matching
3. **Extracts answers** using LLM from relevant transcripts
4. **Permanently saves** to `dynamic_fields` column
5. **Logs learning event**: "Cortex learned new field: 'morning_routine' for 19 founders"

### Self-Healing "Wow" Factor (Phase 3)
When Cortex finds conflicting data (e.g., revenue $77K in 2021, $150K in 2026):
- Automatically detects the conflict
- Uses **timeline reasoning** to determine newer = truer
- **Auto-heals** if >1 year difference
- Preserves both data points (no data loss)
- Logs healing event with reasoning to `healing_events.log`

## Known Issues & Limitations
1. **Founder name extraction** ~80% accurate ("Floren" vs "Florin", "Umberto" vs "Umberto")
2. **10 videos missing transcripts** (rows 22-31, YouTube IP ban - wait and retry)
3. **Tech stack extraction** needs improvement (regex fallback weak)
4. **Revenue from title only** (doesn't extract from transcript yet)
5. **Dynamic field extraction** depends on transcript quality (empty = can't extract)

## GitHub Repository
**URL**: https://github.com/atifmanzoorali/Cortex
**Branch**: main
**Last Push**: 2026-05-01 (Phase 1-4 Complete)

## Code Quality Status (Updated 2026-05-01)
**Current Status: ✅ EXCELLENT**
- ✅ **Pylint: 9.82/10** (Target: >8.0/10) - EXCEEDED
- ✅ **Black: 0 formatting issues** (Target: 0) - PASSED
- ✅ **Mypy: 0 type errors** (Target: 0) - PASSED
- ✅ **Bandit: 0 high-severity issues** (Target: 0) - PASSED
- ✅ **Syntax errors: 0** - All files pass `py_compile`
- ✅ **Hardcoded secrets: 0** - API keys moved to `.env`

## Next Steps for Improvement
**Phase B: Functional Testing (Manual + Automated)** ⏳ *Ready to implement*
1. Create `tests/` directory with unit tests:
   - `test_schema.py` - Validate KnowledgeNode creation, dynamic_fields
   - `test_db.py` - Test init_db, insert_node, find_existing, migration
   - `test_extract.py` - Mock LLM responses, test field extraction
   - `test_query_engine.py` - Test DynamicSchemaManager, field identification
   - `test_health_check.py` - Test conflict detection, auto-healing
   - `test_conflict_resolver.py` - Test timeline reasoning
2. Run integration tests (DB migration, dynamic learning, health check, full ingest)
3. Test edge cases (empty transcript, malformed JSON, missing API key, duplicate nodes)

**Phase C: Security & Best Practices** ⏳ *Ready to implement*
1. Add type hints to all functions (COMPLETE ✅)
2. Add docstrings to all classes/functions (Google style)
3. Replace print() with logging module
4. Create `config.py` for constants
5. Add file encoding='utf-8' to all file operations (COMPLETE ✅)

**Phase D: Evals Framework** ⏳ *Ready to implement*
1. Create `.github/workflows/qa.yml` for CI/CD
2. Set up automated QA pipeline (black, pylint, mypy, bandit, pytest)

**Future Enhancements:**
1. Get valid transcripts for rows 22-31 (wait for YouTube IP ban to clear)
2. Improve LLM prompt for better founder name extraction
3. Add more training examples to extraction prompt
4. Implement semantic search (embeddings) for better transcript matching
5. Add web UI for querying (Streamlit or Flask)

## Resume Command (What to do in new session)
```bash
cd C:\Users\Atif Manzoor\Documents\Cortex

# 1. Run module tests (Phase E - COMPLETE ✅)
python -m cortex

# 2. Check code quality (Phase A - COMPLETE ✅)
black cortex/ --check && pylint cortex/ && mypy cortex/ && bandit cortex/ -r

# 3. Check current status
python cortex.py --status

# 4. Check if YouTube IP ban cleared, then:
python ingest_links.py  # Re-process rows 22-31 for transcripts
python cortex.py --ingest  # Re-ingest with new transcripts

# 5. Test queries (triggers dynamic learning if needed)
python cortex.py --ask "What startups make over $100k/month?"
python cortex.py --ask "What are the most common pivot reasons?"

# 6. Run health check
python cortex.py --health

# 7. Next: Implement Phase B (Functional Testing)
```

---
*Last Updated: 2026-05-01 (Phase 1-4, E, A Complete)*
