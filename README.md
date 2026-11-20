# Palletizer

A 3D pack planner for shipping fabricated pieces on racked LTL pallets or in a rental or box truck. Each job is a **project** in a small project library; the 30 aluminum arches are the first one.

Open `index.html` in a browser. It loads three.js from jsDelivr and needs to be served over HTTP (not opened as a file) to read `projects/`.

## How projects get in

Source models (usually a Rhino file with every asset and its quantity) go through Claude: Claude interprets the model, works out the shippable pieces, their quantities and weights, and writes a project file to `projects/` (listed in `projects/index.json`). In the app, a project file that isn't in your library yet shows up as "· new"; opening it adds it.

You can also import or export project files from the ⋯ menu, duplicate a project to try another pack, and add simple box items (crates, bundles) yourself.

## Storage

- Hosted on claude.ai, projects live in the page's database (one record per project, geometry in separate records), private to the owner and editors.
- Anywhere else (e.g. GitHub Pages), projects come from `projects/` and your edits are saved in the browser's local storage.

## Project file format (`palletizer-project`, version 1)

```
id, name, notes, source, created, updated
settings: { tol, tooth, pallet: { L, W, deckStd, deckLow, maxH, tallMaxH } }   // inches
groups:   [{ id, name, qty, color }]                                            // assemblies, e.g. "Arch A" ×2
items:    [{ id, name, desc, group, perGroup | qty, kind: "profile" | "box",
             t (thickness), lb (each),
             pieces: [{ k: "main" | "rung" | "plate", p: [[x, y], ...] }],     // profile outline, inches
             hull: [[x, y], ...],                                               // convex hull of the outline
             box: { l, h } }]                                                   // for kind "box"
shipping: { mode, vehicle, veh, prio, moves, costs }
edits:    { itemId: { name, qty, perGroup, t, lb } }                            // user overrides
extraItems: [ ...box items added in the app ]
```

An item's total quantity is `qty`, or `perGroup × group.qty`.

## Features

- Pallet mode with racked slots, packing tolerance per face, comb teeth (⅜" UHMW or ½" plywood), tall racks for pieces that need them, and pallet size and height limits per project.
- Truck mode: U-Haul 10', 15', 20', 26' or a custom box truck; fit, payload, door, ramp, wheel-well and center-of-gravity checks.
- Load sequence with "unload first" by group, weight and balance, packing list (copies to a spreadsheet), cost comparison, manual moves, and dimension lines.

## Layout

```
index.html                 built, standalone app
src/head.html              markup and styles
src/app.html               app logic (three.js module)
projects/                  project files and index.json
tools/build.py             rebuilds index.html from src/
tools/geometry/            scripts that derived the arches project from its Rhino model
```

Edit `src/`, then run `python3 tools/build.py`.
