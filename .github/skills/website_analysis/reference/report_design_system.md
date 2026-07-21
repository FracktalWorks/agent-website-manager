# Report Design System

The house style for every `website_analysis` report, so a site owner recognizes
them as one series. Reports are published with the **Artifact** tool (load the
`artifact-design` skill first to calibrate how much polish the request warrants).
This is a *utilitarian-analytical* treatment: information design first —
summary-before-detail, severity encoded in color and form, scannable.

## Palette (tokens)

Define as CSS custom properties on `:root`; redefine under
`@media (prefers-color-scheme: dark)` **and** `:root[data-theme="dark"|"light"]`
so the viewer's theme toggle wins. Style components through the tokens only.

**Brand accent** — one per brand, used sparingly (masthead rule, eyebrows, links).
Not the same as severity color. Fracktal = coral `#d84332` (dark: `#f0685a`).

**Neutrals** — a *picked* warm-neutral, never a flat mid-grey:
- ground `#f7f6f3` · surface `#ffffff` · surface-2 `#faf8f5`
- ink `#17171a` · ink-2 `#565660` · ink-3 `#86858f` · hairline `#e7e4dd`
- masthead band `#18171b` on `#f4f2ee`

**Semantic status** — distinct from the accent; this is the report's real signal:
| Meaning | light | dark |
|---|---|---|
| built / good / working | `#2c845f` | `#4eb489` |
| thin / warning | `#a8720f` | `#e0a63c` |
| orphan / critical / not-working | `#cf4032` | `#f2685c` |
| at-risk / broken (404, decaying) | `#b5192b` | `#ff6b78` |
| to-build (new) | `#3f6bd0` | `#7ba0ec` |
| consolidate / restructure | `#6a5aa0` | `#a596d8` |

Dark theme: ground `#131317` · surface `#1a1a1f` · ink `#f1efec` · hairline `#2b2b33`.

## Type

- **Sans** (headings + body): `"Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif`. Strong weight/size hierarchy; `text-wrap: balance` on headings.
- **Mono** (URLs, counts, slugs, data — the report's signature): `"SF Mono", "Cascadia Mono", "JetBrains Mono", Consolas, ui-monospace, monospace`. Use `font-variant-numeric: tabular-nums` wherever digits align.
- The CSP blocks font CDNs — use these system stacks (do **not** link a webfont URL).

## Components

- **Masthead** — dark band, brand-colored mono **eyebrow** (report type), balanced `h1`, one-line subhead, a row of goal/meta chips, a 3px brand rule at the bottom.
- **Metric strip** — 3–5 big `tabular-nums` numbers (total + the severity buckets), each with a colored left rule matching its status.
- **Distribution bar** — a single stacked bar showing the good/warn/critical split, with a legend.
- **Status chips** — small mono pills using the semantic tokens. Fixed vocabulary: `✓ built` · `◐ thin` · `⚠ orphan` · `● at-risk` · `⇄ consolidate` · `＋ to build`.
- **Finding tables** — scannable rows with a severity stripe (`box-shadow: inset 3px 0`), the URL in mono, a one-line note, and a concrete suggested fix. Wrap wide tables in `overflow-x:auto`.
- **Callout** — brand left-border card for the single most important structural insight ("the root cause").
- **Open decisions** — end with the calls only the user can make.

## Rules

- Lead with the verdict and the metric strip; detail comes after.
- Triage every finding: **fix / improve / leave-or-noindex** — don't list problems you'd never act on as if they're all equal.
- Separate signal from artifact in the *copy*: nav/footer inflate inbound-link counts; sidebars inflate "missing alt". Say so rather than reporting the raw number as a problem.
- Numbering/eyebrows must encode something true (a real sequence or category), not decorate.
- Both themes styled; visible keyboard focus; `max-width:100%` media; body never scrolls sideways.
- Favicon per report topic (🔗 linking · 🗺️ architecture · 🩺 health · 📊 SEO); keep it stable across redeploys of the *same* report.

## Skeleton

Copy `report_template.html`, replace the marked content regions, and publish.
It already ships the full token set, both themes, the masthead, metric strip,
distribution bar, chip vocabulary, and a finding table.
