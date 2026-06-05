#!/usr/bin/env python3
"""Composite snacks onto the hand-painted Miep koala: Miep eating a frikandel
speciaal (frikandel into the mouth) + a few extras. Loads FrietFromDesireMiep.kla
as the base index image, draws the snack(s) over it, repacks to a KoalaPainter
image (out/friet.koa) + the player import bins, and writes a PNG preview.
"""
import os, numpy as np, math

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, PLAYER = os.path.join(BASE,'out'), os.path.join(BASE,'src','player')
SRC = os.path.join(BASE, 'FrietFromDesireMiep.kla')
W,H = 160,200
WHITE,RED,YELLOW,ORANGE,BROWN,LRED,WHITEc = 1,2,7,8,9,10,1

# ---- decode the .kla into a 160x200 index image (the base) -------------
d=open(SRC,'rb').read(); bm=d[2:8002]; scr=d[8002:9002]; col=d[9002:10002]; BG=d[10002]
img=np.zeros((H,W),np.uint8)
for cy in range(25):
    for cx in range(40):
        s=scr[cy*40+cx]; c=col[cy*40+cx]; pal=[BG,s>>4,s&0xF,c&0xF]
        for r in range(8):
            byte=bm[cy*320+cx*8+r]
            for p in range(4): img[cy*8+r,cx*4+p]=pal[(byte>>(6-2*p))&3]

def disc(cx,cy,r,c):
    for y in range(max(0,cy-r),min(H,cy+r+1)):
        for x in range(max(0,cx-r),min(W,cx+r+1)):
            if (x-cx)**2+(y-cy)**2<=r*r: img[y,x]=c
def thick_line(x0,y0,x1,y1,r,c,t_lo=0.0,t_hi=1.0):
    n=int(math.hypot(x1-x0,y1-y0))+1
    for i in range(n+1):
        t=i/n
        if t<t_lo or t>t_hi: continue
        disc(int(round(x0+(x1-x0)*t)), int(round(y0+(y1-y0)*t)), r, c)
def rect(x0,y0,x1,y1,c): img[max(0,y0):min(H,y1), max(0,x0):min(W,x1)] = c
def dith(x0,y0,x1,y1,c1,c2):
    for y in range(max(0,y0),min(H,y1)):
        for x in range(max(0,x0),min(W,x1)): img[y,x]=c1 if (x^y)&1 else c2

# ---- frikandel speciaal going INTO Miep's mouth -----------------------
# Open mouth is rows ~96-100, x71-87 -> centre (79,99). (y82 was the nostril.)
MX,MY = 79,99          # mouth centre — frikandel tip goes in here
OX,OY = 8,106          # outer end (sticks out to the lower-left)
thick_line(OX,OY, MX,MY, 5, BROWN)                 # sausage body
thick_line(OX,OY, MX,MY, 5, ORANGE, t_lo=0.0, t_hi=0.10)  # rounded cut end
# curry + uitjes on the TOP side of the bar (-normal)
dx,dy = MX-OX, MY-OY; L=math.hypot(dx,dy); nx,ny = -dy/L, dx/L
for i in range(0, int(L)-9, 2):                    # stop short so it enters the mouth
    t=i/L; bx=OX+dx*t; by=OY+dy*t
    px,py=int(bx-nx*3), int(by-ny*3)               # TOP side (curry)
    if 0<=px<W and 0<=py<H: img[py,px]= YELLOW if (i//2)%2 else ORANGE
    if i%8==0:                                      # uitjes (onion specks)
        ox,oy=int(bx-nx*2),int(by-ny*2)
        if 0<=ox<W and 0<=oy<H: img[oy,ox]=WHITE

# ---- a few frietjes also poking out of the mouth ----------------------
for (fx0,fy0,fx1,fy1) in [(78,96,62,76),(82,96,74,72),(80,97,86,74)]:
    thick_line(fx0,fy0,fx1,fy1,1,YELLOW)
    thick_line(fx0,fy0,fx1,fy1,1,ORANGE,t_lo=0.0,t_hi=0.25)   # fried base

# ---- MAYO blob in the mouth corner, on top of the frikandel -----------
disc(60,94,4,WHITE); disc(55,96,3,WHITE)

# ---- kaassouffle: RECTANGULAR breaded block, bottom-left corner -------
rect(10,156,48,182, YELLOW)                        # breaded crust (outer)
dith(13,159,45,179, ORANGE, BROWN)                 # golden breaded body
rect(10,156,48,159, YELLOW); rect(10,179,48,182, YELLOW)   # top/bottom crust
rect(10,156,13,182, YELLOW); rect(45,156,48,182, YELLOW)   # side crust
rect(26,166,33,173, WHITE)                         # melted cheese ooze

# ====================================================================
def clash():
    return sum(1 for cy in range(25) for cx in range(40)
               if len(np.unique(img[cy*8:cy*8+8,cx*4:cx*4+4]))>4)
print(f"  clash cells: {clash()}")

bitmap=bytearray(8000); screen=bytearray(1000); colram=bytearray(1000)
for cy in range(25):
    for cx in range(40):
        block=img[cy*8:cy*8+8, cx*4:cx*4+4]
        vals,counts=np.unique(block,return_counts=True)
        nb=sorted([(int(v),int(n)) for v,n in zip(vals,counts) if v!=BG],key=lambda z:-z[1])
        chosen=[v for v,_ in nb[:3]]; code={BG:0}
        for i,c in enumerate(chosen): code[c]=i+1
        fb=chosen[0] if chosen else BG
        screen[cy*40+cx]=((chosen[0] if chosen else 0)<<4)|(chosen[1] if len(chosen)>1 else 0)
        colram[cy*40+cx]=(chosen[2] if len(chosen)>2 else 0)
        for r in range(8):
            byte=0
            for p in range(4): byte=(byte<<2)|code.get(int(block[r,p]),code.get(fb,0))
            bitmap[cy*320+cx*8+r]=byte
koala=bytes([0,0x60])+bytes(bitmap)+bytes(screen)+bytes(colram)+bytes([BG])
open(os.path.join(OUT,'friet.koa'),'wb').write(koala)
for nm,dt in [('koala_bitmap.bin',bitmap),('koala_screen.bin',screen),('koala_color.bin',colram)]:
    open(os.path.join(PLAYER,nm),'wb').write(bytes(dt))
open(os.path.join(PLAYER,'koala_bg.bin'),'wb').write(bytes([BG]))
print("wrote out/friet.koa + player bins")

PEPTO=[(0,0,0),(255,255,255),(136,57,50),(103,182,189),(139,63,150),(85,160,73),(64,49,141),
 (191,206,114),(139,84,41),(87,66,0),(184,105,98),(80,80,80),(120,120,120),(148,224,137),(120,105,196),(159,159,159)]
rgb=np.zeros((H,W*2,3),np.uint8)
for i,co in enumerate(PEPTO):
    m=img==i; rgb[:,0::2][m]=co; rgb[:,1::2][m]=co
open(os.path.join(OUT,'friet_koala_preview.ppm'),'wb').write(f"P6\n{W*2} {H}\n255\n".encode()+rgb.tobytes())
print("wrote preview")
