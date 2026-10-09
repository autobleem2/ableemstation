"""Check of the base's switch bracket with two 6x6x5 tact switches (through-hole, legs 6.5 x 4.5 mm) and the
button caps; prints where a switch hits the bracket.
Run from the repo root:  python src/checks/make_switch_check.py
Writes build/checks/switch-check.html"""
import base64, json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))          # the generators (make_case.py ...)
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "build", "checks"))   # git-ignored
sys.path.insert(0, SRC)
os.chdir(SRC)
import make_case as mc  # noqa: E402
from build123d import Pos, export_stl  # noqa: E402

base = mc.base()
yb = mc.switch_floor() - 3.0
# a window of the base round the bracket
win = mc.box(mc.BTN_X[0] - 14, yb - 8, -1, mc.BTN_X[1] - mc.BTN_X[0] + 28, 30, mc.BTN_Z + 10)
bracket = base & win


def switch(x):
    """6x6 tact switch lying on its back in the bracket: body 6 x 6 x 3.5, plunger 3.5 dia x 1.5 to the front,
    four legs 0.7 x 0.3 at 6.5 x 4.5 mm, 3.5 mm long, out of the back"""
    y0 = yb + 3.0                                     # the body's back face (the pocket's floor)
    z = mc.BTN_Z
    s = mc.box(x - 3, y0, z - 3, 6, 3.5, 6)
    s += mc.cyl_y(x, y0 + 3.5, z, 1.75, 1.5)
    for sx in (-1, 1):
        for sz in (-1, 1):
            s += mc.box(x + sx * 3.25 - 0.35, y0 - 3.5, z + sz * 2.25 - 0.15, 0.7, 3.5, 0.3)
    return s


sw = mc.switch_ghost(mc.BTN_X[0]) + mc.switch_ghost(mc.BTN_X[1])
caps = None
for x in mc.BTN_X:
    c = Pos(x, mc.CAP_REST, mc.BTN_Z) * mc.button()
    caps = c if caps is None else caps + c
hit = (sw & bracket).volume
print("switch x bracket overlap: %.2f mm3 (0 = the switch fits)" % hit)
parts = {"bracket": bracket, "switches": sw, "caps": caps}
stl, tmp = {}, tempfile.mkdtemp()
for n, p in parts.items():
    f = os.path.join(tmp, n + ".stl")
    export_stl(p, f, tolerance=0.01, angular_tolerance=0.1)
    stl[n] = base64.b64encode(open(f, "rb").read()).decode()
tpl = open(os.path.join(HERE, "bottom-check-template.html"), encoding="utf-8").read()
os.makedirs(OUT, exist_ok=True)
page = os.path.join(OUT, "switch-check.html")
open(page, "w", encoding="utf-8", newline="\n").write(
    tpl.replace("__STL__", json.dumps(stl)).replace("__TITLE__", "switch bracket, 6x6x5 tact switches")
    .replace("__COL__", json.dumps({"bracket": 0x6aaacd, "switches": 0x9aa0a8, "caps": 0xe8aa3c})))
print("page:", page)
