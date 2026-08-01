# Skill Observation Log

Observations captured during task-oriented work. Each entry identifies a
potential skill improvement or new skill opportunity.

**Status key:** OPEN = not yet actioned | ACTIONED = skill updated/created |
DECLINED = user decided not to pursue

---

## 2026-07-30

### Observation 1: Opening VS Code's Simple Browser from a dev server

**Status:** OPEN
**Date:** 2026-07-30
**Session context:** Porting open-design viewer features into the drvarada live editor
**Skill:** site_generator
**Type:** internal
**Phase/Area:** Live editor / IDE integration

**Issue:** No CLI or env-var route exists for a terminal-launched process to open
VS Code's built-in Simple Browser. The only working mechanism is a tasks.json
input of `"type": "command"` invoking `simpleBrowser.show` with the URL as args,
referenced as the task's `command` (`${input:...}`) — the documented
Panel/Holoviz recipe.

**Suggested improvement:** site_generator SKILL.md should document the tasks.json
recipe and that editor.py binds its port before the first build so an
instantly-opened preview pane gets a "building…" page instead of a refusal.

**Principle:** When a process cannot invoke an IDE command directly, invert
control: ship an IDE-side task the user (or agent instructions) trigger, and
make the server tolerate being opened "too early".

### Observation 2: Windows SO_REUSEADDR makes double-bind succeed

**Status:** OPEN
**Date:** 2026-07-30
**Session context:** Same session — adding a single-instance guard to editor.py
**Skill:** site_generator
**Type:** open-source
**Phase/Area:** Live editor server startup

**Issue:** Detecting "another editor is already running" via bind failure never
fires on Windows: Python's HTTPServer sets SO_REUSEADDR, and on Windows that
lets a second socket bind a live port, silently splitting requests between two
server instances.

**Suggested improvement:** Always detect a live sibling with a connect() probe
before binding, never by catching a bind OSError.

**Principle:** On Windows, port-in-use must be asked (connect), not caught
(bind) — SO_REUSEADDR semantics differ from POSIX.

### Observation 3: Headless-Chrome --dump-dom cannot probe pages holding an SSE stream

**Status:** OPEN
**Date:** 2026-07-30
**Session context:** Smoke-testing the live editor's device preview headlessly
**Skill:** site_generator
**Type:** open-source
**Phase/Area:** Verification tooling (verify.py-style probes)

**Issue:** A verify.py-style `--dump-dom` probe against the live editor hung
forever under `--virtual-time-budget` (the overlay's open EventSource stream
never lets virtual time expire) and dumped too early under `--timeout` (which
fires at load, before probe timers run). Working alternative: launch a
dedicated headless Chrome with `--remote-debugging-port` + `--user-data-dir`
and drive it over CDP (browser-use harness with `BU_CDP_URL`), which also
avoids needing the user to enable debugging on their own Chrome.

**Suggested improvement:** Note in site_generator SKILL.md's verification
guidance that dump-dom probes only suit static pages (dist/ files); pages
served by editor.py need the CDP route.

**Principle:** `--dump-dom` timing flags assume a page that finishes; any page
holding a live connection needs a driven browser, not a dumped one.

### Observation 4: Shell-app navigation patterns worth reusing (from Open Design)

**Status:** OPEN
**Date:** 2026-07-30
**Session context:** Rebuilding hub.py into a persistent workspace shell
**Skill:** site_generator
**Type:** open-source
**Phase/Area:** Workspace shell (hub.py)

**Issue:** The first hub was a landing page whose links navigated away — once
inside a project or design system there was no way back. Open Design's model
fixed it: a never-unmounted tab bar with a pinned Home tab; one tab per
entity with prefix-encoded ids; inactive views kept mounted and hidden
(display:none + inert, NOT unmounted — preserves iframe state); URL as the
source of truth with localStorage as best-effort cache; close-active
activates the slot neighbour; history-originated activations use
replaceState so the forward stack survives.

**Suggested improvement:** Already applied to hub.py; keep these rules stable
when extending the shell (e.g. adding terminal or chat tabs later).

**Principle:** In an embedded-viewer shell, tab switching must never reload
the content pane — keep views alive and hidden — and navigation state must
live in the URL, with storage only as a cache the URL can override.

### Observation 5: Live-edited artifacts must be ingested in place, never copied

**Status:** OPEN
**Date:** 2026-07-30
**Session context:** Separating user design systems from the vendored corpus
**Skill:** design_system_management
**Type:** open-source
**Phase/Area:** User/site-owned systems (§4b)

**Issue:** The obvious way to show the drvarada design system alongside the
corpus was to copy it into `agent-data/design-systems/`. That copy would
drift immediately — the live editor writes `system/variables.css` on every
Tokens-panel edit. Instead the hub discovers site-owned systems in place,
re-reads their tokens per request, and marks scope ("mine" vs "official") in
the index; only static vendored packages are cached.

**Suggested improvement:** Applied (SKILL §4b documents the contract). Keep
the rule when adding future scopes (e.g. org-shared systems).

**Principle:** Registry design follows mutability: cache and copy immutable
corpus entries freely, but anything a live tool writes must be read from its
one true location every time it is displayed.

### Observation 6: Visual feedback tools should target the agent's actual senses

**Status:** OPEN
**Date:** 2026-07-31
**Session context:** Porting OD's comment/mark/screenshot tools into the editor
**Skill:** site_generator
**Type:** open-source
**Phase/Area:** Feedback loop (Note/Mark/Shot)

**Issue:** OD's annotation tools feed its own runtime. Ours had to feed a
repo-based coding agent instead, so the design target changed: notes carry
the machine-usable handle (data-od address / CSS path) next to the human text,
and marks are burned into a server-rendered PNG (a second headless Chrome
hitting the same server with an inject-marks query param) rather than kept as
vector overlays — because the agent reads files and images, not live DOM.

**Suggested improvement:** Applied; contract lives in the site AGENTS.md and
SKILL.md. When porting any "annotate for AI" feature, ask what the consuming
agent can actually read and store THAT.

**Principle:** Feedback capture must serialize to the consumer's input
modality — for a repo agent that is plain files and rendered pixels, not
app-internal state.

### Observation 7: Feeding browser-captured feedback into chat sidebars — push vs pull

**Status:** OPEN
**Date:** 2026-07-31
**Session context:** Wiring Note/Mark/Shot into the Claude Code and Copilot sidebars
**Skill:** site_generator
**Type:** open-source
**Phase/Area:** Feedback loop → sidebar integration

**Issue:** "Seamless" means different things per sidebar because their
integration surfaces differ. Claude Code has hooks → PUSH (a UserPromptSubmit
hook injects open feedback into every prompt; silent when empty so the common
case costs nothing). Copilot has no hooks → PULL (an MCP server gives its
agent mode the tools, and the page UI hands the user a one-click ready
prompt). A browser page can invoke neither sidebar directly. Two traps: a
pure-stdlib stdio MCP server (newline-delimited JSON-RPC) avoids any install
step; and in VS Code's Simple Browser webview `clipboard-write` is refused
AND `window.prompt` blocks or no-ops — the copy fallback must be an inline
selected textarea, never a modal.

**Suggested improvement:** Applied (SKILL.md documents the wiring). Reuse the
push-vs-pull framing for any future "browser tool → chat agent" bridge.

**Principle:** Integrate with each agent's strongest native inlet — hooks
where they exist (push), MCP tools plus a user-carried prompt where they
don't (pull) — and never rely on clipboard or modals inside embedded
webviews.
