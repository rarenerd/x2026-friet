#!/usr/bin/env python3
"""Convert a Spritemate .spm project into raw C64 sprite data.

Each sprite -> 63 bytes (21 rows x 3 bytes), padded to 64. Hires: a pixel
is "set" when its value != 0. Output is all sprites concatenated, ready to
.import as consecutive 64-byte sprite blocks.

Usage: spm_to_sprites.py <in.spm> <out.bin> [stride]

stride>1 keeps every Nth frame (e.g. 32 frames, stride 2 -> 16 frames that
still span the full rotation) — used to fit the cube data into a 1KB hole.
"""
import json, sys, os

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mijn zuigendeKubuz.spm')
DST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'player', 'sprite_cube.bin')
STRIDE = int(sys.argv[3]) if len(sys.argv) > 3 else 1

d = json.load(open(SRC))
out = bytearray()
for s in d['sprites'][::STRIDE]:
    px = s['pixels']
    b = bytearray(64)
    for y in range(21):
        row = px[y]
        for x in range(24):
            if row[x] != 0:
                b[y*3 + x//8] |= 0x80 >> (x % 8)
    out += b
open(DST, 'wb').write(bytes(out))
print(f"{os.path.basename(SRC)} -> {DST}: {len(out)//64} frames (stride {STRIDE} "
      f"of {len(d['sprites'])}), {len(out)} bytes")
