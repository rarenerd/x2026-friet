#!/usr/bin/env python3
"""Mix the hand-painted dragon (FrietFromDesireMiep.kla) into a nicer
composition: dragon hero + frikandel speciaal in his mouth, on a dithered
blue glow-vignette background (instead of flat black). Repacks to a Koala
+ the player import bins. The swirl ornaments become bouncing sprites
(see src/player/sprite_orn.bin / friet_koala.asm).
"""
import os, numpy as np, math

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT,PLAYER=os.path.join(BASE,'out'),os.path.join(BASE,'src','player')
SRC=os.path.join(BASE,'FrietFromDesireMiep.kla')
W,H=160,200
WHITE,RED,CYAN,PURPLE,BLUE,YELLOW,ORANGE,BROWN,LRED,DGREY,GREY,LBLUE=1,2,3,4,6,7,8,9,10,11,12,14
BAYER=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],float)/16.0

# ---- decode the dragon -------------------------------------------------
d=open(SRC,'rb').read(); bm=d[2:8002]; scr=d[8002:9002]; col=d[9002:10002]; BG=d[10002]
img=np.zeros((H,W),np.uint8)
for cy in range(25):
    for cx in range(40):
        s=scr[cy*40+cx]; c=col[cy*40+cx]; pal=[BG,s>>4,s&0xF,c&0xF]
        for r in range(8):
            byte=bm[cy*320+cx*8+r]
            for p in range(4): img[cy*8+r,cx*4+p]=pal[(byte>>(6-2*p))&3]

# ---- nicer background: blue glow-vignette behind the dragon ------------
# Only repaint cells that are entirely "empty" (all index 0 = black), so the
# dragon stays untouched and no cell gains a 5th colour.
GCX,GCY=84,86            # glow centre (roughly the dragon's heart)
for cy in range(25):
    for cx in range(40):
        blk=img[cy*8:cy*8+8, cx*4:cx*4+4]
        if not np.all(blk==0):       # not a pure-black background cell -> skip
            continue
        for r in range(8):
            for p in range(4):
                x=cx*4+p; y=cy*8+r
                dist=math.hypot((x-GCX)/90.0,(y-GCY)/70.0)
                glow=max(0.0,1.0-dist)            # 1 at centre -> 0 at edge
                # two-stop dither: near=CYAN over BLUE, mid=BLUE over PURPLE, far=PURPLE/BLACK
                if glow>0.55:   cl,cd=CYAN,BLUE
                elif glow>0.28: cl,cd=BLUE,PURPLE
                else:           cl,cd=PURPLE,0
                lvl=(glow-0.0)
                img[y,x]= cl if (lvl*1.6)>BAYER[y&3,x&3] else cd

# ---- frikandel speciaal into the dragon's mouth (rows ~96-100) ---------
def disc(cx,cy,r,c):
    for y in range(max(0,cy-r),min(H,cy+r+1)):
        for x in range(max(0,cx-r),min(W,cx+r+1)):
            if (x-cx)**2+(y-cy)**2<=r*r: img[y,x]=c
def thick(x0,y0,x1,y1,r,c,t0=0.0,t1=1.0):
    n=int(math.hypot(x1-x0,y1-y0))+1
    for i in range(n+1):
        t=i/n
        if t0<=t<=t1: disc(int(round(x0+(x1-x0)*t)),int(round(y0+(y1-y0)*t)),r,c)
MX,MY,OX,OY=79,99,8,106
thick(OX,OY,MX,MY,5,BROWN); thick(OX,OY,MX,MY,5,ORANGE,0,0.10)
dx,dy=MX-OX,MY-OY; L=math.hypot(dx,dy); nx,ny=-dy/L,dx/L
for i in range(0,int(L)-9,2):
    t=i/L; bx,by=OX+dx*t,OY+dy*t
    px,py=int(bx-nx*3),int(by-ny*3)
    if 0<=px<W and 0<=py<H: img[py,px]=YELLOW if (i//2)%2 else ORANGE
    if i%8==0:
        ox,oy=int(bx-nx*2),int(by-ny*2)
        if 0<=ox<W and 0<=oy<H: img[oy,ox]=WHITE
disc(60,94,4,WHITE); disc(55,96,3,WHITE)     # mayo

# ====================================================================
def clash(): return sum(1 for cy in range(25) for cx in range(40)
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
