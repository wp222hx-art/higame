#!/usr/bin/env python3
"""
SYNAPSE Sprite Generator v3.0 - High quality pixel art
Generates detailed sprites with proper pixel art techniques
"""
from PIL import Image, ImageDraw
import os, json, math, random

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'game', 'assets', 'sprites')
os.makedirs(OUT, exist_ok=True)
random.seed(42)

# ========================
# PALETTE
# ========================
def c(r,g,b,a=255): return (r,g,b,a)
CLEAR = (0,0,0,0)

# Unified warm palette
SKN  = c(255,220,180); SKN2 = c(230,190,150); SKN3 = c(200,160,120)
EYE  = c(30,25,40);    EYEW = c(255,255,255); MOUTH = c(180,100,80)
HAIR_B = c(35,30,45);  HAIR_BR = c(100,65,35); HAIR_G = c(150,150,160)

# Clothing palettes per character
CLOTH = {
  'chief':     (c(180,50,40), c(140,35,25), c(220,180,60), c(50,45,60)),  # red suit, gold trim
  'farmer':    (c(60,150,70), c(40,110,50), c(100,75,45), c(80,60,40)),   # green overalls
  'tech':      (c(50,90,170), c(35,65,130), c(240,240,250), c(45,45,55)), # blue coat
  'sales':     (c(220,130,40), c(180,100,25), c(60,55,50), c(60,55,65)), # orange jacket
  'delivery':  (c(50,170,160), c(35,130,125), c(70,70,80), c(55,55,65)), # teal uniform
  'livestream':(c(230,110,150), c(190,75,115), c(255,220,230), c(55,45,60)), # pink outfit
  'inspector': (c(235,235,245), c(195,195,205), c(50,50,60), c(50,50,55)),   # white coat
  'finance':   (c(130,65,160), c(95,40,120), c(220,200,240), c(50,45,60)),  # purple suit
}

HAIR_MAP = {
  'chief': HAIR_B, 'farmer': HAIR_BR, 'tech': HAIR_B, 'sales': HAIR_BR,
  'delivery': HAIR_B, 'livestream': HAIR_B, 'inspector': HAIR_G, 'finance': HAIR_B
}

FEMALE = {'farmer', 'livestream'}
HATS   = {'chief': 'official', 'farmer': 'straw'}
GLASSES= {'tech', 'inspector'}

# Nature palette
GR1=c(75,165,55); GR2=c(55,135,40); GR3=c(95,185,75); GR4=c(110,200,85)
DT1=c(155,115,65); DT2=c(135,95,50); DT3=c(175,135,85)
WT1=c(55,125,195); WT2=c(35,95,165); WT3=c(75,155,215); WT4=c(100,175,230)
PD1=c(65,145,95); PD2=c(45,115,70); PD3=c(85,165,115)
ST1=c(135,135,145); ST2=c(105,105,115); ST3=c(165,165,175)
SA1=c(215,195,145); SA2=c(195,175,125); SA3=c(235,215,165)

# Building colors
WD=c(145,95,45); WDD=c(115,70,30); WDL=c(170,120,65)
RF=c(175,55,35); RFD=c(135,35,20); RFL=c(195,75,55)
WALL=c(228,218,198); WALLD=c(198,188,168); WALLL=c(242,235,220)
GLASS=c(175,215,235); GLASSD=c(135,185,205); GLASSL=c(200,235,250)
DOOR=c(125,75,35); DOORD=c(95,55,22)
METAL=c(155,165,175); METALD=c(120,128,138)

# Crop colors
SEED=c(135,195,95); STEM=c(65,135,45); STEMD=c(45,100,30)
LEAF=c(85,170,55); LEAFD=c(60,125,35); LEAFL=c(110,195,75)

def mk(w,h):
    return Image.new('RGBA',(w,h),CLEAR)

def px(d,x,y,col):
    if col and col != CLEAR and 0 <= x and 0 <= y:
        d.point((int(x),int(y)), fill=col)

def rect(d,x,y,w,h,col):
    if col and col != CLEAR:
        d.rectangle([int(x),int(y),int(x+w-1),int(y+h-1)], fill=col)

# ========================
# TERRAIN 48x48
# ========================
def gen_terrains():
    T=48
    # GRASS
    img=mk(T,T); d=ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            r=random.random()
            noise=math.sin(x*0.4)*0.1+math.cos(y*0.3)*0.1
            r+=noise
            col=GR1 if r<0.45 else GR2 if r<0.7 else GR3 if r<0.9 else GR4
            px(d,x,y,col)
    # Grass tufts
    for _ in range(12):
        gx,gy=random.randint(3,T-4),random.randint(3,T-4)
        px(d,gx,gy-1,GR4); px(d,gx,gy,GR3)
        if random.random()<0.3:
            px(d,gx-1,gy,GR4); px(d,gx+1,gy-1,GR3)
    # Tiny flowers
    for _ in range(3):
        fx,fy=random.randint(4,T-5),random.randint(4,T-5)
        fc=c(240,220,100) if random.random()<0.5 else c(220,180,230)
        px(d,fx,fy,fc)
    img.save(os.path.join(OUT,'terrain-grass.png'))

    # DIRT
    img=mk(T,T); d=ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            r=random.random()+math.sin(x*0.5+y*0.3)*0.15
            col=DT1 if r<0.45 else DT2 if r<0.7 else DT3
            px(d,x,y,col)
    for _ in range(6):
        sx,sy=random.randint(2,T-3),random.randint(2,T-3)
        sc=c(ST2[0],ST2[1],ST2[2],180)
        px(d,sx,sy,sc)
    img.save(os.path.join(OUT,'terrain-dirt.png'))

    # WATER
    img=mk(T,T); d=ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            wave=math.sin(x*0.25+y*0.15)*0.3
            r=random.random()+wave
            col=WT1 if r<0.35 else WT2 if r<0.6 else WT3 if r<0.85 else WT4
            px(d,x,y,col)
    for _ in range(10):
        hx,hy=random.randint(4,T-5),random.randint(4,T-5)
        px(d,hx,hy,c(180,220,250,200)); px(d,hx+1,hy,c(160,210,240,150))
    img.save(os.path.join(OUT,'terrain-water.png'))

    # PADDY
    img=mk(T,T); d=ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            r=random.random()+math.sin(x*0.3)*0.1
            col=PD1 if r<0.4 else PD2 if r<0.65 else PD3
            if random.random()<0.12:
                col=c(col[0]-10,col[1]+15,col[2]+25,255)
            px(d,x,y,col)
    img.save(os.path.join(OUT,'terrain-paddy.png'))

    # STONE
    img=mk(T,T); d=ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            r=random.random()
            col=ST1 if r<0.4 else ST2 if r<0.7 else ST3
            px(d,x,y,col)
    # Cobblestone outlines
    for by in range(0,T,10):
        for bx in range(0,T,12):
            ox=6 if (by//10)%2 else 0
            cx2,cy2=bx+ox,by
            if cx2<T-8 and cy2<T-7:
                for i in range(8):
                    px(d,cx2+i,cy2,ST2); px(d,cx2+i,cy2+7,ST2)
                for j in range(8):
                    px(d,cx2,cy2+j,ST2); px(d,cx2+7,cy2+j,ST2)
    img.save(os.path.join(OUT,'terrain-stone.png'))

    # SAND
    img=mk(T,T); d=ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            r=random.random()+math.sin(x*0.6)*0.08
            col=SA1 if r<0.45 else SA2 if r<0.7 else SA3
            px(d,x,y,col)
    img.save(os.path.join(OUT,'terrain-sand.png'))
    print("  6 terrain tiles")

# ========================
# CHARACTER SPRITES 96x128 (3 frames x 4 dirs, 32x32 each)
# ========================
def draw_char(d, ox, oy, name, direction, frame):
    """Draw character at 32x32 cell, dir: 0=down,1=left,2=up,3=right"""
    body_c, body_d, trim_c, pant_c = CLOTH[name]
    hair = HAIR_MAP[name]
    female = name in FEMALE
    has_hat = name in HATS
    has_glass = name in GLASSES

    # Center offset
    cx, cy = ox+16, oy+4

    # ===== HAIR / HAT =====
    if has_hat and HATS[name]=='official':
        # Official cap
        for dx in range(-4,5): px(d,cx+dx,cy,c(50,45,60,255))
        for dx in range(-5,6): px(d,cx+dx,cy+1,c(50,45,60,255))
        for dx in range(-3,4): px(d,cx+dx,cy-1,c(60,55,70,255))
        # Gold band
        for dx in range(-4,5): px(d,cx+dx,cy+2,c(220,180,60,255))
    elif has_hat and HATS[name]=='straw':
        for dx in range(-6,7): px(d,cx+dx,cy,c(200,175,100,255))
        for dx in range(-5,6): px(d,cx+dx,cy+1,c(190,165,90,255))
        for dx in range(-4,5): px(d,cx+dx,cy-1,c(210,185,110,255))
        for dx in range(-3,4): px(d,cx+dx,cy-2,c(200,175,100,255))
    else:
        # Regular hair
        for dx in range(-4,5):
            px(d,cx+dx,cy,hair)
            px(d,cx+dx,cy+1,hair)
        for dx in range(-3,4):
            px(d,cx+dx,cy-1,hair)
        if female:
            # Longer hair
            for dy in range(2,8):
                px(d,cx-4,cy+dy,hair)
                px(d,cx-5,cy+dy,hair)
                px(d,cx+4,cy+dy,hair)
                px(d,cx+5,cy+dy,hair)

    # ===== FACE =====
    face_top = cy+2
    for dy in range(6):
        for dx in range(-3,4):
            col = SKN if dx>-3 and dx<3 else SKN2
            if dy==0 and (dx==-3 or dx==3): continue
            px(d,cx+dx,face_top+dy,col)
    # Face shadow
    for dx in range(-3,4):
        if dx>-3 and dx<3:
            px(d,cx+dx,face_top+5,SKN2)

    if direction == 0:  # facing down
        # Eyes
        px(d,cx-2,face_top+2,EYE); px(d,cx-1,face_top+2,EYE)
        px(d,cx+1,face_top+2,EYE); px(d,cx+2,face_top+2,EYE)
        # Eye highlights
        px(d,cx-2,face_top+1,EYEW); px(d,cx+1,face_top+1,EYEW)
        # Mouth
        px(d,cx-1,face_top+4,MOUTH); px(d,cx,face_top+4,MOUTH); px(d,cx+1,face_top+4,MOUTH)
        # Blush
        px(d,cx-3,face_top+3,c(255,190,170,200)); px(d,cx+3,face_top+3,c(255,190,170,200))
    elif direction == 2:  # facing up
        # Hair covers face from behind
        for dy in range(3):
            for dx in range(-3,4):
                px(d,cx+dx,face_top+dy,hair)
    else:  # side
        side = -1 if direction==1 else 1
        px(d,cx+side,face_top+2,EYE); px(d,cx+side+side,face_top+2,EYE)
        px(d,cx+side,face_top+1,EYEW)
        px(d,cx,face_top+4,MOUTH)

    # Glasses
    if has_glass:
        px(d,cx-2,face_top+2,c(180,200,220,255)); px(d,cx+2,face_top+2,c(180,200,220,255))
        px(d,cx-1,face_top+2,METALD); px(d,cx+1,face_top+2,METALD)
        px(d,cx,face_top+2,METALD)

    # ===== BODY =====
    body_top = cy + 9
    for dy in range(8):
        for dx in range(-4,5):
            col = body_d if abs(dx)>=3 else body_c
            if dy==0 and abs(dx)>=4: continue
            px(d,cx+dx,body_top+dy,col)
    # Collar/neck
    px(d,cx-1,body_top,SKN); px(d,cx,body_top,SKN); px(d,cx+1,body_top,SKN)
    # Trim/detail
    if trim_c:
        for dy in range(2,6):
            px(d,cx,body_top+dy,trim_c)

    # ===== ARMS =====
    arm_y = body_top + 1
    walk_offset = 0
    if frame == 1: walk_offset = -1
    elif frame == 2: walk_offset = 1

    for dy in range(6):
        larm_x = cx - 5
        rarm_x = cx + 5
        px(d,larm_x,arm_y+dy+walk_offset,body_c)
        px(d,rarm_x,arm_y+dy-walk_offset,body_c)
    # Hands
    px(d,cx-5,arm_y+6+walk_offset,SKN)
    px(d,cx+5,arm_y+6-walk_offset,SKN)

    # ===== LEGS =====
    leg_top = body_top + 8
    leg_h = 6
    for dy in range(leg_h):
        # Left leg
        llx = cx - 2
        rlx = cx + 1
        if frame == 1:
            llx += (dy > 2) * 1
            rlx -= (dy > 2) * 1
        elif frame == 2:
            llx -= (dy > 2) * 1
            rlx += (dy > 2) * 1

        for dx in range(2):
            px(d,llx+dx,leg_top+dy,pant_c)
            px(d,rlx+dx,leg_top+dy,pant_c)

    # Shoes
    shoe_y = leg_top + leg_h
    shoe_off_l = 1 if frame==1 else (-1 if frame==2 else 0)
    shoe_off_r = -1 if frame==1 else (1 if frame==2 else 0)
    for dx in range(-3,0):
        px(d,cx+dx+shoe_off_l,shoe_y,c(40,35,30,255))
    for dx in range(0,3):
        px(d,cx+dx+1+shoe_off_r,shoe_y,c(40,35,30,255))

def gen_characters():
    for name in ['chief','farmer','tech','sales','delivery','livestream','inspector','finance']:
        img = mk(96, 128)
        d = ImageDraw.Draw(img)
        for dir in range(4):
            for frame in range(3):
                draw_char(d, frame*32, dir*32, name, dir, frame)
        img.save(os.path.join(OUT, f'char-{name}.png'))
    print("  8 character sheets")

# ========================
# CROPS 128x32 (4 stages, 32x32 each)
# ========================
def draw_soil(d, ox, oy):
    """Draw soil base at bottom of cell"""
    for x in range(ox+4, ox+28):
        r = random.random()
        col = DT1 if r<0.4 else DT2 if r<0.7 else DT3
        px(d,x,oy+29,col); px(d,x,oy+30,col)

def gen_crops():
    crops_data = {
        'rice': {'stages': [
            lambda d,o: [px(d,o[0]+16+i,o[1]+28-j,SEED) for i in range(-1,2) for j in range(3)],
            lambda d,o: [px(d,o[0]+16+i*3,o[1]+28-j,STEM if j<6 else LEAF) for i in range(-2,3) for j in range(8)],
            lambda d,o: [px(d,o[0]+16+i*3,o[1]+28-j,LEAF if j<10 else LEAFL) for i in range(-2,3) for j in range(12)] or
                         [px(d,o[0]+16+i*3+1,o[1]+16,LEAFL) for i in range(-2,3)],
            lambda d,o: [px(d,o[0]+16+i*3,o[1]+28-j,c(180,170,60,255) if j>10 else c(160,150,50,255) if j>6 else STEM) for i in range(-2,3) for j in range(15)] or
                         [px(d,o[0]+16+i*3+dx,o[1]+13+dy,c(220,195,55,255)) for i in range(-2,3) for dx in range(-1,2) for dy in range(-1,1)]
        ]},
        'wheat': {'stages': [
            lambda d,o: [px(d,o[0]+16+i,o[1]+28-j,SEED) for i in range(-1,2) for j in range(2)],
            lambda d,o: [px(d,o[0]+16+i*2,o[1]+28-j,STEM) for i in range(-3,4) for j in range(7)],
            lambda d,o: [px(d,o[0]+16+i*2,o[1]+28-j,c(170,150,75,255)) for i in range(-3,4) for j in range(12)],
            lambda d,o: [px(d,o[0]+16+i*2,o[1]+28-j,c(210,180,65,255) if j>8 else c(190,165,70,255)) for i in range(-3,4) for j in range(16)] or
                         [px(d,o[0]+16+i*2,o[1]+12,c(230,200,80,255)) for i in range(-3,4)]
        ]},
        'tomato': {'stages': [
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,SEED) for j in range(3)],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(8)] or
                         [px(d,o[0]+16+dx,o[1]+22,LEAF) for dx in range(-2,3)],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(12)] or
                         [px(d,o[0]+16+dx,o[1]+20,LEAF) for dx in range(-3,4)] or
                         [px(d,o[0]+14+dx,o[1]+17+dy,c(80,160,50,255)) for dx in range(2) for dy in range(2)] or
                         [px(d,o[0]+19+dx,o[1]+18+dy,c(80,160,50,255)) for dx in range(2) for dy in range(2)],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(14)] or
                         [px(d,o[0]+16+dx,o[1]+18,LEAF) for dx in range(-3,4)] or
                         [px(d,o[0]+13+dx,o[1]+15+dy,c(220,45,25,255)) for dx in range(3) for dy in range(3)] or
                         [px(d,o[0]+18+dx,o[1]+16+dy,c(220,45,25,255)) for dx in range(3) for dy in range(3)] or
                         [px(d,o[0]+15+dx,o[1]+20+dy,c(200,40,20,255)) for dx in range(3) for dy in range(3)]
        ]},
        'cabbage': {'stages': [
            lambda d,o: [px(d,o[0]+16+dx,o[1]+28-dy,SEED) for dx in range(-1,2) for dy in range(2)],
            lambda d,o: [px(d,o[0]+16+dx,o[1]+26-dy,LEAF) for dx in range(-2,3) for dy in range(4) if abs(dx)+dy<5],
            lambda d,o: [px(d,o[0]+16+dx,o[1]+24+dy,c(95,175,75,255) if dx*dx+dy*dy>9 else c(175,215,145,255)) for dx in range(-4,5) for dy in range(-4,5) if dx*dx+dy*dy<=16],
            lambda d,o: [px(d,o[0]+16+dx,o[1]+23+dy,c(90,170,70,255) if dx*dx+dy*dy>20 else c(165,210,140,255) if dx*dx+dy*dy>8 else c(200,235,170,255)) for dx in range(-5,6) for dy in range(-5,6) if dx*dx+dy*dy<=25] or
                         [px(d,o[0]+16+dx,o[1]+23,LEAFL) for dx in [-6,6]]
        ]},
        'strawberry': {'stages': [
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,SEED) for j in range(2)],
            lambda d,o: [px(d,o[0]+16+dx,o[1]+26-dy,LEAF) for dx in range(-3,4) for dy in range(4) if abs(dx)<4-dy],
            lambda d,o: [px(d,o[0]+16+dx,o[1]+25-dy,LEAF) for dx in range(-3,4) for dy in range(5) if abs(dx)<4-dy//2] or
                         [px(d,o[0]+14,o[1]+26,c(230,100,140,255))] or [px(d,o[0]+19,o[1]+27,c(230,100,140,255))],
            lambda d,o: [px(d,o[0]+16+dx,o[1]+24-dy,LEAF) for dx in range(-4,5) for dy in range(5) if abs(dx)<5-dy//2] or
                         [px(d,o[0]+12+dx,o[1]+26+dy,c(220,35,55,255)) for dx in range(2) for dy in range(2)] or
                         [px(d,o[0]+16+dx,o[1]+27+dy,c(220,35,55,255)) for dx in range(2) for dy in range(2)] or
                         [px(d,o[0]+20+dx,o[1]+25+dy,c(220,35,55,255)) for dx in range(2) for dy in range(2)]
        ]},
        'orange': {'stages': [
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,STEMD) for j in range(3)],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,WD) for j in range(8)] or
                         [px(d,o[0]+16+dx,o[1]+20+dy,LEAF) for dx in range(-3,4) for dy in range(-3,4) if dx*dx+dy*dy<=9],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,WD) for j in range(12)] or [px(d,o[0]+17,o[1]+28-j,WDD) for j in range(10)] or
                         [px(d,o[0]+16+dx,o[1]+16+dy,LEAF if (dx+dy)%3 else LEAFD) for dx in range(-5,6) for dy in range(-5,6) if dx*dx+dy*dy<=25],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,WD) for j in range(14)] or [px(d,o[0]+17,o[1]+28-j,WDD) for j in range(12)] or
                         [px(d,o[0]+16+dx,o[1]+14+dy,LEAF if (dx+dy)%3 else LEAFD) for dx in range(-6,7) for dy in range(-6,7) if dx*dx+dy*dy<=36] or
                         [px(d,o[0]+13+dx,o[1]+13+dy,c(240,160,35,255)) for dx in range(2) for dy in range(2)] or
                         [px(d,o[0]+18+dx,o[1]+12+dy,c(240,160,35,255)) for dx in range(2) for dy in range(2)] or
                         [px(d,o[0]+15+dx,o[1]+16+dy,c(235,155,30,255)) for dx in range(2) for dy in range(2)]
        ]},
        'pepper': {'stages': [
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,SEED) for j in range(3)],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(7)] or
                         [px(d,o[0]+16+dx,o[1]+23,LEAF) for dx in range(-2,3)],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(11)] or
                         [px(d,o[0]+16+dx,o[1]+20+dy,LEAF) for dx in range(-3,4) for dy in range(-2,2)] or
                         [px(d,o[0]+14+dx,o[1]+22+dy,c(80,160,45,255)) for dx in range(1) for dy in range(3)],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(13)] or
                         [px(d,o[0]+16+dx,o[1]+18+dy,LEAF) for dx in range(-3,4) for dy in range(-2,2)] or
                         [px(d,o[0]+13+dx,o[1]+20+dy,c(200,35,18,255)) for dx in range(1) for dy in range(4)] or
                         [px(d,o[0]+18+dx,o[1]+21+dy,c(200,35,18,255)) for dx in range(1) for dy in range(3)] or
                         [px(d,o[0]+15+dx,o[1]+23+dy,c(195,30,15,255)) for dx in range(1) for dy in range(3)]
        ]},
        'lotus': {'stages': [
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,SEED) for j in range(2)] or
                         [px(d,o[0]+x,o[1]+29,WT2) for x in range(4,28)],
            lambda d,o: [px(d,o[0]+x,o[1]+29,WT2) for x in range(4,28)] or
                         [px(d,o[0]+x,o[1]+30,WT1) for x in range(4,28)] or
                         [px(d,o[0]+16+dx,o[1]+28,PD1) for dx in range(-3,4)] or
                         [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(5)],
            lambda d,o: [px(d,o[0]+x,o[1]+29,WT2) for x in range(2,30)] or
                         [px(d,o[0]+x,o[1]+30,WT1) for x in range(2,30)] or
                         [px(d,o[0]+12+dx,o[1]+28,PD1) for dx in range(-3,4)] or
                         [px(d,o[0]+20+dx,o[1]+28,PD3) for dx in range(-3,4)] or
                         [px(d,o[0]+12,o[1]+28-j,STEM) for j in range(8)] or
                         [px(d,o[0]+20,o[1]+28-j,STEM) for j in range(7)] or
                         [px(d,o[0]+12+dx,o[1]+20+dy,c(240,135,175,255)) for dx in range(-1,2) for dy in range(-1,2)],
            lambda d,o: [px(d,o[0]+x,o[1]+29,WT2) for x in range(2,30)] or
                         [px(d,o[0]+x,o[1]+30,WT1) for x in range(2,30)] or
                         [px(d,o[0]+10+dx,o[1]+28,PD1) for dx in range(-3,4)] or
                         [px(d,o[0]+22+dx,o[1]+28,PD3) for dx in range(-3,4)] or
                         [px(d,o[0]+16+dx,o[1]+29,PD1) for dx in range(-2,3)] or
                         [px(d,o[0]+10,o[1]+28-j,STEM) for j in range(10)] or
                         [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(12)] or
                         [px(d,o[0]+22,o[1]+28-j,STEM) for j in range(9)] or
                         [px(d,o[0]+16+dx,o[1]+16+dy,c(245,140,180,255)) for dx in range(-2,3) for dy in range(-2,3) if dx*dx+dy*dy<=4] or
                         [px(d,o[0]+10+dx,o[1]+19+dy,c(240,130,170,255)) for dx in range(-1,2) for dy in range(-1,2)] or
                         [px(d,o[0]+22+dx,o[1]+20+dy,c(240,130,170,255)) for dx in range(-1,2) for dy in range(-1,2)]
        ]},
        'tea': {'stages': [
            lambda d,o: [px(d,o[0]+16+dx,o[1]+28-dy,SEED) for dx in range(-1,2) for dy in range(3)],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,WD) for j in range(5)] or
                         [px(d,o[0]+16+dx,o[1]+24+dy,c(55,125,45,255)) for dx in range(-3,4) for dy in range(-2,3) if abs(dx)+abs(dy)<=3],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,WD) for j in range(7)] or
                         [px(d,o[0]+16+dx,o[1]+22+dy,c(55,125,45,255) if (dx+dy)%2 else c(45,105,35,255)) for dx in range(-5,6) for dy in range(-3,4) if abs(dx)+abs(dy)<=5],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,WD) for j in range(9)] or
                         [px(d,o[0]+16+dx,o[1]+20+dy,c(55,125,45,255) if (dx+dy)%2 else c(45,105,35,255)) for dx in range(-6,7) for dy in range(-4,5) if abs(dx)+abs(dy)<=6] or
                         [px(d,o[0]+16+dx,o[1]+16,c(115,195,75,255)) for dx in range(-5,6,2)]
        ]},
        'corn': {'stages': [
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,SEED) for j in range(3)],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(9)] or
                         [px(d,o[0]+16+dx,o[1]+22,LEAF) for dx in [-3,-2,2,3]] or
                         [px(d,o[0]+16+dx,o[1]+25,LEAF) for dx in [-2,-1,1,2]],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(16)] or [px(d,o[0]+17,o[1]+28-j,STEM) for j in range(14)] or
                         [px(d,o[0]+16+dx,o[1]+20,LEAF) for dx in [-4,-3,3,4]] or
                         [px(d,o[0]+16+dx,o[1]+16,LEAF) for dx in [-3,-2,2,3]] or
                         [px(d,o[0]+18+dx,o[1]+14+dy,c(100,170,50,255)) for dx in range(2) for dy in range(3)],
            lambda d,o: [px(d,o[0]+16,o[1]+28-j,STEM) for j in range(20)] or [px(d,o[0]+17,o[1]+28-j,STEM) for j in range(18)] or
                         [px(d,o[0]+16+dx,o[1]+18,LEAFL) for dx in [-5,-4,-3,3,4,5]] or
                         [px(d,o[0]+16+dx,o[1]+14,LEAFL) for dx in [-4,-3,3,4]] or
                         [px(d,o[0]+18+dx,o[1]+10+dy,c(240,200,55,255)) for dx in range(2) for dy in range(4)] or
                         [px(d,o[0]+16,o[1]+8,c(210,175,65,255))] or
                         [px(d,o[0]+15,o[1]+9,c(210,175,65,255))] or [px(d,o[0]+17,o[1]+9,c(210,175,65,255))]
        ]}
    }

    for name, data in crops_data.items():
        img = mk(128,32)
        d = ImageDraw.Draw(img)
        for stage_i, draw_fn in enumerate(data['stages']):
            ox = stage_i * 32
            draw_soil(d, ox, 0)
            draw_fn(d, (ox, 0))
        img.save(os.path.join(OUT, f'crop-{name}.png'))
    print(f"  {len(crops_data)} crop sprites")

# ========================
# BUILDINGS 64x64
# ========================
def gen_buildings():
    builds = {
      'village-hall': (RF, RFD, WALL, WALLD, 'flag'),
      'market': (c(60,80,140,255), c(40,55,100,255), WALL, WALLD, 'sign'),
      'warehouse': (RFD, c(100,30,20,255), ST1, ST2, None),
      'greenhouse': (GLASS, GLASSD, WALL, WALLD, 'glass_roof'),
      'weather-station': (METAL, METALD, WALL, WALLD, 'antenna'),
      'lab': (c(235,235,245,255), c(205,205,215,255), WALL, WALLD, None),
      'training': (RF, RFD, WALL, WALLD, None),
      'logistics': (c(220,130,40,255), c(180,100,25,255), ST1, ST2, None),
      'livestream': (c(230,110,150,255), c(190,75,115,255), WALL, WALLD, 'antenna'),
    }

    S = 64
    for name, (roof, roofd, wall, walld, feat) in builds.items():
        img = mk(S, S); d = ImageDraw.Draw(img)

        # Foundation
        rect(d, 8, S-10, S-16, 4, ST2)

        # Walls
        for y in range(22, S-10):
            for x in range(10, S-10):
                col = wall if (x+y)%8 else walld
                px(d,x,y,col)

        # Wall outlines
        for y in range(20, S-10):
            px(d,9,y,walld); px(d,S-10,y,walld)

        # Door
        dx_s = S//2-4
        rect(d, dx_s, S-18, 8, 8, DOOR)
        rect(d, dx_s+6, S-18, 2, 8, DOORD)
        px(d, dx_s+6, S-14, c(220,180,60,255))  # handle

        # Windows
        for wx in [14, S-22]:
            rect(d, wx, 26, 6, 6, GLASS)
            rect(d, wx, 26, 6, 1, WD)  # top frame
            rect(d, wx, 31, 6, 1, WD)  # bottom frame
            rect(d, wx, 26, 1, 6, WD)  # left frame
            rect(d, wx+5, 26, 1, 6, WD)  # right frame
            px(d, wx+2, 26, WD); px(d, wx+2, 31, WD)  # cross

        # Roof
        if feat == 'glass_roof':
            for ry in range(16):
                ind = ry
                for x in range(7+ind, S-7-ind):
                    col = GLASS if (x//4+ry//4)%2 else GLASSD
                    px(d,x,5+ry,col)
                # Metal frame lines
                if ry % 4 == 0:
                    for x in range(7+ind, S-7-ind):
                        px(d,x,5+ry,METALD)
        else:
            for ry in range(16):
                ind = ry
                for x in range(7+ind, S-7-ind):
                    col = roof if ry%4 else roofd
                    px(d,x,5+ry,col)
            # Ridge
            for x in range(S//2-2, S//2+3):
                px(d,x,5,roofd)

        # Features
        if feat == 'antenna':
            for y in range(0,7): px(d,S//2,y,METAL)
            px(d,S//2-1,1,METAL); px(d,S//2+1,1,METAL)
            px(d,S//2-2,2,METAL); px(d,S//2+2,2,METAL)
            px(d,S//2,0,c(220,40,40,255))  # red light
        elif feat == 'flag':
            for y in range(0,8): px(d,S-14,y,WD)
            rect(d,S-13,0,6,4,c(220,40,30,255))
        elif feat == 'sign':
            rect(d,S//2-8,S-8,16,3,WD)
            for x in range(S//2-6,S//2+7):
                px(d,x,S-7,c(255,230,180,255))

        img.save(os.path.join(OUT, f'bld-{name}.png'))
    print(f"  {len(builds)} building sprites")

# ========================
# MAIN
# ========================
if __name__ == '__main__':
    print("SYNAPSE Sprite Gen v3.0")
    print("="*40)
    gen_terrains()
    gen_characters()
    gen_crops()
    gen_buildings()

    atlas = {
        "characters": ["chief","farmer","tech","sales","delivery","livestream","inspector","finance"],
        "crops": ["rice","wheat","tomato","cabbage","strawberry","orange","pepper","lotus","tea","corn"],
        "buildings": ["village-hall","market","warehouse","greenhouse","weather-station","lab","training","logistics","livestream"],
        "terrains": ["grass","dirt","water","paddy","stone","sand"],
        "charSheet": {"frameW":32,"frameH":32,"cols":3,"rows":4,"desc":"3 frames(idle,walk1,walk2) x 4 dirs(down,left,up,right)"},
        "cropSheet": {"frameW":32,"frameH":32,"stages":4,"desc":"4 growth stages left-to-right: seedling,growing,flowering,mature"},
        "buildingSize": 64,
        "terrainSize": 48,
        "style": "16-bit pixel art, warm Stardew Valley tones, consistent palette across all assets",
        "aiSpec": "All sprites use transparent PNG with RGBA. Characters: 96x128 spritesheet. Crops: 128x32 spritesheet. Buildings: 64x64. Terrain: 48x48 tileable."
    }
    with open(os.path.join(OUT,'atlas.json'),'w') as f:
        json.dump(atlas,f,indent=2)
    print("\nDone! All sprites at:", OUT)
