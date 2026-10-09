# ABleemStation - notes for contributors

A 3D-printable Raspberry Pi console case. Everything under `files/` is **generated** by the scripts in `src/` -
never edit a generated file, change the script and rebuild. This file holds the structure, the rebuild steps, the
design numbers and the rules behind them. The user-facing description is `README.md`.

## Structure

```
src/make_case.py        the Pi 3 case: shell, base, button tree, lens, LED holder; the fit checks; STEP/STL/3MF
src/make_universal.py   the universal case (Pi 2/3/3B+/4/5): port panels, uni-base, uni-bottom, shells
src/make_stickers.py    the stickers (SVG, PNG, A4 PDF, Cricut PNGs), two sets: default and special/
src/make_viewer.py      the two 3D viewers (HTML, three.js) + the renders + the colourways + "Download ZIP" pack
src/make_wiring.py      the two wiring diagrams (plain LED, RGB pixel)
src/make_orca_profile.py  the Orca Slicer process profiles
src/make_all.py         runs case -> universal -> stickers -> viewer -> universal viewer, in that order
src/checks/             development checks and the fit coupon (run from the repo root, outputs go to build/checks/,
                        git-ignored); each has a header comment saying what it checks. They import the generators
                        and are not part of make_all.py
LICENSE, LICENSE-CODE   CC BY-SA 4.0 (models, wiring, stickers, renders, docs) and MIT (scripts in src/)
src/fonts/              Open Sans, Red Hat Text (SIL OFL; the licences sit next to them)
files/                  generated outputs; files/viewer/ and files/universal/viewer/ hold the meshes and
                        params.json the viewers read (so the viewers never copy a size)
```

## Rebuilding

Needs Python 3, `pip install build123d`, and Chrome / Chromium (headless, for the renders, the PDF and the PNGs;
`CHROME=<path>` if it is not found). Pillow for the render sheets.

```
cd src
python make_all.py              # regenerates everything except the wiring diagrams and the Orca profiles
python make_wiring.py           # the wiring diagrams
python make_orca_profile.py     # the Orca profiles to files/orca/ (--install also copies them into Orca's user
                                # folder, never overwriting an existing one; run with Orca closed)
```

Order matters: the universal case imports `make_case`; the viewers read the meshes, `params.json` and the stickers the
others wrote. After any change run `make_all.py`, never one script on its own, or a viewer is left from an older model.
`make_viewer.py` has a self-test for the ZIP download (`&zipcheck=1`) that it runs itself.

## Before changing anything

1. Change a variable at the top of `make_case.py` / `make_universal.py` (every size is one), not a number in a file.
2. Run `make_all.py`. It must finish with "all done": the scripts **assert** their fit checks and stop on a failure.
3. Look at the renders and the viewer; print a fit coupon or a prototype (Orca profile "... ASA Prototype") before
   a long print when a tolerance changed.
4. Commit the scripts and the regenerated `files/` together.

The checks that stop a build: the Pi (a ghost solid) overlaps the case by 0 mm3 for every board and every shell/panel
combination; every roof vent slot is open on both roof faces along its whole length; each LED holder is one body
with the shell, clear of the lens and not showing outside; the button tree clears the shell; the switches clear their
bracket; every boss is clear of the walls and the plate edge; the universal case checks each board against each shell
and its panels (0 mm3), the front USB sockets against the base, and the panel tongues against their grooves.

## Coordinate system and the main numbers (mm)

x = width, y = depth (0 = back wall, D = front), z = up. Outer size 140 x 105; height **27.6** (the Pi's USB stack of
16 + 1 + roof 3.2, on a 3.0 base plate and 3.0 standoffs). Walls 2.4, roof 3.2, the two cut corners 16 (top right and
bottom left of the plan: the memory card's shape). Base plate 3.0, 0.3 gap to the walls. The Pi board corner is at
(BX, BY): USB 2 mm past the board edge, HDMI side 1 mm. Pi mechanical data: board 85 x 56 x 1.4, mounting holes 58 x 49
from (3.5, 3.5), from Raspberry Pi Ltd's drawings (3B+, 4B, 5).

- **Waist groove** at z = 11 (`BAND`): below it the second colour, so the filament change sits at the groove.
- **Buttons**: holes at x = 24 and 44, z = 16.5, 4.6 mm radius; LED / lens at x = 118; lens shaft 3.0 mm radius,
  flange 4.0 radius, 1.0 thick, in a counterbore.
- **Bosses** for M3 heat-set inserts (M3 x 5 x 4, hole radius 2.35 = 4.7 mm, 6 mm deep): (12.5, 14.5), (10, 84),
  (131, 66), (128.5, 90.5). They sit off the cut corners; the earlier positions broke through the wall at the corners.
- **Standoffs** 3 mm (clears the microSD socket under the board), M2.5 self-tapping in a 2.3 mm hole with a 0.6 mm
  lead-in chamfer. The microSD window in the base floor is **35 x 20 mm**, reaching out past the board edge (a
  smaller window was too small to get a card out).
- **Filament change heights** are printed by the scripts, never typed: shell 16.68 mm = layer 104 at 0.16 mm layers,
  16.80 mm = layer 70 at 0.24; panels (printed standing) 10.92 mm = layer 68 at 0.16, 10.80 = layer 45 at 0.24.
  `LAYERS` in `make_case.py` holds the two profiles' first-layer and layer heights.

## Design rules and why

- **No supports anywhere.** Every part is shaped to print without them: the shell roof-down, the base flat, the
  button tree flat with the shafts up, the lens on its flange, panels standing. Overhangs are 45 degrees at most, and
  holes whose first layers would hang get a sacrificial bridge step (`BRIDGE_STEP` 0.48 mm: 3 layers at 0.16, 2 at
  0.24) over the screw-head recess.
- **Hidden vents, no line of sight into the case.** Roof slots run through the 3.2 mm roof at 45 degrees; the slot's
  inner end is 3.2 mm in front of its outer end, more than the slot is wide (2.4), so you only ever see the slot's
  sloping wall. A 45 degree wall prints without a bridge. (An earlier labyrinth with a bridged channel printed shut:
  the bridge sagged.) Side vents: slots through the wall with a baffle 1.8 mm behind them, closed at both ends and
  open below.
- **Sticker recesses** 0.4 mm deep (roof logo plate 62 x 18, front label strip 44 x 5), so a sticker sits flush.
- **Button tree**: both caps are one printed part on flexible strips; its two ears are melted onto two pins in the
  shell. The pins are low and outboard so the strips are long enough to flex; the right ear is cut flat at x = 58.85 to
  clear the universal front panel's groove lip.
- **LED holder**: a part of its own, reaching 0.6 mm into the front wall and roof so the slicer welds it to the
  shell (one 3MF object, two parts). One shell body serves both lights; `shell` vs `shell-rgb` differ only in the
  holder (a 5 mm LED tube with the tip 0.3 mm behind the lens, or a 10.6 x 2.4 mm slot for a WS2812B strip piece).
- **Universal panels**: clearance 0.15 mm each side in the opening, tongue 1.2 mm thick reaching 1.2 mm into its
  groove with 0.15 clearance, inner lip 1.45; the shell's openings and grooves are a further 0.15 mm wider on every
  side (`EASE`) so the top slides over standing panels. Panels sit in rebates of the base (tab seat 1 mm below the
  plate top); in the one-piece bottom the tabs are welded to the base with a 0.6 mm joint fill.
- **Print orientation of panels**: standing on the bottom edge, so a filament change gives them the shell's colours at
  the same line. Panels are printed fused to the base in
  the one-piece bottoms; the separate panel files print standing, with a brim.
  Panel "noses" (extra locating bumps) were tried and removed.
- **Front USB** (universal): the common 17 x 17 mm "USB-A to DIP" breakout board lies flat on base pedestals, held by two
  ~1.85 mm sheet-metal screws in 1.7 mm holes (1.9 mm gripped too little). The socket sits 1.3 mm above the board
  (`SOCKET_LIFT`); the shell's front sticks out 5.4 mm past the board, with a 0.3 mm gap at the step. Cradles snap the
  sockets in.
- **Active shell**: 8 slots over the Pi 5 Active Cooler (63.5 x 42.5 x 13.7 mm), field centred at (BX+35, BY+31),
  64 mm long; the cooler fits under the roof with 3 mm to spare.
- **Colour choices**: colourways are real ASA colours, listed in `COLORWAYS` in `make_viewer.py` (top, band, base,
  buttons, optional sticker set). The "Grey 94" set uses colours only, no third-party marks. Sticker colours come from
  `PALETTES` in `make_stickers.py`. Never add a third-party logo or mark to a sticker or panel.

## Wiring facts (the electronics the files assume)

- POWER: GPIO3 (pin 5) + GND (pin 9), `dtoverlay=gpio-shutdown` (shuts down; wakes a Pi 2/3/4 from halt; a Pi 5 cannot
  be woken by GPIO3 - wire POWER to the board's J2 pads instead).
- RESET: GPIO23 (pin 16) + GND (pin 20), `dtoverlay=gpio-key,gpio=23,active_low=1,gpio_pull=up,keycode=164`. Keycode 164
  is the key the PlayStation Classic's Reset button sends. A software reset, not a power cycle.
- LED: GPIO14 / TXD (pin 8) -> 330 ohm -> LED -> GND (pin 6), with `enable_uart=1` (lit while the Pi runs). Blue / white /
  cyan LEDs want 100 ohm.
- RGB: 5V (pin 2), GND (pin 6), DIN <- 330 ohm <- GPIO10 / SPI MOSI (pin 19), `dtparam=spi=on`; software sets green
  while running, orange at shutdown; the pixel keeps its colour while it has 5 V (so standby stays orange).
- `src/make_wiring.py` draws both diagrams; keep it in step with the README wiring section.

## Printing facts

- Profiles target a Voron Trident 300 (0.4 nozzle, Klipper) on Orca's "MyKlipper 0.4 nozzle" printer and inherit
  "0.20mm Standard @MyKlipper"; they carry no filament settings (temperature, flow and shrink come from the user's
  ASA profile). Quality: 0.16 mm layers (first 0.2), 5 walls, Arachne, outer wall / top at 60 mm/s, 3000 mm/s2, seam
  at the back, hole compensation 0.1, elephant-foot 0.15, mouse-ear brim, gyroid 25 %. Base: 0.20 mm, 4 walls, gyroid
  20 %. Prototype: 0.24 mm, 3 walls, 12 % grid. A small prime tower (20 mm) is set for multi-material printers.
- ASA wants a closed, warm chamber; the lens is clear PETG at 100 % infill, slow.

## Conventions

- Commits: plain, one change each, scripts and regenerated files together. No generated file edited by hand.
- Plain facts in docs: no private notes, names or workflow chatter. Keep the README in step with the scripts (sizes,
  filament-change numbers, file names), since users print from it.
- Generated paths are repo-relative (`HERE`-based); no absolute machine paths in any file.
