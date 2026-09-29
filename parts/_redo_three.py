"""Rebuild lineman torso, alt helmet, and open-hand forearm from existing art."""
from pathlib import Path

import numpy as np
from PIL import Image

PARTS = Path(__file__).resolve().parent
MAGENTA = np.array([255, 0, 255], dtype=np.uint8)
MASK = np.array([0x3A, 0x3F, 0x45], dtype=np.uint8)
MASK_DK = np.array([0x2A, 0x2E, 0x33], dtype=np.uint8)
MASK_HI = np.array([0x4A, 0x50, 0x58], dtype=np.uint8)
LINE = np.array([0x0D, 0x0F, 0x12], dtype=np.uint8)
GOLD = np.array([175, 141, 77], dtype=np.float64)


def rgba_to_rgb(im, a_cut=36):
    a = np.array(im.convert("RGBA"), dtype=np.uint8)
    out = np.broadcast_to(MAGENTA, (a.shape[0], a.shape[1], 3)).copy()
    m = a[:, :, 3] >= a_cut
    out[m] = a[:, :, :3][m]
    return out, a


def is_navy(p):
    r, g, b = int(p[0]), int(p[1]), int(p[2])
    return b > r + 18 and b > g + 8 and not (r == 255 and b == 255)


def is_magenta(p):
    return p[0] > 240 and p[2] > 240 and p[1] < 20


def sample_rgba(src, x, y):
    """Bilinear sample RGBA array. Outside -> transparent magenta."""
    h, w = src.shape[:2]
    if x < 0 or y < 0 or x > w - 1 or y > h - 1:
        return np.array([255, 0, 255, 0], dtype=np.float64)
    x0 = int(np.floor(x))
    y0 = int(np.floor(y))
    x1 = min(x0 + 1, w - 1)
    y1 = min(y0 + 1, h - 1)
    tx, ty = x - x0, y - y0
    c00 = src[y0, x0].astype(np.float64)
    c10 = src[y0, x1].astype(np.float64)
    c01 = src[y1, x0].astype(np.float64)
    c11 = src[y1, x1].astype(np.float64)
    return (
        c00 * (1 - tx) * (1 - ty)
        + c10 * tx * (1 - ty)
        + c01 * (1 - tx) * ty
        + c11 * tx * ty
    )


def row_span(alpha_row, cut=36):
    xs = np.where(alpha_row >= cut)[0]
    if len(xs) == 0:
        return None
    return int(xs[0]), int(xs[-1])


def make_torso():
    im = Image.open(PARTS / "football-torso.png")
    src = np.array(im.convert("RGBA"), dtype=np.uint8)
    sh, sw = src.shape[:2]
    W, H = 91, 160
    dst = np.broadcast_to(MAGENTA, (H, W, 3)).copy()

    # Precompute source row spans
    spans = [row_span(src[y, :, 3]) for y in range(sh)]

    def sy_of(dy):
        # Lift the wide pad shelf to the top (squarer, higher pads).
        if dy <= 26:
            return 16.0 + dy * (38.0 - 16.0) / 26.0
        return 38.0 + (dy - 26) * (159.0 - 38.0) / (159.0 - 26.0)

    def expand(dy, slo, shi):
        src_c = (slo + shi) / 2.0
        src_w = shi - slo + 1
        t = dy / 159.0
        if dy <= 30:
            fac = 1.18
        elif dy <= 90:
            fac = 1.14
        else:
            fac = 1.16 + 0.70 * ((dy - 90) / 69.0) ** 1.15
        new_w = min(W - 1, src_w * fac)
        lo = src_c - new_w / 2.0
        hi = src_c + new_w / 2.0
        if lo < 0:
            hi -= lo
            lo = 0
        if hi > W - 1:
            lo -= hi - (W - 1)
            hi = W - 1
        return max(0.0, lo), min(W - 1.0, hi)

    for dy in range(H):
        sy = sy_of(dy)
        sy0 = int(np.clip(round(sy), 0, sh - 1))
        sp = spans[sy0]
        if sp is None:
            continue
        slo, shi = sp
        dlo, dhi = expand(dy, slo, shi)
        if dhi <= dlo:
            continue
        for dx in range(W):
            if dx < dlo - 0.5 or dx > dhi + 0.5:
                continue
            u = (dx - dlo) / (dhi - dlo)
            sx = slo + u * (shi - slo)
            c = sample_rgba(src, sx, sy)
            if c[3] < 36:
                continue
            dst[dy, dx] = np.clip(c[:3], 0, 255).astype(np.uint8)

    # Gold sleeve stripe on the deltoid, luminance-matched to the jersey shading.
    for y in range(38, 50):
        for x in range(66, 91):
            p = dst[y, x]
            if is_magenta(p) or not is_navy(p):
                continue
            # keep an organic right edge — skip the last anti-aliased rim
            if x > 86 and is_magenta(dst[y, min(W - 1, x + 1)]):
                continue
            lum = 0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2]
            g = np.clip(GOLD * (lum / 52.0), 0, 255).astype(np.uint8)
            dst[y, x] = g

    Image.fromarray(dst, "RGB").save(PARTS / "football-torso-lineman.png")
    return dst


def make_helmet():
    im = Image.open(PARTS / "football-helmet.png")
    dst, src = rgba_to_rgb(im)
    H, W = dst.shape[:2]

    def navy_at(x, y):
        if x < 0 or y < 0 or x >= W or y >= H:
            return False
        return is_navy(dst[y, x])

    def gold_at(x, y):
        p = dst[y, x]
        return int(p[0]) > 180 and int(p[1]) > 140 and int(p[2]) < 90

    # Fill genuine interior holes in the cage with visor grey so new bars
    # have something to sit on and the cage stays one piece.
    visor = np.array([78, 81, 88], dtype=np.uint8)
    visor_dk = np.array([62, 65, 72], dtype=np.uint8)
    for y in range(56, 140):
        xs = [x for x in range(80, W) if not is_magenta(dst[y, x]) and not navy_at(x, y)]
        if len(xs) < 8:
            continue
        left, right = xs[0], xs[-1]
        for x in range(left, right + 1):
            if is_magenta(dst[y, x]) and not navy_at(x, y) and not gold_at(x, y):
                dst[y, x] = visor if (y + x) % 5 else visor_dk

    def paint_bar(y0, y1, curve=0.07):
        for y in range(y0, y1 + 1):
            x_att = None
            x_start = None
            for x in range(70, 125):
                if navy_at(x, y):
                    x_att = x
                elif x_att is not None and not is_magenta(dst[y, x]):
                    x_start = x
                    break
            if x_start is None:
                continue
            x_end = W - 1
            for x in range(W - 1, 120, -1):
                if not is_magenta(dst[y, x]) or navy_at(x, y):
                    x_end = x
                    break
            t = (y - y0) / max(1, y1 - y0)
            col = MASK_HI if t < 0.28 else (MASK if t < 0.72 else MASK_DK)
            for x in range(x_start, x_end + 1):
                # slight downward curve toward the nose, matching the brow bar
                yb = y + int(curve * (x - x_start))
                if yb < 0 or yb >= H:
                    continue
                if gold_at(x, yb) or navy_at(x, yb):
                    continue
                dst[yb, x] = col

    # Extra horizontal cage bars across the visor, plus one in the chin gap.
    paint_bar(68, 73)
    paint_bar(80, 85)
    paint_bar(92, 97)
    paint_bar(118, 124)

    # Extra vertical bar between the two existing posts, connected top-to-bottom.
    for y in range(62, 136):
        for x in range(128, 134):
            if gold_at(x, y) or navy_at(x, y):
                continue
            if is_magenta(dst[y, x]):
                continue
            t = (x - 128) / 5.0
            dst[y, x] = MASK_HI if t < 0.25 else (MASK_DK if t > 0.75 else MASK)

    Image.fromarray(dst, "RGB").save(PARTS / "football-helmet-alt.png")
    return dst


def make_forearm():
    im = Image.open(PARTS / "football-forearm.png")
    dst, src_rgba = rgba_to_rgb(im)
    H, W = dst.shape[:2]
    src = np.array(im.convert("RGBA"), dtype=np.uint8)

    # Glove colours from the existing fist, for sampling.
    glove_pts = []
    for y in range(H):
        for x in range(104, W):
            r, g, b, a = src[y, x]
            if a >= 36 and r < 100:
                glove_pts.append((x, y, r, g, b))
    glove_pts = np.array(glove_pts)

    def glove_color(x, y):
        # nearest existing glove pixel, with a slight darkening toward the tip
        d = (glove_pts[:, 0] - min(x, 150)) ** 2 + (glove_pts[:, 1] - y) ** 2
        i = int(np.argmin(d))
        col = glove_pts[i, 2:5].astype(np.float64)
        tip = max(0.0, (x - 124) / 40.0)
        col = col * (1.0 - 0.22 * tip)
        return np.clip(col, 0, 255).astype(np.uint8)

    def in_capsule(x, y, x0, x1, yc, r0, r1):
        if x < x0 or x > x1:
            return False
        u = (x - x0) / max(1.0, x1 - x0)
        r = r0 * (1 - u) + r1 * u
        # rounded tip: shrink radius near the end
        if u > 0.86:
            r *= 1.0 - (u - 0.86) / 0.18 * 0.55
        return abs(y - yc) <= r

    # Clear the old closed fist to the right of the palm, keep forearm + palm + thumb.
    palm_cut = 126
    for y in range(H):
        for x in range(palm_cut, W):
            # keep the high thumb bump from the original (y < 7, x < 141)
            if y <= 6 and x <= 140 and not is_magenta(dst[y, x]):
                continue
            dst[y, x] = MAGENTA

    # Fill a solid palm so finger gaps stay glove, not magenta holes.
    for y in range(7, 27):
        for x in range(104, 136):
            if is_magenta(dst[y, x]):
                dst[y, x] = glove_color(x, y)

    # Four fingers, overlapping the palm so they stay attached. Spread, rounded tips.
    fingers = [
        (120, 159, 3.8, 3.6, 2.0),
        (123, 159, 10.2, 3.4, 1.9),
        (123, 159, 16.8, 3.4, 1.9),
        (120, 159, 24.0, 3.6, 2.0),
    ]
    for x0, x1, yc, r0, r1 in fingers:
        for y in range(H):
            for x in range(x0, x1 + 1):
                if in_capsule(x, y, x0, x1, yc, r0, r1):
                    dst[y, x] = glove_color(x, y)

    # Fill webbing between fingers with glove (dark lines go on top of this).
    for y in range(6, 26):
        for x in range(126, 150):
            if is_magenta(dst[y, x]):
                # only fill if a finger is above and below (webbing)
                up = any(not is_magenta(dst[yy, x]) for yy in range(max(0, y - 4), y))
                dn = any(not is_magenta(dst[yy, x]) for yy in range(y + 1, min(H, y + 5)))
                if up and dn:
                    dst[y, x] = glove_color(x, y)

    # Thin dark separators between fingers — drawn ON the glove, not as holes.
    for y_line in (7, 13, 20):
        for x in range(128, 156):
            if is_magenta(dst[y_line, x]):
                continue
            dst[y_line, x] = LINE
            if y_line + 1 < H and not is_magenta(dst[y_line + 1, x]):
                # 1px only; slight neighbour darken for softness
                pass

    Image.fromarray(dst, "RGB").save(PARTS / "football-forearm-hand.png")
    return dst


def report(name, arr):
    h, w = arr.shape[:2]
    mag = (arr[:, 0] != MAGENTA).any() or (arr[0] != MAGENTA).any()
    L = (arr[:, 0] != MAGENTA).any(axis=1).any() if False else np.any(np.any(arr[:, 0] != MAGENTA, axis=1))
    # simpler:
    def edge(xs):
        return bool(np.any(np.any(xs != MAGENTA, axis=-1)))

    print(
        name,
        w,
        h,
        "LRTB",
        edge(arr[:, 0]),
        edge(arr[:, -1]),
        edge(arr[0]),
        edge(arr[-1]),
    )


if __name__ == "__main__":
    t = make_torso()
    h = make_helmet()
    f = make_forearm()
    report("torso", t)
    report("helmet", h)
    report("forearm", f)
