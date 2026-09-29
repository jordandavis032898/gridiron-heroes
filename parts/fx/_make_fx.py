"""Arcade additive FX sprites for Gridiron Heroes."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
RNG = np.random.default_rng(12)

MAGENTA = np.array([255, 0, 255], dtype=np.uint8)
BROWN = np.array([0x6D, 0x58, 0x36], dtype=np.uint8)
TAN = np.array([0x7D, 0x6A, 0x45], dtype=np.uint8)
DIRT_DK = np.array([0x4A, 0x3C, 0x24], dtype=np.uint8)
DIRT_LT = np.array([0x8A, 0x75, 0x50], dtype=np.uint8)


def save_rgb(arr, name):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").save(OUT / name)


def down2(hi):
    h, w = hi.shape[:2]
    return hi.reshape(h // 2, 2, w // 2, 2, 3).mean(axis=(1, 3))


def dist_to_segment(px, py, x0, y0, x1, y1):
    vx, vy = x1 - x0, y1 - y0
    l2 = vx * vx + vy * vy
    t = np.clip(((px - x0) * vx + (py - y0) * vy) / max(l2, 1e-6), 0.0, 1.0)
    return np.hypot(px - (x0 + t * vx), py - (y0 + t * vy))


def make_impact():
    N = 512
    cx = cy = (N - 1) / 2.0
    n_pts = 11
    xy = []
    for i in range(n_pts):
        a = -np.pi / 2 + i * (2 * np.pi / n_pts)
        long = 250 + 30 * np.sin(i * 2.1 + 0.5) + (20 if i % 3 == 0 else -8)
        xy.append((cx + long * np.cos(a), cy + long * np.sin(a)))
        a2 = a + np.pi / n_pts
        short = 22 + 7 * (i % 3)
        xy.append((cx + short * np.cos(a2), cy + short * np.sin(a2)))

    mask_im = Image.new("L", (N, N), 0)
    ImageDraw.Draw(mask_im).polygon(xy, fill=255)
    m = np.array(mask_im, dtype=np.float64) / 255.0

    y, x = np.mgrid[0:N, 0:N]
    r = np.hypot(x - cx, y - cy)
    fall = np.clip(1.0 - r / 255.0, 0, 1) ** 0.9
    val = m * (0.18 + 0.82 * fall)
    core = np.clip(1.0 - r / 40.0, 0, 1) ** 1.25
    bloom = np.exp(-((r / 26.0) ** 2)) * 0.75
    val = np.maximum(val, np.maximum(core, bloom))
    out = np.stack([val, val, val * 0.99], axis=-1) * 255.0
    return down2(out)


def make_shock():
    N = 512
    y, x = np.mgrid[0:N, 0:N]
    cx = cy = (N - 1) / 2.0
    r = np.hypot(x - cx, y - cy)
    ring_r = 186.0
    # hollow centre: inner edge is hard-ish, outer is a soft falloff
    inner = 1.0 / (1.0 + np.exp(-(r - (ring_r - 10)) / 1.6))
    core = np.exp(-0.5 * ((r - ring_r) / 5.2) ** 2)
    outer = np.exp(-0.5 * ((r - ring_r) / 22.0) ** 2) * 0.42
    v = np.clip((core + outer) * inner, 0, 1)
    # kill anything near the origin so the hole stays black
    v = np.where(r < ring_r - 16, 0.0, v)
    out = np.stack([v, v, v], axis=-1) * 255.0
    return down2(out)


def hex_corners(cx, cy, s):
    ang = np.linspace(0, 2 * np.pi, 7) + np.pi / 6
    return cx + s * np.cos(ang), cy + s * np.sin(ang)


def make_dome():
    N = 512
    v = np.zeros((N, N), dtype=np.float64)
    cx = (N - 1) / 2.0
    bottom = N - 20.0
    rad = 228.0
    cy = bottom
    yy, xx = np.mgrid[0:N, 0:N]
    dx, dy = xx - cx, yy - cy
    dist = np.hypot(dx, dy)
    inside = (dist <= rad) & (yy <= bottom)

    fill = np.where(inside, 0.09 + 0.07 * (1.0 - dist / rad), 0.0)
    rim = np.exp(-0.5 * ((dist - rad) / 6.5) ** 2)
    rim = np.where((yy <= bottom) & (np.abs(dist - rad) < 22), rim, 0.0)
    v = np.maximum(fill, rim)

    def stamp_line(x0, y0, x1, y1, val=0.62, rad_px=1.6):
        n = int(max(abs(x1 - x0), abs(y1 - y0), 1)) + 1
        xs = np.linspace(x0, x1, n)
        ys = np.linspace(y0, y1, n)
        rpi = int(np.ceil(rad_px))
        for px, py in zip(xs, ys):
            ix, iy = int(round(px)), int(round(py))
            for oy in range(-rpi, rpi + 1):
                for ox in range(-rpi, rpi + 1):
                    jx, jy = ix + ox, iy + oy
                    if jx < 0 or jy < 0 or jx >= N or jy >= N:
                        continue
                    if not inside[jy, jx]:
                        continue
                    if ox * ox + oy * oy <= rad_px * rad_px:
                        if v[jy, jx] < val:
                            v[jy, jx] = val

    size = 20.0
    hex_w = np.sqrt(3) * size
    hex_h = 1.5 * size
    row0 = int((-rad) / hex_h) - 1
    row1 = 2
    col0 = int((-rad) / hex_w) - 1
    col1 = int((rad) / hex_w) + 2
    angs = np.linspace(0, 2 * np.pi, 7) + np.pi / 6
    for row in range(row0, row1 + 1):
        for col in range(col0, col1 + 1):
            hx = cx + hex_w * (col + 0.5 * (row & 1))
            hy = cy + hex_h * row
            if hy > bottom - 6:
                continue
            if (hx - cx) ** 2 + (hy - cy) ** 2 > (rad - 14) ** 2:
                continue
            ptsx = hx + size * np.cos(angs)
            ptsy = hy + size * np.sin(angs)
            for i in range(6):
                stamp_line(ptsx[i], ptsy[i], ptsx[i + 1], ptsy[i + 1])

    bottom_band = (np.abs(yy - bottom) < 3.2) & (np.abs(dx) <= rad * 0.995)
    v = np.where(bottom_band, np.maximum(v, 0.88), v)
    v = np.where(yy > bottom, 0.0, v)
    out = np.stack([v, v * 0.99, v * 0.97], axis=-1) * 255.0
    return down2(out)


def make_streak():
    w, h = 256, 64
    y, x = np.mgrid[0:h, 0:w]
    cx_line = (h - 1) / 2.0
    u = x / (w - 1.0)  # 0 left, 1 right
    # brightest and thickest at the right
    amp = u ** 1.55
    half = 2.2 + 14.5 * (u ** 1.25)
    dy = np.abs(y - cx_line)
    # sharp core, not a blur: power falloff, hard-ish shoulders
    core = np.clip(1.0 - dy / (half * 0.38), 0, 1) ** 0.55
    wing = np.clip(1.0 - dy / half, 0, 1) ** 2.4
    v = np.clip(amp * (0.55 * core + 0.45 * wing), 0, 1)
    v = np.where(dy > half, 0.0, v)
    # fade the last few pixels on the left to nothing
    v *= np.clip((x - 4) / 18.0, 0, 1)
    out = np.stack([v, v, v], axis=-1) * 255.0
    return out


def make_bolt():
    w, h = 256, 128
    # four direction changes, full width, centred vertically overall
    pts = np.array(
        [
            [0.0, 64.0],
            [52.0, 38.0],
            [108.0, 86.0],
            [168.0, 34.0],
            [215.0, 78.0],
            [255.0, 64.0],
        ]
    )
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    d = np.full((h, w), 1e9)
    for i in range(len(pts) - 1):
        d = np.minimum(
            d, dist_to_segment(xx, yy, pts[i, 0], pts[i, 1], pts[i + 1, 0], pts[i + 1, 1])
        )
    # a couple of short forks
    forks = [
        (52.0, 38.0, 68.0, 18.0),
        (168.0, 34.0, 180.0, 14.0),
        (108.0, 86.0, 122.0, 110.0),
    ]
    for x0, y0, x1, y1 in forks:
        d = np.minimum(d, dist_to_segment(xx, yy, x0, y0, x1, y1))

    core = np.clip(1.0 - d / 1.35, 0, 1) ** 0.7
    glow = np.exp(-0.5 * (d / 6.5) ** 2) * 0.38
    v = np.clip(core + glow, 0, 1)
    out = np.stack([v, v, v * 0.98], axis=-1) * 255.0
    return out


def blob(img, cx, cy, rx, ry, color, hardness=2.2):
    h, w = img.shape[:2]
    y, x = np.mgrid[0:h, 0:w]
    u = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
    m = np.clip(1.0 - u, 0, 1) ** hardness
    key = (img[:, :, 0] > 240) & (img[:, :, 2] > 240) & (img[:, :, 1] < 20)
    paint = m > 0.18
    # Never blend dirt into magenta — chroma key needs a hard edge.
    for c in range(3):
        over = (~key) & paint
        img[:, :, c] = np.where(key & paint, color[c], img[:, :, c])
        img[:, :, c] = np.where(over, img[:, :, c] * (1 - m) + color[c] * m, img[:, :, c])


def make_dust():
    n = 128
    img = np.broadcast_to(MAGENTA, (n, n, 3)).copy().astype(np.float64)
    # denser at the bottom: more / larger blobs low in the frame
    specs = [
        (64, 98, 38, 22, BROWN, 1.6),
        (48, 104, 28, 18, TAN, 1.8),
        (82, 106, 30, 16, BROWN, 1.7),
        (36, 92, 18, 14, TAN, 2.0),
        (96, 94, 20, 14, BROWN, 1.9),
        (58, 84, 22, 16, TAN, 1.7),
        (74, 88, 16, 12, DIRT_DK, 2.2),
        (44, 78, 12, 10, BROWN, 2.0),
        (88, 80, 14, 11, TAN, 1.8),
        (64, 72, 18, 12, BROWN, 1.9),
        (52, 110, 16, 10, DIRT_DK, 2.4),
        (76, 112, 14, 9, TAN, 2.1),
        (30, 108, 12, 9, BROWN, 2.2),
        (100, 108, 13, 9, DIRT_DK, 2.3),
        (62, 60, 10, 8, TAN, 2.0),
        (70, 54, 8, 7, BROWN, 2.2),
        (54, 52, 7, 6, TAN, 2.4),
    ]
    for cx, cy, rx, ry, col, hard in specs:
        blob(img, cx, cy, rx, ry, col, hard)
    # darker flecks
    rng = np.random.default_rng(4)
    for _ in range(28):
        fx = rng.uniform(22, 106)
        fy = rng.uniform(48, 118)
        fr = rng.uniform(1.2, 2.8)
        col = DIRT_DK if rng.random() < 0.65 else BROWN
        blob(img, fx, fy, fr, fr * 0.75, col, 1.3)
    # a few lighter chips near the top of the puff
    for _ in range(8):
        fx = rng.uniform(40, 90)
        fy = rng.uniform(46, 70)
        blob(img, fx, fy, rng.uniform(2.0, 3.5), rng.uniform(1.4, 2.4), DIRT_LT, 1.6)
    return img


def main():
    save_rgb(make_impact(), "fx-impact.png")
    save_rgb(make_shock(), "fx-shock.png")
    save_rgb(make_dome(), "fx-dome.png")
    save_rgb(make_streak(), "fx-streak.png")
    save_rgb(make_bolt(), "fx-bolt.png")
    save_rgb(make_dust(), "fx-dust.png")
    for name in (
        "fx-impact.png",
        "fx-shock.png",
        "fx-dome.png",
        "fx-streak.png",
        "fx-bolt.png",
        "fx-dust.png",
    ):
        im = Image.open(OUT / name)
        a = np.array(im)
        print(name, im.size, im.mode, "min", a.min(axis=(0, 1)), "max", a.max(axis=(0, 1)))


if __name__ == "__main__":
    main()
