"""Check of the button tree: both caps as ONE part (caps + flexible strips + two ears that go on pins in
the shell, the pins' ends melted flat). Prints the fit checks (the tree against the shell).
Run from the repo root:  python src/checks/make_cap_tree_check.py [page.html]
Writes build/checks/cap-tree.html unless a path is given."""
import base64, json, math, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))          # the generators (make_case.py ...)
sys.path.insert(0, SRC)
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "build", "checks"))   # git-ignored
PAGE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(OUT, "cap-tree.html")
os.makedirs(os.path.dirname(os.path.abspath(PAGE)), exist_ok=True)
os.chdir(SRC)
import make_case as mc  # noqa: E402
from build123d import Plane, Polygon, Pos, export_stl, extrude  # noqa: E402

D, WALL, BTN_Z, BX = mc.D, mc.WALL, mc.BTN_Z, mc.BTN_X
YW = D - WALL                       # the wall's inner face
YB = mc.CAP_REST                    # the flanges' back face = the tree's back face (it prints on it)
T = 0.8                             # strip thickness: the strips bend out of their plane when a cap is pressed
SW = 3.0                            # strip width
EARS = [(8.0, 7.0), (57.5, 7.0)]    # the pins (x, z): low and outboard, so each strip runs ~12 mm to its cap
EAR_R, PIN_R, HOLE_R, BOSS_R = 3.0, 1.0, 1.15, 2.2


def strip(p0, p1, w=SW, t=T):
    """a flat strip in the tree's plane from p0 to p1 (x, z), t thick from the back face"""
    (x0, z0), (x1, z1) = p0, p1
    a = math.atan2(z1 - z0, x1 - x0)
    nx, nz = -math.sin(a) * w / 2, math.cos(a) * w / 2
    pts = [(x0 + nx, z0 + nz), (x1 + nx, z1 + nz), (x1 - nx, z1 - nz), (x0 - nx, z0 - nz)]
    pl = Plane(origin=(0, YB, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    return extrude(pl * Polygon(*[(x, -z) for x, z in pts], align=None), amount=t, dir=(0, 1, 0))


tree = None
for x in BX:
    c = Pos(x, YB, BTN_Z) * mc.button()
    tree = c if tree is None else tree + c
r_fl = 5.6
(lx, lz), (rx, rz) = EARS
tree += strip((lx, lz), (BX[0] - r_fl * 0.7, BTN_Z - r_fl * 0.7))           # left ear -> left cap
tree += strip((rx, rz), (BX[1] + r_fl * 0.7, BTN_Z - r_fl * 0.7))           # right ear -> right cap
tree += strip((BX[0] + r_fl - 0.5, BTN_Z), (BX[1] - r_fl + 0.5, BTN_Z), w=2.0, t=0.6)   # the thin link between the caps
for x, z in EARS:
    tree += mc.cyl_y(x, YB, z, EAR_R, T)
    tree -= mc.cyl_y(x, YB - 1, z, HOLE_R, T + 2)
# on the shell: a boss from the wall to the tree's front face, then a pin through the ear, 1.4 mm left to melt
pins = None
for x, z in EARS:
    p = mc.cyl_y(x, YB + T, z, BOSS_R, YW - YB - T + 0.01) + mc.cyl_y(x, YB - 1.4, z, PIN_R, YW - YB + 1.4)
    pins = p if pins is None else pins + p
heads = None
for x, z in EARS:
    h = mc.cyl_y(x, YB - 0.8, z, 2.0, 0.8)                                  # the pin end after the iron
    heads = h if heads is None else heads + h

shell = mc.shell() & mc.box(2, 90, -1, 62, 20, mc.H - mc.ROOF - 0.5)
base = mc.base() & mc.box(2, 88, -1, 62, 20, mc.H + 2)
sw = mc.switch_ghost(BX[0]) + mc.switch_ghost(BX[1])
print("tree x shell %.2f, x base %.2f, x switches %.2f, pins+heads x base %.2f, x switches %.2f mm3" % (
    (tree & shell).volume, (tree & base).volume, (tree & sw).volume, ((pins + heads) & base).volume, ((pins + heads) & sw).volume))
L = math.hypot(BX[0] - r_fl * 0.7 - lx, BTN_Z - r_fl * 0.7 - lz), math.hypot(rx - BX[1] - r_fl * 0.7, BTN_Z - r_fl * 0.7 - rz)
E, d = 2000.0, 1.0
for n, l in zip(("left", "right"), L):
    I = SW * T ** 3 / 12
    print("%s strip %.1f mm: %.2f N extra at 1 mm, strain %.2f %%" % (n, l, 3 * E * I * d / l ** 3, 150 * T * d / l ** 2))
print("the tree prints flat on its back face, shafts up: %.1f x %.1f mm" % (rx - lx + 2 * EAR_R, BTN_Z + r_fl - lz + EAR_R))

parts = {"shell": shell, "base": base, "switches": sw, "button tree": tree, "pins (melted)": pins + heads}
COL = {"shell": 0xb8c0c8, "base": 0x6aaacd, "switches": 0x9aa0a8, "button tree": 0xe8aa3c, "pins (melted)": 0xff46aa}
stl, tmp = {}, tempfile.mkdtemp()
for n, p in parts.items():
    f = os.path.join(tmp, "p%d.stl" % len(stl))
    export_stl(p, f, tolerance=0.01, angular_tolerance=0.1)
    stl[n] = base64.b64encode(open(f, "rb").read()).decode()
tpl = open(os.path.join(HERE, "bottom-check-template.html"), encoding="utf-8").read()
tpl = tpl.replace("cam.position.set(c.x - s.x * 0.9, c.y - s.y * 1.6, c.z + s.x * 0.9);",
                  "cam.position.set(c.x - s.x * 0.1, c.y - s.x * 0.85, c.z + s.x * 0.35);")
open(PAGE, "w", encoding="utf-8", newline="\n").write(
    tpl.replace("__STL__", json.dumps(stl)).replace("__COL__", json.dumps(COL)).replace("__TITLE__", "button tree"))
print("page:", PAGE)
