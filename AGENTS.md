# AGENTS.md - Project Context & Progress

## Project Overview
Automated ingestion system for Starter Story YouTube videos. Downloads metadata + transcripts and saves as JSON files.

## Directory Structure
```
Cortex/
├── AGENTS.md                    # This file
├── Starter-Story-Links.xlsx    # Source file with YouTube URLs (Status column added)
├── ingest_links.py              # Main processing script (processes range of rows)
├── process_one.py               # Single-link test script with Option 2 filename format
├── update_excel.py              # Marks rows as Completed in Excel
└── Raw_Data/                    # Output folder for JSON files
    └── {video_id}_{sanitized_title}.json
```

## Output Format (Option 2 Naming)
- **Filename**: `{video_id}_{sanitized_title}.json`
- **Sanitization**: Removes invalid chars (`\/*?:"<>|`), replaces spaces with underscores, truncates to 50 chars
- **JSON Structure**:
  ```json
  {
    "video_id": "abc123",
    "metadata": {
      "title": "...",
      "description": "...",
      "duration": 1234,
      "channel": "Starter Story",
      "view_count": 12345,
      "upload_date": "20260426",
      "tags": [],
      "thumbnail": "https://...",
      "categories": ["People & Blogs"]
    },
    "transcript": "Full transcript text here..."
  }
  ```

## Progress Tracking

### Excel File Status (Starter-Story-Links.xlsx)
- **Column A**: Video Links (YouTube URLs)
- **Column B**: Status ("Completed" or error message)
- **Total URLs**: Check Excel for current count

### Processed Rows

| Rows | Status | Transcripts | Notes |
|------|--------|-------------|-------|
| 2 | ✅ Completed | ✅ Full (10,121 chars) | D4fkiQfzw_I - Test run |
| 3-6 | ✅ Completed | ✅ Full | 4 links processed |
| 7-11 | ✅ Completed | ✅ Full | 5 links processed |
| 12-21 | ✅ Completed | ✅ Full | 10 links processed |
| 22-31 | ⚠️ Metadata Only | ❌ Blocked | IP ban - transcripts empty |

### Files Created in Raw_Data (21 total)
1. `D4fkiQfzw_I_How_I_Work_$77KMonth_Solopreneur.json`
2. `iVy5J7iE-3Q_I_Spent_24_Hours_With_A_SaaS_Millionaire.json`
3. `bq3-qH-CpYQ_I_Made_$1.5M_From_An_App_Youve_Never_Heard_Of.json`
4. `PIXXEAfo6MY_My_Niche_Mobile_App_Makes_$20KMonth.json`
5. `rGLXc1GmsaI_How_This_App_Makes_$35KMonth.json`
6. `dWeoSKLt_fc_I'm_14_And_I_Built_A_$14KMonth_App.json`
7. `DkmStHS8NP0_My_App_Made_$120K_in_24_Hours.json`
8. `0pp4X58q_0s_I_Built_a_$100KMonth_Android_App.json`
9. `spiC5m6AJNs_I_Make_$250KMonth_From_13_Businesses_(After_Losing.json`
10. `4KfFB-dh71Y_I_Make_$17KMonth_With_One_Strategy.json`
11. `LRX8TWC2hTM_I_Make_$60KMonth_From_the_Most_Boring_SaaS_on_the.json`
12. `l4WEqPX52Cg_How_This_$250KMonth_SaaS_Got_Its_First_100_Users_(.json`
13. `LKARRA0MvY4_I_Built_a_$10KMonth_SaaS_Using_Other_People's_Cust.json`
14. `E_rX4JJrYkY_Zero_to_$40KMonth_With_One_Marketing_Channel_(No_S.json`
15. `qIlX7cQ2UdU_I_Make_$15KMonth_From_One_Website.json`
16. `7vz6b_Ohdl0_I_Built_a_Niche_App_to_$9K_MRR.json`
17. `W48emwbUlUE_How_I_Built_a_$12KMonth_Micro-SaaS.json`
18. `9sJ2R0rM3CA_I_Make_$150KMonth_From_20_Tiny_Apps.json`
19. `hYF4fQYlrso_I_Make_$16KMonth..._Even_In_A_Tiny_Niche.json`
20. `47QXbPGyzBI_I_Made_$500K_From_8_Different_Income_Streams.json`
21-30. (Rows 22-31 metadata-only files with no transcripts)

## Critical Issue: YouTube IP Ban
- **Problem**: YouTube blocking transcript API requests from current IP
- **Cause**: Too many requests in short period
- **Solution**: Wait 1-2 hours, then retry
- **Affected**: Rows 22-31 have metadata but empty transcripts

## Dependencies
```bash
pip install yt-dlp openpyxl youtube-transcript-api
```

## Next Steps for New Session

### Immediate (after IP ban clears):
1. Retry transcripts for rows 22-31:
   - Edit `ingest_links.py` to set row range: `if 22 <= i <= 31:`
   - Run `python ingest_links.py`
   - This will overwrite JSON files with transcript data

### Continue Processing:
2. Process next batch (rows 32-41):
   - Edit `ingest_links.py`: `if 32 <= i <= 41:`
   - Run `python ingest_links.py`

3. Continue in batches of 10 until all links processed

### Script Usage:
- **Process specific rows**: Edit `ingest_links.py`, change line with `if X <= i <= Y:`
- **Test single link**: Use `process_one.py` (update video_url and video_id variables)
- **Excel auto-updates**: Status column (B) updates automatically

## Key Technical Notes
- Video ID extraction: Handles both `v=` and `be/` URL formats
- Transcript preference: Manual transcript first, then auto-generated
- yt-dlp used for metadata, youtube-transcript-api for transcripts
- Excel reading: openpyxl, starts from row 2 (row 1 is header)

## Cortex Brain Module (NEW - Added 2026-05-01)

### Structure
```
cortex/
├── __init__.py
├── schema.py          # Pydantic models (KnowledgeNode, RevenueMetrics)
├── extract.py         # LLM extraction (DeepSeek) + fallback regex
├── db.py              # SQLite operations
├── ingest_loop.py     # Raw_Data → Knowledge Nodes
├── brain.py           # Natural language query engine
├── conflict_resolver.py # Self-healing logic
├── knowledge_base.db  # SQLite database (gitignored)
└── cortex_logs.txt    # Conflict log (gitignored)
```

### Status
- ✅ Schema designed (flattened revenue fields for SQLite)
- ✅ Extraction logic (DeepSeek API + fallback regex)
- ✅ SQLite database initialized
- ✅ Ingestion loop (20/21 files processed, 10 skipped - empty transcripts)
- ✅ Brain query engine (natural language → SQL)
- ✅ Conflict resolver (detects >10% revenue diff, flags both nodes)
- ⚠️ **DeepSeek API key invalid** — extraction quality poor (regex fallback only)
- ⚠️ Needs valid API key for demo-quality extraction

### Resume Command
```bash
cd C:\Users\Atif Manzoor\Documents\Cortex
# Fix API key in .env, then:
python cortex/ingest_loop.py
python cortex/brain.py "What are the most common tech stacks for businesses making >$10k/month?"
```
