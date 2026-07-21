# DFM Engine — High-Level System Prompt & PRD

> **Purpose:** Automated Design-for-Manufacturing analysis for FDM 3D printing.
> **Input:** STL / STEP / OBJ / 3MF file.
> **Output:** DFM report — issues found, severity per issue, fix recommendations, printability score, material-specific warnings.
> **Scope:** FDM/FFF only (Phase 1). SLA, SLS, MJF added in later phases.
> **Date:** July 2026 · **Updated:** July 2026

---

## 1. Core Engine Philosophy

The DFM engine is **not a slicer**. It does not generate G-code. It analyzes geometry and flags manufacturability issues _before_ slicing — catching problems that would cause print failure, poor quality, or excessive post-processing.

**Key Constraints:**
- **No printer-model-specific checks.** Only check against a universal build volume of **600 × 600 × 600 mm**. Assume a standard 0.4mm nozzle for all feature-size calculations unless the user specifies a different nozzle.
- **DFM checks must be realistic, not overly aggressive.** A check should only fire when there is a _genuine, well-understood_ risk of print failure or unacceptable quality. False positives erode trust. When in doubt, downgrade severity (Fail→Warn, Warn→Info) rather than over-flag. Thresholds should be set at values where the engineering literature and practitioner experience agree there is a real problem — not theoretical edge cases.
- **Every check must be implementable with known mesh analysis techniques.** No "AI magic" without a concrete algorithm behind it. See §7 for recommended implementation approaches.

**Design Principle:** Every check must return:
- **Priority:** 🔴 Must-Have (MVP) or 🟡 Nice-to-Have (Post-MVP)
- **Pass / Warn / Fail** severity
- **Location(s)** on the model where the issue occurs (highlightable in 3D viewer)
- **Human-readable explanation** ("Wall thickness 0.6mm at [location] is below the 1.2mm minimum for Nylon PA12. Risk: wall will collapse during printing.")
- **Fix suggestion** ("Increase this wall to at least 1.2mm, or switch to PLA which supports 0.8mm walls.")

---

## 2. DFM Check Categories

Each check is marked:
- 🔴 **Must-Have** — Build for MVP. These catch the issues that cause outright print failure or make a part unprintable.
- 🟡 **Nice-to-Have** — Add post-MVP. These improve quality, reduce post-processing, or catch edge cases but aren't blockers.

### 2.1 Mesh Integrity & File Health

| # | Prio | Check | Description | Severity |
|---|------|-------|-------------|----------|
| M1 | 🔴 | **Non-Manifold Geometry** | Detect edges shared by ≠2 faces, holes in mesh, unclosed volumes. A non-manifold mesh has undefined inside/outside — slicers will produce garbage or crash. | **Fail** (blocker) |
| M2 | 🔴 | **Inverted / Flipped Normals** | Detect faces whose normals point inward. Causes slicers to misidentify interior vs exterior surfaces. | **Fail** (blocker) |
| M3 | 🟡 | **Degenerate Faces** | Faces with zero area (collapsed vertices). Wasteful and can cause slicer artifacts. Simple to detect: check for faces where all 3 vertices are colinear or coincident. | **Warn** |
| M4 | 🔴 | **Self-Intersecting Geometry** | Detect where mesh triangles intersect each other. Produces undefined slicer behavior. Implement via bounding volume hierarchy (BVH) intersection tests. | **Fail** (blocker) |
| M5 | 🟡 | **Duplicate / Floating Geometry** | Detect disconnected mesh components not attached to the main body. May indicate export errors. Detect via connected-component analysis on the face adjacency graph. | **Warn** |
| M6 | 🟡 | **Excessively High Polygon Count** | >1M triangles for a simple mechanical part inflates file size without benefit. Can slow or crash slicers. | **Warn** |
| M7 | 🟡 | **Excessively Low Polygon Count** | <200 triangles for a curved surface produces visible faceting in the print. Informational — the part will print, it just won't look smooth. | **Info** |
| M8 | 🔴 | **Missing / Corrupt File Header** | File cannot be parsed as valid STL/STEP/OBJ/3MF. | **Fail** (blocker) |
| M9 | 🟡 | **Unit Scale Ambiguity** | STL files carry no unit information. If bounding box is exactly 25.4× or 0.03937× typical dimensions, the model was likely exported in inches. Flag and ask user to confirm. | **Warn** |

---

### 2.2 Build Volume

All checks use a single build volume: **600 × 600 × 600 mm** (X × Y × Z). No printer-model-specific constraints.

| # | Prio | Check | Description | Severity |
|---|------|-------|-------------|----------|
| B1 | 🔴 | **Part Exceeds Build Volume** | Any dimension (X, Y, or Z) exceeds 600mm. The part cannot be printed in one piece. | **Fail** (blocker — suggest splitting into sub-parts or scaling down) |
| B2 | 🟡 | **Part Approaches Build Limits** | Part within 10mm of build plate edge on X/Y. Slight risk of adhesion loss or uneven heating near bed perimeter. Not a hard block — just a caution for large parts. | **Info** |
| B3 | 🟡 | **Part Too Tall Relative to Base** | Tall parts with a small footprint (>3:1 height-to-base-aspect ratio) risk wobble, layer shift, or bed detachment — especially at higher print speeds. | **Warn** |
| B4 | 🟡 | **Excessive Z-Height (Long Print Time)** | Parts >200mm in Z may require 20+ hour prints. Not a DFM failure, but a scheduling consideration for a service bureau. | **Info** |

---

### 2.3 Wall Thickness & Feature Size

Assumes standard **0.4mm nozzle diameter** unless the user overrides. Minimum structural wall = 2× nozzle (0.8mm). Minimum cosmetic wall = 1× nozzle (0.4mm). Material-specific adjustments in §3.

| # | Prio | Check | Description | Severity |
|---|------|-------|-------------|----------|
| W1 | 🔴 | **Below Minimum Wall Thickness** | Any wall thinner than the material-specific minimum. Implementation: ray-cast through the mesh at sampled points; measure distance between entry and exit. Walls below 2× nozzle diameter risk collapsing or not printing at all. | **Fail** if structural walls below minimum; **Warn** if cosmetic/non-structural |
| W2 | 🟡 | **Inconsistent Wall Thickness** | Walls that vary >30% in thickness along their length. Uneven cooling causes differential shrinkage and warping. Thin sections adjacent to thick sections create stress risers. | **Warn** |
| W3 | 🟡 | **Below Minimum Feature Size** | Embossed/debossed details (text, ribs, small bosses) smaller than 2× nozzle diameter (0.8mm) in X/Y. Will not resolve cleanly. | **Warn** |
| W4 | 🟡 | **Below Minimum Hole Diameter** | Holes smaller than ~1.5mm diameter in the X/Y plane. FDM holes consistently print undersized by 0.2–0.4mm. A 1mm designed hole may close entirely. | **Warn** |
| W5 | 🟡 | **Thick Monolithic Sections** | Solid sections >10mm thick waste material and time. Causes excessive heat buildup which can degrade layer adhesion. Suggest using infill or shelling the part. | **Info** |

---

### 2.4 Overhangs, Bridging & Supports

These checks are **orientation-dependent** — they must be re-evaluated whenever the user changes the print orientation (see §2.6).

| # | Prio | Check | Description | Severity |
|---|------|-------|-------------|----------|
| O1 | 🔴 | **Unsupported Overhang (Angle-Based)** | Faces whose downward-facing normal exceeds the material-specific maximum overhang angle (see §3). Implementation: for each face, compute angle between face normal and the Z-axis. If angle > threshold AND the face points downward (normal.z < 0), flag it. These regions will sag, curl, or fail without supports. | **Warn** (requires supports) / **Fail** (if supports are physically impossible — see O4) |
| O2 | 🟡 | **Unsupported Bridging** | Horizontal spans between two supported points exceeding material-specific maximum bridge length (see §3). Implementation: detect horizontal edges with nothing below them; measure span between supported endpoints. FDM can bridge short gaps; long bridges sag. | **Warn** |
| O3 | 🔴 | **First-Layer Overhang** | Features that overhang relative to the part's footprint on the build plate — i.e., geometry that starts printing in mid-air. Detect by projecting the first few layers onto the build plane and checking for unsupported regions. | **Fail** (blocker — no first-layer adhesion = guaranteed print failure) |
| O4 | 🔴 | **Unsupportable Overhang (Trapped)** | Overhangs inside enclosed or near-enclosed cavities where support material, once printed, cannot be physically removed. Detection: find overhanging faces, then check if the cavity opening is large enough (>10mm) and the reach is short enough (<30mm) for tool access. This is a hard DFM failure. | **Fail** (blocker — part cannot be printed as-designed in FDM) |
| O5 | 🟡 | **Excessive Support Volume** | Support material exceeds ~30% of total print volume. Suggests the part is poorly oriented. Recommend trying a different orientation. | **Info** (advisory — the part WILL print, but it's wasteful) |

---

### 2.5 Sharp Corners, Stress & Warping

| # | Prio | Check | Description | Severity |
|---|------|-------|-------------|----------|
| S1 | 🔴 | **Sharp External Corners (Warping Initiation)** | External corners with radius < 0.5mm in warp-prone materials (ABS, ASA, Nylon, PC, PP). Sharp corners are where warping starts — the corner lifts first, then peels inward. Also produce visible seam artifacts. Implementation: detect edges with dihedral angle > 60° and check adjacent face curvature. Only flag when material warping tendency ≥ 5 (see §3). | **Warn** — suggest adding ≥1mm fillet, or acknowledge risk if the material is low-warp (PLA/PETG) |
| S2 | 🟡 | **Sharp Internal Corners (Stress Risers)** | Internal/re-entrant corners with radius < 1mm. Under load, these concentrate stress and crack along layer lines. Critical for functional/load-bearing parts only — cosmetic parts can ignore. | **Warn** — suggest ≥2mm fillet |
| S3 | 🔴 | **Large Flat Bottom Surface (Warping Risk)** | Solid rectangular footprint >80×80mm in warp-prone materials. Large flat surfaces cool unevenly → corners lift. Implementation: detect the largest planar region on the bottom face. Flag if area exceeds threshold AND material warping tendency ≥ 5 (see §3). Orientation-dependent — the "bottom" changes with orientation. | **Warn** — suggest brim, enclosure, or material switch. For warp tendency ≥ 7 (ABS, Nylon, PC, PP), escalate severity. |
| S4 | 🟡 | **High-Aspect-Ratio Thin Features (Curling)** | Long, thin unsupported features with length:width >10:1. Uneven cooling causes the tip to curl upward ("taco-ing"). Common in thin blades, fins, or overhanging tabs. | **Warn** |
| S5 | 🟡 | **Sharp Cross-Section Transitions** | Abrupt change (>50%) in layer cross-sectional area between consecutive layers. Thick→thin: heat buildup at the transition. Thin→thick: weak interlayer bond because previous layer was too small. | **Warn** |
| S6 | 🟡 | **Thermally Isolated Fine Features** | Tall, thin standalone features (pins, towers, spikes). The nozzle dwells too briefly on each layer → the previous layer doesn't cool before the next one is deposited → the feature "melts" and loses geometry. | **Warn** — suggest printing multiples or adding a "cooling tower" |

---

### 2.6 Orientation — Auto-Orientation & User Interaction ⭐

> **This is a critical, user-facing feature.** The DFM analysis is highly dependent on print orientation — change the orientation and the overhangs, supports, warping risk, and strength profile all change. The system must handle orientation intelligently while respecting the user's intent.

#### 2.6.1 The Core Tension

FDM parts are **anisotropic** — properties differ by axis. The user may care about:
- **Strength direction:** Load should be perpendicular to layer lines (in the X/Y plane, not Z)
- **Surface finish:** Layer lines visible on large near-horizontal surfaces (stair-step effect)
- **Dimensional accuracy:** Z-axis is typically more precise than X/Y for vertical features
- **Support minimization:** Fewer supports = faster, cheaper, cleaner print
- **Build plate adhesion:** Largest flat face on the bed for stability

These goals often conflict. The best orientation for strength may be the worst for supports. The system must optimize intelligently but defer to the user when they have specific requirements.

#### 2.6.2 Auto-Orientation Algorithm (Runs Immediately After Upload)

**Goal:** Find the orientation that produces the best print with minimal user intervention.

**Algorithm — Greedy Multi-Factor Scoring:**

1. **Generate candidate orientations** by sampling the rotation space:
   - Try placing each large, relatively flat face of the model onto the build plate (convex hull face sampling — typically 6–20 candidates)
   - For each candidate, compute a composite score:
     - **Support volume** (40% weight): Estimate % of model that needs supports at this orientation. Lower = better.
     - **Base stability** (25% weight): Contact area with build plate. Larger = better adhesion.
     - **Z-height** (15% weight): Shorter Z = faster print, less wobble risk.
     - **Overhang severity** (20% weight): Weighted by how far beyond the angle limit each overhanging face is. Mild overhangs (50°) are less bad than severe ones (80°).

2. **Select the top-scoring orientation** as the default.

3. **Also compute 2 alternative orientations** by re-running with the next-best candidates, or by perturbing the optimal (rotate 90° around Z, flip 180°, etc.) to give the user choices.

**Implementation note:** This is _not_ a full slicer simulation. Use fast heuristics:
- **Support volume estimation:** For each face, if the angle from the Z-axis exceeds the material's max overhang angle, project its area downward to estimate support volume. Sum all flagged faces. This is approximate but fast — no need to generate actual support structures.
- **Base contact:** Project the convex hull of downward-facing geometry onto the build plane. The area of this projection is the base contact patch.

**Complexity:** Moderate. The face-sampling approach (try N orientations defined by the model's own faces) is much cheaper than brute-force grid search and works well for mechanical parts. For organic/sculpted models with no clear flat faces, fall back to a 30°-increment grid search.

#### 2.6.3 User Interaction Flow for Orientation

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: UPLOAD                                                  │
│  User uploads STL/STEP/OBJ/3MF                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: AUTO-ORIENT (instant, <2 seconds)                       │
│  System runs auto-orientation algorithm.                         │
│  Part appears in 3D viewer at the computed optimal orientation.  │
│                                                                  │
│  System shows a banner:                                          │
│  "Auto-oriented for best printability.                            │
│   [Keep this orientation]  [Customize orientation →]"            │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
              ┌────────────────────────┐
              │  User decision point    │
              └───────────┬────────────┘
                          │
        ┌─────────────────┼─────────────────────┐
        ▼                 ▼                       ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐
│ PATH A:       │  │ PATH B:       │  │ PATH C:                   │
│ ACCEPT DEFAULT│  │ MANUAL ROTATE │  │ SPECIFY LAYER DIRECTION   │
│               │  │               │  │                            │
│ User clicks   │  │ User drags to │  │ User clicks "Specify       │
│ "Keep this    │  │ rotate freely │  │ layer direction" and then: │
│ orientation". │  │ in 3D viewer. │  │                            │
│               │  │               │  │ • Clicks a face → "Layers  │
│ Proceed to    │  │ Re-run DFM    │  │   parallel to this face"   │
│ DFM analysis. │  │ after user     │  │ • Clicks a face → "This   │
│               │  │ confirms.      │  │   face on build plate"    │
│               │  │               │  │ • Enters rotation angles   │
│               │  │               │  │   manually (X°, Y°, Z°)   │
│               │  │               │  │                            │
│               │  │               │  │ System snaps to the        │
│               │  │               │  │ closest valid orientation. │
│               │  │               │  │ Re-run DFM.                │
└──────┬───────┘  └──────┬───────┘  └─────────────┬────────────┘
       │                 │                         │
       └─────────────────┼─────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: ORIENTATION SUMMARY (shown before full DFM)             │
│  Quick preview of the chosen orientation:                        │
│  • Estimated support material: Xg / Y% of total                  │
│  • Estimated print time: ~X hours                                 │
│  • Base contact area: X cm²                                       │
│  • Z-height: X mm                                                 │
│                                                                  │
│  User can still go back and change orientation before full DFM.  │
│  [Run Full DFM Analysis →]   [Change Orientation]                 │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: FULL DFM ANALYSIS                                       │
│  All checks (§2.1–2.10) run against the confirmed orientation.   │
│  Reports overhangs, walls, warping etc. specific to this setup.  │
│                                                                  │
│  Orientation is LOCKED for this analysis session.                 │
│  If user changes orientation → DFM re-runs automatically.        │
└─────────────────────────────────────────────────────────────────┘
```

**Key UX Decisions:**

1. **Auto-orient by default.** Most users don't know or care about orientation. Give them the best one automatically. Power users can override.

2. **Show orientation BEFORE running the full (slow) DFM analysis.** The orientation summary (Step 3) is fast (<2 sec). Full DFM (wall thickness, overhang detection, etc.) may take 5–15 seconds. Don't make the user wait for full DFM before they can change orientation.

3. **"Face-on-plate" and "layers-parallel-to-face" are the most intuitive inputs for non-experts.** Most users think in terms of "I want this face to be smooth" or "I want this flat side down." Don't ask them to input Euler angles.

4. **Re-run DFM automatically on orientation change.** After the initial analysis, if the user rotates the part, re-run DFM checks that are orientation-dependent (O1–O5, S3, L1–L2). Cache orientation-independent checks (M1–M9, W1–W5, S1–S2, C1–C4, T1–T3).

5. **Persist orientation choice through to order.** The orientation the user confirms is what the print operator will use. Attach it to the order as a rotation matrix + a preview image.

#### 2.6.4 Orientation-Dependent vs Orientation-Independent Checks

**Must re-run when orientation changes:**

| # | Check | Why Orientation-Dependent |
|---|-------|--------------------------|
| O1 | Unsupported Overhang (Angle) | Overhang angle measured relative to Z-axis |
| O2 | Unsupported Bridging | Bridge direction depends on orientation |
| O3 | First-Layer Overhang | What counts as "first layer" changes |
| O4 | Unsupportable Overhang (Trapped) | Cavity accessibility may change with orientation |
| O5 | Excessive Support Volume | Support volume is orientation-dependent |
| S3 | Large Flat Bottom (Warping) | What's "bottom" changes |
| L1 | Z-Axis Strength | Load direction relative to layers changes |
| L2 | Layer Line Visibility | Which surfaces are near-horizontal changes |
| B2–B4 | Build volume edge cases | Bounding box in Z changes with rotation |

**Cacheable — independent of orientation:**

| # | Category |
|---|----------|
| M1–M9 | Mesh integrity — geometry is geometry regardless of rotation |
| W1–W5 | Wall thickness — measured in 3D, not axis-dependent |
| S1–S2 | Sharp corners — geometric, not orientation-dependent |
| S4–S6 | Stress/warp nuance — mostly geometric |
| C1–C4 | Cavities — geometry is invariant under rotation |
| T1–T3 | Tolerances — clearance is clearance |
| P1–P3 | Post-processing — geometry-based |

---

### 2.7 Layer Adhesion & Strength Considerations

| # | Prio | Check | Description | Severity |
|---|------|-------|-------------|----------|
| L1 | 🟡 | **Load-Bearing Features in Z-Axis** | FDM parts are weakest in Z (interlayer bond ≈ 50–70% of X/Y strength). If thin load-bearing features are aligned with Z (e.g., a cantilever snap-fit printed standing up), flag it. Only meaningful if the user has indicated the part is functional/load-bearing. Implementation: detect long thin features oriented vertically; flag if height:width > 3:1. | **Warn** — suggest re-orienting so load is in X/Y plane. For CF-filled materials (Z-strength ~40%), escalate to higher severity. |
| L2 | 🟡 | **Visible Layer Lines on Key Surfaces** | Large, gently-sloped surfaces (5–30° from horizontal) show pronounced stair-step layer lines. Informational — the part prints fine but may need sanding/filling for a smooth finish. | **Info** |

---

### 2.8 Tolerances, Fits & Clearances

| # | Prio | Check | Description | Severity |
|---|------|-------|-------------|----------|
| T1 | 🟡 | **Insufficient Clearance for Mating Parts** | Detect mateable feature pairs (peg-in-hole, sliding dovetail, snap-fit) with clearance below the FDM-printable minimum. Implementation heuristic: find cylindrical features (pegs) and corresponding holes within 2× diameter distance; check diametral clearance. Minimum loose-fit clearance: 0.3mm (PLA/PETG) to 0.4mm (Nylon/PC). | **Warn** |
| T2 | 🟡 | **Insufficient Thread Clearance** | Threaded features need clearance to function after FDM printing. Detect via helical geometry pattern recognition, or simply flag all holes in the 2–10mm range that have nearby cylindrical features. | **Warn** |
| T3 | 🟡 | **Hole Diameter Compensation Advisory** | FDM holes are consistently undersized by 0.2–0.4mm in diameter. Flag all holes ≤10mm and note the expected as-printed diameter. | **Info** |

---

### 2.9 Internal Geometry & Cavities

| # | Prio | Check | Description | Severity |
|---|------|-------|-------------|----------|
| C1 | 🔴 | **Fully Enclosed Hollow Cavity** | A void with zero opening to the exterior. In FDM, this cavity will be filled with infill or trapped support material — it cannot remain hollow. Implementation: compute connected components of the void space; check if any void component has no path to the exterior. | **Fail** (blocker — suggest adding a drain/escape hole ≥3mm diameter) |
| C2 | 🔴 | **Cavity with Inaccessible Supports** | Internal cavity contains overhangs that need supports, but the cavity opening is too small (<10mm) or the reach is too deep (>30mm) for support removal tools. Implementation: for each overhanging face, ray-cast toward the nearest exterior opening; measure path length and minimum passage diameter along the path. | **Fail** (blocker) |
| C3 | 🟡 | **Deep Blind Hole** | Hole depth > 5× diameter. Hard to clean, hard to cool during printing, may trap debris. | **Warn** |
| C4 | 🟡 | **Long Internal Channel** | Internal channels >50mm long. FDM cannot produce clean, smooth internal channels — rough surfaces, partial blockages, trapped material. | **Warn** — suggest splitting along channel and bonding |

---

### 2.10 Post-Processing Feasibility

All post-processing checks are 🟡 **Nice-to-Have**. None affect printability — they affect finish quality and labor.

| # | Prio | Check | Description | Severity |
|---|------|-------|-------------|----------|
| P1 | 🟡 | **Support Removal Difficulty** | Score 1–10 based on support volume, number of supported faces, and accessibility. >7 = labor-intensive or high risk of breaking fine features during removal. | **Info** |
| P2 | 🟡 | **Sanding Accessibility** | Flag deep concave surfaces, narrow crevices (<10mm), and internal corners that are physically impossible or extremely tedious to sand smooth. | **Info** |
| P3 | 🟡 | **Vapor Smoothing Compatibility** | For ABS/ASA/PVB materials: detect walls <1.5mm or fine details that would dissolve or lose definition during vapor smoothing. | **Info** |

---

## 3. Material-Specific Thresholds

The DFM engine must apply **different thresholds per material**. These are the key parameters:

| Parameter | PLA | PLA+ / Tough PLA | PETG | ABS | ASA | Nylon PA12 | Nylon PA6 | PA-CF (Nylon+CF) | PETG-CF | PC | TPU 95A | PP |
|-----------|-----|------------------|------|-----|-----|------------|-----------|-------------------|---------|-----|---------|-----|
| **Min Wall Thickness (structural)** | 0.8mm | 0.8mm | 1.0mm | 1.0mm | 1.0mm | 1.2mm | 1.2mm | 1.2mm | 1.0mm | 1.2mm | 1.2mm | 1.0mm |
| **Min Wall Thickness (cosmetic)** | 0.4mm | 0.4mm | 0.6mm | 0.6mm | 0.6mm | 0.8mm | 0.8mm | 0.8mm | 0.6mm | 0.8mm | 1.0mm | 0.8mm |
| **Max Overhang Angle (no support)** | 45° | 45° | 45° | 50° | 50° | 55° | 55° | 60° | 50° | 55° | 40° | 45° |
| **Max Bridge Span (no support)** | 50mm | 50mm | 40mm | 30mm | 30mm | 20mm | 20mm | 15mm | 25mm | 25mm | 30mm | 20mm |
| **Min Feature Size (X/Y detail)** | 0.4mm | 0.4mm | 0.6mm | 0.6mm | 0.6mm | 0.6mm | 0.6mm | 0.8mm | 0.6mm | 0.6mm | 0.8mm | 0.6mm |
| **Min Hole Diameter (functional)** | 1.5mm | 1.5mm | 2.0mm | 2.0mm | 2.0mm | 2.5mm | 2.5mm | 2.5mm | 2.0mm | 2.0mm | 2.5mm | 2.0mm |
| **Warping Tendency (1–10)** | 2 | 2 | 4 | 7 | 6 | 8 | 9 | 3 | 4 | 9 | 1 | 9 |
| **Enclosure Required?** | No | No | No | Yes | Yes | Yes | Yes | Recommended | Recommended | Yes | No | Yes |
| **Bed Temp Required** | 50–60°C | 50–60°C | 70–80°C | 100–110°C | 100–110°C | 80–100°C | 80–100°C | 80–100°C | 70–80°C | 100–110°C | 40–50°C | 85–100°C |
| **Z-Strength (% of XY)** | 60% | 65% | 70% | 65% | 65% | 50% | 50% | 40% | 60% | 60% | 80% | 45% |
| **Min Clearance (moving fit)** | 0.3mm | 0.3mm | 0.3mm | 0.3mm | 0.3mm | 0.4mm | 0.4mm | 0.35mm | 0.3mm | 0.4mm | 0.3mm | 0.4mm |
| **Hole Undersize Compensation** | 0.2mm | 0.2mm | 0.25mm | 0.3mm | 0.3mm | 0.35mm | 0.35mm | 0.25mm | 0.25mm | 0.35mm | 0.2mm | 0.4mm |

---

## 4. Build Volume & Nozzle Specification

The DFM engine uses a **single, universal build volume** rather than per-printer-model profiles:

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Max Build Volume (X × Y × Z)** | **600 × 600 × 600 mm** | Any part fitting within this is printable. Larger parts flagged as B1-Fail. |
| **Default Nozzle Diameter** | 0.4 mm | Used for all minimum-wall and minimum-feature calculations. Overridable per order if the service bureau uses a different nozzle. |
| **Default Layer Height** | 0.20 mm | Used for print-time estimates only. Not used for DFM checks (checks are geometry-based, not layer-based). |

**Rationale:** A 600mm³ build volume covers virtually all consumer and prosumer FDM printers (Bambu Lab, Prusa, Creality, etc.) plus most mid-format industrial machines. The DFM engine doesn't need to know _which_ printer will run the job — the print farm scheduler handles that later. As long as the part fits within 600×600×600, it's printable somewhere in the farm. This simplifies the DFM engine significantly and avoids false failures from printer-model mismatches.

---

## 5. DFM Report Output Structure

The DFM report delivered to the user should contain:

```
DFM REPORT
├── Part Summary
│   ├── File name, format, upload timestamp
│   ├── Bounding box dimensions (X×Y×Z mm)
│   ├── Mesh stats: triangle count, volume (cm³), surface area (cm²)
│   ├── Detected unit scale (with confidence)
│   ├── Chosen orientation (rotation matrix + preview thumbnail)
│   └── Estimated material usage (g) and print time (hh:mm)
│
├── Printability Score (0–100)
│   ├── 90–100: Ready to print. Minor advisories only.
│   ├── 70–89: Printable with warnings. Review recommendations.
│   ├── 40–69: Significant issues. Design changes recommended.
│   └── 0–39: Not printable as-is. Critical failures require redesign.
│
├── Critical Failures (Blockers — MUST fix before printing)
│   ├── [M1, M2, M4, M8, B1, O3, O4, C1, C2]
│   └── Each with: location highlight, explanation, fix suggestion
│
├── Warnings (Should fix — may cause print failure or poor quality)
│   ├── [W1, O1, S1, S3, L1, etc.]
│   └── Each with: location highlight, explanation, fix suggestion
│
├── Advisories (FYI — non-critical, quality-of-life)
│   ├── [M5, M6, M7, B4, W5, O5, P1, etc.]
│   └── Each with: location highlight, explanation
│
├── Orientation Summary ⭐
│   ├── Current orientation preview (3D viewer thumbnail)
│   ├── Why this orientation was chosen (e.g., "Minimizes supports, largest flat face on build plate")
│   ├── Support material estimate: Xg (Y% of total)
│   ├── Estimated print time: ~X hours
│   ├── Base contact area: X cm²
│   ├── Z-height: X mm
│   ├── [Change Orientation] button → returns to orientation picker
│   └── Alternative orientations (2 options) with quick-compare stats
│
├── Material-Specific Notes
│   ├── Selected material: name, properties summary
│   ├── Warping risk score (1–10) + mitigation steps
│   ├── Enclosure requirement (yes/no/recommended)
│   ├── Bed adhesion recommendation (none / brim / raft)
│   └── Post-processing notes (support removal difficulty, sanding, vapor smoothing compatibility)
│
├── Material Options
│   ├── Selected material: price estimate, lead time
│   ├── Alternative 1 (cheaper): material, price, trade-offs
│   └── Alternative 2 (stronger/better): material, price, trade-offs
│
└── Actions
    ├── [Get Instant Quote] (if score ≥ 70)
    ├── [Change Orientation & Re-Analyze]
    ├── [Try a Different Material]
    ├── [Fix Issues & Re-upload]
    ├── [Download DFM Report PDF]
    ├── [Share Report Link]
    └── [Contact Engineer for Design Review] (human review escalation)
```

---

## 6. DFM Engine Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────┐
│                     UPLOAD LAYER                         │
│  File ingestion (STL/STEP/OBJ/3MF) → format validation  │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              MESH PRE-PROCESSING                         │
│  • Tessellation normalization (convert to triangle mesh) │
│  • Unit detection & scaling                              │
│  • Mesh repair (optional: attempt to fix minor issues)   │
│  • Bounding box, volume, surface area computation        │
│  • Face adjacency graph, connected components            │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│           AUTO-ORIENTATION ENGINE  ⭐                     │
│  • Convex hull face sampling → candidate orientations    │
│  • Multi-factor scoring (supports, base, Z, overhangs)   │
│  • Select top orientation + 2 alternatives               │
│  • User interaction layer (accept / rotate / specify)    │
│  • Orientation confirmed → lock for this DFM session      │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   DFM ANALYSIS ENGINE                    │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ORIENTATION-INDEPENDENT (run once, cache)        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │   │
│  │  │  Mesh    │ │  Wall    │ │ Cavities │          │   │
│  │  │ Integrity│ │Thickness │ │  & Int.  │          │   │
│  │  │ (M1-M9)  │ │ (W1-W5)  │ │ (C1-C4)  │          │   │
│  │  └──────────┘ └──────────┘ └──────────┘          │   │
│  │  ┌──────────┐ ┌──────────┐                       │   │
│  │  │Tolerances│ │  Sharp   │                       │   │
│  │  │  & Fits  │ │ Corners  │                       │   │
│  │  │ (T1-T3)  │ │ (S1-S2)  │                       │   │
│  │  └──────────┘ └──────────┘                       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ORIENTATION-DEPENDENT (re-run on rotate)         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │   │
│  │  │ Overhang │ │Warping & │ │  Layer   │          │   │
│  │  │ & Bridge │ │  Stress  │ │ Adhesion │          │   │
│  │  │ (O1-O5)  │ │ (S3-S6)  │ │ (L1-L2)  │          │   │
│  │  └──────────┘ └──────────┘ └──────────┘          │   │
│  │  ┌──────────┐                                    │   │
│  │  │  Build   │                                    │   │
│  │  │  Volume  │                                    │   │
│  │  │ (B1-B4)  │                                    │   │
│  │  └──────────┘                                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  POST-PROCESSING (informational only)             │   │
│  │  ┌──────────┐                                    │   │
│  │  │  Post-   │                                    │   │
│  │  │Processing│                                    │   │
│  │  │ (P1-P3)  │                                    │   │
│  │  └──────────┘                                    │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              MATERIAL RULES ENGINE                       │
│  Applies material-specific thresholds (§3) to each check│
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              REPORT GENERATOR                            │
│  • Severity classification (Fail/Warn/Info)              │
│  • Printability Score computation                        │
│  • Fix suggestion generation                             │
│  • Report structured per §5                              │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│               OUTPUT LAYER                               │
│  • Interactive 3D viewer (issues highlighted on model)   │
│  • JSON report (API-consumable)                          │
│  • PDF report (downloadable)                             │
│  • Quote API integration (score ≥ 70 → instant price)    │
│  • Orientation + DFM attached to order for print operator │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Key Technical Decisions (To Be Made During Architecture)

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Mesh processing library** | Trimesh (Python), CGAL (C++), Manifold (Rust/WASM), libigl (C++) | **Trimesh** for MVP — fast Python prototyping, excellent STL/OBJ support, built-in repair, convex hull, ray-casting. Port hot paths to Rust/C++ in production if needed. |
| **3D viewer (frontend)** | Three.js, Babylon.js, Google model-viewer | **Three.js** — most flexible, vast ecosystem, STL/OBJ/GLTF loaders, orbit controls, supports face highlighting. |
| **Deployment model** | Server-side API, client-side WASM, hybrid | **Hybrid:** mesh analysis + DFM checks server-side (Python/C++). 3D rendering + orientation interaction + report UI client-side. |
| **Auto-orientation algorithm** | Face-sampling (convex hull), grid search (N° increments), genetic algorithm | **Face-sampling first** — fast (~6–20 candidates), works well for mechanical parts with flat faces. Fall back to 30° grid search for organic shapes with no clear flat faces. |
| **Wall thickness computation** | Ray-casting from faces, signed distance field (SDF), medial axis transform | **Ray-casting per sampled point** for MVP — shoot rays from surface points inward, measure distance to opposite face. Fast and sufficient for prismatic parts. SDF for complex/organic shapes in Phase 2. |
| **Overhang detection** | Face normal vs Z-axis angle, ray-casting from below | **Face normal angle check** (fast, covers 90% of cases) + **ray casting downward** for trapped/unsupportable overhang detection (O4). |
| **Support volume estimation** | Full slicer simulation, heuristic projection | **Heuristic:** for each overhanging face, project area downward × estimated support density factor. No need to generate actual support geometry — this is a DFM check, not a slicer. |
| **Hole/feature detection** | ML-based, geometric heuristics, user annotation | **Geometric heuristics for MVP:** detect cylindrical features via curvature analysis, peg-hole pairs via proximity + diameter matching. User annotation ("mark this face as critical") in Phase 2. |

---

## 8. Integration Points

| System | Integration | Purpose |
|--------|------------|---------|
| **Instant Quoting Engine** | DFM score → price eligibility. Score ≥ 70 → auto-generate quote. Score < 70 → show issues, no quote until fixed or user acknowledges risks. | Prevent quoting unprintable parts |
| **Print Farm Scheduler** | Pass final bounding box dimensions (X×Y×Z) and estimated print time. Scheduler assigns to best-fit printer. | DFM doesn't need to know which printer — just that it fits in 600³ |
| **Material Inventory** | Pull current material availability + pricing → surface only materials that are in stock. DFM thresholds use the selected material's properties from §3. | Accurate quoting, avoid selling out-of-stock materials |
| **User Account System** | Save DFM reports + confirmed orientation to user history. Track recurring DFM issues across a user's designs (e.g., "You frequently have wall thickness issues — here's a guide.") | Personalization + data moat |
| **Order Management** | Attach full DFM report + confirmed orientation (rotation matrix + preview image) to each order. | Print operator knows exactly how to orient and what to watch for |
| **Learning / Feedback Loop** | After print completes, operator records: success/failure, any DFM issues missed or over-flagged → feeds back to tune DFM thresholds and severity calibration. | Continuous improvement of the DFM engine |

---

## 9. MVP Scope — What to Build First

### 🔴 Must-Have (MVP — Build These First, ~13 Checks + Orientation Engine)

| Category | Checks | Rationale |
|----------|--------|-----------|
| **Mesh Integrity** | M1, M2, M4, M8 | If the mesh is broken, nothing else matters. These catch the 4 most common unprintable-mesh errors. |
| **Build Volume** | B1 | The single most common blocker: part too big for the printer (600³). |
| **Wall Thickness** | W1 | Thin walls are the #1 cause of print failure after bad mesh. |
| **Overhangs** | O1, O3, O4 | Overhang detection is the core DFM value proposition. O4 (trapped supports) is a true differentiator — nobody else checks this. |
| **Sharp Corners / Warping** | S1, S3 | Warping is the #1 quality complaint in FDM. Catching warp-prone geometry before printing saves reprints. Note: flag only for warp-prone materials (tendency ≥5). Don't false-flag PLA. |
| **Internal Cavities** | C1, C2 | Trapped volumes and inaccessible supports are hard blockers that customers don't understand until their part fails. |
| **Auto-Orientation** | §2.6.2 Algorithm + §2.6.3 Flow (Paths A & B) | Automatic optimal orientation is a delight factor and essential for accurate overhang/warping analysis. Manual rotation covers power users. Path C (face-based layer specification) can wait for post-MVP. |

**MVP Total: ~13 checks + orientation engine.** Estimated: 4–8 weeks with one skilled developer using Trimesh + Three.js.

### 🟡 Nice-to-Have (Post-MVP — Add Iteratively)

| Category | Checks | When to Add | Complexity |
|----------|--------|-------------|------------|
| **Mesh polish** | M3, M5, M6, M7, M9 | Month 2 — quick wins once the mesh pipeline exists | Low |
| **Build nuance** | B2, B3, B4 | Month 2 | Low |
| **Wall nuance** | W2, W3, W4, W5 | Month 3 — need more sophisticated analysis (curvature, feature detection) | Medium |
| **Bridge detection** | O2, O5 | Month 2 — O2 is a natural extension of O1 overhang detection | Low |
| **Stress/warp nuance** | S2, S4, S5, S6 | Month 3–4 — some need per-layer analysis (S5) | Medium-High |
| **Layer adhesion** | L1, L2 | Month 3 — require orientation + load-direction context | Low |
| **Tolerances & fits** | T1, T2, T3 | Month 4 — need feature-pair detection (peg-hole matching), which is non-trivial | High |
| **Cavity nuance** | C3, C4 | Month 3 | Low-Medium |
| **Post-processing** | P1, P2, P3 | Month 4 — informational only, low urgency | Low |
| **Orientation Path C** | Face-based layer specification | Month 3 — UX refinement for power users | Low-Medium |

### Recommended Build Order

```
Week 1-2:  Mesh ingestion (Trimesh) + 3D viewer (Three.js) + M1, M2, M4, M8
Week 3-4:  Auto-orientation engine + B1 + W1
Week 5-6:  O1, O3, O4 (overhang detection) + material rules engine
Week 7-8:  S1, S3 + C1, C2 + report generator + quote integration
         → MVP SHIPS HERE ←
Week 9-10: M3, M5, M6, M7, M9 + O2, O5 + B2, B3, B4 (quick wins)
Week 11-12: W2, W3, W4, W5 + L1, L2 + S2, S4
Week 13-16: S5, S6 + C3, C4 + T1, T2, T3 + P1, P2, P3 (complex checks)
```

---

## 10. Phase 2+ Enhancements (Post-MVP)

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| **Multi-Material DFM** | Analyze parts designed for soluble supports (PVA/BVOH) or multi-material printing (rigid + TPU). | Medium |
| **Lattice / Infill Optimization** | Suggest optimal infill pattern + density based on part function (load-bearing, cosmetic, lightweight). | Low |
| **Cost Optimization Mode** | Analyze part and suggest design changes that reduce print cost (hollowing, ribbing instead of solid, orientation for min supports). | Medium |
| **Design Comparison** | Upload two versions of a part → DFM engine highlights which is more printable and why. | Low |
| **Generative DFM Fixes** | AI suggests automatic geometry fixes for common issues (thicken walls, add fillets, add escape holes). | High (long-term) |
| **SLA/SLS/MJF DFM Rules** | Extend engine to other 3D printing technologies with their own rule sets. | Medium |
| **CNC DFM Rules** | Extend to subtractive manufacturing for the eventual CNC service offering. | Low |
| **Batch/Multi-Part DFM** | Analyze multiple STLs together — check nesting, inter-part clearances, consolidated print time. | Medium |

---

*This PRD defines WHAT the DFM engine must do. Architecture and implementation details to be defined in separate technical design documents.*
