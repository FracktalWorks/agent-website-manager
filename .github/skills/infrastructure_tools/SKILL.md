---
name: infrastructure_tools
description: >
  Infrastructure Tools Directive
when_to_use: "User asks about infrastructure tools"
authority: read
cost_tier: 1
version: 0.1.0
---
# Infrastructure Tools Directive


> Standard operating procedures for the DOE Framework infrastructure: Tool Registry, Task Graphs, Human-in-the-Loop, and Execution Traces.

## Tool Registry

The tool registry (`execution/tool_registry.json`) provides formal JSON Schema definitions for every execution script. This enables structured tool discovery and validation.

### When to Use
- **Before any task**: Run `python execution/tool_registry.py find "<query>"` to discover relevant tools
- **Before calling a tool**: Run `python execution/tool_registry.py show <tool_name>` to get parameter schemas
- **On setup**: Run `python execution/tool_registry.py validate` to verify all scripts exist and env vars are set

### Commands
```bash
python execution/tool_registry.py list                   # List all tools by category
python execution/tool_registry.py show <tool_name>       # Full schema for a tool
python execution/tool_registry.py find "<query>"         # Search tools by keyword
python execution/tool_registry.py validate               # Validate all tool schemas
python execution/tool_registry.py schema <tool_name>     # Get OpenAI function-call schema
python execution/tool_registry.py export --format json   # Export full registry
```

### Adding New Tools
When creating a new execution script, add an entry to `execution/tool_registry.json`:
```json
{
  "name": "my_new_tool",
  "script": "execution/my_new_tool.py",
  "description": "What it does",
  "category": "category_name",
  "tags": ["relevant", "tags"],
  "parameters": [
    {"name": "--input", "type": "string", "required": true, "description": "Input file"}
  ],
  "returns": "Description of output",
  "env_vars": ["API_KEY_NEEDED"],
  "cost_estimate": "~$0.01/call",
  "side_effects": ["What external things it changes"],
  "requires_confirmation": true
}
```

## Task Graphs (DAG-based Execution Plans)

Task graphs let you plan multi-step workflows as directed acyclic graphs (DAGs) with dependency resolution, checkpointing, and resume-from-failure.

### When to Use
- **Multi-step pipelines**: Scrape -> Enrich -> Upload -> Email
- **Resumable workflows**: If step 3 fails, resume from step 3 without re-running steps 1-2
- **Complex dependencies**: Some steps can run in parallel, others must wait

### Workflow
1. **Plan**: Create a task plan with steps and dependencies
2. **Execute**: Query ready steps, run them, mark as completed/failed
3. **Resume**: If a step fails, fix the issue and resume from that step

### Commands
```bash
# Create a plan with inline steps (id:name[:dep1,dep2])
python execution/task_graph.py create "Pipeline Name" \
  --step "scrape:Scrape leads" \
  --step "enrich:Enrich emails:scrape" \
  --step "upload:Upload to sheet:enrich"

# Or from a JSON file
python execution/task_graph.py create "Pipeline Name" --steps steps.json

# Check plan status
python execution/task_graph.py show <plan_id>
python execution/task_graph.py list

# Find steps ready to execute (all dependencies met)
python execution/task_graph.py ready <plan_id>

# Mark step completed/failed
python execution/task_graph.py mark <plan_id> <step_id> completed --output "Result data"
python execution/task_graph.py mark <plan_id> <step_id> failed --error "Error message"

# Reset a step and all downstream for re-execution
python execution/task_graph.py reset <plan_id> <step_id>
```

### Step Statuses
- `pending` — Not yet started
- `running` — Currently executing
- `completed` — Successfully finished
- `failed` — Execution failed
- `skipped` — Intentionally skipped
- `blocked` — Cannot proceed (manual block)

### JSON Steps File Format
```json
[
  {"id": "scrape", "name": "Scrape Google Maps", "tool": "scrape_google_maps", "tool_args": {"search": "plumbers in Austin", "limit": 50}},
  {"id": "enrich", "name": "Enrich emails", "tool": "enrich_emails", "depends_on": ["scrape"], "requires_confirmation": true},
  {"id": "upload", "name": "Upload to sheet", "tool": "append_to_sheet", "depends_on": ["enrich"]}
]
```

## Human-in-the-Loop (Approval Gates)

The confirmation system provides approval gates for irreversible agent actions. It adapts to deployment mode:

- **Copilot mode**: Outputs a clear prompt for the LLM to present to the user
- **Interactive mode**: stdin prompt (for terminal use)
- **Auto-approve mode**: For testing/CI (`AGENT_AUTO_APPROVE=true`)

### When to Use
- Before any action with `requires_confirmation: true` in the tool registry
- Before sending emails, making API calls that cost money, or modifying external data
- Before any action flagged as high-risk

### Commands
```bash
# Create an approval request
python execution/confirm_action.py request "Send 50 emails" --tool instantly_create_campaigns --risk high

# Check request status
python execution/confirm_action.py check <request_id>

# Approve or deny
python execution/confirm_action.py approve <request_id> --reason "Approved by user"
python execution/confirm_action.py deny <request_id> --reason "Budget exceeded"

# List pending approvals
python execution/confirm_action.py list-pending
```

### Programmatic Use (from other scripts)
```python
from confirm_action import confirm, check_tool_approval

# Quick confirmation
if confirm("Send 50 cold emails?", details={"count": 50}):
    # proceed
    pass

# Check if a tool needs approval based on registry
needs_approval = check_tool_approval("instantly_create_campaigns")
```

### Environment Variables
- `AGENT_AUTO_APPROVE=true` — Auto-approve all confirmations (testing/CI only)
- `AGENT_CONFIRM_MODE=interactive|file|auto` — Confirmation mode

## Execution Traces (Observability)

Structured trace logging for every tool call. Tracks timing, costs, tokens, errors, and provides aggregate statistics.

### When to Use
- **Every pipeline execution**: Wrap tool calls in a trace to track performance
- **Cost tracking**: Monitor API spend across tools
- **Debugging**: Trace back through execution timeline when errors occur
- **Reporting**: Generate stats dashboards for cost/quality analysis

### Commands
```bash
# Start a trace
python execution/execution_trace.py start "Lead Gen Run" --plan <plan_id>

# Log tool execution events (step auto-increments if omitted)
python execution/execution_trace.py log <trace_id> --tool scrape_google_maps --status success --duration 12.5
python execution/execution_trace.py log <trace_id> --tool enrich_emails --status success --duration 8.3 --cost 0.05

# End the trace
python execution/execution_trace.py end <trace_id> --status success

# View trace details
python execution/execution_trace.py show <trace_id>

# List recent traces
python execution/execution_trace.py list

# Aggregate statistics
python execution/execution_trace.py stats --days 7
```

### Programmatic Use (from other scripts)
```python
from execution_trace import Tracer

with Tracer("Lead Gen Pipeline") as t:
    t.log_step("scrape", tool="scrape_google_maps", duration_s=12.5,
               input_data={"search": "plumbers"}, output_data={"count": 50})
    t.log_step("enrich", tool="enrich_emails", duration_s=8.3,
               cost_usd=0.05)
# Auto-ends trace on context exit; captures errors automatically
```

## Standard Pipeline Pattern

For every multi-step task, follow this pattern:

```
1. Search tool registry for relevant tools
2. Create a task graph with steps and dependencies
3. Start an execution trace
4. For each ready step:
   a. If step requires_confirmation -> create approval request
   b. Log trace event (status=running)
   c. Execute the tool
   d. Log trace event (status=success/failed, duration, cost)
   e. Mark step in task graph (completed/failed)
5. If a step fails -> store error as insight, reset downstream steps, resume
6. End the trace
7. Store lessons learned in memory
```

## Lessons Learned
- PowerShell heredoc expands `$` to null bytes — never use it for content with dollar signs
- Always qualify column names with table aliases in JOIN queries to avoid ambiguity
- The Tracer context manager auto-catches exceptions and logs them as failed trace events

## Scripts

| `scripts/tool_registry.py` | Execute with `python .github/skills/infrastructure_tools/scripts/tool_registry.py` |
| `scripts/tool_registry.json` | Execute with `python .github/skills/infrastructure_tools/scripts/tool_registry.json` |
| `scripts/task_graph.py` | Execute with `python .github/skills/infrastructure_tools/scripts/task_graph.py` |
| `scripts/execution_trace.py` | Execute with `python .github/skills/infrastructure_tools/scripts/execution_trace.py` |
| `scripts/confirm_action.py` | Execute with `python .github/skills/infrastructure_tools/scripts/confirm_action.py` |

## Usage

```bash
# From agent root:
python .github/skills/infrastructure_tools/scripts/<script>.py --help
```

## Outputs

Writes to `outputs/{campaign-slug}/step_N_*.json`.
