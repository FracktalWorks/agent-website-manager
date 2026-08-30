# Prospects: manufacturing & hardware (3D printing in detail)

Read with `universal.md`. Written for a machine/materials manufacturer;
the 3D printing rows are specific, the headings transfer to any hardware
vertical (CNC, robotics, electronics, lab equipment).

Link type key: **F** followed · **N** nofollow · **M** mention/entity only.

## Product databases (links from the pages buyers actually compare on)

| Target | Type | Note |
|---|---|---|
| Aniwaa (aniwaa.com) | F | 2,400+ AM products; takes manufacturer submissions. **Check for stale listings first** — retired models with links to dead URLs are a redirect job, then an update request. |
| All3DP (all3dp.com) | F | Buyer's guides and "best of" lists; pitch the editors with a data point, not a brochure |
| Pick3DPrinter, 3DSourced, Top3DShop database | F/N | Verify each one's listing path; some are affiliate stores |
| Manufactur3D (manufactur3dmag.com) | F | **India's AM magazine** — company directory, news, "Made in India" features |
| 3D Printing Industry directory / 3DPrint.com company pages | F | Verify current directory status; both run vendor news |
| Marketplace product pages (Amazon, IndiaMART, Moglix, Robu.in, etc.) | N | Entity and reviews for consumables |

## Trade press (news track pieces go here first)

Global: 3DPrint.com, Fabbaloo, VoxelMatters, 3Dnatives, TCT Magazine,
3D Printing Industry, 3D ADEPT Media, All3DP news, Develop3D, Hackaday
(for open hardware/firmware stories).
India: Manufactur3D, The Machinist, Machine Maker, Electronics For You
(EFY), Industrial Automation India, Manufacturing Today India, Autocar
Professional (automotive applications), ET Manufacturing, Express
Computer (Industry 4.0).
Hooks that get run: a launch with specs and price, a customer application
with a picture, a materials data release, a policy comment (PLI, budget,
import duty), a manufacturing-in-India milestone with a number.

## Open-source and software registries (followed links on very high-authority domains)

| Target | What to contribute | Note |
|---|---|---|
| OrcaSlicer `resources/profiles/` (github.com/SoftFever/OrcaSlicer) | vendor printer + filament profiles | Vendor appears in the slicer's printer list; README/vendor JSON carries the site URL |
| PrusaSlicer vendor profiles (github.com/prusa3d/PrusaSlicer-settings) | printer bundle `.ini` | Same effect in PrusaSlicer's wizard |
| Cura definitions (github.com/Ultimaker/Cura `resources/definitions/`) and `fdm_materials` | printer definition, material profiles | Cura shows the manufacturer in "Add printer" |
| Klipper config examples (github.com/Klipper3d/klipper `config/`) | `printer-<vendor>-<model>.cfg` | If the machine runs Klipper |
| Marlin configurations (github.com/MarlinFirmware/Configurations) | config set per model | If the machine runs Marlin |
| OctoPrint plugin repository (plugins.octoprint.org) | any maintained plugin | Plugin page links to the vendor |
| Printables, Thingiverse, MakerWorld, Thangs | test models, upgrades, fixtures under the brand account | Profile links + the models get embedded and cited |
| Own GitHub org | firmware, slicer forks, profiles, datasets | Keep READMEs current; pin the repos |

## Academic and institutional

- Google Scholar alert for the brand and each product name; ResearchGate
  search for "‹brand› ‹model›" — every paper that used the machine is a
  citation to collect into the research roundup page, and a lab to email.
- University lab "equipment / facilities" pages (IISc, IITs, NITs,
  Manipal, VIT, SRM, private engineering colleges) — ask for the machine's
  listing to link to its page.
- Shodhganga (Indian theses) — mentions, no links; still entity evidence.
- Atal Tinkering Labs / Atal Incubation Centres that run the machines —
  the AIM site and each centre's page.
- AMSI — Additive Manufacturing Society of India (amsi.org.in): member
  directory, conference proceedings and speaker pages.

## Government and scheme pages

DPIIT / Startup India profile; GeM catalogue; state startup cell showcase;
the beneficiary or partner page of any ministry scheme the brand appears
under (DST, MeitY, Ministry of Heavy Industries — Samarth Udyog Industry
4.0 centres, capital goods schemes); Make in India / Invest India sector
pages when there is a story.

## Events (exhibitor and speaker listings)

IMTEX (Bengaluru), Bengaluru Tech Summit, AMSI's international conference,
AMTech / AM expos in India (verify the current name each year), Formnext
(Frankfurt) and TCT 3Sixty exhibitor lists if exhibiting abroad, Maker
Faire events, college tech fests where the brand sponsors or judges.

## Communities

Reddit: r/3Dprinting, r/FixMyPrint, r/functionalprint, r/3DPrintingIndia
(verify activity), r/india and city subs for the Made-in-India angle.
Forums: Printables community, RepRap forums, Klipper and OrcaSlicer
Discords, Indian maker WhatsApp/Telegram groups. YouTube: reviewers
accept loan units — a review is a video, an article and a link.

## Linkable assets this vertical rewards

| Asset | Source the brand already has |
|---|---|
| Material property database with measured values and radar/scatter charts | the materials the brand sells and tests |
| Filament / consumable price index for the country, updated quarterly | the brand's own price list and competitor scrape |
| 3D printing cost index (per cm³ by process) from real quotes | the service floor's quote log |
| HSN / GST / import-duty reference for printers, filaments, parts | the accountant's table — accountants and importers link to it |
| Bed-adhesion or material test matrix with photographs | one day on the production floor |
| "Research using ‹brand› machines" roundup with citations | Scholar + ResearchGate search |
| Slicer profile downloads page (mirrors the upstream contributions) | the profiles just contributed |
