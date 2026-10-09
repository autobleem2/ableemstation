"""Quick test print for the switch bracket: a slice of the base around the two tact-switch pockets and their leg holes
(the plate flat on the bed, as the base prints). Prints in a few minutes, so a switch can be tried in the pocket and its
legs through the holes before the whole base is printed.
Run from the repo root:  python src/checks/make_switch_coupon.py
Writes build/checks/switch-coupon/switch-coupon.3mf"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))          # the generators (make_case.py ...)
sys.path.insert(0, SRC)
os.chdir(SRC)
from make_case import BTN_X, BTN_Z, base, box, switch_floor, write_parts_3mf, SW_BACK  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "build", "checks", "switch-coupon"))   # git-ignored
os.makedirs(OUT, exist_ok=True)

yb = switch_floor() - SW_BACK                    # the bracket's back face
window = box(BTN_X[0] - 12, yb - 1, -1, BTN_X[1] - BTN_X[0] + 24, 9, BTN_Z + 8)
coupon = base() & window
write_parts_3mf(os.path.join(OUT, "switch-coupon.3mf"), "switch-coupon", [("coupon", coupon)])
bb = coupon.bounding_box()
print("coupon %.1f x %.1f x %.1f mm, %.1f cm3" % (bb.size.X, bb.size.Y, bb.size.Z, coupon.volume / 1000))
