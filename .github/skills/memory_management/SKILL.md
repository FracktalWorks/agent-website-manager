---
name: memory_management
description: >
  ﻿# Memory Management Directive
when_to_use: "User asks about memory management"
authority: read
cost_tier: 1
version: 0.1.0
---
# ﻿# Memory Management Directive


## Purpose
Manage persistent memory across sessions so the agent gets smarter over time. Memory is the agent's competitive advantage over generic AI chat — it enables continuity, learning, and personalization.

## Architecture: Dual-Tier Memory System

### Tier 1: Working Memory (JSON + Markdown via `memory_bank.py`)
Fast, structured files read at session start. Small enough to fit in LLM context.

| File | Purpose | Format |
|------|---------|--------|
| `context.json` | Current state — active projects, goals, challenges, relationships | JSON |
| `interaction_log.json` | Past conversation summaries with topics and follow-ups | JSON |
| `decision_journal.json` | Decisions made with reasoning and outcome tracking | JSON |
| `insights.md` | Accumulated wisdom and lessons learned (append-only) | Markdown |

Custom memory types can be registered: `python execution/memory_bank.py --register <name> <filename>`

### Tier 2: Long-Term Memory (SQLite FTS via `memory_db.py`)
Searchable database for deep history. Queried on demand when Tier 1 doesn't have the answer.

| Table | Purpose |
|-------|---------|
| `stm` | Short-term session/task state with optional TTL |
| `facts` | Atomic searchable knowledge units |
| `entities` | People, companies, tools, concepts |
| `insights` | Accumulated lessons (also mirrors Tier 1 insights.md) |
| `interactions` | Detailed conversation logs |
| `decisions` | Choices with reasoning and outcomes |
| `context` | Key-value current state |
| `profile` | Agent/project identity info |

**Relationship:** Tier 1 (JSON) is the primary read/write surface for current state. Tier 2 (SQLite) is the search engine for when you need to find something specific from deep history. When updating memory, always update Tier 1 JSON files. Use Tier 2 for search and for storing atomic facts/entities that don't fit neatly in the JSON structure.

---

## Memory Retrieval Routing

The routing system decides which tier to query. **Getting this wrong** means either: (a) wasting time searching when the answer is already loaded, or (b) giving incomplete answers because relevant history wasn't retrieved.

### Routing Decision Tree

```
Is the topic about CURRENT STATE?
  (active tasks, current goals, who's involved, what should I do)
  → YES: Use Tier 1 (Working Memory). It has the latest.
  → NO: Continue ↓

Is the answer clearly in the loaded JSON files?
  (agent can see the relevant data already in context)
  → YES: Use Tier 1. Don't waste a search.
  → NO: Continue ↓

Does the question reference a SPECIFIC PAST EVENT?
  ("what did we do about X?", "when did Y happen?", "what was the exact approach for Z?")
  → YES: Use Tier 2. Search with the key entity/topic as query.
  → NO: Continue ↓

Does the question mention a NAME or ENTITY not in current JSON?
  (someone from an older session, a tool researched previously)
  → YES: Use Tier 2. Search by name.
  → NO: Continue ↓

Is the question about PATTERNS OVER TIME?
  ("have we dealt with this before?", "track record on X decisions?")
  → YES: Use BOTH. Tier 1 for recent pattern, Tier 2 for historical.
  → NO: Continue ↓

Is the agent about to take a MAJOR ACTION? (irreversible, expensive, strategic)
  → YES: Use BOTH. Major actions deserve full context retrieval.
  → NO: Use Tier 1 (default).
```

### Pre-Response Memory Check

**Before every substantive response, the agent should internally ask:**

1. **Do I have enough context from working memory to answer this well?**
   - If YES → respond using Tier 1.
   - If NO or UNCERTAIN → search Tier 2 with 1-2 targeted queries before responding.

2. **Am I about to ask the user something they already told me?**
   - If the topic rings a bell but you can't find it in loaded JSON → search Tier 2 BEFORE asking.
   - Asking a repeat question erodes trust for an agent that "remembers everything."

3. **Is this topic one we've discussed before but I only see a summary?**
   - `interaction_log.json` has compressed summaries for older sessions.
   - If you need the DETAIL behind a summary → search Tier 2.

### Search Query Best Practices

When searching Tier 2 (`memory_db.py search`):
- **Use the most distinctive keyword**, not generic ones
- **Use entity names** for people/company lookups
- **Use `--type` filter** when you know the table: `--type interactions`, `--type facts`
- **Use `--after` filter** when you know the approximate time
- **If first search returns nothing**, try synonyms or related terms

---

## Tool: execution/memory_bank.py (Tier 1 — Working Memory)

### Read
```bash
python execution/memory_bank.py --read context                # Read one file
python execution/memory_bank.py --read all                    # Read everything (session start)
python execution/memory_bank.py --status                      # Check what's populated
```

### Update Context
```bash
# Update a specific field (dot notation)
python execution/memory_bank.py --update context --key "goals.q2" --value "Launch product"

# Merge a JSON object
python execution/memory_bank.py --update context --data '{"stage": "growth", "revenue": "growing"}'
```

### Log Interactions
```bash
python execution/memory_bank.py --log-interaction --summary "Discussed launch timing" --topics "launch,timeline"
```

### Log Decisions
```bash
python execution/memory_bank.py --log-decision --decision "Delay launch to Q2" --context "Dependencies not ready" --reasoning "Risk reduction"
```

### Update Decision Outcomes
```bash
python execution/memory_bank.py --update-outcome 1 --outcome "Good call — dependencies resolved by Q2"
```

### Add Insights
```bash
python execution/memory_bank.py --add-insight "Always validate API responses before caching" --category "api"
```

### Search Working Memory
```bash
python execution/memory_bank.py --search "funding"
```

### Register Custom Memory Types
```bash
python execution/memory_bank.py --register profile profile.json      # Add agent-specific memory files
python execution/memory_bank.py --register birth_chart birth_chart.json
```

### Initialize Memory
```bash
python execution/memory_bank.py --init                        # Create default files if missing
```

## Tool: execution/memory_db.py (Tier 2 — Long-Term Memory)

### Universal Search (Primary Interface)
`ash
python execution/memory_db.py search "rate limit API"
python execution/memory_db.py search "client preferences" --type facts
python execution/memory_db.py search "last week" --after 2026-03-10
python execution/memory_db.py search "onboarding" --json
`

### Short-Term Memory
`ash
python execution/memory_db.py stm set "current_task" "Processing batch 3"
python execution/memory_db.py stm set "retry_count" "2" --ttl 3600    # Expires in 1hr
python execution/memory_db.py stm get "current_task"
python execution/memory_db.py stm show
python execution/memory_db.py stm clear                                # Clear expired
python execution/memory_db.py stm clear --all                         # Clear everything
`

### Long-Term Memory: Facts
`ash
python execution/memory_db.py add-fact "SerpAPI free tier: 100 searches/month" \
    --category "api_limits" --tags "serpapi,rate-limit"
python execution/memory_db.py add-fact "Client prefers bullet-point format" \
    --category "preferences" --entity "Acme Corp"
`

### Long-Term Memory: Entities
`ash
python execution/memory_db.py add-entity "Acme Corp" --type company \
    --details "Primary client, SaaS, 50 employees" --tags "client,active"
python execution/memory_db.py add-entity "Jane Doe" --type person \
    --details "CTO at Acme Corp, decision maker" --tags "contact,stakeholder"
`

### Long-Term Memory: Insights (append-only)
`ash
python execution/memory_db.py add-insight "Add 200ms delays between API calls to avoid 429s" \
    --category "api"
python execution/memory_db.py add-insight "PDF extraction is better with pymupdf than pdfplumber" \
    --category "tools"
`

### Interactions & Decisions
`ash
python execution/memory_db.py log-interaction --summary "Generated 50 leads" \
    --topics "lead-gen,google-maps" --follow-ups "Enrich emails"
    
python execution/memory_db.py log-decision --decision "Switch to direct scraping" \
    --context "Apify costs too high" --reasoning "Direct is 3x cheaper"
    
python execution/memory_db.py update-outcome 1 "Direct scraping worked, 3x savings"
`

### Context & Profile
`ash
python execution/memory_db.py context set "project.stage" "data_collection"
python execution/memory_db.py context show
python execution/memory_db.py profile set "agent.type" "lead_generation"
python execution/memory_db.py profile show
`

### Maintenance
```bash
python execution/memory_db.py status                    # Table row counts
python execution/memory_db.py rebuild-fts               # Repair search indexes
python execution/memory_db.py export --format json      # Full memory dump
```

### Embedding / Semantic Search (Optional)
Requires `pip install sentence-transformers`. Falls back to BM25 if not installed.

```bash
python execution/memory_db.py embed-sync                # Build/refresh embeddings for all facts, insights, entities
python execution/memory_db.py embed-search "rate limits" --top-k 5
python execution/memory_db.py hybrid-search "API billing" --semantic-weight 0.3 --json
```

### Memory Consolidation / Reflection
```bash
python execution/memory_db.py consolidate-stm --days 1  # Promote high-access STM to facts, discard stale
python execution/memory_db.py deduplicate-facts          # Remove exact duplicate facts
python execution/memory_db.py reflect --json             # Generate consolidation report (pending decisions, stale STM, suggestions)
```

### Evaluation & Guardrails
```bash
python execution/memory_db.py log-eval --task "scrape_leads" --status success --cost 0.10 --tokens 2000 --duration 15.0
python execution/memory_db.py check-guardrails --task "email_gen" --output-text "Hello..." --cost 0.05 --tokens 500 --json
python execution/memory_db.py eval-summary --days 7 --json
```

Guardrail checks (run automatically via `check-guardrails`):
- **output_not_empty** — Output must not be blank
- **no_sensitive_data** — Regex scan for API keys, passwords, SSNs, credit cards
- **cost_within_budget** — Daily cost tracked against `DAILY_COST_BUDGET_USD` env var (default $10)
- **token_usage_ok** — Per-task tokens against `MAX_TOKENS_PER_TASK` env var (default 100k)
- **output_length_ok** — Output must be under 1MB

## Memory Hygiene Protocol

### REAL-TIME UPDATE RULE (CRITICAL)
**Do not wait until the end of a conversation to update memory.** Update memory files immediately when new information is received, in the same response turn. This prevents context loss if a session is interrupted and ensures the agent is always working from the latest state.

**Pattern:**
1. User shares new info → 2. Agent responds → 3. Agent updates memory files — all in the same turn.

**Triggers for immediate update:**
- New person, company, or entity mentioned
- Project/task status changes
- New constraints, preferences, or requirements discovered
- Strategic decisions or options under consideration
- New insights or patterns observed
- Changes to goals or priorities

**Rule of thumb:** If in doubt, write it. Retrieval is cheap. Lost context is expensive.

### After EVERY substantive task (final sweep):
1. **Log the interaction** — `memory_bank.py --log-interaction --summary "..." --topics "..."`
2. **Store new facts** in Tier 2 — `memory_db.py add-fact "..." --category x`
3. **Update entities** in Tier 2 — `memory_db.py add-entity "..." --type x`
4. **Update context** in Tier 1 — `memory_bank.py --update context --key "..." --value "..."`
5. **Add insights** — `memory_bank.py --add-insight "..."` (Tier 1) and/or `memory_db.py add-insight "..."` (Tier 2)
6. **Log decisions** — `memory_bank.py --log-decision --decision "..." --context "..." --reasoning "..."`
7. **Log evaluation** — `memory_db.py log-eval --task "..." --status success --cost X --tokens Y`

### Before EVERY new task:
1. **Read working memory**: `memory_bank.py --read all`
2. **Search for context**: `memory_db.py search "<task keywords>"`
3. **Check STM**: `memory_db.py stm show`

### When errors occur (self-annealing):
1. Store the error pattern as a fact: `memory_db.py add-fact "X API returns 429 after 50 req/min" --category api_limits`
2. Store the fix as an insight: `memory_bank.py --add-insight "Batch X API calls in groups of 40" --category "fixes"`
3. Update the directive with the learning

---

## Self-Organizing Memory Protocol

Memory grows with every session. Without periodic maintenance, files become bloated, duplicated, and hard to parse. This protocol ensures the agent's memory stays clean and useful.

### When to Self-Organize

**Automatic triggers** — run maintenance when ANY of these are true:
1. **More than 5 sessions since last reorganization** — check `_reorganized` timestamp in `context.json`
2. **Any JSON file exceeds 25KB** — the file is too large for efficient context loading
3. **`insights.md` exceeds 20KB** — needs summarization of older entries
4. **Agent detects conflicting data** — Tier 1 and Tier 2 say different things about the same fact

### File Size Audit
```bash
# Check sizes of all memory files (PowerShell)
Get-ChildItem memory/ -File | Select-Object Name, @{N='SizeKB';E={[math]::Round($_.Length/1KB,1)}}
```

### Restructuring Rules

**`context.json`** — Target: under 25KB
- Structure around: current_projects, goals, challenges, key_relationships, active_deals
- When too large: Extract completed items into a `_archive` section or separate archive file
- Never delete: Active relationships, ongoing projects, current challenges

**`interaction_log.json`** — Target: under 15KB
- When too large: Compress interactions older than 90 days to summary-only (remove details, keep date + 2-sentence summary)
- Keep full detail for the last 10 interactions

**`insights.md`** — Target: under 20KB
- When too large: Summarize entries older than 60 days into a "Historical Insights Summary" section at the bottom
- Never delete: Lessons that are still relevant, validated patterns, recurring observations

**`decision_journal.json`** — No compression needed (decisions are always valuable)
- Archive completed decisions with recorded outcomes to a separate file if it grows large

### Cross-Reference Audit
At each self-organization cycle, check:
- Are entities in `context.json` also present in `memory_db.py` entities table?
- Does `interaction_log.json` cover all sessions without gaps?
- Are any facts in `memory_db.py` more recent than what's in JSON files? If so, migrate forward.

### Self-Organization Log
After every reorganization, update `context.json`:
```json
"_reorganized": "YYYY-MM-DD — Brief description of what was done"
```

And append to `insights.md`:
```markdown
### YYYY-MM-DD [memory maintenance]
- What was reorganized and why
- Any data quality issues found and fixed
```

---

### Periodic maintenance schedule:
1. Clear expired STM: stm clear
2. Consolidate STM: consolidate-stm (promotes valuable short-term entries to long-term facts)
3. Deduplicate facts: deduplicate-facts (removes exact duplicates)
4. Run reflection: reflect --json (review pending decisions, stale entries, suggestions)
5. Sync embeddings: embed-sync (if sentence-transformers installed)
6. Check decision outcomes: search for pending decisions and update outcomes
7. Export memory periodically: export --format json (save to .tmp/memory_backup.json)
8. Review evaluation summary: eval-summary --days 7

## Data Quality Rules
- Every fact should be atomic — one piece of information per row
- Use tags generously — they make search more accurate
- Keep entities deduplicated — search before creating
- Insights are append-only — never delete lessons learned
- Context reflects current state — update as things change
- STM should be cleared between tasks — don't let it grow stale

## Integration with DOE Framework

The memory system enhances the 3-layer architecture:

1. **Before executing a directive**: Search memory for relevant context and past learnings
2. **During execution**: Use STM to track task progress and state
3. **After execution**: Log interactions, store facts, add insights, log evaluation
4. **On errors**: Store error patterns and fixes (self-annealing loop)
5. **On output**: Run guardrails to validate quality and safety
6. **Periodically**: Consolidate STM, deduplicate, reflect, sync embeddings

This creates a flywheel: each task makes the agent smarter for the next one.

## Evaluation & Guardrails Protocol

### After every task that produces output:
1. **Run guardrails**: `check-guardrails --task "task_name" --output-file output.txt --cost X --tokens Y`
2. **Log evaluation**: `log-eval --task "task_name" --status success --cost X --tokens Y --duration Z`
3. **If guardrails fail**: Fix the issue, re-run, log the failure as an insight

### Daily review:
1. **Check eval summary**: `eval-summary --days 1`
2. **Review cost burn**: Are costs within budget?
3. **Check guardrail failures**: Any recurring patterns?

### Environment variables for guardrails:
- `DAILY_COST_BUDGET_USD` — Maximum daily spend (default: 10.0)
- `MAX_TOKENS_PER_TASK` — Maximum tokens per task (default: 100000)
- `EMBEDDING_MODEL` — Sentence-transformers model name (default: all-MiniLM-L6-v2)

## Scripts

| `scripts/memory_db.py` | Execute with `python .github/skills/memory_management/scripts/memory_db.py` |
| `scripts/memory_bank.py` | Execute with `python .github/skills/memory_management/scripts/memory_bank.py` |

## Usage

```bash
# From agent root:
python .github/skills/memory_management/scripts/<script>.py --help
```

## Outputs

Writes to `outputs/{campaign-slug}/step_N_*.json`.
