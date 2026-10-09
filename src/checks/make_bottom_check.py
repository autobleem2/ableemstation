"""Check of the universal case's one-piece bottom: the base with its three panels (back, right,
front) standing in their rebates, in a WebGL page with a section slider; prints how much each
panel overlaps the base (the weld). Builds only these parts, so it takes seconds, not a full
make_universal run.
Run from the repo root:  python src/checks/make_bottom_check.py [model] [front]
  model pi23|pi4|pi5, front usb|usb-open|blank.  Writes build/checks/bottom-check-<model>-<front>.html"""
import base64, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))          # the generators (make_case.py ...)
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "build", "checks"))   # git-ignored
sys.path.insert(0, SRC)
os.chdir(SRC)
import make_universal as mu  # noqa: E402
from build123d import export_stl  # noqa: E402

model = sys.argv[1] if len(sys.argv) > 1 else "pi4"
front = sys.argv[2] if len(sys.argv) > 2 else "usb"
os.makedirs(OUT, exist_ok=True)
right = mu.panel("right", mu.right_cuts(model, front == "usb"))
fpanel = mu.front_usb_panel() if front.startswith("usb") else mu.panel("front")
parts = {"base": mu.bottom_base(), "panel-back": mu.panel("back", mu.back_cuts(model)), "panel-right": right, "panel-front": fpanel}
if front.startswith("usb"):
    parts["usb-boards"] = mu.usb_sockets()          # the sockets on their boards (ghost)
stl, tmp = {}, tempfile.mkdtemp()
for n, p in parts.items():
    f = os.path.join(tmp, n + ".stl")
    export_stl(p, f, tolerance=0.02, angular_tolerance=0.2)
    stl[n] = base64.b64encode(open(f, "rb").read()).decode()
    if n.startswith("panel"):
        print("%s overlaps the base by %.1f mm3" % (n, (p & parts["base"]).volume))
import json  # noqa: E402
page = os.path.join(OUT, "bottom-check-%s-%s.html" % (model, front))
open(page, "w", encoding="utf-8", newline="\n").write("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Bottom check</title>
<style>body{margin:0;background:#16191d;color:#dde;font:14px system-ui,sans-serif;overflow:hidden}
#ui{position:fixed;left:12px;top:12px;background:#22262cdd;padding:10px 12px;border-radius:8px;max-width:calc(100vw - 48px)}
button{font:inherit;margin:2px;padding:4px 10px;border-radius:5px;border:1px solid #556;background:#2b3038;color:#dde;cursor:pointer}
button.on{border-color:#36d9e0;color:#36d9e0}input{width:260px;vertical-align:middle}</style>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
</head><body><div id="ui"><b>Bottom check - __TITLE__</b><br>
<span id="parts"></span><br>
Section <select id="ax"><option value="off">off</option><option value="x">across back/front (X)</option><option value="y">across right (Y)</option></select>
<input id="cut" type="range" min="0" max="1000" value="500"> <span id="cv"></span></div>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
const STL = __STL__, COL = {"base": 0x6aaacd, "panel-back": 0xe8aa3c, "panel-right": 0xe8783c, "panel-front": 0xdcc850, "usb-boards": 0x9aa0a8};
const r = new THREE.WebGLRenderer({antialias: true}); r.setSize(innerWidth, innerHeight); r.localClippingEnabled = true;
document.body.appendChild(r.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x16191d);
const cam = new THREE.PerspectiveCamera(35, innerWidth / innerHeight, 1, 2000); cam.up.set(0, 0, 1);
scene.add(new THREE.HemisphereLight(0xffffff, 0x404050, 1.1)); const dl = new THREE.DirectionalLight(0xffffff, 1.4); dl.position.set(80, -120, 160); scene.add(dl);
const plane = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0), loader = new STLLoader(), meshes = {}, box = new THREE.Box3();
for (const [n, b] of Object.entries(STL)) {
  const g = loader.parse(Uint8Array.from(atob(b), c => c.charCodeAt(0)).buffer); g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({color: COL[n], roughness: 0.7, side: THREE.DoubleSide, clippingPlanes: [plane]}));
  scene.add(m); meshes[n] = m; box.expandByObject(m);
}
const c = box.getCenter(new THREE.Vector3()), s = box.getSize(new THREE.Vector3());
cam.position.set(c.x - s.x * 0.9, c.y - s.y * 1.6, c.z + s.x * 0.9);
const ctl = new OrbitControls(cam, r.domElement); ctl.target.copy(c); ctl.update();
document.getElementById("parts").innerHTML = Object.keys(meshes).map(n => `<button class="on" data-n="${n}">${n}</button>`).join("");
document.querySelectorAll("[data-n]").forEach(b => b.onclick = () => { const m = meshes[b.dataset.n]; m.visible = !m.visible; b.classList.toggle("on", m.visible); });
const ax = document.getElementById("ax"), cut = document.getElementById("cut");
function setCut() {
  const a = ax.value; if (a === "off") { plane.constant = 1e6; plane.normal.set(-1, 0, 0); document.getElementById("cv").textContent = ""; return; }
  const lo = box.min[a], hi = box.max[a], v = lo + (hi - lo) * cut.value / 1000;
  plane.normal.set(a === "x" ? -1 : 0, a === "y" ? -1 : 0, 0); plane.constant = v;
  document.getElementById("cv").textContent = a.toUpperCase() + " = " + v.toFixed(1) + " mm";
}
ax.onchange = cut.oninput = setCut; setCut();
addEventListener("resize", () => { cam.aspect = innerWidth / innerHeight; cam.updateProjectionMatrix(); r.setSize(innerWidth, innerHeight); });
(function loop() { ctl.update(); r.render(scene, cam); requestAnimationFrame(loop); })();
</script></body></html>""".replace("__STL__", json.dumps(stl)).replace("__TITLE__", "%s, front %s" % (model, front)))
print("page:", page)
