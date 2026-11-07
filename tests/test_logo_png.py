#!/usr/bin/env python3
"""Check that /images/logo.png is a real PNG and that metadata points at it.

The file is the existing header wordmark (iLoveTurtle, #1d4a1d), not a new drawing.
"""

import pathlib
import struct
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGO = ROOT / "images" / "logo.png"
LOGO_URL = "https://www.iloveturtle.com/images/logo.png"
BRAND = (29, 74, 29)


def fail(msg):
    print("FAIL:", msg)
    return 1


def read_png(path):
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError(f"{path} is not a PNG (got {data[:12]!r})")
    if data[12:16] != b"IHDR":
        raise AssertionError("missing IHDR")
    width, height, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
    if bit_depth != 8 or color_type not in (2, 6):
        raise AssertionError(f"unexpected PNG type bit={bit_depth} color={color_type}")
    channels = 3 if color_type == 2 else 4
    idat = b""
    pos = 8
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        chunk = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        if chunk == b"IDAT":
            idat += payload
        if chunk == b"IEND":
            break
        pos += 12 + length
    raw = zlib.decompress(idat)
    stride = width * channels
    rows = []
    i = 0
    prev = bytearray(stride)
    for _ in range(height):
        filt = raw[i]
        i += 1
        row = bytearray(raw[i:i + stride])
        i += stride
        if filt == 0:
            pass
        elif filt == 1:  # Sub
            for x in range(stride):
                left = row[x - channels] if x >= channels else 0
                row[x] = (row[x] + left) & 255
        elif filt == 2:  # Up
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 255
        elif filt == 3:  # Average
            for x in range(stride):
                left = row[x - channels] if x >= channels else 0
                row[x] = (row[x] + ((left + prev[x]) // 2)) & 255
        elif filt == 4:  # Paeth
            for x in range(stride):
                a = row[x - channels] if x >= channels else 0
                b = prev[x]
                c = prev[x - channels] if x >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
                row[x] = (row[x] + pr) & 255
        else:
            raise AssertionError(f"unsupported PNG filter {filt}")
        rows.append(bytes(row))
        prev = row
    return width, height, channels, rows


def nearest_brand(rows, channels):
    best = 255 * 3
    for row in rows:
        for x in range(0, len(row), channels):
            r, g, b = row[x], row[x + 1], row[x + 2]
            if r > 245 and g > 245 and b > 245:
                continue
            dist = abs(r - BRAND[0]) + abs(g - BRAND[1]) + abs(b - BRAND[2])
            if dist < best:
                best = dist
    return best


def main():
    errors = 0
    if not LOGO.is_file():
        return fail(f"missing {LOGO}")
    try:
        width, height, channels, rows = read_png(LOGO)
    except Exception as exc:
        return fail(str(exc))
    print(f"logo.png PNG {width}x{height} channels={channels} bytes={LOGO.stat().st_size}")
    if width < 200 or height < 112:
        errors += fail(f"logo is too small for metadata crawlers: {width}x{height}")
    if nearest_brand(rows, channels) > 12:
        errors += fail("no pixel close to the header wordmark color rgb(29, 74, 29)")
    else:
        print("brand color rgb(29, 74, 29) is present")

    refs = []
    for html in ROOT.rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        if "logo.png" not in text:
            continue
        count = text.count(LOGO_URL)
        other = text.count("logo.png") - count
        refs.append((html.relative_to(ROOT).as_posix(), count, other))
        if other:
            errors += fail(f"{html} has a logo.png reference that is not {LOGO_URL}")
    if not refs:
        errors += fail("no HTML references logo.png")
    print(f"html files referencing {LOGO_URL}: {len(refs)}")
    if errors:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
