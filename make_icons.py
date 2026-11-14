"""Draw the home-screen icon (a simple globe) as PNG with only the standard library."""
import math, struct, zlib, pathlib

BG = (180, 68, 31)
FG = (255, 255, 255)


def png(path, w, h, rows):
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    pathlib.Path(path).write_bytes(data)


def ink(x, y, s):
    """Coverage 0..1 of the globe strokes at point (x, y) in a unit square."""
    cx = cy = 0.5
    r = 0.30
    t = 0.028 * (1 if s > 200 else 1.25)
    dx, dy = x - cx, y - cy
    d = math.hypot(dx, dy)
    if abs(d - r) < t:
        return 1
    if d > r:
        return 0
    if abs(dy) < t * 0.8:  # equator
        return 1
    for k in (0.42, 1.0):  # meridians as ellipses
        rx = r * k
        e = math.hypot(dx / rx, dy / r)
        if abs(e - 1) * rx < t * 0.8:
            return 1
    if abs(dx) < t * 0.8:
        return 1
    for lat in (-0.5, 0.5):  # parallels
        yy = r * lat
        half = math.sqrt(max(r * r - yy * yy, 0))
        if abs(dy - yy) < t * 0.7 and abs(dx) < half:
            return 1
    return 0


def make(size, path):
    ss = 3
    rows = []
    for py in range(size):
        row = []
        for px in range(size):
            c = 0
            for sy in range(ss):
                for sx in range(ss):
                    c += ink((px + (sx + .5) / ss) / size, (py + (sy + .5) / ss) / size, size)
            a = c / (ss * ss)
            row += [round(BG[i] * (1 - a) + FG[i] * a) for i in range(3)]
        rows.append(row)
    png(path, size, size, rows)


here = pathlib.Path(__file__).parent
make(180, here / "icon-180.png")
make(512, here / "icon-512.png")
print("icons written")
