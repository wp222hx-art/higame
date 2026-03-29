#!/usr/bin/env python3
"""
SYNAPSE Sprite Generator v4.0 — TRUE Q-Version (Chibi) Pixel Art
=================================================================
Key improvements over v3:
- Characters: Big head (60% of body), round face, expressive 2-px eyes, 
  anime blush, detailed hair with highlights, 3-color shading on clothes
- Buildings: Isometric-ish perspective, tile-roof textures, glowing windows,
  chimney smoke, sign boards, shadow bases
- Crops: Lush multi-shade foliage, visible soil mounds, dewdrops on mature,
  flowers on flowering stage
- Terrain: Richer noise, grass blades, water caustics, path cracks,
  edge dithering for seamless tiling
- All sprites use outlined style (1px dark outline) for Q-version pop
"""
from PIL import Image, ImageDraw, ImageFilter
import os, json, math, random

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'game', 'assets', 'sprites')
os.makedirs(OUT, exist_ok=True)
random.seed(42)

# ─── HELPERS ───────────────────────────────────────────────
CLEAR = (0, 0, 0, 0)

def c(r, g, b, a=255):
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), max(0, min(255, a)))

def lighter(col, amt=30):
    return c(col[0]+amt, col[1]+amt, col[2]+amt, col[3] if len(col) > 3 else 255)

def darker(col, amt=30):
    return c(col[0]-amt, col[1]-amt, col[2]-amt, col[3] if len(col) > 3 else 255)

def mk(w, h):
    return Image.new('RGBA', (w, h), CLEAR)

def px(img_draw, x, y, col):
    x, y = int(x), int(y)
    if col and col != CLEAR and x >= 0 and y >= 0:
        try:
            img_draw.point((x, y), fill=col)
        except:
            pass

def rect(d, x, y, w, h, col):
    if col and col != CLEAR:
        d.rectangle([int(x), int(y), int(x+w-1), int(y+h-1)], fill=col)

def ellipse_fill(d, cx, cy, rx, ry, col):
    """Fill an ellipse pixel by pixel for precise control"""
    for dy in range(-ry, ry+1):
        for dx in range(-rx, rx+1):
            if (dx*dx)/(rx*rx+0.01) + (dy*dy)/(ry*ry+0.01) <= 1.0:
                px(d, cx+dx, cy+dy, col)

def outline_ellipse(d, cx, cy, rx, ry, col):
    """Draw ellipse outline"""
    for angle in range(360):
        rad = math.radians(angle)
        x = cx + rx * math.cos(rad)
        y = cy + ry * math.sin(rad)
        px(d, x, y, col)

def circle_fill(d, cx, cy, r, col):
    ellipse_fill(d, cx, cy, r, r, col)

# ─── COLOR PALETTES ───────────────────────────────────────
# Skin tones (warm)
SKN   = c(255, 224, 189)
SKN_H = c(255, 235, 210)  # highlight
SKN_S = c(235, 195, 155)  # shadow
SKN_D = c(210, 170, 130)  # deep shadow
BLUSH = c(255, 180, 170, 160)

# Eyes
EYE_W = c(255, 255, 255)
EYE_B = c(25, 20, 35)      # pupil
EYE_I = c(60, 45, 80)      # iris outer
EYE_HL = c(255, 255, 255)  # highlight
MOUTH = c(210, 120, 100)
MOUTH_D = c(180, 90, 75)

# Outline
OL = c(35, 28, 42)     # standard dark outline
OL_L = c(55, 45, 65)   # lighter outline for internal

# Hair colors
HAIR = {
    'black':  (c(40, 35, 50),  c(55, 48, 65),  c(30, 25, 38)),
    'brown':  (c(110, 70, 40), c(135, 90, 55), c(80, 50, 28)),
    'gray':   (c(160, 158, 168), c(180, 178, 188), c(130, 128, 138)),
    'red':    (c(165, 55, 40), c(195, 80, 60), c(130, 40, 28)),
    'blonde': (c(200, 170, 90), c(225, 195, 120), c(165, 135, 60)),
}

# Clothing palettes: (main, highlight, shadow, trim/accent, pant, pant_dark)
CLOTH = {
    'chief': {
        'main': c(190, 50, 40), 'hi': c(220, 80, 65), 'sh': c(145, 35, 25),
        'trim': c(225, 190, 65), 'pant': c(50, 45, 60), 'pant_d': c(35, 30, 45),
        'hair': 'black', 'hat': 'official', 'gender': 'M'
    },
    'farmer': {
        'main': c(65, 155, 75), 'hi': c(90, 185, 100), 'sh': c(42, 115, 52),
        'trim': c(200, 175, 100), 'pant': c(100, 78, 48), 'pant_d': c(75, 55, 35),
        'hair': 'brown', 'hat': 'straw', 'gender': 'F'
    },
    'tech': {
        'main': c(55, 95, 178), 'hi': c(80, 120, 205), 'sh': c(38, 68, 135),
        'trim': c(245, 245, 255), 'pant': c(48, 48, 58), 'pant_d': c(32, 32, 42),
        'hair': 'black', 'hat': None, 'gender': 'M', 'glasses': True
    },
    'sales': {
        'main': c(225, 135, 45), 'hi': c(248, 165, 72), 'sh': c(185, 105, 30),
        'trim': c(60, 55, 50), 'pant': c(62, 58, 68), 'pant_d': c(42, 38, 48),
        'hair': 'brown', 'hat': None, 'gender': 'M'
    },
    'delivery': {
        'main': c(55, 175, 165), 'hi': c(80, 205, 195), 'sh': c(38, 135, 128),
        'trim': c(72, 72, 82), 'pant': c(58, 58, 68), 'pant_d': c(38, 38, 48),
        'hair': 'black', 'hat': 'cap', 'gender': 'M'
    },
    'livestream': {
        'main': c(235, 115, 155), 'hi': c(255, 148, 182), 'sh': c(195, 80, 118),
        'trim': c(255, 225, 235), 'pant': c(58, 48, 62), 'pant_d': c(38, 28, 42),
        'hair': 'black', 'hat': None, 'gender': 'F'
    },
    'inspector': {
        'main': c(240, 240, 248), 'hi': c(255, 255, 255), 'sh': c(200, 200, 210),
        'trim': c(50, 50, 60), 'pant': c(52, 52, 58), 'pant_d': c(35, 35, 42),
        'hair': 'gray', 'hat': None, 'gender': 'M', 'glasses': True
    },
    'finance': {
        'main': c(135, 68, 165), 'hi': c(165, 95, 195), 'sh': c(98, 42, 125),
        'trim': c(225, 205, 245), 'pant': c(52, 48, 62), 'pant_d': c(35, 30, 45),
        'hair': 'black', 'hat': None, 'gender': 'M'
    },
}

# Nature
GR  = c(82, 172, 60);  GR_H = c(108, 198, 82);  GR_S = c(58, 140, 42); GR_D = c(45, 115, 32)
GR2 = c(72, 158, 52);  GR3 = c(95, 188, 72)
DT  = c(162, 122, 72); DT_H = c(185, 148, 95);   DT_S = c(138, 98, 52)
WT  = c(60, 130, 200); WT_H = c(85, 162, 228);   WT_S = c(40, 100, 170); WT_D = c(30, 80, 148)
PD  = c(68, 150, 100); PD_H = c(88, 172, 118);   PD_S = c(48, 118, 72)
ST  = c(142, 142, 150); ST_H = c(172, 172, 178);  ST_S = c(110, 110, 118)
SA  = c(220, 200, 150); SA_H = c(242, 225, 175);  SA_S = c(198, 178, 128)

# Building
WOOD   = c(150, 100, 50);  WOOD_H = c(178, 128, 72);  WOOD_D = c(118, 72, 32)
ROOF_R = c(180, 58, 38);   ROOF_H = c(210, 85, 60);   ROOF_D = c(140, 38, 22)
WALL_W = c(232, 222, 202); WALL_H = c(248, 240, 225); WALL_D = c(200, 192, 172)
GLASS  = c(180, 220, 240); GLASS_H = c(210, 242, 255); GLASS_D = c(140, 188, 210)
DOOR   = c(128, 78, 38);   DOOR_D = c(98, 55, 22)
METAL  = c(160, 170, 180); METAL_D = c(125, 132, 142)

# Crop
SEED_C = c(140, 200, 100)
STEM_C = c(68, 140, 48);   STEM_D = c(48, 105, 32);   STEM_H = c(88, 165, 65)
LEAF_C = c(88, 175, 58);   LEAF_D = c(62, 130, 38);   LEAF_H = c(115, 200, 80)

# ═══════════════════════════════════════════════════════════
#  TERRAIN TILES 48×48
# ═══════════════════════════════════════════════════════════
def gen_terrains():
    T = 48

    def noise2d(x, y, freq=0.15):
        return (math.sin(x * freq) * math.cos(y * freq * 1.3) +
                math.sin(x * freq * 2.1 + 1.7) * math.cos(y * freq * 1.8 + 0.9)) * 0.5

    # ── GRASS ──
    img = mk(T, T); d = ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            n = noise2d(x, y, 0.18) + random.random() * 0.3
            if n < -0.1:
                col = GR_D
            elif n < 0.2:
                col = GR_S
            elif n < 0.55:
                col = GR
            elif n < 0.8:
                col = GR_H
            else:
                col = GR3
            # Add subtle warm variation
            if random.random() < 0.05:
                col = c(col[0]+8, col[1]+12, col[2]-5)
            px(d, x, y, col)
    # Grass tufts (V shapes)
    for _ in range(18):
        gx, gy = random.randint(3, T-4), random.randint(3, T-4)
        tc = GR3 if random.random() < 0.5 else GR_H
        px(d, gx-1, gy, tc); px(d, gx, gy-1, lighter(tc, 15)); px(d, gx+1, gy, tc)
        if random.random() < 0.4:
            px(d, gx, gy-2, lighter(tc, 20))
    # Tiny wildflowers
    flowers = [(c(245, 225, 105), c(235, 210, 85)),  # yellow
               (c(225, 185, 235), c(205, 160, 218)),  # lavender
               (c(255, 200, 200), c(235, 175, 178))]  # pink
    for _ in range(4):
        fx, fy = random.randint(4, T-5), random.randint(4, T-5)
        fc = random.choice(flowers)
        px(d, fx, fy, fc[0])
        px(d, fx+1, fy, fc[1])
        px(d, fx, fy+1, STEM_C)
    img.save(os.path.join(OUT, 'terrain-grass.png'))

    # ── DIRT ──
    img = mk(T, T); d = ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            n = noise2d(x, y, 0.2) + random.random() * 0.35
            if n < 0.15:   col = DT_S
            elif n < 0.5:  col = DT
            else:          col = DT_H
            px(d, x, y, col)
    # Pebbles
    for _ in range(8):
        sx, sy = random.randint(2, T-3), random.randint(2, T-3)
        sc = c(ST[0], ST[1], ST[2], 180) if random.random() < 0.5 else darker(DT, 20)
        px(d, sx, sy, sc)
        if random.random() < 0.4:
            px(d, sx+1, sy, lighter(sc, 15))
    # Cracks
    for _ in range(3):
        cx_, cy_ = random.randint(6, T-7), random.randint(6, T-7)
        for i in range(4):
            px(d, cx_+i, cy_+(i%2), darker(DT, 25))
    img.save(os.path.join(OUT, 'terrain-dirt.png'))

    # ── WATER ──
    img = mk(T, T); d = ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            wave = math.sin(x*0.22 + y*0.12) * 0.25 + math.cos(x*0.15 - y*0.2) * 0.15
            n = random.random() * 0.4 + wave
            if n < 0.1:    col = WT_D
            elif n < 0.35: col = WT_S
            elif n < 0.65: col = WT
            elif n < 0.85: col = WT_H
            else:          col = c(110, 185, 238)
            px(d, x, y, col)
    # Caustic highlights
    for _ in range(14):
        hx, hy = random.randint(3, T-4), random.randint(3, T-4)
        ha = 140 + random.randint(0, 60)
        px(d, hx, hy, c(190, 230, 255, ha))
        px(d, hx+1, hy, c(170, 218, 248, ha-40))
        if random.random() < 0.3:
            px(d, hx, hy-1, c(200, 238, 255, ha-50))
    img.save(os.path.join(OUT, 'terrain-water.png'))

    # ── PADDY ──
    img = mk(T, T); d = ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            n = noise2d(x, y, 0.16) + random.random() * 0.3
            if n < 0.2:   col = PD_S
            elif n < 0.55: col = PD
            else:          col = PD_H
            # Water sheen
            if random.random() < 0.08:
                col = c(col[0]-8, col[1]+12, col[2]+22)
            px(d, x, y, col)
    # Rice stubble lines
    for _ in range(6):
        ry_ = random.randint(4, T-5)
        for rx_ in range(0, T, 6):
            px(d, rx_+random.randint(0,2), ry_, lighter(PD_H, 12))
    img.save(os.path.join(OUT, 'terrain-paddy.png'))

    # ── STONE ──
    img = mk(T, T); d = ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            n = random.random()
            if n < 0.35:   col = ST_S
            elif n < 0.65: col = ST
            else:          col = ST_H
            px(d, x, y, col)
    # Cobblestone pattern
    for by_ in range(0, T, 10):
        for bx_ in range(0, T, 14):
            ox_ = 7 if (by_//10)%2 else 0
            cx_, cy_ = bx_+ox_, by_
            if cx_ < T-9 and cy_ < T-8:
                for i in range(10):
                    px(d, cx_+i, cy_, ST_S); px(d, cx_+i, cy_+8, ST_S)
                for j in range(8):
                    px(d, cx_, cy_+j, ST_S); px(d, cx_+9, cy_+j, ST_S)
                # Highlight top-left
                for i in range(1, 9):
                    px(d, cx_+i, cy_+1, ST_H)
                for j in range(1, 7):
                    px(d, cx_+1, cy_+j, ST_H)
    img.save(os.path.join(OUT, 'terrain-stone.png'))

    # ── SAND ──
    img = mk(T, T); d = ImageDraw.Draw(img)
    for y in range(T):
        for x in range(T):
            n = noise2d(x, y, 0.12) + random.random() * 0.35
            ripple = math.sin(x*0.4 + y*0.1) * 0.08
            n += ripple
            if n < 0.2:   col = SA_S
            elif n < 0.6: col = SA
            else:          col = SA_H
            px(d, x, y, col)
    # Shell / small details
    for _ in range(3):
        sx_, sy_ = random.randint(5, T-6), random.randint(5, T-6)
        px(d, sx_, sy_, c(240, 230, 215))
    img.save(os.path.join(OUT, 'terrain-sand.png'))

    print("  6 terrain tiles generated")


# ═══════════════════════════════════════════════════════════
#  CHARACTER SPRITES 96×128 (3 frames × 4 dirs, 32×32 each)
#  TRUE CHIBI: head = 60% of body height, round face, big eyes
# ═══════════════════════════════════════════════════════════
def draw_chibi(d, ox, oy, name, direction, frame):
    """
    Draw a Q-version character in a 32×32 cell.
    Chibi proportions: head ~14px tall, body ~8px, legs ~4px = ~26px total
    Head is ~60% of total height.
    dir: 0=down, 1=left, 2=up, 3=right
    frame: 0=idle, 1=walk_a, 2=walk_b
    """
    info = CLOTH[name]
    hair_set = HAIR[info['hair']]
    hair_c, hair_h, hair_d = hair_set
    mc, hi, sh = info['main'], info['hi'], info['sh']
    trim = info['trim']
    pc, pd = info['pant'], info['pant_d']
    female = info['gender'] == 'F'
    has_hat = info.get('hat')
    has_glass = info.get('glasses', False)

    # Center of the 32×32 cell
    cx = ox + 16
    # Start Y (head top)
    sy = oy + 3

    # Walk animation offsets
    walk_off = 0
    body_bounce = 0
    if frame == 1:
        walk_off = -1
        body_bounce = -1
    elif frame == 2:
        walk_off = 1
        body_bounce = -1

    # ═══ HAIR (back layer, behind head for side/up views) ═══
    if direction == 2:  # facing up — draw full back hair
        # Back of head (hair covers everything)
        for dy in range(-1, 9):
            half_w = 6 if dy < 6 else 5
            for dx in range(-half_w, half_w+1):
                shade = hair_d if abs(dx) >= half_w-1 else (hair_h if dy < 2 else hair_c)
                px(d, cx+dx, sy+dy, shade)
        if female:
            # Long hair flowing down
            for dy in range(9, 18):
                hw = max(1, 6 - (dy-9)//3)
                for dx in [-5, -6, 5, 6]:
                    if abs(dx) <= hw+5:
                        px(d, cx+dx, sy+dy, hair_c if (dy+dx)%3 else hair_d)

    # ═══ HEAD (Big round chibi head) ═══
    head_cy = sy + 5  # center of head
    head_rx, head_ry = 6, 5  # radius

    # Head outline
    outline_ellipse(d, cx, head_cy, head_rx+1, head_ry+1, OL)
    # Head fill (skin)
    ellipse_fill(d, cx, head_cy, head_rx, head_ry, SKN)
    # Skin shading (right side shadow for 3D)
    if direction != 2:
        for dy in range(-head_ry, head_ry+1):
            for dx in range(1, head_rx+1):
                if (dx*dx)/(head_rx*head_rx+0.01) + (dy*dy)/(head_ry*head_ry+0.01) <= 1.0:
                    if dx > head_rx - 2:
                        px(d, cx+dx, head_cy+dy, SKN_S)
        # Forehead highlight
        for dx in range(-2, 1):
            px(d, cx+dx, head_cy-head_ry+1, SKN_H)
            px(d, cx+dx, head_cy-head_ry+2, SKN_H)

    # ═══ FACE FEATURES (only for front/side views) ═══
    if direction == 0:  # FRONT
        # Eyes — big chibi eyes (2×3 px each)
        for eye_x in [-3, 2]:
            # Eye white
            px(d, cx+eye_x, head_cy-1, EYE_W)
            px(d, cx+eye_x+1, head_cy-1, EYE_W)
            # Iris/pupil
            px(d, cx+eye_x, head_cy, EYE_I)
            px(d, cx+eye_x+1, head_cy, EYE_B)
            px(d, cx+eye_x, head_cy+1, EYE_B)
            px(d, cx+eye_x+1, head_cy+1, EYE_I)
            # Eye highlight (key for anime/chibi look!)
            px(d, cx+eye_x, head_cy-1, EYE_HL)
        # Eyebrows
        px(d, cx-4, head_cy-2, OL_L)
        px(d, cx-3, head_cy-3, OL_L)
        px(d, cx+2, head_cy-3, OL_L)
        px(d, cx+3, head_cy-2, OL_L)
        # Mouth (small, cute)
        px(d, cx-1, head_cy+3, MOUTH)
        px(d, cx, head_cy+3, MOUTH_D)
        px(d, cx+1, head_cy+3, MOUTH)
        # Blush spots (essential for Q-version!)
        px(d, cx-5, head_cy+1, BLUSH)
        px(d, cx-4, head_cy+1, BLUSH)
        px(d, cx+4, head_cy+1, BLUSH)
        px(d, cx+5, head_cy+1, BLUSH)
        # Nose dot
        px(d, cx, head_cy+1, SKN_S)

    elif direction == 1:  # LEFT
        # Side face — one eye visible
        ex = cx - 2
        px(d, ex, head_cy-1, EYE_W)
        px(d, ex, head_cy, EYE_B)
        px(d, ex+1, head_cy, EYE_I)
        px(d, ex, head_cy-1, EYE_HL)
        # Mouth
        px(d, cx-3, head_cy+3, MOUTH)
        px(d, cx-2, head_cy+3, MOUTH_D)
        # Blush
        px(d, cx-4, head_cy+1, BLUSH)
        # Nose
        px(d, cx-4, head_cy+1, SKN_D)

    elif direction == 3:  # RIGHT
        ex = cx + 2
        px(d, ex, head_cy-1, EYE_W)
        px(d, ex, head_cy, EYE_B)
        px(d, ex-1, head_cy, EYE_I)
        px(d, ex, head_cy-1, EYE_HL)
        px(d, cx+3, head_cy+3, MOUTH)
        px(d, cx+2, head_cy+3, MOUTH_D)
        px(d, cx+4, head_cy+1, BLUSH)
        px(d, cx+4, head_cy+1, SKN_D)

    # Glasses
    if has_glass and direction != 2:
        gc = c(185, 205, 228)
        gf = c(140, 160, 180)
        if direction == 0:
            for gx in [-4, -3, 2, 3]:
                px(d, cx+gx, head_cy-1, gf)
                px(d, cx+gx, head_cy+1, gf)
            px(d, cx-1, head_cy, gf)  # bridge
            px(d, cx, head_cy, gf)
            px(d, cx+1, head_cy, gf)
            px(d, cx-3, head_cy, gc); px(d, cx+2, head_cy, gc)
        else:
            side = -1 if direction == 1 else 1
            for dx in range(3):
                px(d, cx+side*(dx+1), head_cy-1, gf)
                px(d, cx+side*(dx+1), head_cy+1, gf)
            px(d, cx+side*2, head_cy, gc)

    # ═══ HAIR (front layer) ═══
    if has_hat == 'official':
        # Official cap
        for dx in range(-5, 6):
            px(d, cx+dx, sy, OL)
        for dx in range(-6, 7):
            px(d, cx+dx, sy+1, c(50,45,60))
        for dx in range(-5, 6):
            px(d, cx+dx, sy-1, c(60,55,70))
        # Gold band
        for dx in range(-5, 6):
            px(d, cx+dx, sy+2, c(225,185,65))
        # Visor
        for dx in range(-4, 5):
            px(d, cx+dx, sy+2, c(35,30,45))
    elif has_hat == 'straw':
        # Straw hat (wide brim)
        brim_c = c(205, 180, 108)
        brim_h = c(228, 205, 135)
        brim_d = c(178, 155, 85)
        for dx in range(-7, 8):
            px(d, cx+dx, sy+1, brim_c if abs(dx) < 6 else brim_d)
            px(d, cx+dx, sy+2, brim_d if abs(dx) > 4 else brim_c)
        for dx in range(-5, 6):
            px(d, cx+dx, sy, brim_h)
            px(d, cx+dx, sy-1, brim_c)
        for dx in range(-3, 4):
            px(d, cx+dx, sy-2, brim_h)
        # Band
        for dx in range(-4, 5):
            px(d, cx+dx, sy+1, c(180, 80, 60))
    elif has_hat == 'cap':
        cap_c = info['main']
        for dx in range(-5, 6):
            px(d, cx+dx, sy, darker(cap_c, 15))
        for dx in range(-4, 5):
            px(d, cx+dx, sy-1, cap_c)
        for dx in range(-3, 4):
            px(d, cx+dx, sy-2, lighter(cap_c, 15))
        # Brim
        if direction == 0:
            for dx in range(-5, 6):
                px(d, cx+dx, sy+2, darker(cap_c, 25))
        elif direction == 1:
            for dx in range(-7, -1):
                px(d, cx+dx, sy+2, darker(cap_c, 25))
        elif direction == 3:
            for dx in range(2, 8):
                px(d, cx+dx, sy+2, darker(cap_c, 25))
    else:
        # Regular hair
        if direction == 0:  # front
            # Top hair
            for dx in range(-5, 6):
                px(d, cx+dx, sy-1, hair_c)
                px(d, cx+dx, sy, hair_c if abs(dx) < 4 else hair_d)
            for dx in range(-4, 5):
                px(d, cx+dx, sy+1, hair_h if dx < 0 else hair_c)
            # Bangs
            for dx in range(-5, 6):
                px(d, cx+dx, sy+2, hair_c)
            # Side hair
            for dy in range(3, 7):
                px(d, cx-6, sy+dy, hair_d)
                px(d, cx+6, sy+dy, hair_d)
            if female:
                for dy in range(7, 16):
                    px(d, cx-6, sy+dy, hair_c if dy%2 else hair_d)
                    px(d, cx-7, sy+dy, hair_d)
                    px(d, cx+6, sy+dy, hair_c if dy%2 else hair_d)
                    px(d, cx+7, sy+dy, hair_d)
        elif direction == 1:  # left
            for dx in range(-5, 4):
                px(d, cx+dx, sy-1, hair_c)
                px(d, cx+dx, sy, hair_c if dx > -4 else hair_d)
                px(d, cx+dx, sy+1, hair_h if dx < -2 else hair_c)
            for dx in range(-5, 3):
                px(d, cx+dx, sy+2, hair_c)
            for dy in range(3, 7):
                px(d, cx-6, sy+dy, hair_d)
            if female:
                for dy in range(7, 16):
                    px(d, cx-6, sy+dy, hair_c if dy%2 else hair_d)
                    px(d, cx-7, sy+dy, hair_d)
        elif direction == 3:  # right
            for dx in range(-3, 6):
                px(d, cx+dx, sy-1, hair_c)
                px(d, cx+dx, sy, hair_c if dx < 4 else hair_d)
                px(d, cx+dx, sy+1, hair_h if dx > 2 else hair_c)
            for dx in range(-2, 6):
                px(d, cx+dx, sy+2, hair_c)
            for dy in range(3, 7):
                px(d, cx+6, sy+dy, hair_d)
            if female:
                for dy in range(7, 16):
                    px(d, cx+6, sy+dy, hair_c if dy%2 else hair_d)
                    px(d, cx+7, sy+dy, hair_d)

    # ═══ BODY (compact chibi torso) ═══
    body_top = sy + 11 + body_bounce
    body_h = 8

    # Body outline
    for dy in range(body_h):
        w_ = 5 if dy < 2 else (6 if dy < 5 else 5)
        px(d, cx - w_ - 1, body_top + dy, OL)
        px(d, cx + w_ + 1, body_top + dy, OL)
    for dx in range(-5, 6):
        px(d, cx+dx, body_top-1, OL)
        px(d, cx+dx, body_top+body_h, OL)

    # Body fill with shading
    for dy in range(body_h):
        w_ = 5 if dy < 2 else (6 if dy < 5 else 5)
        for dx in range(-w_, w_+1):
            if dx < -w_+1:
                col = sh
            elif dx > w_-1:
                col = sh
            elif dy < 2:
                col = hi
            else:
                col = mc
            px(d, cx+dx, body_top+dy, col)

    # Neck (skin)
    px(d, cx-1, body_top, SKN)
    px(d, cx, body_top, SKN)
    px(d, cx+1, body_top, SKN)

    # Collar / trim detail
    if direction == 0:
        px(d, cx-1, body_top+1, trim)
        px(d, cx, body_top+1, trim)
        px(d, cx+1, body_top+1, trim)
        # Button line
        for dy in range(2, body_h-1):
            px(d, cx, body_top+dy, trim)

    # ═══ ARMS ═══
    arm_top = body_top + 1
    for dy in range(6):
        lx = cx - 7
        rx = cx + 7
        ly_off = walk_off if dy > 2 else 0
        ry_off = -walk_off if dy > 2 else 0
        # Left arm
        px(d, lx, arm_top+dy+ly_off, OL)
        px(d, lx+1, arm_top+dy+ly_off, mc if dy < 4 else sh)
        # Right arm
        px(d, rx, arm_top+dy+ry_off, OL)
        px(d, rx-1, arm_top+dy+ry_off, mc if dy < 4 else sh)
    # Hands
    px(d, cx-7, arm_top+6+walk_off, SKN)
    px(d, cx-6, arm_top+6+walk_off, SKN_S)
    px(d, cx+7, arm_top+6-walk_off, SKN)
    px(d, cx+6, arm_top+6-walk_off, SKN_S)

    # ═══ LEGS ═══
    leg_top = body_top + body_h
    leg_h = 4

    for dy in range(leg_h):
        # Left leg
        llx = cx - 3
        rlx = cx + 1
        if frame == 1:
            llx += 1 if dy >= 2 else 0
            rlx -= 1 if dy >= 2 else 0
        elif frame == 2:
            llx -= 1 if dy >= 2 else 0
            rlx += 1 if dy >= 2 else 0

        for dx in range(3):
            lc = pd if dx == 0 else pc
            px(d, llx+dx, leg_top+dy, lc)
            px(d, rlx+dx, leg_top+dy, lc)
        # Outline
        px(d, llx-1, leg_top+dy, OL)
        px(d, llx+3, leg_top+dy, OL)
        px(d, rlx-1, leg_top+dy, OL)
        px(d, rlx+3, leg_top+dy, OL)

    # ═══ SHOES ═══
    shoe_y = leg_top + leg_h
    shoe_c = c(42, 36, 32)
    shoe_h = c(62, 55, 48)
    sl = 1 if frame == 1 else (-1 if frame == 2 else 0)
    sr = -1 if frame == 1 else (1 if frame == 2 else 0)

    for dx in range(-4, 0):
        px(d, cx+dx+sl, shoe_y, shoe_c)
        px(d, cx+dx+sl, shoe_y-1, OL) if dx == -4 else None
    for dx in range(1, 5):
        px(d, cx+dx+sr, shoe_y, shoe_c)
    # Shoe highlight
    px(d, cx-2+sl, shoe_y, shoe_h)
    px(d, cx+2+sr, shoe_y, shoe_h)
    # Shoe outline
    for dx in range(-4, 0):
        px(d, cx+dx+sl, shoe_y+1, OL)
    for dx in range(1, 5):
        px(d, cx+dx+sr, shoe_y+1, OL)


def gen_characters():
    names = ['chief', 'farmer', 'tech', 'sales', 'delivery', 'livestream', 'inspector', 'finance']
    for name in names:
        img = mk(96, 128)
        d = ImageDraw.Draw(img)
        for dir_ in range(4):
            for frame in range(3):
                draw_chibi(d, frame*32, dir_*32, name, dir_, frame)
        img.save(os.path.join(OUT, f'char-{name}.png'))
    print(f"  {len(names)} character sprite sheets generated")


# ═══════════════════════════════════════════════════════════
#  CROP SPRITES 128×32 (4 stages, 32×32 each)
# ═══════════════════════════════════════════════════════════
def draw_soil_mound(d, ox, oy):
    """Draw a small soil mound at bottom of cell"""
    cx_ = ox + 16
    for x in range(ox+4, ox+28):
        n = random.random()
        col = DT if n < 0.4 else DT_H if n < 0.7 else DT_S
        px(d, x, oy+29, col)
        px(d, x, oy+30, darker(col, 15))
    # Mound shape
    for x in range(ox+6, ox+26):
        dist = abs(x - cx_)
        if dist < 8:
            px(d, x, oy+28, DT_H if dist < 4 else DT)

def draw_plant_outline(d, points, col):
    """Draw outline around a set of points"""
    for (x, y) in points:
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if (nx, ny) not in points:
                px(d, nx, ny, col)

def gen_crops():
    crop_configs = {
        'rice': {
            'colors': [SEED_C, STEM_C, LEAF_C, c(190, 175, 65)],
            'mature_accent': c(225, 200, 60),
        },
        'wheat': {
            'colors': [SEED_C, STEM_C, c(175, 155, 80), c(215, 185, 70)],
            'mature_accent': c(235, 205, 85),
        },
        'tomato': {
            'colors': [SEED_C, STEM_C, c(85, 165, 55), c(225, 48, 28)],
            'mature_accent': c(245, 65, 40),
            'fruit_col': c(220, 45, 25),
        },
        'cabbage': {
            'colors': [SEED_C, LEAF_C, c(100, 180, 80), c(95, 175, 72)],
            'mature_accent': c(175, 218, 148),
        },
        'strawberry': {
            'colors': [SEED_C, LEAF_C, c(235, 105, 145), c(225, 40, 58)],
            'mature_accent': c(245, 60, 75),
        },
        'orange': {
            'colors': [c(100, 70, 40), WOOD, LEAF_C, c(245, 165, 38)],
            'mature_accent': c(255, 180, 50),
        },
        'pepper': {
            'colors': [SEED_C, STEM_C, LEAF_C, c(205, 38, 20)],
            'mature_accent': c(230, 55, 30),
        },
        'lotus': {
            'colors': [SEED_C, STEM_C, c(245, 140, 182), c(248, 145, 185)],
            'mature_accent': c(255, 165, 200),
        },
        'tea': {
            'colors': [SEED_C, WOOD, c(58, 128, 48), c(58, 130, 48)],
            'mature_accent': c(120, 200, 80),
        },
        'corn': {
            'colors': [SEED_C, STEM_C, LEAF_C, c(245, 205, 60)],
            'mature_accent': c(255, 215, 75),
        },
    }

    for name, cfg in crop_configs.items():
        img = mk(128, 32)
        d = ImageDraw.Draw(img)
        cols = cfg['colors']
        acc = cfg['mature_accent']

        for stage in range(4):
            ox = stage * 32
            draw_soil_mound(d, ox, 0)
            cx_ = ox + 16
            base_y = 28

            if stage == 0:
                # Seedling: tiny sprout
                px(d, cx_, base_y-1, cols[0])
                px(d, cx_, base_y-2, cols[0])
                px(d, cx_-1, base_y-3, lighter(cols[0], 15))
                px(d, cx_+1, base_y-3, lighter(cols[0], 15))
                px(d, cx_, base_y-4, lighter(cols[0], 25))

            elif stage == 1:
                # Growing: small plant
                for j in range(7):
                    px(d, cx_, base_y-j, STEM_C if j < 5 else STEM_H)
                # Leaves
                for dx in [-2, -1, 1, 2]:
                    for dy in range(2):
                        leaf_shade = LEAF_H if dy == 0 else LEAF_C
                        px(d, cx_+dx, base_y-5-dy, leaf_shade)
                # Small side leaves
                px(d, cx_-3, base_y-4, LEAF_D)
                px(d, cx_+3, base_y-4, LEAF_D)

            elif stage == 2:
                # Flowering: taller with flowers/early fruit
                for j in range(11):
                    sc = STEM_H if j > 8 else (STEM_C if j > 3 else STEM_D)
                    px(d, cx_, base_y-j, sc)
                    if j > 6:
                        px(d, cx_+1, base_y-j, STEM_D)
                # Leaves
                for dx in range(-3, 4):
                    for dy in range(3):
                        if abs(dx) + dy < 4:
                            lc = LEAF_H if dy == 0 and abs(dx) < 2 else (LEAF_C if dy < 2 else LEAF_D)
                            px(d, cx_+dx, base_y-8-dy, lc)
                # Side leaves
                for dx in [-4, -3, 3, 4]:
                    px(d, cx_+dx, base_y-6, LEAF_C)
                    px(d, cx_+dx, base_y-5, LEAF_D)
                # Flower buds or early fruit
                fc = cols[2]
                px(d, cx_-2, base_y-10, fc)
                px(d, cx_+2, base_y-9, lighter(fc, 20))

            else:  # stage 3 — mature
                # Tall plant with fruit
                for j in range(14):
                    sc = STEM_H if j > 11 else (STEM_C if j > 5 else STEM_D)
                    px(d, cx_, base_y-j, sc)
                    if j > 4:
                        px(d, cx_+1, base_y-j, STEM_D)
                # Lush leaves
                for dx in range(-4, 5):
                    for dy in range(4):
                        if abs(dx) + dy < 5:
                            lc = LEAF_H if dy == 0 else (LEAF_C if dy < 3 else LEAF_D)
                            px(d, cx_+dx, base_y-10-dy, lc)
                for dx in [-5, -4, 4, 5]:
                    px(d, cx_+dx, base_y-8, LEAF_C)
                    px(d, cx_+dx, base_y-7, LEAF_D)
                # Mature fruit
                fruit_c = cols[3]
                fruit_h = acc
                # Main fruits
                for pos in [(-3, -12), (2, -11), (-1, -14), (3, -8)]:
                    fx_, fy_ = cx_ + pos[0], base_y + pos[1]
                    for fdx in range(2):
                        for fdy in range(2):
                            fc_ = fruit_h if fdx == 0 and fdy == 0 else fruit_c
                            px(d, fx_+fdx, fy_+fdy, fc_)
                    # Fruit outline
                    px(d, fx_-1, fy_, OL_L)
                    px(d, fx_+2, fy_+1, OL_L)

                # Dewdrop / sparkle on mature
                px(d, cx_-2, base_y-13, c(255, 255, 255, 200))
                px(d, cx_+3, base_y-10, c(255, 255, 255, 150))

        img.save(os.path.join(OUT, f'crop-{name}.png'))
    print(f"  {len(crop_configs)} crop sprite sheets generated")


# ═══════════════════════════════════════════════════════════
#  BUILDING SPRITES 64×64 — with isometric depth and detail
# ═══════════════════════════════════════════════════════════
def gen_buildings():
    builds = {
        'village-hall': {
            'roof': ROOF_R, 'roof_h': ROOF_H, 'roof_d': ROOF_D,
            'wall': WALL_W, 'wall_h': WALL_H, 'wall_d': WALL_D,
            'feature': 'flag', 'stories': 2, 'wide': True
        },
        'market': {
            'roof': c(65, 85, 145), 'roof_h': c(90, 110, 172), 'roof_d': c(42, 58, 105),
            'wall': WALL_W, 'wall_h': WALL_H, 'wall_d': WALL_D,
            'feature': 'sign', 'stories': 1, 'wide': True
        },
        'warehouse': {
            'roof': c(140, 95, 55), 'roof_h': c(168, 120, 78), 'roof_d': c(108, 68, 35),
            'wall': c(178, 172, 162), 'wall_h': c(195, 190, 182), 'wall_d': c(155, 148, 138),
            'feature': 'crate', 'stories': 1, 'wide': True
        },
        'greenhouse': {
            'roof': GLASS, 'roof_h': GLASS_H, 'roof_d': GLASS_D,
            'wall': WALL_W, 'wall_h': WALL_H, 'wall_d': WALL_D,
            'feature': 'glass_roof', 'stories': 1, 'wide': True
        },
        'weather-station': {
            'roof': METAL, 'roof_h': lighter(METAL, 20), 'roof_d': METAL_D,
            'wall': WALL_W, 'wall_h': WALL_H, 'wall_d': WALL_D,
            'feature': 'antenna', 'stories': 1, 'wide': False
        },
        'lab': {
            'roof': c(240, 240, 248), 'roof_h': c(255, 255, 255), 'roof_d': c(208, 208, 218),
            'wall': WALL_W, 'wall_h': WALL_H, 'wall_d': WALL_D,
            'feature': 'beaker', 'stories': 1, 'wide': False
        },
        'training': {
            'roof': ROOF_R, 'roof_h': ROOF_H, 'roof_d': ROOF_D,
            'wall': WALL_W, 'wall_h': WALL_H, 'wall_d': WALL_D,
            'feature': 'book', 'stories': 1, 'wide': False
        },
        'logistics': {
            'roof': c(225, 135, 45), 'roof_h': c(250, 165, 70), 'roof_d': c(185, 105, 30),
            'wall': c(178, 172, 162), 'wall_h': c(195, 190, 182), 'wall_d': c(155, 148, 138),
            'feature': 'truck', 'stories': 1, 'wide': True
        },
        'livestream': {
            'roof': c(235, 115, 155), 'roof_h': c(255, 148, 185), 'roof_d': c(195, 82, 120),
            'wall': WALL_W, 'wall_h': WALL_H, 'wall_d': WALL_D,
            'feature': 'antenna', 'stories': 1, 'wide': False
        },
    }

    S = 64
    for name, cfg in builds.items():
        img = mk(S, S); d = ImageDraw.Draw(img)
        rc, rh, rd = cfg['roof'], cfg['roof_h'], cfg['roof_d']
        wc, wh, wd = cfg['wall'], cfg['wall_h'], cfg['wall_d']
        feat = cfg['feature']
        wide = cfg['wide']

        margin = 6 if wide else 10
        bw = S - margin * 2  # building width

        # ── Foundation shadow ──
        for x in range(margin+2, S-margin+2):
            for dy in range(3):
                a = 80 - dy * 20
                px(d, x, S-6+dy, c(20, 15, 10, a))

        # ── Foundation ──
        for x in range(margin-1, S-margin+1):
            px(d, x, S-8, ST_S)
            px(d, x, S-7, ST)
            px(d, x, S-6, ST_H)

        # ── Walls ──
        wall_top = 22
        wall_bot = S - 8
        for y in range(wall_top, wall_bot):
            for x in range(margin, S-margin):
                # Left side shadow
                if x < margin + 2:
                    col = wd
                # Right edge highlight
                elif x > S - margin - 3:
                    col = wh
                # Brick pattern
                elif (x + y) % 8 == 0 and y % 4 == 0:
                    col = wd
                else:
                    col = wc
                px(d, x, y, col)

        # Wall outline
        for y in range(wall_top, wall_bot):
            px(d, margin-1, y, OL)
            px(d, S-margin, y, OL)
        for x in range(margin-1, S-margin+1):
            px(d, x, wall_bot, OL)

        # ── Door ──
        door_w = 8
        door_h = 10
        door_x = S // 2 - door_w // 2
        door_y = wall_bot - door_h
        rect(d, door_x, door_y, door_w, door_h, DOOR)
        rect(d, door_x + door_w - 2, door_y, 2, door_h, DOOR_D)
        # Door frame
        for dy in range(door_h):
            px(d, door_x-1, door_y+dy, WOOD_D)
            px(d, door_x+door_w, door_y+dy, WOOD_D)
        for dx in range(-1, door_w+1):
            px(d, door_x+dx, door_y-1, WOOD)
        # Handle
        px(d, door_x+door_w-3, door_y+door_h//2, c(228, 192, 68))
        px(d, door_x+door_w-3, door_y+door_h//2+1, c(195, 162, 48))

        # ── Windows ──
        win_positions = [margin+3, S-margin-9] if wide else [margin+2]
        for wx in win_positions:
            wy = wall_top + 4
            ww_, wh_ = 6, 6
            # Window glass
            for dy in range(wh_):
                for dx in range(ww_):
                    gc = GLASS_H if dx < 2 and dy < 2 else (GLASS if dy < 3 else GLASS_D)
                    px(d, wx+dx, wy+dy, gc)
            # Window frame (wood)
            for dx in range(ww_):
                px(d, wx+dx, wy, WOOD); px(d, wx+dx, wy+wh_-1, WOOD)
            for dy in range(wh_):
                px(d, wx, wy+dy, WOOD); px(d, wx+ww_-1, wy+dy, WOOD)
            # Cross
            px(d, wx+ww_//2-1, wy+1, WOOD)
            px(d, wx+ww_//2-1, wy+wh_-2, WOOD)
            px(d, wx+1, wy+wh_//2, WOOD)
            px(d, wx+ww_-2, wy+wh_//2, WOOD)
            # Warm glow inside
            px(d, wx+2, wy+2, c(255, 235, 180, 120))
            px(d, wx+3, wy+3, c(255, 225, 160, 100))

        # ── Roof ──
        roof_h_px = 16
        if feat == 'glass_roof':
            for ry in range(roof_h_px):
                indent = ry
                for x in range(margin-2+indent, S-margin+2-indent):
                    # Checkerboard glass
                    if (x//4 + ry//4) % 2:
                        col = GLASS
                    else:
                        col = GLASS_H
                    px(d, x, 5+ry, col)
                # Metal frame lines
                if ry % 4 == 0:
                    for x in range(margin-2+indent, S-margin+2-indent):
                        px(d, x, 5+ry, METAL_D)
            # Ridge
            for x in range(S//2-2, S//2+3):
                px(d, x, 5, METAL)
        else:
            for ry in range(roof_h_px):
                indent = ry
                for x in range(margin-2+indent, S-margin+2-indent):
                    # Tile texture
                    if ry % 4 == 0:
                        col = rd  # tile edge
                    elif ry % 4 == 1:
                        col = rh  # tile highlight
                    else:
                        col = rc
                    # Left shadow
                    if x < margin + indent:
                        col = rd
                    px(d, x, 5+ry, col)
            # Ridge highlight
            for x in range(S//2-2, S//2+3):
                px(d, x, 5, rh)
                px(d, x, 4, rd)

        # Roof outline
        for ry in range(roof_h_px):
            indent = ry
            lx = margin-2+indent
            rx = S-margin+1-indent
            if lx < rx:
                px(d, lx, 5+ry, OL)
                px(d, rx, 5+ry, OL)
        for x in range(margin-2, S-margin+2):
            px(d, x, 5+roof_h_px, OL)

        # ── Features ──
        if feat == 'antenna':
            for y in range(0, 6):
                px(d, S//2, y, METAL)
            px(d, S//2-1, 1, METAL); px(d, S//2+1, 1, METAL)
            px(d, S//2-2, 2, METAL_D); px(d, S//2+2, 2, METAL_D)
            # Blinking red light
            px(d, S//2, 0, c(225, 45, 35))
            px(d, S//2-1, 0, c(255, 80, 70, 120))
            px(d, S//2+1, 0, c(255, 80, 70, 120))
        elif feat == 'flag':
            pole_x = S - margin - 2
            for y in range(0, 8):
                px(d, pole_x, y, WOOD)
            # Flag
            flag_c = c(225, 45, 32)
            for dx in range(6):
                for dy in range(3):
                    fc = lighter(flag_c, 15) if dy == 0 else (darker(flag_c, 10) if dy == 2 else flag_c)
                    px(d, pole_x-1-dx, dy, fc)
            # Star on flag
            px(d, pole_x-3, 1, c(255, 215, 0))
        elif feat == 'sign':
            # Sign board under roof
            sign_x = S//2 - 8
            sign_y = wall_bot - 12
            rect(d, sign_x, sign_y-3, 16, 3, WOOD)
            for x in range(sign_x, sign_x+16):
                px(d, x, sign_y-4, c(255, 235, 185))
                px(d, x, sign_y-3, c(245, 225, 172))
        elif feat == 'crate':
            # Crates outside
            cx_ = margin + 1
            cy_ = wall_bot - 5
            rect(d, cx_, cy_, 4, 4, WOOD)
            rect(d, cx_+1, cy_+1, 2, 2, WOOD_H)
            px(d, cx_+1, cy_+2, WOOD_D)  # cross
            px(d, cx_+2, cy_+1, WOOD_D)
        elif feat == 'beaker':
            # Small beaker on windowsill
            bx = S//2 + 5
            by = wall_top + 2
            px(d, bx, by, c(200, 230, 245))
            px(d, bx, by+1, c(180, 215, 235))
            px(d, bx-1, by+1, c(170, 205, 225))
            px(d, bx+1, by+1, c(170, 205, 225))
            px(d, bx, by-1, c(220, 245, 255))  # liquid glow
        elif feat == 'book':
            # Book icon near door
            bx = door_x - 5
            by = wall_bot - 6
            rect(d, bx, by, 3, 4, c(180, 60, 50))
            px(d, bx+1, by+1, c(255, 240, 220))
            px(d, bx+1, by+2, c(255, 240, 220))
        elif feat == 'truck':
            # Small truck outline
            tx = margin + 1
            ty = wall_bot - 4
            rect(d, tx, ty, 6, 3, cfg['roof'])
            rect(d, tx+6, ty+1, 3, 2, METAL)
            px(d, tx+1, ty+3, c(30, 25, 22))  # wheel
            px(d, tx+7, ty+3, c(30, 25, 22))  # wheel

        # ── Chimney ──
        if name in ['village-hall', 'training', 'lab']:
            chx = S//2 + 6
            for y in range(2, 6):
                px(d, chx, y, c(145, 88, 48))
                px(d, chx+1, y, c(125, 72, 35))
            # Smoke
            px(d, chx, 1, c(200, 200, 210, 80))
            px(d, chx-1, 0, c(210, 210, 220, 50))
            px(d, chx+1, 0, c(205, 205, 215, 60))

        img.save(os.path.join(OUT, f'bld-{name}.png'))
    print(f"  {len(builds)} building sprites generated")


# ═══════════════════════════════════════════════════════════
#  UI ICONS 32×32
# ═══════════════════════════════════════════════════════════
def gen_icons():
    # Coin icon
    img = mk(32, 32); d = ImageDraw.Draw(img)
    circle_fill(d, 16, 16, 10, c(255, 215, 0))
    circle_fill(d, 16, 16, 8, c(245, 200, 30))
    circle_fill(d, 16, 16, 6, c(255, 225, 80))
    outline_ellipse(d, 16, 16, 10, 10, c(180, 140, 0))
    # $ symbol
    px(d, 16, 12, c(180, 140, 0)); px(d, 16, 13, c(180, 140, 0))
    px(d, 15, 14, c(180, 140, 0)); px(d, 16, 15, c(180, 140, 0))
    px(d, 17, 16, c(180, 140, 0)); px(d, 16, 17, c(180, 140, 0))
    px(d, 15, 18, c(180, 140, 0)); px(d, 16, 19, c(180, 140, 0))
    px(d, 16, 20, c(180, 140, 0))
    img.save(os.path.join(OUT, 'icon-coin.png'))

    # Grain icon
    img = mk(32, 32); d = ImageDraw.Draw(img)
    # Wheat stalk
    for i in range(10):
        px(d, 16, 8+i, STEM_C)
    for side in [-1, 1]:
        for i in range(4):
            px(d, 16+side*(i+1), 10+i, c(215, 185, 70))
            px(d, 16+side*(i+1), 14+i, c(225, 195, 80))
    px(d, 16, 7, c(235, 205, 85))
    px(d, 15, 6, c(225, 195, 75))
    px(d, 17, 6, c(225, 195, 75))
    img.save(os.path.join(OUT, 'icon-grain.png'))

    # Star icon
    img = mk(32, 32); d = ImageDraw.Draw(img)
    star_c = c(255, 215, 0)
    star_h = c(255, 235, 100)
    pts = [(16,6),(18,13),(25,13),(20,18),(22,25),(16,21),(10,25),(12,18),(7,13),(14,13)]
    for i in range(0, len(pts), 2):
        if i+1 < len(pts):
            x1, y1 = pts[i]
            x2, y2 = pts[i+1]
            for t_ in range(20):
                t = t_ / 19
                px(d, x1+(x2-x1)*t, y1+(y2-y1)*t, star_c)
    circle_fill(d, 16, 16, 4, star_h)
    circle_fill(d, 16, 16, 2, c(255, 245, 180))
    img.save(os.path.join(OUT, 'icon-star.png'))

    print("  3 UI icons generated")


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 50)
    print("  SYNAPSE Sprite Generator v4.0")
    print("  TRUE Q-Version (Chibi) Pixel Art")
    print("=" * 50)

    gen_terrains()
    gen_characters()
    gen_crops()
    gen_buildings()
    gen_icons()

    atlas = {
        "version": "4.0",
        "style": "Q-version chibi pixel art with dark outlines, 3-shade coloring, anime eyes, warm palette",
        "characters": ["chief", "farmer", "tech", "sales", "delivery", "livestream", "inspector", "finance"],
        "crops": ["rice", "wheat", "tomato", "cabbage", "strawberry", "orange", "pepper", "lotus", "tea", "corn"],
        "buildings": ["village-hall", "market", "warehouse", "greenhouse", "weather-station", "lab", "training", "logistics", "livestream"],
        "terrains": ["grass", "dirt", "water", "paddy", "stone", "sand"],
        "icons": ["coin", "grain", "star"],
        "charSheet": {
            "frameW": 32, "frameH": 32, "cols": 3, "rows": 4,
            "desc": "3 frames(idle,walk_a,walk_b) x 4 dirs(down,left,up,right)",
            "style": "Big chibi head (60% body height), round face, 2px anime eyes with highlights, blush marks, outlined"
        },
        "cropSheet": {
            "frameW": 32, "frameH": 32, "stages": 4,
            "desc": "4 growth stages: seedling, growing, flowering, mature with fruit/dewdrops"
        },
        "buildingSize": 64,
        "terrainSize": 48,
        "aiSpec": "All sprites: transparent RGBA PNG, dark outline style, 3-shade shading (highlight/base/shadow). Characters: 96x128 spritesheet. Crops: 128x32. Buildings: 64x64. Terrain: 48x48 tileable."
    }
    with open(os.path.join(OUT, 'atlas.json'), 'w') as f:
        json.dump(atlas, f, indent=2)

    print()
    print("  All sprites saved to:", OUT)
    print("=" * 50)
