---
abstract: "Measured record of which EasyEDA view-control mechanisms can and cannot drive the canonical K1-Core-Val-R0 schematic view from CDP. The whole extension-API zoom surface is dead in build V2.2.40 (no RPC responder); the editor's own toolbar view controls plus readback-gated selection do work. Read before attempting any programmatic zoom, selection or screenshot of this schematic, or before trusting an easyeda-mcp view call."
---

# Evidence capture — what can and cannot move the canonical schematic view

Target: project `64325d0e55e0435abd018defb0089a9b` "K1-Core-Val-R0", schematic
`cffcdb562c1b48d1a5214cfc263b6c90`, page `1435cb46f39e48c8a8aadbb84ca81603`,
tab `1435cb46f39e48c8a8aadbb84ca81603@64325d0e55e0435abd018defb0089a9b`.
Host: EasyEDA Pro **V2.2.40**, Full Online, CDP on `127.0.0.1:9223`, devicePixelRatio 1,
window 1800x1129. The document was left **unsaved and unmutated** throughout: only view
operations (selection, zoom, fit) and screenshots were performed.

## Headline

Every `_EXTAPI_ROOT_.dmt_EditorControl` zoom method is **dead in this build** — not
mis-argued, not mis-bound: *nothing answers them*. So are both "fit" buttons that would have
replaced them. What does work is: **Fit All in Window**, **Zoom In / Zoom Out**, the mouse
wheel as a **pan**, and selection **confirmed by readback**. Those are enough to build a
measured schematic-to-screen transform and to aim the view, and the tool does that — but at
the time of writing it has **not yet produced a capture that clears its own readability
gate**, and it says so rather than writing a picture it cannot defend.

Tool: `harness/easyeda_readable_capture.mjs` (this repo). Status: **navigation and
measurement work and are verified; framing to a readable scale is not yet closed.**

## The two wrong premises that cost the previous attempt

1. **Context binding was backwards.** The canonical sch iframe
   `frame_<PAGE>@<PROJECT>` (execution context 7) can only *push* RPC requests; the **top
   frame** (context 1) is the one whose bus *answers*. Proof: `getSplitScreenTree()` settles
   with real data in context 1 and never settles in context 7. Both frames expose
   `_EXTAPI_ROOT_`, which is what made the wrong one look right.
2. **"It never settles" was read as "it is slow".** These methods are
   `rpcCall(topic, payload)` over `_MSG_BUS2_EXTAPI_`. A topic with no responder produces a
   promise that never settles, which from the caller is indistinguishable from a slow call.
   The bus itself carries the answer: `bus.pulled` is the set of topics a frame can service.

### The responder registry — the decisive measurement

Read from `window._MSG_BUS2_EXTAPI_` in the top frame (context 1):

| Topic | In the top frame's `pulled` (can be serviced)? |
|---|---|
| `DMT_EditorControl.activateDocument` | yes |
| `DMT_EditorControl.getSplitScreenTree` | yes |
| `DMT_EditorControl.getCurrentRenderedAreaImage` | yes |
| `DMT_EditorControl.generateIndicatorMarkers` / `removeIndicatorMarkers` | yes (listed, but never answered in practice — see table) |
| `SCH_SelectControl.doSelectPrimitives` | yes |
| `SCH_SelectControl.getAllSelectedPrimitives_PrimitiveId` | yes |
| `SCH_PrimitiveComponent.get` / `getAll` | yes |
| **`DMT_EditorControl.zoomToRegion`** | **no** |
| **`DMT_EditorControl.zoomTo`** | **no** |
| **`DMT_EditorControl.zoomToAllPrimitives`** | **no** |
| **`DMT_EditorControl.zoomToSelectedPrimitives`** | **no** |
| **`SCH_Primitive.getPrimitivesBBox`** | **no** |

The zoom topics appear only in `bus.pushed` — i.e. as requests this session sent and nobody
ever answered. All five extension script spaces in the top frame carry a bound `eda` root,
and calling through those bound roots is dead too, so this is a property of the build, not
of the caller's identity.

## Mechanisms tried, with before/after witnesses

Screenshots are `Page.captureScreenshot` on the top-level target; hashes are the first 16 hex
of the SHA-256 of the PNG. "settled" means the host promise resolved.

| # | Mechanism | Context | Settled? | before → after | Moved? |
|---|---|---|---|---|---|
| 1 | `zoomToRegion(l,r,t,b,TAB)` | sch frame (ctx 7) | never | `1eda008ed720578c` → `1eda008ed720578c` | no |
| 2 | `doSelectPrimitives(ids,TAB)` + `zoomToSelectedPrimitives(TAB)` | sch frame | never | `1eda008ed720578c` → `1eda008ed720578c` | no |
| 3 | `zoomToAllPrimitives()` | top frame | never | `1eda008ed720578c` → `1eda008ed720578c` | no |
| 4 | `zoomToAllPrimitives(TAB)` | top frame | never | `1eda008ed720578c` → `1eda008ed720578c` | no |
| 5 | `zoomToAllPrimitives({tabId})` | top frame | never | `1eda008ed720578c` → `1eda008ed720578c` | no |
| 6 | `zoomTo(600,4500,4)` | top frame | never | `1eda008ed720578c` → `1eda008ed720578c` | no |
| 7 | `zoomToRegion(400,800,4300,4700)` (no tab) | top frame | never | `1eda008ed720578c` → `1eda008ed720578c` | no |
| 8 | `zoomToRegion(...,TAB)` | top frame | never | `1eda008ed720578c` → `1eda008ed720578c` | no |
| 9 | same six calls through each of the 5 extension script spaces' bound `eda` roots | top frame | never | unchanged each time | no |
| 10 | `activateDocument(TAB)` | top frame | **yes → `true`** | `3438fa79950d4357` → `3438fa79950d4357` | no (correctly — it only activates) |
| 11 | `getSplitScreenTree()` | top frame | **yes → real tab tree** | n/a (read) | n/a |
| 12 | `getCurrentRenderedAreaImage()` / `(TAB)` / `({tabId})` | top frame | **yes → `undefined`** | `3438fa79950d4357` → `3438fa79950d4357` | no image, no move |
| 13 | `generateIndicatorMarkers([{x,y}],'#F00',4,true,TAB)` (3 payload shapes) | top frame | never | `3438fa79950d4357` → `3438fa79950d4357` | no |
| 14 | `removeIndicatorMarkers(TAB)` | top frame | never | `3438fa79950d4357` → `3438fa79950d4357` | no |
| 15 | **`doSelectPrimitives(ids)`** | top frame | **yes → `true`** | `3438fa79950d4357` → changed | **yes — highlight renders** |
| 16 | **`sch_PrimitiveComponent.get(id)`** | top frame | **yes → `{x:560,y:4515,net:"GND",…}`** | n/a (read) | n/a |
| 17 | plain mouse wheel over the canvas | — | n/a | changed | **pans, does not zoom** |
| 18 | ctrl+wheel / meta+wheel over the canvas | — | n/a | negligible | no measurable scale change |
| 19 | toolbar **Fit All in Window**, **Zoom In**, **Zoom Out** | — | n/a | changed | **yes — the working view levers** |
| 20 | toolbar **Fit Selection View** (with a readback-confirmed selection) | — | n/a | `1dbf65eef05445b4` → `1dbf65eef05445b4` | no |
| 21 | toolbar **Fit Area Selection View** + slow stepped rubber-band drag | — | n/a | scale 0.2092 → 0.2091 | no |

### The capture pipeline itself was proved alive first

A witness that can never change is not a witness. Positive control: inject a transient
magenta overlay into the top frame, capture, remove it, capture again.
`1eda008ed720578c` → `ba7a8ec76ed23816` (overlay visible) → `1eda008ed720578c` (restored
byte-identical). `fromSurface:false` behaves the same with a different baseline
(`8da9274126862367` → `4c8d56c800d1af1d`). So every "unchanged" row above is a real
negative, not a dead screenshot path.

### A green light that is not wired to anything — and the reason behind it

`sch_SelectControl.doSelectPrimitives(ids)` **returns `true` while selecting nothing**, every
single time, for every component:

| selected id | call returned | `getAllSelectedPrimitives_PrimitiveId()` readback |
|---|---|---|
| `e153999` (GND net flag) | `true` | `["e153999"]` |
| `e153914` (the target wire) | `true` | `["e153912"]` |
| `$1I72` (component C1-PWR1) | `true` | `[]` |

The cause is an **id-namespace split that no error ever reports**.
`sch_PrimitiveComponent.getAll()` / `getAllPrimitiveId()` return ids of the form `$1I72`;
`doSelectPrimitives` accepts them and silently ignores them. Only `e…` primitive ids select.
`sch_PrimitiveWire.getAll()` returns `e…` ids **and** the wire geometry, so it is the correct
anchor source and is what the tool uses. Hours were spent treating this as flakiness before
the readback made it deterministic.

**Any future code that treats the return value of `doSelectPrimitives` as evidence is wrong.**
Confirm every selection with `getAllSelectedPrimitives_PrimitiveId()`.

### The selection highlight can be switched off by an unrelated panel

With the **DRC results pane open** at the bottom of the window, deselecting a confirmed
selection changed **zero pixels** — the highlight simply does not render, so nothing can be
located visually. Collapsing that pane and clicking the schematic document tab restored it
(`02589d8fb2edacd6` → `1f0379682abe2a72` on the very next deselect). The same pane also
shrinks the drawing canvas, so a viewport rectangle derived from the window height is wrong
whenever it is open. The tool now derives the viewport from the ruler's own container and
collapses the pane before it starts.

### Which view controls actually move the view

| Control | Effect, judged by measured px-per-schematic-unit |
|---|---|
| **Fit All in Window** | works — the whole sheet, scale ≈ 0.209 px/unit |
| **Zoom In / Zoom Out** | work — the view changes measurably |
| Mouse wheel over the canvas | **pans**, does not zoom |
| ctrl+wheel / meta+wheel | no measurable scale change |
| **Fit Selection View** | **inert** on this build: with a readback-confirmed selection, clicking it left the frame byte-identical (`1dbf65eef05445b4` before and after) |
| **Fit Area Selection View** + rubber-band drag | **inert**: scale 0.2092 before, 0.2091 after, including with a slow, stepped, properly delayed drag |

## What works — the exact invocation

```
node harness/easyeda_readable_capture.mjs <out.png> select <id[,id...]> [--context N] [--min-scale S] [--trace]
node harness/easyeda_readable_capture.mjs <out.png> region <l> <r> <t> <b> [--min-scale S] [--trace]
```

Mechanism, in order:

1. Bind the **top frame** execution context (the one where `typeof window._EXTAPI_ROOT_ ===
   'object'` and `auxData.frameId` is the root frame).
2. `activateDocument(TAB)` — settles `true`.
3. Discover the view controls **by tooltip** from the DOM (`[title]` starting with
   "Zoom In", "Zoom Out", "Fit All in Window", "Fit Selection View",
   "Fit Area Selection View"), never by hardcoded pixel positions.
4. `select` mode: confirm the selection by readback, click **Fit Selection View**, then click
   **Zoom Out** `--context` times so the target's neighbours are in frame.
   `region` mode: click **Fit All in Window**, measure the schematic→screen transform, then
   click **Fit Area Selection View** and drag the projected rectangle.
5. Measure the achieved scale in **px per schematic unit** by locating two components whose
   true coordinates come from `sch_PrimitiveComponent.getAll()`, each located by diffing the
   frame before and after selecting it. Solve x and y independently and cross-check them.
6. Refuse to report success unless **all three** witnesses hold: the pixels changed since the
   run began, the measured scale is at or above `--min-scale`, and the target is in the
   viewport in the final frame.

## Correction: the readback "mismatch" is not a mismatch

`doSelectPrimitives(['e153914'])` reads back `["e153912"]` because selecting a WIRE selects its
parent NET GROUP — `getPrimitiveTypeByPrimitiveId('e153914')` returns `NetGroup`. An
id-equality gate on the readback would therefore refuse **every wire target**, including both
lead repairs. The tool instead gates GEOMETRICALLY: it reads the requested primitive's own
coordinates from `sch_PrimitiveWire.get` / `sch_PrimitiveComponent.get` (independent of the
selection), projects them through the verified transform, and requires them to land inside the
highlight. A highlight on the wrong object fails that; a highlight on the wire's own net group
passes it. This is the fourth witness, `highlight_on_target`.

## The one defect that still blocks a readable capture, and its exact fix

The tool now: binds the answering frame, collapses the panel that suppresses highlights,
reads the target's true coordinates from the live API, fits the whole sheet, and measures a
**third-anchor-verified** transform there (residual 0-1 px, scale 0.209 px/unit). It then
pans with the wheel toward the target and raises the scale with Zoom In.

The pan-and-zoom loop demonstrably reaches a readable scale: mid-run the target wire's own
selection highlight was measured at **2012 changed pixels spanning 186x137 px** (at fit-all
the same wire is 17x1 px), so the view really did land on it, magnified. What is not yet
closed is holding that state through the next measurement.

**Current state after raising the zoom cap.** The cap was the first blocker and is fixed: the
climb now computes its own click count from the fit-all scale and is capped at 30, with a
2%-gain saturation break. What that exposed is the real remaining gap — **the target is never
centred before the climb**. Toolbar Zoom In zooms about the VIEWPORT CENTRE, and at Fit All the
target sits wherever it sits, so ~14 clicks walk it off screen: after the climb no anchor near
the target is locatable and the run ends at the measure gate. The mouse wheel pans (measured),
so the fix is to centre the target first — calibrate pixels-per-notch by measuring the
transform offset change across a few notches, then pan by the computed notch count — and only
then climb. One pan calibration attempt failed mid-run and needs a retry path.

It fails in the loop after the first pan. `measureTransform` filters its candidate anchors by
predicting their screen position from the **previous** transform — but the pan has just moved
the view, so every prediction is stale by exactly the pan offset, and the search walks 20+
off-screen candidates and gives up. **The fix is to offset the prediction by the intended pan
before filtering** (`prev.ox += dx; prev.oy += dy`), or to re-measure with an unfiltered
nearest-to-seed ordering when the filtered search finds no second anchor. Until that is done
the run ends at the witness gate with `scale_ok: false` and writes nothing — which is the
correct behaviour, not a workaround.

## Still broken / still true

- The entire `dmt_EditorControl` zoom API and `SCH_Primitive.getPrimitivesBBox` are
  unavailable on build V2.2.40. Do not build anything on them, and do not read a
  non-settling promise as "slow".
- `getCurrentRenderedAreaImage()` settles and returns `undefined` — there is no direct
  canvas-image API to fall back on.
- `generateIndicatorMarkers` is listed as serviceable but never answered any of the three
  payload shapes tried, so there is no marker-annotation path either.
- `doSelectPrimitives` is unreliable, badly so for large id arrays. Always gate on readback.
- Selection highlight is the only way to locate a primitive on screen, so a primitive that is
  off-view cannot be found without first widening the view.

## What this means for gate closure

Not closed yet, and no capture should be treated as evidence until it is. Across every run
the tool wrote **zero PNGs** — it refused each time rather than emitting a picture whose
readability it could not defend, which is the property that matters most here.

What is now settled and will not have to be rediscovered: the extension-API zoom surface is
dead on this build, the answering frame is the top frame, selection needs readback and the
right id namespace, wires are the usable anchor source, the wheel pans, Zoom In/Out and Fit
All work, and both "fit" buttons do not. The remaining work is one bug in anchor
re-acquisition after a view move, described above with its fix.

Whatever lands, the path is GUI-dependent: it needs the editor window open at
devicePixelRatio 1 with the canonical tab active and no bottom panel expanded. It is not a
headless path, and it cannot be run while anything else is driving the same editor — two
concurrent runs corrupted each other's measurements early in this session.
