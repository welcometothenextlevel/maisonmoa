/* Maison Môa — natures mortes 3D.
   Every element with [data-scene="name"] receives its own WebGL still life:
   objects modelled in code, lit by a low sun through swaying olive leaves,
   on an invisible ivory cyclorama that only keeps the shadows. */
import * as THREE from 'three';
import { RoomEnvironment } from './vendor/addons/RoomEnvironment.js';
import { RoundedBoxGeometry } from './vendor/addons/RoundedBoxGeometry.js';
import { SVGLoader } from './vendor/addons/SVGLoader.js';
import { MONO, MONO_BOX } from './mono.js';

const mq = (q) => window.matchMedia(q).matches;
const COARSE = mq('(pointer: coarse)');
const SMALL = mq('(max-width: 820px)');
const REDUCE = mq('(prefers-reduced-motion: reduce)');
const PARAMS = new URLSearchParams(location.search);
const STILL = PARAMS.has('still');
const TIER = (() => {
  const cores = navigator.hardwareConcurrency || 8, mem = navigator.deviceMemory || 8;
  if (PARAMS.has('tier')) return +PARAMS.get('tier');
  if (cores <= 2 || mem <= 3) return 0;
  return (COARSE || SMALL) ? 1 : 2;
})();
const TAU = Math.PI * 2;
const V2 = (x, y) => new THREE.Vector2(x, y);
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
function rng(seed) { let a = seed | 0; return () => { a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

/* ------------------------------------------------------------------ textures */
const TEX = {};
function canvasTex(w, h, draw, { data = false, repeat = null } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = data ? THREE.NoColorSpace : THREE.SRGBColorSpace;
  t.anisotropy = 8;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
  return t;
}
function fibres(g, w, h, n, rgb, a, len, r) {
  for (let i = 0; i < n; i++) {
    const x = r() * w, y = r() * h, ang = r() * TAU, l = len * (0.3 + r());
    g.strokeStyle = `rgba(${rgb},${a * (0.4 + r())})`; g.lineWidth = 0.6 + r() * 0.8;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(ang) * l, y + Math.sin(ang) * l); g.stroke();
  }
}
const travertineTex = () => TEX.trav || (TEX.trav = canvasTex(1024, 1024, (g, w, h) => {
  const r = rng(11);
  g.fillStyle = '#ebe1d3'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 220; i++) {
    const y = r() * h, a = 0.025 + r() * 0.07;
    g.strokeStyle = `rgba(${150 + r() * 40 | 0},${122 + r() * 30 | 0},${92 + r() * 26 | 0},${a})`;
    g.lineWidth = 0.6 + r() * 4; g.beginPath(); g.moveTo(-10, y);
    for (let x = 0; x <= w + 40; x += 40) g.lineTo(x, y + Math.sin(x * 0.006 + i) * 6 + (r() - 0.5) * 3);
    g.stroke();
  }
  for (let i = 0; i < 520; i++) {
    const x = r() * w, y = r() * h, rx = 0.6 + r() * 4.5;
    g.fillStyle = `rgba(118,92,64,${0.1 + r() * 0.28})`;
    g.beginPath(); g.ellipse(x, y, rx, rx * (0.25 + r() * 0.35), 0, 0, TAU); g.fill();
  }
}, { repeat: [1, 1] }));
const linenTex = () => TEX.linen || (TEX.linen = canvasTex(512, 512, (g, w, h) => {
  const r = rng(5);
  g.fillStyle = '#efe7dc'; g.fillRect(0, 0, w, h);
  for (let y = 0; y < h; y += 3) { g.fillStyle = `rgba(140,118,92,${0.05 + r() * 0.06})`; g.fillRect(0, y, w, 1); }
  for (let x = 0; x < w; x += 3) { g.fillStyle = `rgba(140,118,92,${0.04 + r() * 0.05})`; g.fillRect(x, 0, 1, h); }
  fibres(g, w, h, 500, '120,98,72', 0.08, 8, r);
}, { repeat: [3, 3] }));
const woodTex = () => TEX.wood || (TEX.wood = canvasTex(512, 128, (g, w, h) => {
  const r = rng(3);
  g.fillStyle = '#dcc39f'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 60; i++) {
    const y = r() * h; g.strokeStyle = `rgba(150,112,70,${0.08 + r() * 0.15})`; g.lineWidth = 0.5 + r() * 2;
    g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= w; x += 16) g.lineTo(x, y + Math.sin(x * 0.02 + i) * 2); g.stroke();
  }
}));
const kraftTex = () => TEX.kraft || (TEX.kraft = canvasTex(512, 512, (g, w, h) => {
  const r = rng(21);
  g.fillStyle = '#b18c66'; g.fillRect(0, 0, w, h);
  fibres(g, w, h, 3200, '86,58,32', 0.12, 10, r);
  fibres(g, w, h, 1400, '238,214,182', 0.09, 9, r);
}, { repeat: [1.5, 1.5] }));
const speckleTex = () => TEX.speck || (TEX.speck = canvasTex(512, 512, (g, w, h) => {
  const r = rng(8);
  g.fillStyle = '#2f2d2a'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 5000; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '90,86,80' : '20,19,18'},${0.3 + r() * 0.5})`; g.fillRect(r() * w, r() * h, 1 + r() * 2, 1 + r() * 2); }
}));
const dotTex = () => TEX.dot || (TEX.dot = canvasTex(64, 64, (g, w) => {
  const gr = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.4, 'rgba(255,255,255,.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, w, w);
}));
const glowTex = () => TEX.glow || (TEX.glow = canvasTex(256, 256, (g, w) => {
  const gr = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.35, 'rgba(255,255,255,.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, w, w);
}));
const monoPath = () => new Path2D(MONO);
function drawMono(g, cx, top, height, color) {
  const s = height / MONO_BOX[3];
  g.save(); g.translate(cx - (MONO_BOX[2] * s) / 2, top); g.scale(s, s); g.translate(-MONO_BOX[0], -MONO_BOX[1]);
  g.fillStyle = color; g.fill(monoPath(), 'evenodd'); g.restore();
}
function spaced(g, text, x, y, sp) {
  if ('letterSpacing' in g) { g.letterSpacing = sp + 'px'; g.fillText(text, x + sp / 2, y); g.letterSpacing = '0px'; return; }
  g.fillText(text, x, y);
}
function paperTex(lines, { w = 1024, h = 512, mono = true, frame = true, bg = '#f5eee3', ink = '#3F4A3A' } = {}) {
  return canvasTex(w, h, (g) => {
    const r = rng(lines.join('').length);
    g.fillStyle = bg; g.fillRect(0, 0, w, h);
    fibres(g, w, h, 900, '140,116,90', 0.05, 7, r);
    if (frame) { g.strokeStyle = 'rgba(63,74,58,.45)'; g.lineWidth = 2; g.strokeRect(26, 26, w - 52, h - 52); }
    let y = h * 0.16;
    if (mono) { drawMono(g, w / 2, y, h * 0.36, ink); y += h * 0.36 + h * 0.13; }
    g.textAlign = 'center'; g.fillStyle = ink;
    lines.forEach(([font, text, sp, gap]) => { g.font = font; spaced(g, text, w / 2, y, sp || 0); y += gap; });
  });
}

/* ------------------------------------------------------------------ materials */
const C = (hex) => new THREE.Color(hex);
const MAT = {
  hidden() { const m = new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false, side: THREE.DoubleSide }); m.shadowSide = THREE.DoubleSide; return m; },
  glass({ att = 0xffffff, dist = 2, thick = 0.25, rough = 0.04, ior = 1.5, fallback = 0xe9e4da, opacity = 0.5, tint = 0xffffff } = {}) {
    if (TIER > 0) return new THREE.MeshPhysicalMaterial({ color: tint, transmission: 1, thickness: thick, roughness: rough, ior, attenuationColor: C(att), attenuationDistance: dist, clearcoat: 0.3, clearcoatRoughness: 0.05, specularIntensity: 1, envMapIntensity: 1.15 });
    return new THREE.MeshPhysicalMaterial({ color: fallback, roughness: 0.06, clearcoat: 1, transparent: true, opacity, envMapIntensity: 1.5, depthWrite: false });
  },
  amber() { return this.glass({ att: 0x7d4612, dist: 0.42, thick: 0.4, rough: 0.035, fallback: 0x7a4414, opacity: 0.9, tint: 0xffecd2 }); },
  jade() {
    if (TIER > 0) return new THREE.MeshPhysicalMaterial({ color: 0x6f9468, transmission: 0.22, thickness: 0.9, roughness: 0.2, ior: 1.61, attenuationColor: C(0x3a6234), attenuationDistance: 0.14, clearcoat: 0.7, clearcoatRoughness: 0.12, envMapIntensity: 0.8, sheen: 0.3, sheenColor: C(0xd9ead2) });
    return new THREE.MeshPhysicalMaterial({ color: 0x7f9a76, roughness: 0.22, clearcoat: 0.8, sheen: 0.4, sheenColor: C(0xd6e6cf) });
  },
  oil() { return new THREE.MeshPhysicalMaterial({ color: 0xc4913f, roughness: 0.04, metalness: 0.35, clearcoat: 1, clearcoatRoughness: 0.02, emissive: 0x3a2208, emissiveIntensity: 0.12, envMapIntensity: 1.8 }); },
  drop() {
    if (TIER > 0) return new THREE.MeshPhysicalMaterial({ color: 0xf2c06a, transmission: 0.75, thickness: 0.08, roughness: 0.02, ior: 1.47, attenuationColor: C(0xb8641c), attenuationDistance: 0.12, clearcoat: 1 });
    return new THREE.MeshPhysicalMaterial({ color: 0xd49433, roughness: 0.03, clearcoat: 1 });
  },
  wax() {
    if (TIER > 0) return new THREE.MeshPhysicalMaterial({ color: 0xf0b98e, transmission: 0.42, thickness: 0.6, roughness: 0.1, ior: 1.46, attenuationColor: C(0xc2683a), attenuationDistance: 0.35, clearcoat: 1, clearcoatRoughness: 0.04, sheen: 0.3, sheenColor: C(0xffd9bf) });
    return new THREE.MeshPhysicalMaterial({ color: 0xdf9e76, roughness: 0.12, clearcoat: 1 });
  },
  ceramic(color = 0xebe2d6, rough = 0.55) { return new THREE.MeshPhysicalMaterial({ color, roughness: rough, clearcoat: 0.25, clearcoatRoughness: 0.4, sheen: 0.2, sheenColor: C(0xffffff) }); },
  stone(color = 0xffffff) { return new THREE.MeshStandardMaterial({ color, map: travertineTex(), bumpMap: travertineTex(), bumpScale: 0.6, roughness: 0.82 }); },
  metal(color = 0xcdb495, rough = 0.28) { return new THREE.MeshStandardMaterial({ color, metalness: 1, roughness: rough, envMapIntensity: 1.2 }); },
  rubber(color = 0xf1ebe1) { return new THREE.MeshPhysicalMaterial({ color, roughness: 0.48, sheen: 0.5, sheenColor: C(0xffffff), clearcoat: 0.15 }); },
  plastic(color = 0x2b2926, rough = 0.32) { return new THREE.MeshPhysicalMaterial({ color, roughness: rough, clearcoat: 0.5, clearcoatRoughness: 0.2 }); },
  paper(map) { return new THREE.MeshStandardMaterial({ map, roughness: 0.92 }); },
  linen(color = 0xffffff) { return new THREE.MeshStandardMaterial({ color, map: linenTex(), roughness: 0.95 }); },
  wood() { return new THREE.MeshStandardMaterial({ map: woodTex(), roughness: 0.75 }); },
  kraft() { return new THREE.MeshStandardMaterial({ map: kraftTex(), roughness: 0.9, bumpMap: kraftTex(), bumpScale: 0.4 }); },
  basalt() { return new THREE.MeshPhysicalMaterial({ color: 0xffffff, map: speckleTex(), roughness: 0.58, clearcoat: 0.55, clearcoatRoughness: 0.3, envMapIntensity: 0.9 }); },
  leaf(color = 0x6d7956) { return new THREE.MeshStandardMaterial({ color, roughness: 0.7, side: THREE.DoubleSide }); },
  petal() { return new THREE.MeshPhysicalMaterial({ color: 0xfbf7f0, roughness: 0.6, sheen: 1, sheenColor: C(0xffffff), side: THREE.DoubleSide, transmission: TIER > 0 ? 0.15 : 0, thickness: 0.05 }); },
  polish(color) { return new THREE.MeshPhysicalMaterial({ color, roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.03 }); },
  gel() {
    if (TIER > 0) return new THREE.MeshPhysicalMaterial({ color: 0xfff6ea, transmission: 0.95, thickness: 0.1, roughness: 0.1, ior: 1.38, attenuationColor: C(0xd9a65c), attenuationDistance: 0.7, iridescence: 0.35, iridescenceIOR: 1.3, clearcoat: 1 });
    return new THREE.MeshPhysicalMaterial({ color: 0xe8c47e, roughness: 0.15, clearcoat: 1, transparent: true, opacity: 0.85 });
  },
  water() {
    if (TIER > 0) return new THREE.MeshPhysicalMaterial({ color: 0xffffff, transmission: 1, thickness: 0.25, roughness: 0.03, ior: 1.33, attenuationColor: C(0xa9c3b8), attenuationDistance: 0.9, clearcoat: 0.4, envMapIntensity: 1.3 });
    return new THREE.MeshPhysicalMaterial({ color: 0xc9d8d2, roughness: 0.04, clearcoat: 1, transparent: true, opacity: 0.55 });
  },
};

/* ------------------------------------------------------------------ geometry helpers */
const lathe = (pts, seg = 64) => new THREE.LatheGeometry(pts.map(([x, y]) => V2(x, y)), seg);
function shadowy(o, cast = true, receive = true) { o.traverse((m) => { if (m.isMesh) { m.castShadow = cast; m.receiveShadow = receive; } }); return o; }
function cycloGeo(W = 30, F = 10, R = 2.6, H = 10) {
  const prof = [];
  for (let i = 0; i <= 8; i++) prof.push([F - i * (F / 8), 0]);
  for (let i = 1; i <= 20; i++) { const t = (i / 20) * Math.PI / 2; prof.push([-R * Math.sin(t), R - R * Math.cos(t)]); }
  for (let i = 1; i <= 6; i++) prof.push([-R, R + (i * (H - R)) / 6]);
  const pos = [], idx = [];
  prof.forEach(([z, y]) => pos.push(-W / 2, y, z, W / 2, y, z));
  for (let i = 0; i < prof.length - 1; i++) { const a = i * 2, b = a + 1, c = a + 2, d = a + 3; idx.push(a, b, c, b, d, c); }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  return g;
}
function ribbed(geo, ridges = 30, depth = 0.025) {
  const p = geo.attributes.position, v = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i); const rr = Math.hypot(v.x, v.z); if (rr < 1e-4) continue;
    const a = Math.atan2(v.x, v.z), k = 1 + depth * Math.cos(a * ridges);
    p.setXYZ(i, v.x * k, v.y, v.z * k);
  }
  geo.computeVertexNormals(); return geo;
}
function lumpy(geo, amp, seed) {
  const r = rng(seed), f = [r() * 3 + 1.5, r() * 3 + 1.5, r() * 3 + 1.5], ph = [r() * TAU, r() * TAU, r() * TAU];
  const p = geo.attributes.position, v = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i);
    const n = Math.sin(v.x * f[0] + ph[0]) * Math.sin(v.y * f[1] + ph[1]) * Math.sin(v.z * f[2] + ph[2]) + 0.5 * Math.sin(v.x * 7.1 + v.z * 5.3 + ph[1]);
    v.multiplyScalar(1 + amp * n); p.setXYZ(i, v.x, v.y, v.z);
  }
  geo.computeVertexNormals(); return geo;
}
function pebble(rx, ry, rz, seed, mat) {
  const geo = lumpy(new THREE.IcosahedronGeometry(1, 5), 0.06, seed);
  const m = new THREE.Mesh(geo, mat); m.scale.set(rx, ry, rz); m.position.y = ry * 0.92;
  return shadowy(m);
}
function leafShape() {
  const s = new THREE.Shape(); s.moveTo(0, 0);
  s.bezierCurveTo(0.1, 0.16, 0.11, 0.64, 0, 1); s.bezierCurveTo(-0.11, 0.64, -0.1, 0.16, 0, 0);
  return s;
}
function sprig(n, len, seed, mat, curveAmt = 0.2) {
  const g = new THREE.Group(), r = rng(seed), pts = [];
  for (let i = 0; i <= 5; i++) { const t = i / 5; pts.push(V3(Math.sin(t * 2.2) * curveAmt + (r() - 0.5) * 0.05, t * len, (r() - 0.5) * 0.06)); }
  const curve = new THREE.CatmullRomCurve3(pts);
  g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 32, 0.011, 5), mat));
  const lg = new THREE.ShapeGeometry(leafShape(), 10);
  for (let i = 0; i < n; i++) {
    const t = 0.07 + 0.9 * (i / Math.max(1, n - 1)), p = curve.getPointAt(t);
    const leaf = new THREE.Mesh(lg, mat), L = 0.26 + r() * 0.13;
    leaf.scale.set(L * (0.85 + r() * 0.35), L, 1); leaf.position.copy(p);
    const side = i % 2 ? 1 : -1;
    leaf.rotation.set((r() - 0.5) * 0.9, (r() - 0.5) * 0.7, side * (0.5 + r() * 0.55));
    leaf.userData.base = leaf.rotation.clone(); leaf.userData.ph = r() * TAU;
    g.add(leaf);
  }
  return g;
}
/* variable-radius tube that can be re-shaped every frame */
class Ribbon {
  constructor(segs, radial, mat) {
    this.segs = segs; this.radial = radial;
    const g = this.geo = new THREE.BufferGeometry(), n = (segs + 1) * (radial + 1);
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
    const idx = [];
    for (let i = 0; i < segs; i++) for (let j = 0; j < radial; j++) {
      const a = i * (radial + 1) + j, b = a + radial + 1;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
    g.setIndex(idx);
    this.mesh = new THREE.Mesh(g, mat); this.mesh.frustumCulled = false;
    this._T = new THREE.Vector3(); this._N = V3(1, 0, 0); this._B = new THREE.Vector3(); this._v = new THREE.Vector3();
  }
  update(pts, radii) {
    const p = this.geo.attributes.position, R = this.radial, T = this._T, N = this._N.set(1, 0, 0), B = this._B, v = this._v;
    for (let i = 0; i <= this.segs; i++) {
      const a = pts[Math.max(0, i - 1)], b = pts[Math.min(this.segs, i + 1)];
      T.subVectors(b, a).normalize();
      N.sub(v.copy(T).multiplyScalar(N.dot(T))); if (N.lengthSq() < 1e-6) N.set(0, 0, 1).sub(v.copy(T).multiplyScalar(T.z)); N.normalize();
      B.crossVectors(T, N);
      for (let j = 0; j <= R; j++) {
        const ang = (j / R) * TAU, c = Math.cos(ang) * radii[i], s = Math.sin(ang) * radii[i];
        p.setXYZ(i * (R + 1) + j, pts[i].x + N.x * c + B.x * s, pts[i].y + N.y * c + B.y * s, pts[i].z + N.z * c + B.z * s);
      }
    }
    p.needsUpdate = true; this.geo.computeVertexNormals(); this.geo.computeBoundingSphere();
  }
}
/* liquid surface with radial ripples */
class Pool {
  constructor(radius, mat, rings = 26, segs = 80) {
    const g = this.geo = new THREE.RingGeometry(0.0005, radius, segs, rings);
    g.rotateX(-Math.PI / 2);
    this.mesh = new THREE.Mesh(g, mat); this.mesh.receiveShadow = true;
    const p = g.attributes.position; this.r = new Float32Array(p.count); this.a = new Float32Array(p.count);
    for (let i = 0; i < p.count; i++) { this.r[i] = Math.hypot(p.getX(i), p.getZ(i)); this.a[i] = Math.atan2(p.getZ(i), p.getX(i)); }
    this.radius = radius; this.ripples = []; this.base = null; this.amp = 0.011;
  }
  add(t, x = 0, z = 0, amp = 1) { this.ripples.push({ t, x, z, amp }); if (this.ripples.length > 4) this.ripples.shift(); }
  update(t) {
    const p = this.geo.attributes.position, R = this.radius;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), z = p.getZ(i);
      let h = this.base ? this.base(this.r[i], this.a[i], t) : 0;
      for (const rp of this.ripples) {
        const tau = t - rp.t; if (tau < 0 || tau > 4) continue;
        const d = Math.hypot(x - rp.x, z - rp.z), front = tau * 0.42 + 0.02;
        if (d > front) continue;
        h += rp.amp * this.amp * Math.exp(-tau * 1.5) * Math.exp(-d * 2.4) * Math.sin(d * 46 - tau * 13) * clamp((front - d) / 0.06, 0, 1);
      }
      h *= smooth(R, R * 0.86, this.r[i]);
      p.setY(i, h);
    }
    p.needsUpdate = true; this.geo.computeVertexNormals();
  }
}

/* ------------------------------------------------------------------ objects */
function bottle({ r = 0.34, h = 0.8, glass = MAT.amber(), label = null } = {}) {
  const g = new THREE.Group(), n = r * 0.36, c = 0.07, sh = 0.2, nh = 0.09, pts = [[0, 0]];
  for (let i = 0; i <= 6; i++) { const a = -Math.PI / 2 + (i / 6) * Math.PI / 2; pts.push([r - c + Math.cos(a) * c, c + Math.sin(a) * c]); }
  pts.push([r, h]);
  for (let i = 1; i <= 14; i++) { const a = (i / 14) * Math.PI / 2; pts.push([n + (r - n) * Math.cos(a), h + sh * Math.sin(a)]); }
  const top = h + sh + nh;
  pts.push([n, top], [n + 0.022, top + 0.006], [n + 0.022, top + 0.04], [n - 0.03, top + 0.046], [0, top + 0.046]);
  const body = new THREE.Mesh(lathe(pts, 80), glass); g.add(body);
  if (label) {
    const lab = new THREE.Mesh(new THREE.CylinderGeometry(r * 1.008, r * 1.008, h * 0.6, 80, 1, true, -1.2, 2.4), MAT.paper(label));
    lab.position.y = h * 0.47; g.add(lab);
  }
  g.userData.top = top + 0.046;
  return shadowy(g);
}
function pipette(scale = 1) {
  const g = new THREE.Group();
  g.add(new THREE.Mesh(lathe([[0, -0.8], [0.011, -0.8], [0.017, -0.76], [0.031, -0.6], [0.033, -0.1], [0.033, 0], [0, 0]], 40), MAT.glass({ att: 0xf3eadb, dist: 3, thick: 0.05 })));
  g.add(new THREE.Mesh(lathe([[0, -0.77], [0.008, -0.77], [0.021, -0.61], [0.022, -0.36], [0, -0.36]], 28), MAT.oil()));
  const collar = new THREE.Mesh(ribbed(new THREE.CylinderGeometry(0.078, 0.078, 0.15, 120, 1), 36, 0.03), MAT.plastic(0x2c2a27, 0.36));
  collar.position.y = 0.07; g.add(collar);
  const bulb = new THREE.Mesh(lathe([[0, 0], [0.062, 0], [0.066, 0.03], [0.074, 0.1], [0.072, 0.18], [0.058, 0.245], [0.032, 0.27], [0, 0.275]], 56), MAT.rubber());
  bulb.position.y = 0.145; g.add(bulb);
  g.scale.setScalar(scale);
  g.userData.tip = V3(0, -0.805, 0);
  return shadowy(g);
}
function dish(R = 0.6, mat = MAT.stone()) {
  const k = R / 0.6;
  const m = new THREE.Mesh(lathe([[0, 0], [0.34, 0], [0.5, 0.05], [0.6, 0.13], [0.62, 0.165], [0.6, 0.18], [0.565, 0.175], [0.47, 0.11], [0.3, 0.078], [0, 0.072]].map(([x, y]) => [x * k, y * k]), 80), mat);
  return shadowy(m);
}
function guaSha() {
  const s = new THREE.Shape();
  s.moveTo(-0.42, 0.0);
  s.bezierCurveTo(-0.47, 0.23, -0.28, 0.37, -0.12, 0.3);
  s.bezierCurveTo(-0.04, 0.27, 0.0, 0.21, 0.02, 0.16);
  s.bezierCurveTo(0.07, 0.25, 0.21, 0.35, 0.35, 0.26);
  s.bezierCurveTo(0.49, 0.17, 0.47, -0.03, 0.38, -0.11);
  s.bezierCurveTo(0.22, -0.27, -0.03, -0.31, -0.19, -0.24);
  s.bezierCurveTo(-0.35, -0.17, -0.4, -0.1, -0.42, 0.0);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.035, bevelEnabled: true, bevelThickness: 0.022, bevelSize: 0.024, bevelSegments: 6, curveSegments: 40 });
  geo.center();
  return shadowy(new THREE.Mesh(geo, MAT.jade()));
}
function jadeRoller() {
  const g = new THREE.Group(), jade = MAT.jade(), metal = MAT.metal(0xd2bc9c, 0.25);
  const handle = new THREE.Mesh(new THREE.CapsuleGeometry(0.042, 0.46, 10, 32), jade); handle.rotation.z = Math.PI / 2; g.add(handle);
  const roll = (R, L) => new THREE.Mesh(lathe([[0, -L / 2], [R * 0.85, -L / 2], [R, -L / 2 + R * 0.18], [R, L / 2 - R * 0.18], [R * 0.85, L / 2], [0, L / 2]], 56), jade);
  const big = roll(0.078, 0.24); big.rotation.x = Math.PI / 2; big.position.x = 0.47; g.add(big);
  const small = roll(0.048, 0.13); small.rotation.x = Math.PI / 2; small.position.x = -0.42; g.add(small);
  const wire = (x0, x1, w) => {
    [1, -1].forEach((sd) => {
      const c = new THREE.CatmullRomCurve3([V3(x0, 0, 0), V3((x0 + x1) / 2, 0, sd * w * 0.7), V3(x1, 0, sd * w), V3(x1 + 0.0001, 0, sd * w * 0.5)]);
      g.add(new THREE.Mesh(new THREE.TubeGeometry(c, 24, 0.009, 8), metal));
    });
    const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, w * 2 + 0.02, 10), metal); axle.rotation.x = Math.PI / 2; axle.position.x = x1; g.add(axle);
  };
  wire(0.27, 0.47, 0.135); wire(-0.27, -0.42, 0.078);
  g.userData.rollers = [big, small];
  return shadowy(g);
}
function creamJar() {
  const g = new THREE.Group();
  g.add(new THREE.Mesh(lathe([[0, 0], [0.27, 0], [0.3, 0.025], [0.3, 0.25], [0.288, 0.268], [0.262, 0.268], [0.262, 0.05], [0, 0.05]], 80), MAT.ceramic(0xe9dccb, 0.42)));
  const cream = new THREE.Mesh(new THREE.RingGeometry(0.0005, 0.262, 80, 18), new THREE.MeshPhysicalMaterial({ color: 0xfaf4ec, roughness: 0.34, sheen: 0.6, sheenColor: C(0xffffff), clearcoat: 0.35 }));
  cream.geometry.rotateX(-Math.PI / 2);
  const p = cream.geometry.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), z = p.getZ(i), rr = Math.min(1, Math.hypot(x, z) / 0.262), a = Math.atan2(z, x);
    p.setY(i, 0.04 * Math.pow(1 - rr, 1.6) + 0.007 * Math.sin(a * 3 + rr * 14) * (1 - rr));
  }
  cream.geometry.computeVertexNormals(); cream.position.y = 0.2; g.add(cream);
  return shadowy(g);
}
function waxPot() {
  const g = new THREE.Group();
  g.add(new THREE.Mesh(lathe([[0, 0], [0.34, 0], [0.37, 0.03], [0.38, 0.38], [0.365, 0.41], [0.34, 0.41], [0.335, 0.07], [0, 0.07]], 80), MAT.ceramic(0xe9d6c8, 0.38)));
  const band = new THREE.Mesh(new THREE.CylinderGeometry(0.383, 0.383, 0.05, 80, 1, true), MAT.metal(0xc9ab8a, 0.3)); band.position.y = 0.31; g.add(band);
  return shadowy(g);
}
function spatula() {
  const s = new THREE.Shape(), L = 0.9, W = 0.075, rr = W;
  s.moveTo(-W, 0); s.lineTo(-W, L - rr); s.absarc(0, L - rr, W, Math.PI, 0, true); s.lineTo(W, 0); s.absarc(0, 0, W, 0, Math.PI, true);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.01, bevelEnabled: true, bevelThickness: 0.006, bevelSize: 0.006, bevelSegments: 3, curveSegments: 24 });
  geo.translate(0, 0, -0.005);
  const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getY(i) * 1.1, uv.getX(i) * 4);
  return shadowy(new THREE.Mesh(geo, MAT.wood()));
}
function polishBottle(color, capColor = 0x2a2724) {
  const g = new THREE.Group();
  const inner = new THREE.Mesh(new RoundedBoxGeometry(0.25, 0.27, 0.25, 4, 0.05), MAT.polish(color)); inner.position.y = 0.17; g.add(inner);
  const shell = new THREE.Mesh(new RoundedBoxGeometry(0.33, 0.36, 0.33, 6, 0.075), MAT.glass({ att: 0xf6efe6, dist: 4, thick: 0.08, fallback: 0xf3eee6, opacity: 0.35 })); shell.position.y = 0.18; g.add(shell);
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.05, 32), MAT.glass({ att: 0xf6efe6, dist: 4, thick: 0.05 })); neck.position.y = 0.38; g.add(neck);
  const cap = new THREE.Mesh(lathe([[0, 0], [0.072, 0], [0.074, 0.02], [0.068, 0.46], [0.06, 0.48], [0, 0.48]], 48), MAT.plastic(capColor, 0.22)); cap.position.y = 0.395; g.add(cap);
  return shadowy(g);
}
function nailFile(color) {
  const m = new THREE.Mesh(new RoundedBoxGeometry(0.95, 0.018, 0.12, 3, 0.008), new THREE.MeshStandardMaterial({ color, roughness: 0.95, bumpMap: travertineTex(), bumpScale: 0.8 }));
  m.position.y = 0.009; return shadowy(m);
}
function jasmine(seed) {
  const g = new THREE.Group(), r = rng(seed), mat = MAT.petal();
  const s = new THREE.Shape(); s.moveTo(0, 0); s.bezierCurveTo(0.07, 0.04, 0.075, 0.15, 0, 0.19); s.bezierCurveTo(-0.075, 0.15, -0.07, 0.04, 0, 0);
  const pg = new THREE.ShapeGeometry(s, 10); pg.rotateX(-Math.PI / 2);
  const pp = pg.attributes.position; for (let i = 0; i < pp.count; i++) { const d = -pp.getZ(i); pp.setY(i, d * d * 0.9); } pg.computeVertexNormals();
  for (let i = 0; i < 5; i++) { const pm = new THREE.Mesh(pg, mat); pm.rotation.y = (i / 5) * TAU + r() * 0.1; g.add(pm); }
  const c = new THREE.Mesh(new THREE.SphereGeometry(0.022, 12, 8), new THREE.MeshStandardMaterial({ color: 0xe9c770, roughness: 0.6 })); c.position.y = 0.012; g.add(c);
  return shadowy(g, true, false);
}
function hotStone(rx, ry, seed) {
  const m = new THREE.Mesh(lumpy(new THREE.SphereGeometry(1, 64, 40), 0.035, seed), MAT.basalt());
  m.scale.set(rx, ry, rx * 0.86); return shadowy(m);
}
function giftBox() {
  const g = new THREE.Group(), kraft = MAT.kraft(), twine = new THREE.MeshStandardMaterial({ color: 0xf3ece2, roughness: 0.92 });
  const base = new THREE.Mesh(new RoundedBoxGeometry(1.0, 0.5, 0.78, 4, 0.02), kraft); base.position.y = 0.25; g.add(base);
  const tissue = new THREE.Mesh(lumpy(new THREE.PlaneGeometry(0.94, 0.72, 30, 24).rotateX(-Math.PI / 2), 0.0, 1), MAT.linen(0xfffaf3));
  const tp = tissue.geometry.attributes.position; const tr = rng(4);
  for (let i = 0; i < tp.count; i++) tp.setY(i, Math.sin(tp.getX(i) * 18 + tr() * 0.8) * 0.012 + Math.sin(tp.getZ(i) * 22) * 0.01);
  tissue.geometry.computeVertexNormals(); tissue.position.y = 0.48; g.add(tissue);
  const card = new THREE.Mesh(new RoundedBoxGeometry(0.62, 0.4, 0.01, 2, 0.006), [MAT.paper(null), MAT.paper(null), MAT.paper(null), MAT.paper(null), MAT.paper(TEX.voucher || (TEX.voucher = paperTex([['500 74px "Cormorant Garamond", serif', 'BON CADEAU', 16, 78], ['300 34px Jost, sans-serif', 'Maison Môa · Riaz', 6, 0]], { h: 640 }))), MAT.paper(null)]);
  card.material.forEach((m) => { if (!m.map) m.color = C(0xf5eee3); });
  card.position.set(0.0, 0.62, 0.05); card.rotation.x = -0.18; g.add(card); g.userData.card = card;
  const lid = new THREE.Group();
  const lidBox = new THREE.Mesh(new RoundedBoxGeometry(1.05, 0.16, 0.83, 4, 0.02), kraft); lid.add(lidBox);
  const bandX = new THREE.Mesh(new THREE.BoxGeometry(1.062, 0.168, 0.026), twine); lid.add(bandX);
  const bandZ = new THREE.Mesh(new THREE.BoxGeometry(0.026, 0.168, 0.842), twine); lid.add(bandZ);
  [1, -1].forEach((sd) => {
    const loop = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.011, 8, 40, Math.PI * 1.7), twine);
    loop.position.set(sd * 0.09, 0.15, 0); loop.rotation.set(Math.PI / 2 - 0.5, sd > 0 ? 0 : Math.PI, sd * 0.4 - 0.5); lid.add(loop);
    const tail = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([V3(0, 0.09, 0), V3(sd * 0.1, 0.085, 0.12), V3(sd * 0.16, 0.084, 0.27)]), 16, 0.009, 6), twine); lid.add(tail);
  });
  const knot = new THREE.Mesh(new THREE.SphereGeometry(0.025, 16, 12), twine); knot.position.y = 0.095; lid.add(knot);
  const sp = sprig(9, 0.6, 31, MAT.leaf(0x6f7a57), 0.08); sp.rotation.set(-Math.PI / 2 + 0.06, 0, -0.9); sp.position.set(-0.32, 0.1, 0.18); lid.add(sp);
  const tag = new THREE.Mesh(new RoundedBoxGeometry(0.3, 0.19, 0.006, 2, 0.004), [MAT.paper(null), MAT.paper(null), MAT.paper(null), MAT.paper(null), MAT.paper(TEX.tag || (TEX.tag = paperTex([['500 62px "Cormorant Garamond", serif', 'MAISON MÔA', 14, 0]], { h: 620, frame: false }))), MAT.paper(null)]);
  tag.material.forEach((m) => { if (!m.map) m.color = C(0xf5eee3); });
  tag.position.set(0.3, 0.11, 0.34); tag.rotation.set(-Math.PI / 2 + 0.12, 0, 0.35); lid.add(tag);
  lid.position.y = 0.58; g.add(lid); g.userData.lid = lid;
  return shadowy(g);
}
function monogram3D() {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="${MONO}"/></svg>`;
  const data = new SVGLoader().parse(svg), shapes = [];
  data.paths.forEach((p) => SVGLoader.createShapes(p).forEach((s) => shapes.push(s)));
  const geo = new THREE.ExtrudeGeometry(shapes, { depth: 5, bevelEnabled: true, bevelThickness: 1.6, bevelSize: 1.1, bevelSegments: 3, curveSegments: 18 });
  geo.center(); const k = 1.45 / MONO_BOX[3]; geo.scale(k, -k, -k); geo.computeVertexNormals();
  const mat = MAT.metal(0xc9ab84, 0.24); mat.side = THREE.DoubleSide;
  return shadowy(new THREE.Mesh(geo, mat));
}

/* ------------------------------------------------------------------ the studio */
const ACTIVE = new Set();
class Studio {
  constructor(host, kind) {
    this.host = host; this.kind = kind; this.t = PARAMS.has('t') ? +PARAMS.get('t') : 0; this.last = 0; this.p = 0;
    this.pointer = V2(0, 0); this.pTarget = V2(0, 0); this.frames = 0; this.slow = 0;
    const canvas = document.createElement('canvas'); canvas.className = 'scene-canvas'; canvas.setAttribute('aria-hidden', 'true');
    const r = this.renderer = new THREE.WebGLRenderer({ canvas, antialias: TIER > 0, alpha: false, powerPreference: 'high-performance' });
    this.dpr = Math.min(window.devicePixelRatio || 1, TIER > 1 ? 2 : TIER ? 1.6 : 1.25); r.setPixelRatio(this.dpr);
    r.outputColorSpace = THREE.SRGBColorSpace; r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.04;
    r.shadowMap.enabled = true; r.shadowMap.type = THREE.VSMShadowMap;
    host.appendChild(canvas);
    const bg = getComputedStyle(host).getPropertyValue('--scene-bg').trim() || '#f3eee7';
    const scene = this.scene = new THREE.Scene(); scene.background = C(bg);
    const pm = new THREE.PMREMGenerator(r); scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; scene.environmentIntensity = 0.62; pm.dispose();
    this.camera = new THREE.PerspectiveCamera(28, 1, 0.1, 80);
    scene.add(new THREE.HemisphereLight(0xfff6ea, 0xe4d3be, 0.9));
    const sun = this.sun = new THREE.DirectionalLight(0xffdfb6, 3.0);
    sun.position.set(-3.4, 6.2, 5.4); sun.target.position.set(0, 0.5, 0);
    sun.castShadow = true; const sz = TIER > 1 ? 2048 : 1024; sun.shadow.mapSize.set(sz, sz);
    Object.assign(sun.shadow.camera, { left: -4.4, right: 4.4, top: 4.4, bottom: -4.4, near: 0.5, far: 22 });
    sun.shadow.radius = TIER > 1 ? 7 : 4; sun.shadow.blurSamples = TIER > 1 ? 16 : 8; sun.shadow.bias = -0.0006;
    scene.add(sun, sun.target);
    const fill = new THREE.DirectionalLight(0xfff1e2, 0.5); fill.position.set(4, 2.4, 3); scene.add(fill);
    const rim = new THREE.DirectionalLight(0xffffff, 0.75); rim.position.set(2, 3.2, -4.5); scene.add(rim);
    const cyc = new THREE.Mesh(cycloGeo(), new THREE.ShadowMaterial({ color: 0x5c432c, opacity: 0.23, side: THREE.DoubleSide }));
    cyc.receiveShadow = true; scene.add(cyc);
    this.root = new THREE.Group(); scene.add(this.root);
    this.buildCanopy(); this.buildFlecks();
    const spec = SCENES[kind](this);
    this.spec = Object.assign({ target: V3(0, 0.5, 0), radius: 1.1, dir: V3(0.16, 0.3, 1), update: () => {} }, spec);
    this.spec.dir.normalize();
    this.resize(); this.render(0.016);
    host.classList.add('scene-ready');
  }
  buildCanopy() {
    const hidden = MAT.hidden(), g = this.canopy = new THREE.Group();
    const L = this.sun.position.clone().sub(this.sun.target.position).normalize();
    g.position.copy(this.sun.target.position).addScaledVector(L, 3.4);
    g.lookAt(this.sun.position);
    [[-1.5, -1.7, -0.5, 1.9, 15, 3], [0.5, 1.7, 2.7, 1.7, 13, 7], [1.75, -0.6, -1.1, 1.4, 11, 9], [-0.6, 0.6, 0.9, 1.2, 9, 13]].forEach(([x, y, rz, len, n, seed]) => {
      const b = sprig(n, len, seed, hidden, 0.22); b.position.set(x, y, (seed % 3) * 0.12); b.rotation.z = rz;
      b.userData.rz = rz; b.userData.ph = seed; g.add(b);
    });
    shadowy(g, true, false); this.scene.add(g);
  }
  buildFlecks() {
    const n = TIER > 1 ? 70 : 36, pos = new Float32Array(n * 3), r = rng(2);
    for (let i = 0; i < n; i++) { pos[i * 3] = (r() - 0.5) * 4; pos[i * 3 + 1] = r() * 2.6; pos[i * 3 + 2] = (r() - 0.5) * 2.4; }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    this.flecks = new THREE.Points(geo, new THREE.PointsMaterial({ size: 0.02, map: dotTex(), color: 0xc49a6a, transparent: true, opacity: 0.55, depthWrite: false }));
    this.fleckBase = pos.slice(); this.scene.add(this.flecks);
  }
  resize() {
    const w = Math.max(1, this.host.clientWidth), h = Math.max(1, this.host.clientHeight);
    if (w === this.w && h === this.h) return; this.w = w; this.h = h;
    this.renderer.setSize(w, h, false);
    const cam = this.camera; cam.aspect = w / h;
    const mode = this.host.dataset.layout || 'auto';
    const split = mode === 'split' || (mode === 'auto' && w / h > 1.05 && w > 860);
    const cx = split ? parseFloat(this.host.dataset.cx || 0.7) : 0.5;
    const cy = split ? 0.5 : parseFloat(this.host.dataset.cy || 0.24);
    const rw = split ? parseFloat(this.host.dataset.rw || 0.46) : 0.9, rh = split ? 0.74 : parseFloat(this.host.dataset.rh || 0.36);
    cam.setViewOffset(w, h, (0.5 - cx) * w, (0.5 - cy) * h, w, h);
    const th = Math.tan(THREE.MathUtils.degToRad(cam.fov / 2));
    this.dist = clamp(this.spec.radius / Math.min(th * rh, th * cam.aspect * rw), 2.5, 16);
    cam.updateProjectionMatrix();
  }
  render(dt) {
    const s = this.spec, cam = this.camera, t = this.t;
    this.pointer.lerp(this.pTarget, Math.min(1, dt * 3));
    const az = this.pointer.x * 0.16 + (COARSE ? Math.sin(t * 0.25) * 0.08 : 0) + this.p * 0.35, el = this.pointer.y * 0.06 + this.p * 0.18;
    const dir = s.dir.clone().applyAxisAngle(V3(0, 1, 0), az); dir.y += el; dir.normalize();
    cam.position.copy(s.target).addScaledVector(dir, this.dist * (1 + this.p * 0.12));
    cam.lookAt(s.target.x, s.target.y + this.p * 0.2, s.target.z);
    this.canopy.children.forEach((b) => {
      const ph = b.userData.ph;
      b.rotation.z = b.userData.rz + Math.sin(t * 0.5 + ph) * 0.045 + Math.sin(t * 1.3 + ph * 2) * 0.015;
      b.children.forEach((lf) => { if (lf.userData.base) lf.rotation.x = lf.userData.base.x + Math.sin(t * 2.1 + lf.userData.ph) * 0.09; });
    });
    const fp = this.flecks.geometry.attributes.position, fb = this.fleckBase;
    for (let i = 0; i < fp.count; i++) {
      fp.setX(i, fb[i * 3] + Math.sin(t * 0.3 + i) * 0.12);
      fp.setY(i, (fb[i * 3 + 1] + t * 0.04) % 2.6);
      fp.setZ(i, fb[i * 3 + 2] + Math.cos(t * 0.25 + i * 1.7) * 0.1);
    }
    fp.needsUpdate = true;
    s.update(t, dt, this.p);
    this.renderer.render(this.scene, cam);
  }
  frame(now) {
    if (!this.running) return;
    this.raf = requestAnimationFrame((n) => this.frame(n));
    const dt = this.last ? Math.min(0.05, (now - this.last) / 1000) : 0.016; this.last = now;
    if (!STILL && !REDUCE) this.t += dt;
    const rect = this.host.getBoundingClientRect();
    this.p = clamp(-rect.top / Math.max(1, rect.height), 0, 1);
    this.resize(); this.render(dt);
    if (++this.frames > 30 && this.frames < 200) { this.slow += dt > 0.034 ? 1 : 0; if (this.slow > 40 && this.dpr > 1) { this.dpr = Math.max(1, this.dpr - 0.35); this.renderer.setPixelRatio(this.dpr); this.w = 0; this.slow = 0; } }
  }
  start() { if (this.running) return; this.running = true; this.last = 0; this.raf = requestAnimationFrame((n) => this.frame(n)); }
  stop() { this.running = false; cancelAnimationFrame(this.raf); }
}

/* ------------------------------------------------------------------ still lifes */
const SCENES = {
  serum(S) {
    const g = S.root;
    const B = bottle({ r: 0.31, h: 0.78, label: TEX.label || (TEX.label = paperTex([['500 58px "Cormorant Garamond", serif', 'MAISON MÔA', 14, 52], ['300 30px Jost, sans-serif', 'HUILE DE SOIN', 8, 0]])) });
    B.position.set(-0.68, 0, -0.22); B.rotation.y = 0.35; g.add(B);
    const D = dish(0.6); D.position.set(0.36, 0, 0.3); g.add(D);
    const pool = new Pool(0.47, MAT.oil()); pool.mesh.position.set(0.36, 0.098, 0.3); g.add(pool.mesh);
    const P = pipette(0.92); P.position.set(0.36, 1.3, 0.3); g.add(P);
    const drop = new THREE.Mesh(new THREE.SphereGeometry(0.032, 24, 18), MAT.drop()); drop.castShadow = true; g.add(drop);
    const crown = []; for (let i = 0; i < 7; i++) { const c = new THREE.Mesh(new THREE.SphereGeometry(0.008 + (i % 3) * 0.003, 10, 8), MAT.drop()); c.visible = false; g.add(c); crown.push(c); }
    const p1 = pebble(0.16, 0.075, 0.13, 3, MAT.stone(0xf4ece2)); p1.position.set(-0.12, p1.position.y, 0.66); g.add(p1);
    const p2 = pebble(0.1, 0.055, 0.085, 9, MAT.stone(0xe6d8c6)); p2.position.set(0.05, p2.position.y, 0.84); g.add(p2);
    const leafy = sprig(7, 0.55, 17, MAT.leaf(0x6c7855), 0.1); leafy.rotation.set(-Math.PI / 2, 0, 1.9); leafy.position.set(-0.2, 0.012, 0.42); g.add(shadowy(leafy));
    const tipW = new THREE.Vector3(), poolY = 0.098, period = 3.4; let lastCycle = -1;
    return {
      target: V3(-0.12, 0.78, 0.12), radius: 1.24, dir: V3(0.2, 0.3, 1),
      update(t, dt, p) {
        B.rotation.y = 0.35 + Math.sin(t * 0.22) * 0.22;
        P.position.y = 1.3 + Math.sin(t * 0.9) * 0.018 + p * 0.4; P.rotation.z = Math.sin(t * 0.6) * 0.025;
        P.updateMatrixWorld(); tipW.copy(P.userData.tip); P.localToWorld(tipW); g.worldToLocal(tipW);
        const cyc = Math.floor(t / period), ph = t - cyc * period;
        const grow = 1.4, fall = Math.sqrt((2 * Math.max(0.01, tipW.y - 0.035 - poolY)) / 5.5);
        if (ph < grow) {
          const k = smooth(0, grow, ph); drop.visible = true;
          drop.scale.set(k, k * (1 + 0.25 * smooth(grow * 0.6, grow, ph)), k); drop.position.set(tipW.x, tipW.y - 0.03 * k, tipW.z);
        } else if (ph < grow + fall) {
          const tf = ph - grow, v = 5.5 * tf; drop.visible = true;
          drop.position.set(tipW.x, tipW.y - 0.03 - 0.5 * 5.5 * tf * tf, tipW.z); drop.scale.set(0.9, 1.15 + v * 0.18, 0.9);
        } else {
          drop.visible = false;
          if (lastCycle !== cyc) {
            lastCycle = cyc; pool.add(t, tipW.x - 0.36, tipW.z - 0.3);
            crown.forEach((c, i) => { const a = (i / crown.length) * TAU; c.userData = { t0: t, vx: Math.cos(a) * 0.38, vy: 0.75 + (i % 3) * 0.12, vz: Math.sin(a) * 0.38, x: tipW.x, z: tipW.z }; c.visible = true; });
          }
        }
        crown.forEach((c) => {
          if (!c.visible || !c.userData.t0) return; const tc = t - c.userData.t0, y = poolY + c.userData.vy * tc - 3.5 * tc * tc;
          if (y < poolY - 0.01 || tc > 1) { c.visible = false; return; }
          c.position.set(c.userData.x + c.userData.vx * tc, y, c.userData.z + c.userData.vz * tc);
        });
        pool.update(t);
        g.rotation.y = p * 0.25;
      },
    };
  },
  visage(S) {
    const g = S.root;
    const gs = guaSha(); gs.scale.setScalar(0.72); g.add(gs);
    const roller = jadeRoller(); g.add(roller);
    const jar = creamJar(); jar.position.set(-0.36, 0, -0.38); g.add(jar);
    const lid = new THREE.Mesh(lathe([[0, 0], [0.3, 0], [0.31, 0.015], [0.31, 0.06], [0.29, 0.075], [0, 0.075]], 80), MAT.ceramic(0xe9dccb, 0.42));
    lid.position.set(0.32, 0, -0.52); g.add(shadowy(lid));
    const p1 = pebble(0.12, 0.06, 0.1, 5, MAT.stone(0xf0e6da)); p1.position.set(0.55, p1.position.y, 0.5); g.add(p1);
    return {
      target: V3(0, 0.5, 0), radius: 1.08, dir: V3(0.12, 0.36, 1),
      update(t, dt, p) {
        gs.position.set(0.34, 0.78 + Math.sin(t * 0.8) * 0.05 + p * 0.3, 0.12);
        gs.rotation.set(-0.42 + Math.sin(t * 0.5) * 0.1, -0.35 + Math.sin(t * 0.28) * 0.45, 0.22 + Math.sin(t * 0.7) * 0.06);
        roller.position.set(-0.22, 0.34 + Math.sin(t * 0.8 + 1.4) * 0.04 + p * 0.15, 0.36);
        roller.rotation.set(0.2, -0.55 + Math.sin(t * 0.35) * 0.18, 0.22 + Math.sin(t * 0.6) * 0.05);
        roller.userData.rollers.forEach((rl, i) => { rl.rotation.y = t * (i ? 1.6 : 1.1); });
        g.rotation.y = p * 0.3;
      },
    };
  },
  epilation(S) {
    const g = S.root;
    const towel = new THREE.Mesh(new RoundedBoxGeometry(1.25, 0.07, 0.95, 4, 0.03), MAT.linen()); towel.position.set(0, 0.035, 0); towel.rotation.y = 0.12; g.add(shadowy(towel));
    const pot = waxPot(); pot.position.set(0, 0.07, 0); g.add(pot);
    const wax = new Pool(0.336, MAT.wax(), 18, 72); wax.amp = 0.006; wax.base = (r, a, t) => 0.006 * Math.sin(r * 22 - t * 1.2) * (1 - r * 2);
    wax.mesh.position.set(0, 0.07 + 0.33, 0); g.add(wax.mesh);
    const spat = spatula(), pivot = new THREE.Group(); spat.position.y = -0.86; pivot.add(spat); g.add(pivot);
    const ribbon = new Ribbon(48, 14, MAT.wax()); ribbon.mesh.castShadow = true; g.add(ribbon.mesh);
    const heap = new THREE.Mesh(new THREE.TorusGeometry(0.045, 0.022, 12, 32), MAT.wax()); heap.rotation.x = -Math.PI / 2; g.add(heap);
    const tip = new THREE.Vector3(), pts = Array.from({ length: 49 }, () => new THREE.Vector3()), radii = new Float32Array(49);
    const p1 = pebble(0.13, 0.06, 0.11, 12, MAT.stone(0xf2e8dc)); p1.position.set(0.72, p1.position.y, 0.42); g.add(p1);
    const leafy = sprig(6, 0.5, 23, MAT.leaf(0x6c7855), 0.12); leafy.rotation.set(-Math.PI / 2, 0, -2.3); leafy.position.set(-0.5, 0.075, 0.32); g.add(shadowy(leafy));
    let last = -1;
    return {
      target: V3(-0.05, 0.74, 0), radius: 1.22, dir: V3(0.14, 0.38, 1),
      update(t, dt, p) {
        pivot.position.set(0.06 + Math.sin(t * 0.5) * 0.03, 1.0 + Math.sin(t * 0.7) * 0.03 + p * 0.25, 0.04);
        pivot.rotation.set(0.12, 0.35 + Math.sin(t * 0.3) * 0.1, Math.PI + 0.62 + Math.sin(t * 0.5) * 0.05);
        tip.copy(pivot.position);
        const surf = 0.4, land = V3(0.02, surf, 0.02);
        for (let i = 0; i <= 48; i++) {
          const s = i / 48, e = s * s;
          pts[i].set(tip.x + (land.x - tip.x) * (1 - Math.pow(1 - s, 3)) + Math.sin(s * 9 - t * 3.2) * 0.012 * s * (1 - s),
            tip.y + (surf + 0.01 - tip.y) * (s * 0.35 + e * 0.65), tip.z + (land.z - tip.z) * (1 - Math.pow(1 - s, 3)) + Math.cos(s * 7 - t * 2.6) * 0.01 * s * (1 - s));
          radii[i] = 0.011 + 0.03 * Math.exp(-s * 10) + 0.012 * smooth(0.86, 1, s) + 0.002 * Math.sin(s * 30 - t * 6);
        }
        ribbon.update(pts, radii);
        heap.position.set(land.x, surf + 0.012, land.z); heap.rotation.z = t * 0.8; heap.scale.setScalar(1 + Math.sin(t * 2) * 0.05);
        const k = Math.floor(t / 2.2); if (k !== last) { last = k; wax.add(t, land.x, land.z, 0.6); }
        wax.update(t); g.rotation.y = p * 0.3;
      },
    };
  },
  regard(S) {
    const g = S.root, gel = MAT.gel();
    const s = new THREE.Shape();
    s.moveTo(-0.4, 0.03); s.quadraticCurveTo(0, -0.46, 0.4, 0.03); s.quadraticCurveTo(0.39, 0.1, 0.32, 0.08); s.quadraticCurveTo(0, -0.17, -0.32, 0.08); s.quadraticCurveTo(-0.39, 0.1, -0.4, 0.03);
    const pg = new THREE.ExtrudeGeometry(s, { depth: 0.012, bevelEnabled: true, bevelThickness: 0.012, bevelSize: 0.012, bevelSegments: 5, curveSegments: 48 }); pg.center();
    const pa = shadowy(new THREE.Mesh(pg, gel)), pb = shadowy(new THREE.Mesh(pg, gel)); g.add(pa, pb);
    const brush = new THREE.Group();
    brush.add(new THREE.Mesh(lathe([[0, 0], [0.022, 0], [0.032, 0.26], [0.03, 0.6], [0, 0.62]], 32), MAT.plastic(0x2c2a27, 0.3)));
    const fer = new THREE.Mesh(new THREE.CylinderGeometry(0.024, 0.028, 0.14, 32), MAT.metal(0xd8c6ad, 0.22)); fer.position.y = -0.07; brush.add(fer);
    const tuft = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.008, 0.13, 4, 1), new THREE.MeshStandardMaterial({ color: 0x4a3426, roughness: 0.7 }));
    tuft.scale.set(1.4, 1, 0.5); tuft.position.y = -0.19; tuft.rotation.y = Math.PI / 4; brush.add(tuft); g.add(shadowy(brush));
    const bowl = new THREE.Mesh(lathe([[0, 0], [0.16, 0], [0.22, 0.05], [0.24, 0.11], [0.225, 0.115], [0.2, 0.06], [0.14, 0.03], [0, 0.028]], 64), MAT.glass({ att: 0xefe6da, dist: 2, thick: 0.1, fallback: 0xece4d8, opacity: 0.6 }));
    bowl.position.set(0.42, 0, 0.32); g.add(shadowy(bowl));
    const tint = new THREE.Mesh(new THREE.CircleGeometry(0.165, 48).rotateX(-Math.PI / 2), MAT.polish(0x4b3123)); tint.position.set(0.42, 0.045, 0.32); g.add(tint);
    const pads = new THREE.Group(); for (let i = 0; i < 3; i++) { const pd = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.035, 48), MAT.linen(0xffffff)); pd.position.set(i * 0.02, 0.018 + i * 0.036, -i * 0.015); pd.rotation.y = i; pads.add(pd); }
    pads.position.set(-0.55, 0, -0.25); g.add(shadowy(pads));
    return {
      target: V3(0, 0.55, 0), radius: 1.05, dir: V3(0.1, 0.32, 1),
      update(t, dt, p) {
        pa.position.set(-0.28, 0.82 + Math.sin(t * 0.8) * 0.05 + p * 0.25, 0.05); pa.rotation.set(-0.38 + Math.sin(t * 0.5) * 0.1, 0.3, 0.22 + Math.sin(t * 0.4) * 0.08);
        pb.position.set(0.3, 0.68 + Math.sin(t * 0.8 + 1.2) * 0.05 + p * 0.2, 0.18); pb.rotation.set(-0.32 + Math.sin(t * 0.55 + 1) * 0.1, -0.4, -0.18 + Math.sin(t * 0.45) * 0.08);
        brush.position.set(0.05, 0.5 + Math.sin(t * 0.7 + 2) * 0.04, 0.52); brush.rotation.set(0.25, 0, -1.1 + Math.sin(t * 0.5) * 0.06);
        g.rotation.y = p * 0.3;
      },
    };
  },
  mains(S) {
    const g = S.root;
    const b1 = polishBottle(0xd9a797); b1.position.set(-0.52, 0, -0.05); b1.rotation.y = 0.5; g.add(b1);
    const b2 = polishBottle(0xa45f4a); b2.position.set(-0.05, 0, -0.38); b2.rotation.y = -0.3; g.add(b2);
    const b3 = polishBottle(0xeadbcb, 0xe9e0d3); g.add(b3);
    const b4 = polishBottle(0x5d6650); b4.rotation.set(0, 0.8, Math.PI / 2); b4.position.set(0.5, 0.165, -0.12); g.add(b4);
    const f1 = nailFile(0xe9d9c6); f1.position.set(0.05, 0, 0.5); f1.rotation.y = 0.35; g.add(f1);
    const f2 = nailFile(0xd8b4a6); f2.position.set(0.1, 0.019, 0.55); f2.rotation.y = -0.25; g.add(f2);
    return {
      target: V3(0, 0.45, 0), radius: 1.0, dir: V3(0.12, 0.36, 1),
      update(t, dt, p) {
        b3.position.set(0.32, 0.55 + Math.sin(t * 0.8) * 0.06 + p * 0.3, 0.22); b3.rotation.set(0.25 + Math.sin(t * 0.5) * 0.1, t * 0.35, -0.3 + Math.sin(t * 0.6) * 0.06);
        b1.rotation.y = 0.5 + Math.sin(t * 0.3) * 0.1; g.rotation.y = p * 0.3;
      },
    };
  },
  pieds(S) {
    const g = S.root;
    const basin = new THREE.Mesh(lathe([[0, 0], [0.5, 0], [0.68, 0.06], [0.78, 0.2], [0.8, 0.3], [0.77, 0.31], [0.7, 0.22], [0.55, 0.1], [0, 0.085]], 96), MAT.stone(0xfaf3ea)); g.add(shadowy(basin));
    const water = new Pool(0.71, MAT.water(), 24, 90); water.amp = 0.01; water.base = (r, a, t) => 0.003 * Math.sin(r * 16 - t * 1.4) + 0.002 * Math.sin(a * 3 + t * 0.8) * r;
    water.mesh.position.y = 0.235; g.add(water.mesh);
    const flowers = [0, 1, 2, 3].map((i) => { const f = jasmine(40 + i); f.scale.setScalar(0.95 + (i % 2) * 0.25); g.add(f); return f; });
    const towel = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.78, 48), MAT.linen()); towel.rotation.set(0, 0.5, Math.PI / 2); towel.position.set(-0.55, 0.15, 0.62); g.add(shadowy(towel));
    const p1 = pebble(0.15, 0.07, 0.12, 31, MAT.stone(0xf0e5d6)); p1.position.set(0.85, p1.position.y, 0.42); g.add(p1);
    const p2 = pebble(0.09, 0.05, 0.08, 33, MAT.basalt()); p2.position.set(0.68, p2.position.y, 0.62); g.add(p2);
    const drop = new THREE.Mesh(new THREE.SphereGeometry(0.022, 16, 12), MAT.water()); g.add(drop); let last = -1;
    return {
      target: V3(0, 0.3, 0.05), radius: 1.12, dir: V3(0.1, 0.62, 1),
      update(t, dt, p) {
        flowers.forEach((f, i) => {
          const a = t * 0.12 + i * 1.6, rr = 0.2 + (i % 2) * 0.24, x = Math.cos(a) * rr, z = Math.sin(a) * rr;
          f.position.set(x, 0.236 + Math.sin(t * 1.2 + i) * 0.006, z); f.rotation.set(Math.sin(t + i) * 0.05, -a * 1.5, Math.cos(t * 0.9 + i) * 0.05);
        });
        const per = 3.6, k = Math.floor(t / per), ph = t - k * per;
        if (ph < 0.6) { drop.visible = true; drop.position.set(0.08, 1.8 - 0.5 * 4.4 * ph * ph, -0.06); drop.scale.set(0.9, 1.3, 0.9); if (drop.position.y < 0.24) drop.visible = false; }
        else { drop.visible = false; if (k !== last) { last = k; water.add(t, 0.08, -0.06, 1); } }
        water.update(t); g.rotation.y = p * 0.3;
      },
    };
  },
  corps(S) {
    const g = S.root, stack = new THREE.Group(); g.add(stack);
    const dims = [[0.46, 0.13, 1], [0.38, 0.12, 2], [0.31, 0.11, 3], [0.24, 0.1, 4], [0.17, 0.085, 5]], stones = [];
    let y = 0; dims.forEach(([rx, ry, seed], i) => { const st = hotStone(rx, ry, seed); y += ry; st.position.set((i % 2 ? 0.03 : -0.02), y, (i % 2 ? -0.02 : 0.02)); st.rotation.y = i * 1.3; st.userData.y = y; y += ry * 0.92; stack.add(st); stones.push(st); });
    const l1 = hotStone(0.2, 0.09, 8); l1.position.set(0.66, 0.09, 0.36); l1.rotation.y = 0.6; g.add(l1);
    const l2 = hotStone(0.15, 0.07, 9); l2.position.set(0.48, 0.07, 0.62); g.add(l2);
    const B = bottle({ r: 0.17, h: 0.42 }); B.position.set(-0.68, 0, 0.12); g.add(B);
    const leafy = sprig(8, 0.62, 29, MAT.leaf(0x6c7855), 0.15); leafy.rotation.set(-Math.PI / 2, 0, 0.6); leafy.position.set(-0.1, 0.012, 0.6); g.add(shadowy(leafy));
    const fl = jasmine(77); fl.position.set(0.35, 0.02, 0.78); fl.scale.setScalar(1.2); g.add(fl);
    return {
      target: V3(0, 0.62, 0.05), radius: 1.12, dir: V3(0.16, 0.3, 1),
      update(t, dt, p) {
        stack.rotation.y = t * 0.12 + p * 0.6;
        const top = stones[stones.length - 1], lift = Math.max(0, Math.sin(t * 0.9)) * 0.05;
        top.position.y = top.userData.y + lift; top.rotation.z = Math.sin(t * 0.9) * 0.05;
      },
    };
  },
  cadeau(S) {
    const g = S.root, box = giftBox(); box.rotation.y = -0.45; g.add(box);
    const lid = box.userData.lid, card = box.userData.card;
    const p1 = pebble(0.12, 0.06, 0.1, 51, MAT.stone(0xf2e7da)); p1.position.set(0.85, p1.position.y, 0.3); g.add(p1);
    const leafy = sprig(7, 0.55, 37, MAT.leaf(0x6c7855), 0.1); leafy.rotation.set(-Math.PI / 2, 0, 2.2); leafy.position.set(-0.75, 0.012, 0.45); g.add(shadowy(leafy));
    return {
      target: V3(0, 0.6, 0), radius: 0.98, dir: V3(0.18, 0.5, 1),
      update(t, dt, p) {
        const open = 0.5 + 0.5 * Math.sin(t * 0.6 - 1.2);
        lid.position.y = 0.6 + open * 0.32 + p * 0.4; lid.rotation.set(-0.06 * open, open * 0.25, 0.08 * open);
        card.position.y = 0.6 + open * 0.08; box.rotation.y = -0.45 + Math.sin(t * 0.2) * 0.12;
      },
    };
  },
  maison(S) {
    const g = S.root, m = monogram3D(); g.add(m);
    const plinth = new THREE.Mesh(new RoundedBoxGeometry(1.0, 0.2, 0.5, 4, 0.03), MAT.stone(0xfbf4eb)); plinth.position.y = 0.1; g.add(shadowy(plinth));
    const p1 = pebble(0.11, 0.05, 0.09, 61, MAT.stone(0xeee3d6)); p1.position.set(0.7, p1.position.y, 0.36); g.add(p1);
    const leafy = sprig(7, 0.55, 41, MAT.leaf(0x6c7855), 0.1); leafy.rotation.set(-Math.PI / 2, 0, 2.6); leafy.position.set(-0.55, 0.012, 0.45); g.add(shadowy(leafy));
    return {
      target: V3(0, 0.95, 0), radius: 1.05, dir: V3(0.08, 0.2, 1),
      update(t, dt, p) { m.position.set(0, 0.98 + Math.sin(t * 0.8) * 0.03, 0); m.rotation.y = Math.sin(t * 0.35) * 0.55 + p * 0.8; },
    };
  },
};

/* ------------------------------------------------------------------ boot */
function supportsGL() { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; } }
async function boot() {
  const hosts = [...document.querySelectorAll('[data-scene]')];
  if (!hosts.length) return;
  if (!supportsGL()) { hosts.forEach((h) => h.classList.add('scene-off')); return; }
  try { await Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 1200))]); } catch (e) { /* fonts optional */ }
  const io = 'IntersectionObserver' in window ? new IntersectionObserver((es) => es.forEach((e) => { const st = e.target.__studio; if (!st) return; e.isIntersecting ? st.start() : st.stop(); }), { rootMargin: '80px' }) : null;
  hosts.forEach((h) => {
    const kind = h.dataset.scene; if (!SCENES[kind]) return;
    const go = () => {
      try { const st = new Studio(h, kind); h.__studio = st; ACTIVE.add(st); io ? io.observe(h) : st.start(); }
      catch (err) { console.warn('[scene]', kind, err); h.classList.add('scene-off'); }
    };
    if (h.dataset.lazy !== undefined && io) {
      const lio = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { lio.disconnect(); go(); } }, { rootMargin: '600px' });
      lio.observe(h);
    } else go();
  });
  window.addEventListener('pointermove', (e) => {
    const x = (e.clientX / window.innerWidth) * 2 - 1, y = (e.clientY / window.innerHeight) * 2 - 1;
    ACTIVE.forEach((s) => s.pTarget.set(x, -y));
  }, { passive: true });
  document.addEventListener('visibilitychange', () => ACTIVE.forEach((s) => (document.hidden ? s.stop() : (s.host.getBoundingClientRect().bottom > 0 && s.start()))));
  window.__scenes = ACTIVE;
}
boot();
