# TI-84 Plus CE — Physics Force Solver Suite

A TI-BASIC physics force-solver and free-body diagram suite for the **TI-84 Plus CE**, generated as a single calculator group file (`FORCES.8xg`) by `forces_builder.py`.

## Included Programs (8)

* **`FORCEMNU`** — Master menu / launcher for all programs.
* **`GSET`** — Gravity setup (`9.8`, `9.81`, `10`, or custom value stored in `G`; defaults to `9.8` if `G <= 0`).
* **`VECADD`** — 2-D vector addition supporting magnitude + angle (`0°–360°`), x/y components, or N/S/E/W totals.
* **`FLATFRC`** — Horizontal-surface solver (static, constant velocity, accelerating; `KNOWN`, `ZERO`, `UNKNOWN` friction modes).
* **`ANGPULL`** — Force applied above or below the horizontal (`0°–90°`), lift-off check (`FN <= 0`), and equilibrium force solver.
* **`RAMPSLV`** — Inclined-plane solver (`Fg sin θ`, `Fg cos θ`, critical angle `tan⁻¹(μs)`, static/kinetic friction, up/down ramp acceleration).
* **`FBDDRAW`** — Graph-screen free-body diagram viewer for horizontal surfaces, angled pulls/pushes, inclined planes, and hanging objects.
* **`FBDHELP`** — Multi-page free-body-diagram text reference.

## Quick Start & Installation

Requires **Python 3.10+** and `tivars`:

```bash
pip install tivars
python forces_builder.py
```

`forces_builder.py` validates all TI-BASIC sources, tokenizes each program for the TI-84 Plus CE, and packs them into `FORCES.8xg`.

Transfer `FORCES.8xg` to your calculator using **TI Connect CE**, ungroup it via `2ND` `+` (`MEM`) → `8:Group...` → `UNGROUP`, and launch the suite from `PRGM` → `FORCEMNU`.

## Using the Free-Body Diagram Viewer (`FBDDRAW`)

Launch `6 FBD DIAGRAM` from `FORCEMNU` (or run `prgmFBDDRAW` directly):

1. **Select a situation:**
   * `1 HORIZONTAL` — Object on a horizontal surface.
   * `2 ANGLED PULL` — Object on a horizontal surface with a force applied at `0°–90°` above or below horizontal.
   * `3 INCLINED PLANE` — Object on a ramp inclined at `1°–89°`.
   * `4 HANGING ROPE` — Object suspended vertically by tension.
2. **Choose value mode:**
   * `1 SYMBOLS ONLY` — Draws arrows labeled with force symbols only.
   * `2 ENTER VALUES (N)` — Prompts for mass (`kg`, `0` if unknown) and applicable force magnitudes (`N`, `0` if unknown), then displays known magnitudes beside each symbol.
3. **Select active forces:**
   * Choose whether an applied force (`Fa`) or tension (`FT`) acts and its direction.
   * Choose whether friction acts (`NONE`, `Ff`, `Ffs`, or `Ffk`) and its direction. Friction is only drawn when selected (and omitted automatically if `FN <= 0` on an angled pull).
4. **View the diagram:**
   * The object is drawn as a box in the center of the graph screen with labeled force arrows (`Fg`, `FN`, `Fa`, `Ff`, `Ffs`, `Ffk`, `FT`) pointing away from the object.
   * Press any key to return to the `AGAIN` menu (`NEW DIAGRAM` or `MAIN MENU`).

## Shared Variables & Design Rules

* Uses `G` (gravitational acceleration, default `9.8 m/s²`) and lists `L1`–`L4` (`VECADD`).
* Enforces `<= 8`-character program names, matched `Goto`/`Menu(` → `Lbl` targets, balanced `If`/`Then`/`End` blocks, `Output(` bounds (`1–10` rows, `1–26` columns), `Full` screen mode, and `Degree` mode.

## Running Tests

```bash
pip install tivars pytest
python -m pytest -q
```