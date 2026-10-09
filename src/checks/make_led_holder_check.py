"""Check of the shell's LED corner: the same shell twice - left with the 5 mm LED tube, right with the RGB
pixel block - the holder a part of its own that reaches into the wall. Prints how far each holder
overlaps the shell (the volume the slicer merges).
Run from the repo root:  python src/checks/make_led_holder_check.py [page.html]
Writes build/checks/led-holder.html unless a path is given."""
import base64, json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))          # the generators (make_case.py ...)
sys.path.insert(0, SRC)
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "build", "checks"))   # git-ignored
PAGE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(OUT, "led-holder.html")
os.makedirs(os.path.dirname(os.path.abspath(PAGE)), exist_ok=True)
os.chdir(SRC)
import make_case as mc  # noqa: E402
from build123d import Pos, export_stl  # noqa: E402

win = mc.box(mc.LED_X - 16, mc.D - 22, -1, 32, 23, mc.H - mc.ROOF - 0.4)       # the corner, roof cut away
body = mc.shell(None) & win
OFF = 40.0
lens = Pos(mc.LED_X, mc.D - mc.WALL - mc.LENS_FL - 0.2, mc.BTN_Z) * mc.lens()
parts = {"shell (same both)": body + Pos(OFF, 0, 0) * body, "LED tube (5 mm)": mc.led_holder("led5"),
         "RGB block (WS2812B)": Pos(OFF, 0, 0) * mc.led_holder("rgb"), "lens": lens + Pos(OFF, 0, 0) * lens}
for n in ("led5", "rgb"):
    print("%s holder x shell: %.1f mm3 (merged on printing)" % (n, (mc.led_holder(n) & mc.shell(None)).volume))
COL = {"shell (same both)": 0xb8c0c8, "LED tube (5 mm)": 0xe8aa3c, "RGB block (WS2812B)": 0xff46aa, "lens": 0x36d9e0}
stl, tmp = {}, tempfile.mkdtemp()
for n, p in parts.items():
    f = os.path.join(tmp, "p%d.stl" % len(stl))
    export_stl(p, f, tolerance=0.01, angular_tolerance=0.1)
    stl[n] = base64.b64encode(open(f, "rb").read()).decode()
tpl = open(os.path.join(HERE, "bottom-check-template.html"), encoding="utf-8").read()
tpl = tpl.replace("cam.position.set(c.x - s.x * 0.9, c.y - s.y * 1.6, c.z + s.x * 0.9);",
                  "cam.position.set(c.x - s.x * 0.2, c.y - s.x * 0.9, c.z + s.x * 0.5);")
open(PAGE, "w", encoding="utf-8", newline="\n").write(
    tpl.replace("__STL__", json.dumps(stl)).replace("__COL__", json.dumps(COL)).replace("__TITLE__", "LED holder"))
print("page:", PAGE)
