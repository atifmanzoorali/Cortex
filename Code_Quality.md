# Code_Quality.md - Cortex QA & Evals Plan

## **Executive Summary**

**Current Code Quality Status: ⚠️ NEEDS IMMEDIATE ATTENTION**

After reviewing the codebase, I found:
- **15+ syntax errors** (missing commas, extra parentheses, typos)
- **Security vulnerability** (API key hardcoded in `query_engine.py`)
- **Inconsistent naming** (`founder_name` vs `founder_name`, `learned` vs `learned`)
- **Broken functionality** (multiple files won't run due to syntax errors)

---

## **Phase A: Code Quality Audit (Automated)**

### **A1. Syntax & Style Checks**
```bash
# Install QA tools
pip install pylint black mypy bandit

# Run checks
black cortex/ --check                    # Code formatting
pylint cortex/                           # Code quality (0-10 score)
mypy cortex/                            # Type checking
bandit cortex/ -r                       # Security scan (catches hardcoded API keys)
```

**Target Scores:**
- Pylint: >8.0/10
- Black: 0 formatting issues
- Mypy: 0 type errors
- Bandit: 0 high-severity issues

---

## **Phase B: Functional Testing (Manual + Automated)**

### **B1. Unit Tests (Per Module)**

Create `tests/` directory with:

| Test File | Tests |
|-----------|------|
| `test_schema.py` | Validate KnowledgeNode creation, dynamic_fields, defaults |
| `test_db.py` | Test init_db, insert_node, find_existing, migration logic |
| `test_extract.py` | Mock LLM responses, test field extraction |
| `test_query_engine.py` | Test DynamicSchemaManager, field identification, transcript search |
| `test_health_check.py` | Test conflict detection, auto-healing logic |
| `test_conflict_resolver.py` | Test timeline reasoning, conflict logging |

**Example Test (test_schema.py):**
```python
def test_knowledge_node_creation():
    node = KnowledgeNode(node_id="test", video_id="abc")
    assert node.founder_name is None
    assert node.dynamic_fields == {}
    assert node.has_conflict == False
```

### **B2. Integration Tests**

| Test Case | Command | Expected Result |
|-----------|---------|-----------------|
| DB Migration | `python cortex.py --status` | Shows 38 nodes, no errors |
| Dynamic Learning | `python cortex.py --ask "What is pivot reason?"` | Learns field, returns results |
| Health Check | `python cortex.py --health` | Scans nodes, 0 errors |
| Full Ingest | `python cortex.py --ingest` | Processes all transcripts |

### **B3. Edge Cases to Test**

| Scenario | Test |
|----------|------|
| Empty transcript | Should skip, not crash |
| Malformed JSON | Should handle gracefully |
| Missing API key | Should show clear error |
| Duplicate nodes | Should detect conflict |
| Special characters | Should handle UTF-8 correctly |
| Windows paths | No Unicode encoding errors (emoji issue fixed) |

---

## **Phase C: Security & Best Practices**

### **C1. Critical Fixes Needed**

| Issue | File | Fix |
|-------|------|-----|
| **API key hardcoded** | `query_engine.py:17` | Move to `.env`, read via `os.getenv()` |
| **Syntax errors** | Multiple files | Fix missing commas, parentheses |
| **Typos in variables** | `db.py`, `query_engine.py` | `founder_name` → `founder_name` |
| **Inconsistent naming** | `learned` vs `learned` | Standardize to `learned` |

### **C2. Professional Standards Checklist**

- [ ] **Type Hints**: All functions have proper type annotations
- [ ] **Docstrings**: All classes/functions documented (Google style)
- [ ] **Error Handling**: Try/except with specific exceptions (not bare `except:`)
- [ ] **Logging**: Use `logging` module, not `print()`
- [ ] **Constants**: API keys, paths in config or `.env`
- [ ] **No Hardcoded Values**: Model names, paths as variables
- [ ] **SQL Injection Protection**: Use parameterized queries (already done ✅)
- [ ] **File Encoding**: Always specify `encoding='utf-8'`

---

## **Phase D: Evals Framework**

### **D1. Automated Evals (CI/CD Ready)**

Create `.github/workflows/qa.yml`:
```yaml
name: Cortex QA
on: [push, pull_request]
jobs:
  qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install -r requirements.txt && pip install pylint black mypy bandit pytest
      - name: Run syntax checks
        run: black cortex/ --check && pylint cortex/ && mypy cortex/
      - name: Security scan
        run: bandit cortex/ -r
      - name: Run tests
        run: pytest tests/
```

### **D2. Manual Evals Checklist**

After ANY code change, verify:

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| CLI works | `python cortex.py --status` | Shows stats, no traceback |
| Query works | `python cortex.py --ask "test"` | Returns answer or "not found" |
| Health check | `python cortex.py --health` | Runs without errors |
| DB integrity | `sqlite3 cortex/knowledge_base.db ".schema"` | All tables exist |
| Dynamic fields | Query new field twice | Second time no LLM call |

---

## **Phase E: Implementation Priority**

### **Immediate (Before Any New Features):**
1. [ ] Fix all syntax errors in `db.py`, `query_engine.py`, `health_check.py`
2. [ ] Remove hardcoded API key (security fix)
3. [ ] Fix all typos (`founder` → `founder`, etc.)
4. [ ] Run `black` formatter on all files
5. [ ] Add `__main__.py` tests for each module

### **Short-term (This Week):**
1. [ ] Write unit tests (target: 80% coverage)
2. [ ] Add logging instead of print statements
3. [ ] Create `config.py` for constants
4. [ ] Add type hints to all functions

### **Long-term (Ongoing):**
1. [ ] Set up GitHub Actions for automated QA
2. [ ] Add integration tests
3. [ ] Performance benchmarks (query speed, ingest time)
4. [ ] Documentation (Sphinx or MkDocs)

---

## **Quick Start: Run This Now**

Let me create a simple QA script you can run immediately:

**Would you like me to:**
1. **Exit Plan Mode** and immediately fix all syntax errors?
2. **Create the tests/** directory with starter tests?
3. **Generate a pre-commit hook** that runs these checks automatically?

The code currently has **showstopper bugs** (syntax errors). I recommend fixing those first, then implementing the full QA plan.

---

*Created: 2026-05-01*
*Status: Ready for implementation*
