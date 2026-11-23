# TI-84 Plus CE — Physics Force Solver Suite

A complete TI-BASIC physics suite for the **TI-84 Plus CE**, generated as one
calculator group file, **`FORCES.8xg`**, by a single Python script,
[`forces_builder.py`](forces_builder.py).

Seven programs, every one of them a real calculator program: menus, input
validation, multi-page worked solutions, and no hard-coded worksheet numbers.

| Program | Size | What it does |
|---|---|---|
| `FORCEMNU` | 8 | Master menu / launcher for everything |
| `GSET` | 4 | Gravity setup — 9.8, 9.81, 10, or custom; stores it in `G` |
| `VECADD` | 6 | 2-D vector addition: magnitude+angle, x/y parts, or N/S/E/W totals |
| `FLATFRC` | 7 | Horizontal-surface solver: static, constant velocity, accelerating |
| `ANGPULL` | 7 | Force applied above/below the horizontal, including lift-off |
| `RAMPSLV` | 7 | Inclined plane: static, kinetic, critical angle, up/down the ramp |
| `FBDHELP` | 7 | Multi-page free-body-diagram reference |

## Quick start

```bash
pip install tivars          # the only runtime dependency
python forces_builder.py
```

That writes `FORCES.8xg` into the current directory and prints the program list
and a verification report:

```
Validating TI-BASIC sources ...
  ok: 7 programs, syntax rules satisfied
Tokenizing and packing FORCES.8xg ...
  ok: 7 programs tokenized
    FORCEMNU  master menu and launcher
    GSET      gravity setup, stores g in G
    ...
Wrote /path/to/FORCES.8xg (NNNN bytes)
Verified: all 7 programs are present in the group.
```

Python 3.10 or newer is required by `tivars`. `tivars` itself handles the
TI-BASIC tokenizer and the group-file container; nothing else is needed.

**No Python handy?** Every push builds the file in CI and attaches it:
**Actions → build → latest run → Artifacts → `FORCES-8xg`**. The zip contains
the ready-to-transfer `FORCES.8xg`.

## Installing on the calculator

1. Run `python forces_builder.py` so `FORCES.8xg` exists on your computer.
2. Connect the TI-84 Plus CE with a USB cable and open **TI Connect CE**.
3. Click **Calculator Explorer**.
4. Drag `FORCES.8xg` onto the calculator, or use **Send to Calculator**.
5. On the calculator press `2ND` `+` (**MEM**) → `8:Group…`, highlight
   `FORCES`, press `ENTER`, and choose `UNGROUP`. Ungrouping writes all seven
   programs into RAM.
6. Press `PRGM`, choose `FORCEMNU`, press `ENTER`, and start with
   **1 GRAVITY SETUP**.

A group has to be ungrouped once per calculator; after that the seven programs
sit in the program list on their own.

## Using it

The launcher is `FORCEMNU`. Everything returns to the menu when a solver
finishes, so you never have to restart a program.

1. **Gravity Setup** — pick `9.8`, `9.81`, `10`, or type a custom value. The
   value lives in the real variable `G`, and every solver reads `G`; nothing
   hard-codes gravity. If `G` is ever zero (fresh calculator), each program
   restores the 9.8 default before using it.
2. **Vector Addition** — three input modes. Angles are standard mathematical
   angles: 0° = east, 90° = north, 180° = west, 270° = south. Each angle must be
   in 0–360°, and magnitudes and the N/S/E/W totals must be non-negative;
   anything else is rejected and re-prompted. You get every vector's `Fx`/`Fy`
   tagged **E/W** and **N/S**, `ΣFx`/`ΣFy` (also tagged), explicit **EAST /
   WEST / NORTH / SOUTH** nets, the resultant's magnitude and quadrant-safe
   direction, the reference angle with the nearest cardinal axis named, and the
   equilibrant. A zero resultant is reported as equilibrium instead of an
   undefined angle.
3. **Horizontal Forces** — mass, push, direction, motion state, and both
   friction coefficients ("KNOWN", "ZERO", or "UNKNOWN" are three separate
   answers, so an unknown µ is never treated as 0). When the object is
   accelerating it asks **which way it is moving** — same way as the push, or
   opposite — because kinetic friction opposes the motion, not the push. Static
   situations are checked against `Fs max`; constant velocity reports the µk it
   requires and flags a supplied µk that does not fit (at constant velocity the
   motion must be along the push, since friction can only oppose, and the screen
   says so); accelerating situations report `Fnet`, `a`, which way `a` points
   relative to the push, and whether the object is speeding up or slowing down.
4. **Angled Forces** — pull up or push down at 0–90° from the horizontal.
   `FN = Fg − Fy` for a pull, `FN = Fg + Fy` for a push, with a lift-off check
   (`FN ≤ 0` → the object leaves the surface, and **no** friction is computed).
   Motion direction is asked here too, so friction is applied against the actual
   motion. Also solves the inverse problem: the applied force needed for
   equilibrium.
5. **Inclined Planes** — `Fg·sin θ` along the ramp, `Fg·cos θ` into it, friction
   direction taken from the actual tendency to move (not assumed to point down
   the ramp), the critical angle `tan⁻¹(µs)`, and the acceleration along the
   ramp when sliding.
6. **FBD Help** — eight pages: force symbols, friction, angled forces, ramp
   components, equilibrium, and Newton's three laws, with text diagrams.

## Shared calculator variables

| Variable | Meaning |
|---|---|
| `G` | gravitational acceleration, used by every solver |
| `L1`–`L4` | vector x-components, y-components, magnitudes, angles (`VECADD`) |

Each solver keeps its own working variables inside single letters, and none of
them clobbers `G` or the lists another program depends on.

## Design rules the sources follow

* Program names ≤ 8 characters, letters and digits, starting with a letter.
* Every `Goto` and every `Menu(` label resolves to a `Lbl` in the same program.
* `If`/`Then`/`End` balanced; every `prgm` call names a program in the group.
* Every `Output(` stays inside rows 1–10 and columns 1–26, **and** the column it
  actually ends on is checked: start column plus the width of the text or number
  must reach column 26 at most. `Output(` wraps onto the next row rather than
  erroring, so without this a long label or number would silently overwrite the
  line below.
* Every program issues `Full` first, because split-screen mode makes `Output(`
  to rows 5–10 an error.
* Values are shown with `round(x,2)`, computed at full precision internally.
* Unknown is never zero: each µ has KNOWN / ZERO / UNKNOWN choices.
* No division by zero: masses and distances are validated positive, and the
  angled-force equilibrium denominator `cos θ + µ·sin θ ≤ 0` is reported as
  "NO SOLUTION" instead of dividing.
* Angles are always in **DEGREE** mode; each program sets it on entry.

`validate_sources()` in the generator enforces all of the structural rules
above every time you run it, and the test suite runs the same checks.

## Tests

```bash
pip install tivars pytest
python -m pytest -q
python forces_builder.py
```

* `tests/test_builder.py` — program names, label/menu/`prgm` targets,
  `Then`/`End` balance, `Output(` bounds **and rendered width**, Menu title/item
  and Input prompt limits, the `Full` guard, the motion-direction wiring in the
  two friction solvers, VECADD's angle and N/S/E/W validation and its cardinal
  direction labels, then actual tokenization of all seven programs, a token
  round trip back to the source, and an ungroup/re-group round trip of the
  written `FORCES.8xg`.
* `tests/test_physics_reference.py` — the physics model, exercised against
  independently hand-worked values: perpendicular and opposite vectors, all
  four quadrants, a zero resultant, static friction below and above its
  maximum, constant velocity, acceleration with kinetic friction, upward and
  downward angled forces, loss of contact, and inclined planes with no friction,
  static friction, kinetic friction, and applied forces in both directions.

GitHub Actions runs both (`tivars` installed, calculator targets are not
needed) and attaches `FORCES.8xg` to the run as a downloadable artifact:
**Actions → build → latest run → Artifacts → FORCES.8xg**.

## Verification status — what was and was not tested

Honest accounting, because "it works" is not a test:

| Claim | Status |
|---|---|
| TI-BASIC sources written and structurally reviewed | **Done** (by hand, line by line) |
| Program names, labels, menu targets, `Then`/`End`, `Output(` bounds, string widths | **Checked** by `validate_sources()` on every run |
| Python generator executed | **Yes — in GitHub Actions** (Python 3.11, `tivars` 1.1.1). Output: `ok: 7 programs, syntax rules satisfied` / `ok: 7 programs tokenized` |
| TI-BASIC tokenized by `tivars` | **Yes** — all 7 programs tokenized, and the token stream decodes back to the exact source (`test_tokens_round_trip_to_the_same_source`), so no command was silently read as single letters |
| `FORCES.8xg` created | **Yes** — 14,943 bytes, re-opened and verified to contain all 7 programs; also published as the `FORCES-8xg` CI artifact |
| Test suite | **50 passed** (`python -m pytest -q`) |
| Execution on a physical TI-84 Plus CE or an emulator | **Not performed.** The arithmetic is validated against the reference model in the test suite and the byte code is verified, but no run has been made on hardware or in an emulator such as CEmu. |

The token sheet used for spelling (`8X.xml` from the TI-Toolkit tokens
project) is what `tivars` matches against, so every command in the sources is
spelled with its documented accessible name (`Disp `, `If `, `Pause `, `Lbl `,
`Goto `, `Output(`, `Menu(`, `sqrt(`, `tan^-1(`, `->`, `>=`, `<=`, …).

## Files

```
forces_builder.py                 generator: TI-BASIC sources + build + validation
tests/test_builder.py             structural and tokenization tests
tests/test_physics_reference.py   physics model tests
.github/workflows/build.yml       CI: tests, build FORCES.8xg, upload artifact
requirements.txt                  tivars
```

## License

MIT. Do what you like with it.
