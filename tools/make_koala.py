#!/usr/bin/env python3
"""deFEEST "Friet met Desire" X2026 — KoalaPainter image.

Composition (ADHD pick): SPLIT-DEPTH TWO-POINT PERSPECTIVE counter. A big
foreground patatzak (messy fries + mayo) anchored bottom-left and clipped by
the frame; a greasy steel counter recedes diagonally to a neon 'FRIET MET
DESIRE' sign at the upper-right power point; frikandel speciaal (curry+uitjes)
and kaassouffle sit at staggered depths (bigger near, smaller far). Ordered
(Bayer) dithering for gradients/glow. Per-cell palette is zoned to respect
the C64 4-colours-per-8x8-cell limit; clash_lint() reports violations.

Multicolor bitmap: 160x200 (px = 2 hires wide), 40x25 cells of 4x8 mc-px.
2 bits/px: 00=bg, 01=screen-hi, 10=screen-lo, 11=colour-RAM.
"""
import os, numpy as np, random, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, 'out'); PLAYER = os.path.join(BASE, 'src', 'player')
os.makedirs(OUT, exist_ok=True)
W, H, BG = 160, 200, 0
BLACK, WHITE, RED, CYAN, PURPLE, GREEN, BLUE, YELLOW = 0,1,2,3,4,5,6,7
ORANGE, BROWN, LRED, DGREY, GREY, LGREEN, LBLUE, LGREY = 8,9,10,11,12,13,14,15
img = np.full((H, W), BG, dtype=np.uint8)
BAYER = np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]], float)/16.0

def rect(x0,y0,x1,y1,c): img[max(0,y0):min(H,y1), max(0,x0):min(W,x1)] = c
def shade(x0,y0,x1,y1,cl,cd,axis='y',invert=False,mask=None):
    for y in range(max(0,y0),min(H,y1)):
        for x in range(max(0,x0),min(W,x1)):
            if mask and not mask(x,y): continue
            t=(y-y0)/max(1,y1-y0) if axis=='y' else (x-x0)/max(1,x1-x0)
            if invert: t=1-t
            img[y,x]=cd if t>BAYER[y&3,x&3] else cl
def dith(x0,y0,x1,y1,c1,c2,mask=None):
    for y in range(max(0,y0),min(H,y1)):
        for x in range(max(0,x0),min(W,x1)):
            if mask and not mask(x,y): continue
            img[y,x]=c1 if (x^y)&1==0 else c2
def fill_mask(x0,y0,x1,y1,c,mask):
    for y in range(max(0,y0),min(H,y1)):
        for x in range(max(0,x0),min(W,x1)):
            if mask(x,y): img[y,x]=c

def _tmask(s,w,h,pt):
    try:
        r=subprocess.run(['magick','-size',f'{w}x{h}','xc:black','-gravity','center',
            '-pointsize',str(pt),'-fill','white','-annotate','+0+0',s,'-depth','8',
            '-compress','none','pgm:-'],capture_output=True)
        t=r.stdout.split()
        if len(t)<4 or t[0]!=b'P2': return None
        ww,hh=int(t[1]),int(t[2])
        return (np.array([int(v) for v in t[4:4+ww*hh]],np.uint8).reshape(hh,ww))>128
    except Exception: return None
def stamp(s,x0,y0,w,h,pt,color,shadow=None):
    m=_tmask(s,w,h,pt)
    if m is None: print(f"  (text '{s}' skipped)"); return
    hh,ww=m.shape
    if shadow is not None:
        for dy in range(hh):
            for dx in range(ww):
                if m[dy,dx] and 0<=y0+dy+1<H and 0<=x0+dx+1<W: img[y0+dy+1,x0+dx+1]=shadow
    for dy in range(hh):
        for dx in range(ww):
            if m[dy,dx] and 0<=y0+dy<H and 0<=x0+dx<W: img[y0+dy,x0+dx]=color

HORIZON, VP_X = 74, 150        # right-ish vanishing point on the horizon

# ---- sky: night gradient, glow at the horizon --------------------------
shade(0, 0, W, HORIZON, BLUE, BLACK, axis='y', invert=True)   # dark top -> blue glow low
dith(0, HORIZON-5, W, HORIZON, LBLUE, BLUE)                   # horizon haze

# ---- counter: steel tiles receding (perspective) to VP_X ---------------
for y in range(HORIZON, H):
    d = (y - HORIZON) + 6
    rowi = int(560 / d)
    for x in range(W):
        u = (x - VP_X) * 42 // d                  # columns fan from the VP
        img[y, x] = GREY if ((u + rowi) & 1) == 0 else DGREY
rect(0, HORIZON, W, HORIZON+2, LGREY)             # bright counter lip
shade(0, HORIZON+2, W, H, GREY, DGREY, axis='y', invert=True)  # darken to the front (subtle)
# redraw tiles faintly on top of the darken? keep simple: tiles already set; lip on top
rect(0, HORIZON, W, HORIZON+2, LGREY)

# ---- NEON sign: 'FRIET MET DESIRE' upper-right power point --------------
rect(86, 4, 158, 50, BLACK)                       # sign backing
rect(86, 4, 158, 6, PURPLE); rect(86, 48, 158, 50, PURPLE)   # frame
# glow halo (dither cyan/blue) then the glyph core in white
dith(88, 8, 156, 46, BLUE, BLACK)
stamp("FRIET MET", 88, 9, 68, 15, 14, CYAN, shadow=BLUE)
stamp("DESIRE",    88, 25, 68, 18, 17, WHITE, shadow=CYAN)
# neon reflection smeared down the steel counter under the sign
for x in range(88, 156, 2):
    for y in range(HORIZON, HORIZON+22):
        if ((x>>1) ^ (y)) & 1 and (y-HORIZON) < BAYER[y&3, x&3]*40:
            img[y, x] = CYAN if (y-HORIZON) < 8 else BLUE
# group tag, top-left of the night sky
stamp("deFEEST  X2026", 4, 5, 78, 8, 8, WHITE, shadow=BLUE)

# ---- kaassouffle: FAR (small), back on the counter, mid-right ----------
def ks_wedge(cx, top, bot, hw, mask_out=None):
    span=bot-top
    for y in range(top,bot):
        w=int(hw*(y-top)/span)
        rect(cx-w,y,cx+w,y+1, YELLOW)
ks_wedge(112, 92, 116, 16)                        # breaded crust (far/small)
shade(96,92,128,116, ORANGE, BROWN, axis='y',
      mask=lambda x,y: 112-int(16*(y-92)/24)+2 <= x < 112+int(16*(y-92)/24)-2 and y>=96)
rect(96,116,128,118, BROWN)

# ---- frikandel speciaal: MID depth, centre-front of the counter --------
shade(40, 150, 130, 168, ORANGE, BROWN, axis='y')         # sausage, sheen on top
rect(38,154,42,164,BROWN); rect(128,154,132,164,BROWN)    # rounded ends
dith(44, 148, 126, 154, YELLOW, ORANGE)                   # curry band
for ox in range(48, 124, 9):                              # uitjes (onions)
    rect(ox,149,ox+3,152,WHITE)

# ---- patatzak: BIG foreground, bottom-LEFT, clipped by the frame -------
BCX = 34
def bag_mask(x,y):
    if not (96 <= y < 205): return False
    t=(y-96)/100.0; hw=int(50*(1-0.55*t))
    return BCX-hw <= x < BCX+hw
shade(-20, 96, BCX+52, 205, LRED, RED, axis='x', mask=bag_mask)   # round shading
for sx in (BCX-26, BCX, BCX+26):                                  # white pleats, clipped
    fill_mask(sx-1, 96, sx+2, 205, WHITE, bag_mask)
rect(-20, 90, BCX+52, 98, WHITE)                                  # rim
rect(-20, 98, BCX+52, 100, LGREY)

# messy fries clump in the bag mouth (irregular, some crispy)
_rng=random.Random(7)
def fry(x,w,top,bot,lean,crispy):
    for y in range(top,bot):
        t=(y-top)/max(1,bot-top); xo=int(round(lean*(1-t))); c=YELLOW
        if crispy and y<top+(bot-top)//3: c=ORANGE
        elif y>bot-16 and ((x+xo)^y)&1: c=ORANGE
        rect(x+xo,y,x+xo+w,y+1,c)
x=2
while x < 70:
    w=_rng.choice([5,6,7,8]); top=_rng.randint(50,82)
    fry(x,w,top,100,_rng.randint(-3,3),crispy=(_rng.random()<0.2)); x+=w+_rng.randint(-1,4)
# MAYO: blob + drizzle over the fries
rect(18,44,54,58,WHITE); rect(24,38,48,46,WHITE)
for i,fx in enumerate(range(6,66,6)):
    yy=60+(4 if i&1 else 0); rect(fx,yy,fx+5,yy+3,WHITE); rect(fx,yy+8,fx+5,yy+10,LGREY)

# ====================================================================
def clash_lint():
    bad=0
    for cy in range(25):
        for cx in range(40):
            n=len(np.unique(img[cy*8:cy*8+8, cx*4:cx*4+4]))
            if n>4: bad+=1
    print(f"  clash_lint: {bad} cells exceed 4 colours (packer will reduce these)")
clash_lint()

bitmap=bytearray(8000); screen=bytearray(1000); colram=bytearray(1000)
for cy in range(25):
    for cx in range(40):
        block=img[cy*8:cy*8+8, cx*4:cx*4+4]
        vals,counts=np.unique(block,return_counts=True)
        nb=sorted([(int(v),int(n)) for v,n in zip(vals,counts) if v!=BG], key=lambda z:-z[1])
        chosen=[v for v,_ in nb[:3]]; code={BG:0}
        for i,c in enumerate(chosen): code[c]=i+1
        fb=chosen[0] if chosen else BG
        screen[cy*40+cx]=((chosen[0] if len(chosen)>0 else 0)<<4)|(chosen[1] if len(chosen)>1 else 0)
        colram[cy*40+cx]=(chosen[2] if len(chosen)>2 else 0)
        for r in range(8):
            byte=0
            for p in range(4): byte=(byte<<2)|code.get(int(block[r,p]),code.get(fb,0))
            bitmap[cy*320+cx*8+r]=byte
koala=bytes([0,0x60])+bytes(bitmap)+bytes(screen)+bytes(colram)+bytes([BG])
assert len(koala)==10003
open(os.path.join(OUT,'friet.koa'),'wb').write(koala)
for nm,dt in [('koala_bitmap.bin',bitmap),('koala_screen.bin',screen),('koala_color.bin',colram)]:
    open(os.path.join(PLAYER,nm),'wb').write(bytes(dt))
open(os.path.join(PLAYER,'koala_bg.bin'),'wb').write(bytes([BG]))
print(f"wrote out/friet.koa ({len(koala)} bytes) + player bins")

PEPTO=[(0,0,0),(255,255,255),(136,57,50),(103,182,189),(139,63,150),(85,160,73),
 (64,49,141),(191,206,114),(139,84,41),(87,66,0),(184,105,98),(80,80,80),(120,120,120),
 (148,224,137),(120,105,196),(159,159,159)]
rgb=np.zeros((H,W*2,3),np.uint8)
for idx,col in enumerate(PEPTO):
    m=img==idx; rgb[:,0::2][m]=col; rgb[:,1::2][m]=col
open(os.path.join(OUT,'friet_koala_preview.ppm'),'wb').write(
    f"P6\n{W*2} {H}\n255\n".encode()+rgb.tobytes())
print("wrote out/friet_koala_preview.ppm")
