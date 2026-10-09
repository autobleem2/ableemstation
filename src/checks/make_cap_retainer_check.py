"""Mockup: two ways to keep the button caps in the shell - A: a plate slid up into rails, B: a plate on
two pins whose heads are melted flat. Both sit between the caps' flanges and the switches, with
slots open at the bottom so the plungers pass while the shell slides down. (The product uses
the pins; this is the comparison that led to it.)
Run from the repo root:  python src/checks/make_cap_retainer_check.py
Writes build/checks/cap-retainer.html"""
import base64, json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))          # the generators (make_case.py ...)
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "build", "checks"))   # git-ignored
sys.path.insert(0, SRC)
os.chdir(SRC)
import make_case as mc  # noqa: E402
from build123d import Pos, export_stl  # noqa: E402

D, WALL, BTN_Z = mc.D, mc.WALL, mc.BTN_Z
YW = D - WALL                                    # the front wall's inner face
PY0, PY1 = 99.2, 100.0                           # the plate (0.8 thick): just in front of the bracket (99.1)
PZ0, PZ1 = mc.BASE_T + 0.2, mc.H - mc.ROOF - 0.9  # stands on the base when assembled, clear of the roof
SLOT_W, SLOT_TOP = 4.5, BTN_Z + 2.5              # plunger 3.5 + clearance; closed above the plunger

crop = mc.box(4, 90, -1, 60, 20, mc.H - mc.ROOF - 0.5)   # roof cut away so the inside shows
shell = mc.shell() & crop
base = mc.base() & mc.box(4, 88, -1, 60, 20, mc.H + 2)
caps = None
for x in mc.BTN_X:
    c = Pos(x, mc.CAP_REST, BTN_Z) * mc.button()
    caps = c if caps is None else caps + c
sw = mc.switch_ghost(mc.BTN_X[0]) + mc.switch_ghost(mc.BTN_X[1])


def plate(x0, x1):
    p = mc.box(x0, PY0, PZ0, x1 - x0, PY1 - PY0, PZ1 - PZ0)
    for x in mc.BTN_X:
        p -= mc.box(x - SLOT_W / 2, PY0 - 1, PZ0 - 1, SLOT_W, 3, SLOT_TOP - PZ0 + 1)      # slot, open at the bottom
    return p


# A: rails - a rib each side on the wall, with a groove the plate's edge slides up in (0.1 mm play each side)
plate_a = plate(14.0, 54.0)
rails = None
for rx0, gx0, gx1 in ((11.5, 12.5, 16.0), (52.5, 52.0, 55.5)):
    r = mc.box(rx0, PY0 - 0.6, PZ0 + 0.2, 4.0, YW - (PY0 - 0.6) + 0.01, PZ1 - PZ0 + 1.0)
    r -= mc.box(gx0, PY0 - 0.1, PZ0 - 1, gx1 - gx0, PY1 - PY0 + 0.2, PZ1 - PZ0 + 1.5)
    rails = r if rails is None else rails + r
# B: pins - two pins out of the wall through the plate, their ends melted into heads
plate_b = plate(9.0, 59.0)
pins, heads = None, None
for x in (11.0, 57.0):
    plate_b -= mc.cyl_y(x, PY0 - 1, BTN_Z, 1.15, 3)
    p = mc.cyl_y(x, PY0 - 1.6, BTN_Z, 1.0, YW - PY0 + 1.6 + 0.01)
    h = mc.cyl_y(x, PY0 - 1.0, BTN_Z, 1.9, 1.0)                                            # the melted head
    pins = p if pins is None else pins + p
    heads = h if heads is None else heads + h

for name, extra in (("A rails", rails), ("B pins", pins + heads)):
    pl = plate_a if name.startswith("A") else plate_b
    print("%s: plate x base %.2f, x switches %.2f, x caps %.2f, fixtures x base %.2f mm3" % (
        name, (pl & base).volume, (pl & sw).volume, (pl & caps).volume, (extra & base).volume))
print("cap travel before the flange meets the plate: %.2f mm (the switch fires after ~0.25 past touching at %.2f)"
      % (mc.CAP_REST - PY1, mc.CAP_REST - (mc.switch_floor() + 3.5 + 1.5)))

OFF = 70.0                                         # B shown beside A
parts = {"shell": shell + Pos(OFF, 0, 0) * shell, "base": base + Pos(OFF, 0, 0) * base,
         "switches": sw + Pos(OFF, 0, 0) * sw, "caps": caps + Pos(OFF, 0, 0) * caps,
         "A plate": plate_a, "A rails": rails, "B plate": Pos(OFF, 0, 0) * plate_b, "B pins": Pos(OFF, 0, 0) * (pins + heads)}
COL = {"shell": 0xb8c0c8, "base": 0x6aaacd, "switches": 0x9aa0a8, "caps": 0xe8aa3c,
       "A plate": 0xe8783c, "A rails": 0x36d9e0, "B plate": 0xe8783c, "B pins": 0xff46aa}
stl, tmp = {}, tempfile.mkdtemp()
for n, p in parts.items():
    f = os.path.join(tmp, n.replace(" ", "_") + ".stl")
    export_stl(p, f, tolerance=0.01, angular_tolerance=0.1)
    stl[n] = base64.b64encode(open(f, "rb").read()).decode()
tpl = open(os.path.join(HERE, "bottom-check-template.html"), encoding="utf-8").read()
page = os.path.join(OUT, "cap-retainer.html")
open(page, "w", encoding="utf-8", newline="\n").write(
    tpl.replace("__STL__", json.dumps(stl)).replace("__COL__", json.dumps(COL))
    .replace("__TITLE__", "button caps - left A: plate in rails, right B: plate on pins melted with an iron"))
print("page:", page)
