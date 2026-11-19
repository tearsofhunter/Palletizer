# Palletizer

A 3D pack planner for shipping 30 aluminum arches (1" × 1" × 0.125" wall tube and 1" × ¼" flat) as 116 bolt-together sections plus 24 bottom bars. Open `index.html` in a browser; it runs standalone and loads three.js from jsDelivr.

## What it does

- **Two shipping modes.** LTL pallets (40" × 48", racked) or a rental or box truck (U-Haul 10', 15', 20', 26', or your own dimensions).
- **Velcro clearance slider.** Sets the space on each face of a piece; slot width, pitch and pallet count re-pack live. The tall E2 racks grow as needed so E2 still fits the 45" rack width.
- **Comb teeth.** ⅜" UHMW (tight) or ½" plywood (standard).
- **Truck checks.** Fit, payload against max load, whether pre-built pallet racks pass the door, ramp width, wheel wells, and center of gravity front-to-back and side-to-side.
- **Load sequence.** Step through or play the load piece by piece. "Unload first" loads a chosen arch last, at the door end.
- **Weight & balance.** Aluminum weight, estimated rack weight and CG for each pallet or the truck.
- **Packing list.** Every piece with an ID (`P2-07b` = pallet 2, slot 7, second piece), location and load step. Copies to a spreadsheet.
- **Cost comparison** from your own quotes.
- **Manual moves.** Move a selected piece to another pallet/slot; the rest re-packs around it.

Section shapes, sizes and weights come from the Rhino model. Racks, ribs, foam and pallets are schematic. The 26' U-Haul deck height and all wheel-well sizes are estimates; edit them in the app.

## Layout

```
index.html                 built, standalone viewer
src/head.html              markup and styles
src/app.html               viewer and packing logic (three.js module)
data/sections.json         section outlines, hulls and weights for each section type
tools/build.py             rebuilds index.html from src/ and data/
tools/geometry/            scripts that derived the section data from the Rhino file
```

## Rebuilding

Edit `src/` or `data/`, then run `python3 tools/build.py`.

## Regenerating the section data

The scripts in `tools/geometry/` read the Rhino model (not included in this repo) with `rhino3dm` and `numpy`, and were run in order from one working folder:

1. `01_parts.py <model.3dm>`: classifies every closed outline as tube or flat and measures its length.
2. `02_curvature.py <model.3dm>`: splits curved rails into straight and arc portions and fits roll radii.
3. `03_marks_and_nest.py`: assigns part marks and nests the cut list onto 24' sticks.
4. `04_sections.py <model.3dm>`: groups pieces into bolt-together sections and measures them.
5. `05_export_sections.py`: writes the section outlines, hulls and weights used by the viewer.
