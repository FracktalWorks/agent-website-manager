# Craft — universal design rules (brand-independent)

Rules a competent designer applies regardless of brand. The active design
system's tokens **win on conflict**; these rules cover everything the brand
does not override. Distilled from Open Design's `craft/` + `taste-skill`
corpus (Apache-2.0).

Each rule is labelled **[auto]** (enforced by the site's `build.py` — see the
gates table in SKILL.md) or **[guidance]** (apply it yourself; nothing checks
it). Keep these labels honest: if you automate a guidance rule, relabel it.

## Colour

- Four-layer pixel budget **[guidance]**: neutrals 70–90% of pixels
  (`--bg --surface --fg --muted --border`), ONE accent 5–10% (`--accent` —
  never invent a second), semantic 0–5% (`--success --warn --danger`),
  effects <1% (gradients, glows — rarely justified).
- **At most 2 visible uses of the accent per screen** **[guidance]**. Links
  count. Focus rings count. Ration accordingly.
- Never `#000`/`#fff` for dark themes **[guidance]**: dark bg `#0f0f0f`-ish,
  fg `#f0f0f0`-ish; on dark surfaces prefer semi-transparent white borders
  (`rgba(255,255,255,.08)`) over solid dark ones.
- The seven AI-default indigos are banned outright **[auto]**:
  `#6366f1 #4f46e5 #4338ca #3730a3 #8b5cf6 #7c3aed #a855f7` — plus purple
  and blue→cyan "trust" gradients **[guidance]**. An LLM left alone regresses
  to the mean: Inter, an indigo accent, a purple gradient. That is off-brand
  for everyone. Every colour must trace to the design system.
- Raw colour values are legal only inside `:root` token blocks **[auto]**.

## Typography

- The single most-skipped rule in AI-generated design **[guidance]**:
  | Context | letter-spacing |
  |---|---|
  | ALL CAPS (eyebrows, tags) | **+0.06em to +0.1em — required** |
  | Headings 32px+ | −0.01em to −0.02em |
  | Display 48px+ | −0.02em to −0.03em |
- Display font comes from the design system and is never Inter/Roboto/Arial/
  system-ui on `h1/h2/h3` **[guidance]**.
- Type scale is a fixed ladder (~8 steps), not a continuum; body line-height
  ≈ 1.5–1.65 **[guidance]**.

## Layout discipline (mechanically countable)

- **Eyebrow restraint** **[guidance]**: uppercase kicker count ≤
  `ceil(section_count / 3)` per page.
- **Zigzag cap**: three consecutive sections of the same layout family read
  as a template, not a page **[auto — warning]**.
- ≥4 distinct layout families on any page with 8+ sections **[guidance]**.
- Bento/grid cell count == item count — no empty trailing cells **[guidance]**.
- **No duplicate CTA intent** on one screen **[guidance]** — two buttons that
  do the same thing compete with each other.
- Hero: fits the viewport, ≤4 text elements, subtext ≤20 words **[guidance]**.

## Copy

- Filler copy never ships **[auto]**: lorem ipsum, "placeholder text",
  "feature one/two/three", "sample content".
- Invented metrics never ship **[auto]**: "10× faster", "99.9% uptime",
  "zero-downtime". Every number must be attributable to a source the client
  can defend ("45 years in practice" — verifiable; "thousands of happy
  patients" — not).
- If a content slot is empty, the section is the wrong choice — pick a
  different layout; never pad **[guidance]**.

## The soul test

Aim for ~80% proven patterns + ~20% distinctive choice. If someone outside
the project can look at a screenshot and identify whose site it is — it has
soul. If not, you shipped a template. **[guidance — by definition]**
