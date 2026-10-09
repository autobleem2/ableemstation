"""Quick test print for the panel fit: the universal shell's front wall around the front opening (roof down,
as the shell prints) + the blank front panel standing - checks the panel clearance (EASE) without
printing a whole shell.
Run from the repo root:  python src/checks/make_fit_coupon.py
Writes build/checks/fit-coupon/fit-coupon-{shell,panel}-front.3mf"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))          # the generators (make_case.py ...)
sys.path.insert(0, SRC)
from build123d import Rot, export_stl  # noqa: E402
from make_case import D, H, box, on_bed, shell, write_parts_3mf  # noqa: E402
from make_universal import OPENINGS, cut_opening, panel, standing  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "build", "checks", "fit-coupon"))   # git-ignored
os.makedirs(OUT, exist_ok=True)

s = shell(None, None)
s = cut_opening(s, "front")
_, a0, a1, _, _, _ = OPENINGS["front"]
coupon = s & box(a0 - 8, D - 10, -1, a1 - a0 + 16, 11, H + 2)
coupon = on_bed(Rot(180, 0, 0) * coupon)
p = standing("front-blank", panel("front"))
write_parts_3mf(os.path.join(OUT, "fit-coupon-shell-front.3mf"), "fit-coupon-shell-front", [("shell", coupon)])
write_parts_3mf(os.path.join(OUT, "fit-coupon-panel-front.3mf"), "fit-coupon-panel-front", [("panel", p)])
bb = coupon.bounding_box()
print("coupon %.1f x %.1f x %.1f mm, %.1f cm3; panel %.1f cm3" % (bb.size.X, bb.size.Y, bb.size.Z, coupon.volume / 1000,
                                                                 p.volume / 1000))
