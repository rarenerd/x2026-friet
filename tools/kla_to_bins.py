#!/usr/bin/env python3
"""Split a KoalaPainter (.kla/.koa, 10003 bytes, load $6000) into the four
binaries the koala player .asm imports, and copy it to out/friet.koa.

Usage: kla_to_bins.py [path-to.kla]   (default: FrietFromDesireMiep.kla)
"""
import os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'FrietFromDesireMiep.kla')
PLAYER = os.path.join(BASE, 'src', 'player')
OUT = os.path.join(BASE, 'out')

d = open(SRC, 'rb').read()
assert len(d) == 10003, f"expected 10003-byte Koala, got {len(d)}"
load = d[0] | (d[1] << 8)
assert load == 0x6000, f"expected load $6000, got ${load:04X}"

bitmap = d[2:8002]          # 8000  $6000-$7F3F
screen = d[8002:9002]       # 1000  screen-RAM (%01 hi, %10 lo)
colram = d[9002:10002]      # 1000  colour-RAM (%11 lo)
bg     = d[10002]           # 1     background ($D021)

os.makedirs(OUT, exist_ok=True)
open(os.path.join(PLAYER, 'koala_bitmap.bin'), 'wb').write(bitmap)
open(os.path.join(PLAYER, 'koala_screen.bin'), 'wb').write(screen)
open(os.path.join(PLAYER, 'koala_color.bin'),  'wb').write(colram)
open(os.path.join(PLAYER, 'koala_bg.bin'),     'wb').write(bytes([bg]))
open(os.path.join(OUT, 'friet.koa'), 'wb').write(d)
print(f"{os.path.basename(SRC)} -> player bins + out/friet.koa (bg={bg})")
