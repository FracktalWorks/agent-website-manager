# Using img2threejs in this repo

Upstream's `SKILL.md` is the operating manual — follow it as written. This
file is only the house context it cannot know.

## When to reach for it

A **3D product moment** on a site this agent manages: an orbitable machine on
a product page (a 3D printer on fracktal.in is the canonical case), a hero
object that rotates, an exploded-view of a part. The input is a reference
photo of the client's real product; the output is a code-only Three.js model —
no mesh downloads, no art packs, works within the static-site pipeline.

It is a **big gun**. For flat pages, `design_taste` motion rules and CSS are
enough; reconstruction is only worth its token cost when the object itself is
the content. Read `docs/TOKEN_COST.md` before committing to one.

## House rules that apply on top

- **Windows console:** run `python`, not `python3`, and expect the cp1252
  trap — set `PYTHONIOENCODING=utf-8` when a forge script prints glyphs.
- **Where output lives:** the generated factory/scene code is a site asset.
  Keep working state under `outputs/<project>/_threejs-<subject>/` (leading
  underscore = not an artefact) and ship only the final JS + a poster image
  into `site/assets/`.
- **Ship discipline:** Three.js is heavy — lazy-load the scene, never in the
  critical path; provide a static poster fallback (`prefers-reduced-motion`,
  no-JS, and mobile-data cases). `verify.py --all` must still pass.
- **WordPress canvas deploys keep only `<body>`** — scene code loads from
  `assets/` files, never inline `<script>` (the `&&`-escaping trap), and
  never from `<head>`.
- **Review gates are visual:** the pass/fail screenshots the pipeline takes
  are headless (house rule: no visible browser windows). LOOK at the final
  render against the reference photo — a clean-scoring model of the wrong
  variant is the known failure mode (generated-image-review lesson).
- The `subskills/` CS2 material is upstream's game-asset specialisation;
  irrelevant for client work here, kept only because upstream's router
  references it.
