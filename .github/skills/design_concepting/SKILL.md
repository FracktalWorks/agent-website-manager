---
name: design_concepting
description: >
  Mockup-first design flow: before building (or rebuilding) a site, walk the
  user through what it should look and feel like, then produce 3 genuinely
  distinct single-file HTML direction mockups, a compare page (phone → desktop
  toggle), and a recorded decision. The hub shows the round as a "Design
  concepts" artefact kind. Nothing real is built until a direction is chosen.
when_to_use: >
  Starting a NEW site; any major redesign/restyle of an existing site; the user
  says "show me options", "let's explore looks", "I'm not sure how it should
  feel", or asks for mockups/variations before committing. Skip only when the
  user names one exact direction ("apply <design-system id>", "match the brand
  kit") — then design_system_management alone is the path.
authority: write
cost_tier: 2
version: 0.1.0
---

# Design Concepting — choose the look before building it

The failure this skill prevents: building a full site on the first aesthetic
that came to mind, then discovering the user wanted something else. A concept
round costs three throwaway HTML files; a wrong site costs days.

**A concept is:** one self-contained `index.html` per direction — inline CSS,
no engine dependencies, no build step — showing the homepage hero plus 2-3
signature sections with the client's *real* facts (name, offer, city, CTA).
**A concept is not:** the site. The winning mockup becomes a reference; real
pages are then built as data through site_generator with a proper design
system. Never copy a mockup into `site/`.

## Files and script

```
outputs/<project>/concepts/
  BRIEF.md                       # the captured design read + interview answers
  <direction>/index.html         # the mockup (authored)
  <direction>/NOTES.md           # title, design read, dials, foundation
  compare.html                   # generated — do not hand-edit
  DECISION.md                    # written when the user chooses
```

| Command | Does |
|---|---|
| `python .github/skills/design_concepting/scripts/concepts.py new <project> <direction> --title "…"` | Scaffold a direction folder + NOTES.md template |
| `… compare <project>` | (Re)generate `compare.html` — run after every mockup edit and after `decide` |
| `… decide <project> <direction>` | Scaffold DECISION.md with the chosen slug |
| `… list <project>` | Directions + which is chosen |

The hub picks the round up automatically: `concepts/` is an artefact kind, so
it appears in the project's **Artefacts** switcher with the compare view
embedded. Standalone: `http://127.0.0.1:8780/collateral/<project>/concepts`,
or open `compare.html` straight from disk.

## The flow

### 1. Interview — read the room, then ask ONE round of questions

Load `design_taste` first and draft the design read from the brief. Then ask
the user **one** AskUserQuestion round (max 3-4 questions) covering only what
the brief left genuinely open — typically:

- **Energy** — calm & assured / confident & modern / bold & loud
- **Ground** — light & airy / warm & natural / dark & premium
- **Reference feel** — offer 3-4 *named* brand references relevant to the
  sector, calibrated from `agent-data/design-md/INDEX.md` ("Linear-clean",
  "Apple-quiet", "Nike-loud"), plus "none of these"

Write the answers into `concepts/BRIEF.md`. Do not ask what can be inferred:
audience, sector constraints, and existing brand assets come from the brief,
memory, and `inputs/`.

### 2. Author 3 directions (3 is the default; 2 for tight scope, 4 max)

For each: `concepts.py new`, then author `index.html` under the full
`design_taste` discipline. Directions must be **genuinely distinct** — differ
in at least two of the three dials *and* in foundation (different design
system from the 152 corpus, or a different brand-DESIGN.md calibration). Three
shades of the same safe idea is a failed round.

Rules that keep mockups honest:

- Real client facts and copy register — no lorem, no invented claims, and the
  copy passes the same slop discipline as a real page.
- **No generated images** (house rule). Use the client's real media if it
  exists (`inputs/`, media library); otherwise labeled neutral placeholder
  blocks styled by the direction.
- Self-contained: system font stacks or a `<link>` to a font the direction's
  design system actually names; inline CSS; works from `file://`.
- Run the `design_taste` pre-flight (core.md §14) on every mockup — a sloppy
  concept poisons the choice.
- NOTES.md filled in: the design read, dials, foundation id, "what to look
  at", "if chosen".

### 3. Compare — `concepts.py compare <project>`, then send the user to look

Point the user at the hub's Design concepts view (or `compare.html`). The
width toggle matters: make them look at phone as well as desktop before
choosing. Screenshots for the record can be captured headlessly (never open a
visible browser) but the live iframes are the review surface.

### 4. Decide — and only then build

`concepts.py decide <project> <direction>`, then fill DECISION.md with the
user's own words and anything to carry over from the losing directions
("direction B's hero, direction A's palette" is a normal outcome — record it).

**Gate: for a new brand, no design system is applied and no content is
authored until DECISION.md exists.** (Brand-launch runbook step 2; the
runbook's step 3 — design system — consumes this decision.)

### 5. Handoff

- Foundation → `design_system_management`: apply the chosen system
  (`brandkit.py apply <id>`) or author a system from the mockup's measured
  values (the mockup is the extraction source).
- Structure → site_generator: the mockup's hero paradigm and section rhythm
  become `content/*.py` sections rendered by `chrome.py` blocks.
- The concepts round stays on disk as the design record for the project.

## Concepting an EXISTING site (restyle round)

Same flow, two changes: the interview starts from the redesign protocol in
`agent-data/design-taste/redesign.md` (preserve vs overhaul — ask once), and
one direction is always **"evolve current"** (the site's own tokens, upgraded
typography/spacing/motion) so the user compares change against continuity,
not only against strangers.
