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

### Observation 8: Verify the served sitemap before starting any SEO overhaul on a live site

**Date:** 2026-08-04
**Session context:** Starting the fracktal.in SEO/website overhaul ("many pages broken, rank higher"). Before touching content, crawled the live sitemap and found the public `*sitemap*.xml` is hijacked: a PHP handler returns a fake 182KB urlset of 1075 spam `/shopdetail/` 404s to anyone (incl. Googlebot) whenever the query string is empty; `?x=1` bypasses it to the real Yoast sitemap. The user's "broken pages" symptom was largely Google having indexed the injected junk.
**Skill:** search_presence (also website_analysis)
**Type:** open-source
**Phase/Area:** Pre-flight / discovery before SEO work

**Issue:** The engagement was framed as content optimization, but the dominant ranking problem was a security compromise masquerading as "broken pages." Had I gone straight to title/meta rewrites and page deploys per the plan, I'd have optimized on top of a site that's feeding Google 1000+ spam 404s — wasted effort and a missed incident.

**Suggested improvement:** Add a mandatory pre-flight step to the search_presence / website_analysis skill: (1) fetch robots.txt and the sitemap it points to; (2) assert the sitemap contains only expected hosts/paths and a sane URL count vs. the WP post/page count; (3) re-fetch key sitemap URLs with a cache-busting query string and diff — a difference is a red flag for a query-gated injector; (4) spot-check a few real pages human-vs-Googlebot UA for cloaking. Only proceed to optimization once the sitemap is verified clean.

**Principle:** On a live site you don't control end-to-end, verify the ground truth (what the site actually serves to crawlers) before acting on the brief. Reported symptoms ("pages broken") can have a root cause (compromise) that no amount of the requested work (content edits) would fix — and that the requested work would paper over.

### Observation 9: A free malware scan can miss a custom wp-config remote-eval loader — read the server config directly

**Date:** 2026-08-04
**Session context:** Cleaning the fracktal.in compromise. Wordfence free scan came back essentially clean (no signatures), but the actual malware was a remote-eval loader injected at the top of wp-config.php (fetch remote URL -> eval on every request) plus a fake-Monarx RCE backdoor in the web root. Found only by reading wp-config.php / .htaccess / mu-plugins / drop-ins directly over FTP.
**Skill:** security_hardening (also search_presence)
**Type:** open-source
**Phase/Area:** Compromise triage / malware hunt

**Issue:** Relying on a signature scanner (Wordfence community) gave a false all-clear. The injector lived in wp-config.php — a file scanners often treat as config, not a scan target — and used a remote eval so no static payload signature existed locally. The decisive artifacts were wp-config.php (top-of-file prepend before the legit `<?php define('WP_CACHE'...`), object-cache.php / advanced-cache.php drop-ins, mu-plugins, and .htaccess.

**Suggested improvement:** In the security_hardening skill, add a "manual triage checklist" that runs regardless of scanner output: read wp-config.php (look for any code ABOVE the WordPress header / any eval/curl/base64), wp-content/{object-cache,advanced-cache}.php, all mu-plugins, .htaccess + .user.ini, and grep the tree for eval\+base64_decode/gzinflate/remote-fetch and known bad IPs. Treat a wp-config.php whose byte-0 is not the WP banner as compromised until proven otherwise. Note that host File Managers (Filester) and Yoast's editor block .htaccess/dotfiles, so SFTP/SSH is required to read them.

**Principle:** A clean signature scan is not proof of a clean site. Loaders that eval remote code leave no local signature, so triage must include reading the always-executed entry points (wp-config, drop-ins, mu-plugins, .htaccess) by eye — the scanner and the human look for different things, and the human catches the bespoke ones.

### Observation 10: Full-page screenshots of pages with vh-sized heroes need a clamped copy

**Status:** OPEN
**Date:** 2026-08-24
**Session context:** Building the fracktal.in alternative home page (home-v2) and reviewing it visually with headless Chrome
**Skill:** website_analysis / site_generator (visual review step)
**Type:** internal
**Phase/Area:** Headless screenshot capture for design review

**Issue:** To review a full page visually, the whole page was captured in one
headless-Chrome shot by setting `--window-size` to the page height (e.g.
1440x16300). Any hero sized in `vh` units then balloons to the window height —
the hero alone consumed ~10 of 16 thousand pixels, the real sections were
squeezed into the tail, and two of the review tiles were just blurred video
frames. The page itself was fine; the capture method distorted it.

**Suggested improvement:** When capturing a full-page shot for review, write a
throwaway copy of the built HTML that clamps the vh-sized bands (e.g.
`<style>.hero-video{min-height:820px!important;max-height:820px;overflow:hidden}</style>`
before `</head>`), screenshot that copy, and delete it. Verify the REAL hero
separately at true viewport sizes (1440x900, 390x844). Windows headless Chrome
also refuses widths under ~500px, so phone captures must use the 390px-iframe
wrapper `mobile.py` already documents.

**Principle:** A full-page screenshot is an instrument, and viewport-relative
CSS couples the instrument to the measurement: any unit tied to the viewport
distorts exactly when the viewport is stretched to fit the page. Decouple the
two — clamp viewport-relative bands in a disposable copy for the panorama, and
judge those bands only at real viewport sizes.

### Observation 11: New-page publish path is broken on WordPress-body sites

**Date:** 2026-08-24
**Session context:** Adding a drone-manufacturing SEO landing page to the Fracktal site (page bodies deployed onto live WordPress)
**Skill:** site_generator / html_deploy (repo skills)
**Type:** internal
**Phase/Area:** Deployment — creating a page that does not exist on WordPress yet

**Issue:** The repo can build and verify a brand-new page end to end (build.py, seo.py, verify.py, pytest all pass), but there is no working path to CREATE the page on fracktal.in. `pushpages.py` only applies bodies to ids already in `.deploy/pagemap.json` and prints SKIP for unmapped slugs; `deploy.py create` exists but uses application-password REST, which Wordfence deliberately blocks on this site. So "add a page" completes in-repo and then dead-ends at publish.

**Suggested improvement:** Extend the token-gated mu-plugin flow (`fracktal-pages.php` + `pushpages.py`) with a create-if-missing step: for slugs in the repo inventory but not in the pagemap, the mu-plugin creates a draft page (slug, parent, `elementor_canvas` template), returns the id, and pushpages writes it back into `pagemap.json` before the normal apply pass. Document it in the html_deploy SKILL.md.

**Principle:** A deploy pipeline that can only update what already exists silently caps the system at its current page count; the gap only surfaces the day someone adds a page, which is exactly when they expect the pipeline to work.

### Observation 12: External skill corpora integrate best as read-only vendor + thin house adapter

**Status:** OPEN
**Date:** 2026-08-29
**Session context:** Vendoring tasteskill.dev, awesome-design-md and img2threejs into the agent, and building the design_concepting mockup-first flow
**Skill:** design_taste (new), design_concepting (new)
**Type:** internal
**Phase/Area:** skill ingestion pattern

**Issue:** Third-party skill content (React/Tailwind-idiom taste rules) partly conflicted with house rules (no auto image generation, static Python pipeline, slop.py copy discipline). Copying upstream text into a house skill would have created a fork that drifts; following it verbatim would have violated house gates.

**Suggested improvement:** Keep the repeatable pattern: vendor upstream verbatim under agent-data/ (or the skill dir) with a PROVENANCE.md in the design-systems format, then write ONE thin .github/skills/<name>/SKILL.md that routes into the corpus and carries an explicit adapter table (upstream idiom → house equivalent) plus a precedence ladder (house gates > client brand > vendored rules > references).

**Principle:** Never edit vendored material and never obey it blindly — orchestrate it. An adapter with an explicit precedence ladder is what lets two rule systems coexist without silent conflicts.

### Observation 13: New scripts keep re-hitting the cp1252 console trap

**Status:** OPEN
**Date:** 2026-08-29
**Session context:** concepts.py `list` crashed on ●/○ under Windows cp1252 stdout; an em-dash in another print rendered as �
**Skill:** site_generator / any skill authoring new scripts
**Type:** internal
**Phase/Area:** script authoring conventions

**Issue:** The UTF-8 subprocess trap is already recorded in memory (fracktal deploy), yet a freshly written script reintroduced non-ASCII console output and crashed on first run.

**Suggested improvement:** Make it a stated convention in the script-authoring sections of the relevant SKILL.mds: console output from repo scripts is ASCII-only (markers like [x]/[ ], hyphens not em-dashes); non-ASCII is fine in files written with encoding="utf-8".

**Principle:** A lesson stored as memory prevents re-debugging but not re-introduction; conventions that recur at authoring time belong in the skill that governs authoring.

### Observation 14: Syncing an agent into a scoped export is an allow-list job, never a mirror

**Status:** OPEN
**Date:** 2026-08-29
**Session context:** Bringing the E:\agent-website-manager-atlaswild handover copy up to the master agent's new skills
**Skill:** New skill candidate: workspace_export (scoped copies + updates of the agent)
**Type:** internal
**Phase/Area:** export / sync procedure

**Issue:** A robocopy list-only dry run showed that a naive tree copy would have re-imported 55 credential-carrying scripts the export had deliberately pruned, plus .env, client_secret_*.json, three token files and a ps1 with a hardcoded API key, and would have overwritten the export's scoped-copy CLAUDE.md banner and its .gitignore (where the project IS tracked).

**Suggested improvement:** Codify the export/update procedure as a skill or runbook section: (1) list-only dry run first, (2) copy by explicit allow-list of agent paths, (3) edit — never overwrite — files the export customised (CLAUDE.md, HANDOVER.md, .gitignore, repointed tests), (4) run the export's own test suite, (5) append a dated HANDOVER section and commit in the export's repo, (6) share from a dedicated folder, not the drive root.

**Principle:** A scoped copy diverges from its source on purpose; every later sync must respect those divergences explicitly, so the safe primitive is "add these named files" rather than "make it look like the master".
