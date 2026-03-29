#!/usr/bin/env python3
"""
SYNAPSE Sprite Generator - Professional pixel art assets
Generates all game sprites with consistent 16-bit style
Target: 48x48 tiles, 32x48 characters (4-dir 3-frame walk), 32x32 crop stages
"""
from PIL import Image, ImageDraw
import os, json, math, random

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'game', 'assets', 'sprites')
os.makedirs(OUT, exist_ok=True)

random.seed(42)

# ===========================================
# COLOR PALETTE (Stardew Valley inspired)
# ===========================================
P = {
    # Skin tones
    'skin': (255, 214, 170), 'skin_shadow': (220, 178, 130), 'skin_dark': (195, 155, 110),
    # Hair
    'hair_black': (40, 35, 50), 'hair_brown': (120, 72, 40), 'hair_gray': (160, 160, 170),
    # Clothing
    'red': (200, 50, 50), 'red_dark': (150, 30, 30),
    'blue': (60, 100, 180), 'blue_dark': (40, 70, 140),
    'green': (50, 160, 70), 'green_dark': (30, 120, 50),
    'orange': (230, 140, 40), 'orange_dark': (190, 110, 20),
    'purple': (140, 70, 170), 'purple_dark': (100, 40, 130),
    'yellow': (240, 210, 60), 'yellow_dark': (200, 170, 30),
    'white': (240, 240, 245), 'white_dark': (200, 200, 210),
    'pink': (230, 120, 160), 'pink_dark': (190, 80, 120),
    'teal': (50, 180, 170), 'teal_dark': (30, 140, 130),
    # Nature
    'grass1': (80, 170, 60), 'grass2': (60, 140, 45), 'grass3': (100, 190, 80),
    'dirt1': (160, 120, 70), 'dirt2': (140, 100, 55), 'dirt3': (180, 140, 90),
    'water1': (60, 130, 200), 'water2': (40, 100, 170), 'water3': (80, 160, 220),
    'sand1': (220, 200, 150), 'sand2': (200, 180, 130), 'sand3': (240, 220, 170),
    'stone1': (140, 140, 150), 'stone2': (110, 110, 120), 'stone3': (170, 170, 180),
    'paddy1': (70, 150, 100), 'paddy2': (50, 120, 75), 'paddy3': (90, 170, 120),
    # Crop colors
    'stem_green': (70, 140, 50), 'stem_dark': (50, 100, 35),
    'leaf_green': (90, 175, 60), 'leaf_dark': (65, 130, 40),
    'seedling': (140, 200, 100), 'mature_gold': (220, 190, 50),
    'tomato_red': (220, 50, 30), 'tomato_green': (80, 160, 50),
    'strawberry': (220, 40, 60), 'pepper_red': (200, 40, 20),
    'cabbage': (100, 180, 80), 'cabbage_inner': (180, 220, 150),
    'orange_fruit': (240, 160, 40), 'lotus_pink': (240, 140, 180),
    'tea_green': (60, 130, 50), 'corn_yellow': (240, 200, 60),
    'wheat_gold': (210, 180, 70), 'wheat_stalk': (170, 150, 80),
    # Building
    'wood': (150, 100, 50), 'wood_dark': (120, 75, 35),
    'roof_red': (180, 60, 40), 'roof_dark': (140, 40, 25),
    'roof_blue': (60, 80, 140), 'roof_blue_dark': (40, 55, 100),
    'wall': (230, 220, 200), 'wall_dark': (200, 190, 170),
    'glass': (180, 220, 240), 'glass_dark': (140, 190, 210),
    'door': (130, 80, 40), 'door_dark': (100, 60, 30),
    'metal': (160, 170, 180), 'metal_dark': (120, 130, 140),
    # Outline
    'outline': (30, 25, 40),
    'outline_light': (60, 50, 70),
}

def px(draw, x, y, color, s=1):
    """Draw a pixel (or scaled pixel)"""
    if isinstance(color, str):
        color = P[color]
    draw.rectangle([x*s, y*s, (x+1)*s-1, (y+1)*s-1], fill=color)

def create_image(w, h):
    return Image.new('RGBA', (w, h), (0,0,0,0))

# ===========================================
# TERRAIN TILES (48x48)
# ===========================================
def gen_terrain():
    TILE = 48
    terrains = {}

    # GRASS
    img = create_image(TILE, TILE)
    d = ImageDraw.Draw(img)
    for y in range(TILE):
        for x in range(TILE):
            r = random.random()
            if r < 0.6: c = P['grass1']
            elif r < 0.85: c = P['grass2']
            else: c = P['grass3']
            # Small flowers randomly
            if random.random() < 0.02:
                c = (220, 220, 100) if random.random() < 0.5 else (200, 180, 220)
            d.point((x, y), fill=c)
    # Grass blades
    for _ in range(15):
        gx, gy = random.randint(2, TILE-3), random.randint(2, TILE-3)
        gc = P['grass3'] if random.random() < 0.5 else (110, 200, 90)
        d.point((gx, gy-1), fill=gc)
        d.point((gx, gy), fill=gc)
    terrains['grass'] = img

    # DIRT
    img = create_image(TILE, TILE)
    d = ImageDraw.Draw(img)
    for y in range(TILE):
        for x in range(TILE):
            r = random.random()
            if r < 0.5: c = P['dirt1']
            elif r < 0.8: c = P['dirt2']
            else: c = P['dirt3']
            if random.random() < 0.03:
                c = tuple(max(0, v - 20) for v in c)
            d.point((x, y), fill=c)
    # Small stones
    for _ in range(5):
        sx, sy = random.randint(3, TILE-4), random.randint(3, TILE-4)
        d.point((sx, sy), fill=P['stone2'])
    terrains['dirt'] = img

    # WATER
    img = create_image(TILE, TILE)
    d = ImageDraw.Draw(img)
    for y in range(TILE):
        for x in range(TILE):
            wave = math.sin(x * 0.3 + y * 0.2) * 0.3
            r = random.random() + wave
            if r < 0.4: c = P['water1']
            elif r < 0.7: c = P['water2']
            else: c = P['water3']
            d.point((x, y), fill=c)
    # Highlights
    for _ in range(8):
        hx, hy = random.randint(5, TILE-6), random.randint(5, TILE-6)
        d.point((hx, hy), fill=(150, 200, 240))
        d.point((hx+1, hy), fill=(140, 190, 230))
    terrains['water'] = img

    # PADDY (rice paddy - wet soil with water)
    img = create_image(TILE, TILE)
    d = ImageDraw.Draw(img)
    for y in range(TILE):
        for x in range(TILE):
            r = random.random()
            if r < 0.4: c = P['paddy1']
            elif r < 0.7: c = P['paddy2']
            else: c = P['paddy3']
            # Water reflection
            if random.random() < 0.15:
                c = (c[0]-10, c[1]+20, c[2]+30)
            d.point((x, y), fill=c)
    terrains['paddy'] = img

    # STONE (path)
    img = create_image(TILE, TILE)
    d = ImageDraw.Draw(img)
    for y in range(TILE):
        for x in range(TILE):
            r = random.random()
            if r < 0.4: c = P['stone1']
            elif r < 0.7: c = P['stone2']
            else: c = P['stone3']
            d.point((x, y), fill=c)
    # Cobblestone pattern
    for by in range(0, TILE, 8):
        for bx in range(0, TILE, 10):
            off = 5 if (by // 8) % 2 else 0
            cx, cy = bx + off, by
            if 0 <= cx < TILE-6 and cy < TILE-5:
                d.rectangle([cx, cy, cx+6, cy+5], outline=P['stone2'])
    terrains['stone'] = img

    # SAND
    img = create_image(TILE, TILE)
    d = ImageDraw.Draw(img)
    for y in range(TILE):
        for x in range(TILE):
            r = random.random()
            if r < 0.5: c = P['sand1']
            elif r < 0.8: c = P['sand2']
            else: c = P['sand3']
            d.point((x, y), fill=c)
    terrains['sand'] = img

    for name, img in terrains.items():
        img.save(os.path.join(OUT, f'terrain-{name}.png'))
    print(f"Generated {len(terrains)} terrain tiles")

# ===========================================
# CHARACTER SPRITES (96x128 = 3 frames x 4 dirs, each 32x32)
# ===========================================
def draw_character(draw, ox, oy, hair_c, clothes_c, clothes_dark, pants_c, accessory=None, is_female=False):
    """Draw a single character frame at offset (ox, oy) within a 32x32 cell"""
    o = P['outline']
    s = P['skin']
    sd = P['skin_shadow']
    h = hair_c
    cl = clothes_c
    cld = clothes_dark

    # Head (8x8 centered)
    hx, hy = ox + 12, oy + 2
    # Hair top
    for x in range(hx-1, hx+9):
        draw.point((x, hy), fill=h)
    for x in range(hx, hx+8):
        draw.point((x, hy+1), fill=h)
    # Face
    for y in range(hy+2, hy+7):
        for x in range(hx, hx+8):
            draw.point((x, y), fill=s)
    # Hair sides
    draw.point((hx, hy+2), fill=h)
    draw.point((hx, hy+3), fill=h)
    draw.point((hx+7, hy+2), fill=h)
    draw.point((hx+7, hy+3), fill=h)
    # Eyes
    draw.point((hx+2, hy+3), fill=o)
    draw.point((hx+3, hy+3), fill=o)
    draw.point((hx+5, hy+3), fill=o)
    draw.point((hx+6, hy+3), fill=o)
    # Eye whites
    draw.point((hx+2, hy+4), fill=(255,255,255))
    draw.point((hx+5, hy+4), fill=(255,255,255))
    # Mouth
    draw.point((hx+3, hy+5), fill=sd)
    draw.point((hx+4, hy+5), fill=sd)
    # Face outline
    draw.point((hx-1, hy+2), fill=o)
    draw.point((hx-1, hy+3), fill=o)
    draw.point((hx-1, hy+4), fill=o)
    draw.point((hx-1, hy+5), fill=o)
    draw.point((hx+8, hy+2), fill=o)
    draw.point((hx+8, hy+3), fill=o)
    draw.point((hx+8, hy+4), fill=o)
    draw.point((hx+8, hy+5), fill=o)
    for x in range(hx, hx+8):
        draw.point((x, hy+7), fill=o)

    if is_female:
        # Long hair sides
        draw.point((hx-1, hy+5), fill=h)
        draw.point((hx-1, hy+6), fill=h)
        draw.point((hx-1, hy+7), fill=h)
        draw.point((hx+8, hy+5), fill=h)
        draw.point((hx+8, hy+6), fill=h)
        draw.point((hx+8, hy+7), fill=h)

    # Body (centered, 10px wide)
    bx, by = ox + 11, oy + 10
    # Torso
    for y in range(by, by+8):
        for x in range(bx, bx+10):
            c = cld if x < bx+2 or x > bx+7 else cl
            draw.point((x, y), fill=c)
    # Collar
    draw.point((bx+4, by), fill=s)
    draw.point((bx+5, by), fill=s)

    # Arms
    for y in range(by+1, by+7):
        draw.point((bx-1, y), fill=cl)
        draw.point((bx+10, y), fill=cl)
    # Hands
    draw.point((bx-1, by+7), fill=s)
    draw.point((bx+10, by+7), fill=s)

    # Pants/Legs
    ly = by + 8
    for y in range(ly, ly+6):
        for x in range(bx+1, bx+4):
            draw.point((x, y), fill=pants_c)
        for x in range(bx+6, bx+9):
            draw.point((x, y), fill=pants_c)
    # Gap between legs
    for y in range(ly+2, ly+6):
        draw.point((bx+4, y), fill=(0,0,0,0))
        draw.point((bx+5, y), fill=(0,0,0,0))

    # Shoes
    sy = ly + 6
    for x in range(bx, bx+4):
        draw.point((x, sy), fill=o)
    for x in range(bx+6, bx+10):
        draw.point((x, sy), fill=o)

    # Accessory
    if accessory == 'hat':
        for x in range(hx-2, hx+10):
            draw.point((x, hy-1), fill=P['yellow'])
        for x in range(hx-1, hx+9):
            draw.point((x, hy-2), fill=P['yellow_dark'])
    elif accessory == 'glasses':
        draw.point((hx+1, hy+3), fill=P['metal'])
        draw.point((hx+2, hy+3), fill=P['glass'])
        draw.point((hx+3, hy+3), fill=P['metal'])
        draw.point((hx+4, hy+3), fill=P['metal'])
        draw.point((hx+5, hy+3), fill=P['glass'])
        draw.point((hx+6, hy+3), fill=P['metal'])
    elif accessory == 'headband':
        for x in range(hx, hx+8):
            draw.point((x, hy+1), fill=P['red'])

def gen_char_sheet(name, hair_c, clothes_c, clothes_dark, pants_c, accessory=None, is_female=False):
    """Generate a 96x128 sprite sheet: 3 columns (frames) x 4 rows (directions)"""
    FW, FH = 32, 32
    img = create_image(FW*3, FH*4)
    d = ImageDraw.Draw(img)

    for direction in range(4):  # down, left, up, right
        for frame in range(3):
            ox = frame * FW
            oy = direction * FH

            # Walk animation: frame 0=idle, 1=left step, 2=right step
            draw_character(d, ox, oy, hair_c, clothes_c, clothes_dark, pants_c, accessory, is_female)

            # Walking leg offset for frames 1 and 2
            bx, by = ox + 11, oy + 10
            ly = by + 8
            if frame == 1:
                # Left leg forward
                d.point((bx+1, ly+6), fill=P['outline'])
                d.point((bx+2, ly+6), fill=P['outline'])
                d.point((bx+7, ly+5), fill=pants_c)
            elif frame == 2:
                # Right leg forward
                d.point((bx+7, ly+6), fill=P['outline'])
                d.point((bx+8, ly+6), fill=P['outline'])
                d.point((bx+2, ly+5), fill=pants_c)

    img.save(os.path.join(OUT, f'char-{name}.png'))

def gen_characters():
    chars = [
        ('chief', P['hair_black'], P['red'], P['red_dark'], (60, 60, 80), 'hat', False),
        ('farmer', P['hair_brown'], P['green'], P['green_dark'], (100, 80, 50), 'hat', True),
        ('tech', P['hair_black'], P['blue'], P['blue_dark'], (50, 50, 60), 'glasses', False),
        ('sales', P['hair_brown'], P['orange'], P['orange_dark'], (70, 60, 50), None, False),
        ('delivery', P['hair_black'], P['teal'], P['teal_dark'], (60, 60, 70), None, False),
        ('livestream', P['hair_black'], P['pink'], P['pink_dark'], (60, 50, 70), 'headband', True),
        ('inspector', P['hair_gray'], P['white'], P['white_dark'], (50, 50, 60), 'glasses', False),
        ('finance', P['hair_black'], P['purple'], P['purple_dark'], (60, 60, 70), None, False),
    ]
    for args in chars:
        gen_char_sheet(*args)
    print(f"Generated {len(chars)} character sprites")

# ===========================================
# CROP SPRITES (128x32 = 4 stages x 32px each)
# ===========================================
def draw_crop_stage(draw, ox, oy, stage, crop_type):
    """Draw a crop at a specific growth stage in a 32x32 cell"""
    # stage: 0=seedling, 1=growing, 2=flowering, 3=mature
    cx, cy = ox + 16, oy + 28  # base center

    if crop_type == 'rice':
        colors = [P['seedling'], P['stem_green'], P['leaf_green'], P['mature_gold']]
        heights = [4, 10, 16, 20]
        c = colors[stage]
        h = heights[stage]
        # Stalks
        for i in range(-2, 3):
            sx = cx + i * 3
            for dy in range(h):
                draw.point((sx, cy - dy), fill=c)
                if stage >= 2 and dy > h-4:
                    draw.point((sx-1, cy - dy), fill=c)
                    draw.point((sx+1, cy - dy), fill=c)
        if stage == 3:
            # Rice grains drooping
            for i in range(-2, 3):
                sx = cx + i * 3
                draw.point((sx+1, cy-h+1), fill=P['mature_gold'])
                draw.point((sx+2, cy-h+2), fill=P['mature_gold'])
                draw.point((sx+2, cy-h+3), fill=P['wheat_gold'])
        # Soil
        for x in range(ox+4, ox+28):
            draw.point((x, cy+1), fill=P['dirt2'])
            draw.point((x, cy+2), fill=P['dirt1'])

    elif crop_type == 'wheat':
        colors = [P['seedling'], P['stem_green'], P['wheat_stalk'], P['wheat_gold']]
        heights = [3, 8, 14, 18]
        c = colors[stage]
        h = heights[stage]
        for i in range(-3, 4):
            sx = cx + i * 2
            for dy in range(h):
                draw.point((sx, cy - dy), fill=c)
        if stage >= 2:
            for i in range(-3, 4):
                sx = cx + i * 2
                draw.point((sx, cy-h), fill=P['wheat_gold'])
                draw.point((sx, cy-h-1), fill=P['wheat_gold'])
        for x in range(ox+4, ox+28):
            draw.point((x, cy+1), fill=P['dirt2'])

    elif crop_type == 'tomato':
        heights = [3, 8, 14, 16]
        h = heights[stage]
        # Stem
        draw.point((cx, cy), fill=P['stem_dark'])
        for dy in range(h):
            draw.point((cx, cy-dy), fill=P['stem_green'])
        if stage >= 1:
            # Leaves
            for dx in [-3, -2, 2, 3]:
                draw.point((cx+dx, cy-h//2), fill=P['leaf_green'])
                draw.point((cx+dx, cy-h//2-1), fill=P['leaf_green'])
        if stage >= 2:
            draw.point((cx-2, cy-h+2), fill=P['tomato_green'])
            draw.point((cx+2, cy-h+2), fill=P['tomato_green'])
        if stage == 3:
            # Red tomatoes
            for tx, ty in [(-3, -4), (0, -6), (3, -3)]:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        draw.point((cx+tx+dx, cy+ty+dy-8), fill=P['tomato_red'])
        for x in range(ox+6, ox+26):
            draw.point((x, cy+1), fill=P['dirt2'])

    elif crop_type == 'cabbage':
        heights = [2, 5, 8, 10]
        h = heights[stage]
        if stage == 0:
            draw.point((cx, cy-1), fill=P['seedling'])
            draw.point((cx, cy-2), fill=P['seedling'])
        elif stage == 1:
            for dx in range(-2, 3):
                for dy in range(h):
                    if abs(dx) + dy < h:
                        draw.point((cx+dx, cy-dy), fill=P['leaf_green'])
        elif stage >= 2:
            sz = 4 if stage == 2 else 6
            for dx in range(-sz, sz+1):
                for dy in range(-sz, sz+1):
                    if dx*dx + dy*dy <= sz*sz:
                        c = P['cabbage_inner'] if dx*dx+dy*dy < (sz-2)*(sz-2) else P['cabbage']
                        draw.point((cx+dx, cy-h//2+dy), fill=c)
            # Outer leaves
            for dx in [-sz-1, sz+1]:
                draw.point((cx+dx, cy-h//2), fill=P['leaf_green'])
                draw.point((cx+dx, cy-h//2+1), fill=P['leaf_green'])
        for x in range(ox+6, ox+26):
            draw.point((x, cy+1), fill=P['dirt2'])

    elif crop_type == 'strawberry':
        heights = [2, 6, 10, 12]
        h = heights[stage]
        # Low bush
        draw.point((cx, cy), fill=P['stem_dark'])
        for dy in range(min(h, 4)):
            draw.point((cx, cy-dy), fill=P['stem_green'])
        if stage >= 1:
            for dx in range(-3, 4):
                for dy in range(0, min(h-2, 5)):
                    if abs(dx) < 4 - dy//2:
                        draw.point((cx+dx, cy-2-dy), fill=P['leaf_green'])
        if stage >= 2:
            draw.point((cx-2, cy-1), fill=P['pink'] if stage == 2 else P['strawberry'])
            draw.point((cx+2, cy-1), fill=P['pink'] if stage == 2 else P['strawberry'])
        if stage == 3:
            for bx, by in [(-3, 0), (0, -1), (3, 0), (-1, 1), (2, 1)]:
                draw.point((cx+bx, cy+by-3), fill=P['strawberry'])
                draw.point((cx+bx, cy+by-2), fill=P['strawberry'])
                draw.point((cx+bx+1, cy+by-3), fill=P['strawberry'])
        for x in range(ox+6, ox+26):
            draw.point((x, cy+1), fill=P['dirt2'])

    elif crop_type == 'orange':
        heights = [3, 10, 16, 20]
        h = heights[stage]
        # Tree trunk
        for dy in range(min(h, 8)):
            draw.point((cx, cy-dy), fill=P['wood'])
            draw.point((cx+1, cy-dy), fill=P['wood_dark'])
        if stage >= 1:
            # Canopy
            sz = 3 if stage == 1 else (5 if stage == 2 else 7)
            top = cy - min(h, 8)
            for dx in range(-sz, sz+1):
                for dy in range(-sz, sz+1):
                    if dx*dx + dy*dy <= sz*sz:
                        draw.point((cx+dx, top+dy), fill=P['leaf_green'] if (dx+dy)%3 else P['leaf_dark'])
        if stage == 3:
            for ox2, oy2 in [(-3, -2), (2, -3), (0, -1), (-2, -4), (3, -1)]:
                draw.point((cx+ox2, cy-10+oy2), fill=P['orange_fruit'])
                draw.point((cx+ox2+1, cy-10+oy2), fill=P['orange_fruit'])
        for x in range(ox+6, ox+26):
            draw.point((x, cy+1), fill=P['dirt2'])

    elif crop_type == 'pepper':
        heights = [3, 8, 12, 14]
        h = heights[stage]
        for dy in range(h):
            draw.point((cx, cy-dy), fill=P['stem_green'])
        if stage >= 1:
            for dx in [-2, -1, 1, 2]:
                draw.point((cx+dx, cy-h//2), fill=P['leaf_green'])
                draw.point((cx+dx, cy-h//2-1), fill=P['leaf_dark'])
        if stage >= 2:
            pc = P['tomato_green'] if stage == 2 else P['pepper_red']
            for px2, py2 in [(-2, -2), (2, -4), (0, -6)]:
                draw.point((cx+px2, cy+py2-4), fill=pc)
                draw.point((cx+px2, cy+py2-3), fill=pc)
                draw.point((cx+px2, cy+py2-2), fill=pc)
        for x in range(ox+6, ox+26):
            draw.point((x, cy+1), fill=P['dirt2'])

    elif crop_type == 'lotus':
        # Water plant
        for x in range(ox+2, ox+30):
            draw.point((x, cy+1), fill=P['water2'])
            draw.point((x, cy+2), fill=P['water1'])
        heights = [2, 6, 10, 14]
        h = heights[stage]
        if stage == 0:
            draw.point((cx, cy), fill=P['seedling'])
            draw.point((cx, cy-1), fill=P['seedling'])
        else:
            # Stems from water
            for i in range(-1, 2):
                sx = cx + i * 4
                for dy in range(h):
                    draw.point((sx, cy-dy), fill=P['stem_green'])
            # Lily pads
            if stage >= 1:
                for i in range(-1, 2):
                    sx = cx + i * 4
                    for dx in range(-2, 3):
                        draw.point((sx+dx, cy), fill=P['paddy1'])
            if stage >= 2:
                # Flower buds/blooms
                fc = P['lotus_pink'] if stage >= 2 else P['pink']
                for i in [-1, 1]:
                    sx = cx + i * 4
                    draw.point((sx, cy-h+1), fill=fc)
                    draw.point((sx-1, cy-h+2), fill=fc)
                    draw.point((sx+1, cy-h+2), fill=fc)
            if stage == 3:
                draw.point((cx, cy-h), fill=P['lotus_pink'])
                draw.point((cx-1, cy-h+1), fill=P['lotus_pink'])
                draw.point((cx+1, cy-h+1), fill=P['lotus_pink'])
                draw.point((cx-2, cy-h+2), fill=(255,180,200))
                draw.point((cx+2, cy-h+2), fill=(255,180,200))

    elif crop_type == 'tea':
        heights = [3, 8, 14, 16]
        h = heights[stage]
        # Bush shape
        draw.point((cx, cy), fill=P['stem_dark'])
        for dy in range(min(h, 5)):
            draw.point((cx, cy-dy), fill=P['wood'])
        if stage >= 1:
            sz = 2 if stage == 1 else (4 if stage == 2 else 6)
            top = cy - 5
            for dx in range(-sz, sz+1):
                for dy in range(-sz//2, sz//2+1):
                    if abs(dx) + abs(dy) <= sz:
                        draw.point((cx+dx, top+dy), fill=P['tea_green'] if (dx+dy)%2 else P['leaf_dark'])
        if stage == 3:
            # Tea leaf tips (lighter)
            for dx in range(-5, 6, 2):
                draw.point((cx+dx, cy-8), fill=(120, 200, 80))
        for x in range(ox+6, ox+26):
            draw.point((x, cy+1), fill=P['dirt2'])

    elif crop_type == 'corn':
        heights = [3, 10, 18, 22]
        h = heights[stage]
        # Stalk
        for dy in range(h):
            draw.point((cx, cy-dy), fill=P['stem_green'])
            if stage >= 2 and dy > 3:
                draw.point((cx+1, cy-dy), fill=P['stem_green'])
        if stage >= 1:
            # Leaves
            for lh in [h//3, h*2//3]:
                draw.point((cx-1, cy-lh), fill=P['leaf_green'])
                draw.point((cx-2, cy-lh), fill=P['leaf_green'])
                draw.point((cx-3, cy-lh+1), fill=P['leaf_green'])
                draw.point((cx+1, cy-lh-1), fill=P['leaf_green'])
                draw.point((cx+2, cy-lh-1), fill=P['leaf_green'])
                draw.point((cx+3, cy-lh), fill=P['leaf_green'])
        if stage >= 2:
            # Corn ear forming
            ey = cy - h + 4
            draw.point((cx+1, ey), fill=P['corn_yellow'] if stage == 3 else P['stem_green'])
            draw.point((cx+1, ey+1), fill=P['corn_yellow'] if stage == 3 else P['stem_green'])
            draw.point((cx+1, ey+2), fill=P['corn_yellow'] if stage == 3 else P['stem_green'])
            draw.point((cx+2, ey+1), fill=P['corn_yellow'] if stage == 3 else P['stem_green'])
        if stage == 3:
            # Tassel
            draw.point((cx, cy-h), fill=P['wheat_gold'])
            draw.point((cx-1, cy-h+1), fill=P['wheat_gold'])
            draw.point((cx+1, cy-h+1), fill=P['wheat_gold'])
        for x in range(ox+6, ox+26):
            draw.point((x, cy+1), fill=P['dirt2'])


def gen_crops():
    crop_types = ['rice', 'wheat', 'tomato', 'cabbage', 'strawberry', 'orange', 'pepper', 'lotus', 'tea', 'corn']
    for ct in crop_types:
        img = create_image(128, 32)
        d = ImageDraw.Draw(img)
        for stage in range(4):
            draw_crop_stage(d, stage * 32, 0, stage, ct)
        img.save(os.path.join(OUT, f'crop-{ct}.png'))
    print(f"Generated {len(crop_types)} crop sprites")

# ===========================================
# BUILDING SPRITES (64x64 for better detail)
# ===========================================
def gen_buildings():
    BSIZ = 64
    buildings = {}

    def make_building(name, roof_c, roof_dc, wall_c, wall_dc, features=None):
        img = create_image(BSIZ, BSIZ)
        d = ImageDraw.Draw(img)
        o = P['outline']

        # Foundation
        for x in range(8, BSIZ-8):
            for y in range(BSIZ-12, BSIZ-6):
                d.point((x, y), fill=P['stone2'])

        # Walls
        for x in range(10, BSIZ-10):
            for y in range(20, BSIZ-12):
                d.point((x, y), fill=wall_c if (x+y)%7 else wall_dc)

        # Door
        dx_start = BSIZ//2 - 4
        for x in range(dx_start, dx_start+8):
            for y in range(BSIZ-20, BSIZ-12):
                d.point((x, y), fill=P['door'] if x < dx_start+7 else P['door_dark'])
        # Door handle
        d.point((dx_start+6, BSIZ-16), fill=P['yellow'])

        # Windows
        for wx in [14, BSIZ-20]:
            for x in range(wx, wx+5):
                for y in range(26, 32):
                    d.point((x, y), fill=P['glass'] if (x+y)%3 else P['glass_dark'])
            d.rectangle([wx, 26, wx+4, 31], outline=P['wood'])

        # Roof (triangular)
        for ry in range(0, 16):
            indent = ry
            for x in range(6+indent, BSIZ-6-indent):
                c = roof_c if ry % 3 else roof_dc
                d.point((x, 4+ry), fill=c)
        # Roof ridge
        for x in range(BSIZ//2-1, BSIZ//2+2):
            d.point((x, 4), fill=roof_dc)

        # Features
        if features == 'antenna':
            for y in range(0, 6):
                d.point((BSIZ//2, y), fill=P['metal'])
            d.point((BSIZ//2-1, 1), fill=P['metal'])
            d.point((BSIZ//2+1, 1), fill=P['metal'])
        elif features == 'chimney':
            for y in range(0, 8):
                d.point((BSIZ-16, y), fill=P['stone2'])
                d.point((BSIZ-15, y), fill=P['stone1'])
        elif features == 'sign':
            for x in range(BSIZ//2-6, BSIZ//2+6):
                for y in range(BSIZ-10, BSIZ-7):
                    d.point((x, y), fill=P['wood'])
        elif features == 'glass_roof':
            # Override roof with glass panels
            for ry in range(0, 16):
                indent = ry
                for x in range(6+indent, BSIZ-6-indent):
                    c = P['glass'] if (x//4 + ry//4) % 2 else P['glass_dark']
                    d.point((x, 4+ry), fill=c)
            # Metal frame
            for ry in range(0, 16, 4):
                indent = ry
                for x in range(6+indent, BSIZ-6-indent):
                    d.point((x, 4+ry), fill=P['metal'])

        buildings[name] = img

    make_building('village-hall', P['roof_red'], P['roof_dark'], P['wall'], P['wall_dark'], 'chimney')
    make_building('market', P['roof_blue'], P['roof_blue_dark'], P['wall'], P['wall_dark'], 'sign')
    make_building('warehouse', P['roof_dark'], (100, 30, 20), P['stone1'], P['stone2'])
    make_building('greenhouse', P['glass'], P['glass_dark'], P['wall'], P['wall_dark'], 'glass_roof')
    make_building('weather-station', P['metal'], P['metal_dark'], P['wall'], P['wall_dark'], 'antenna')
    make_building('lab', (240, 240, 250), (210, 210, 220), P['wall'], P['wall_dark'])
    make_building('training', P['roof_red'], P['roof_dark'], P['wall'], P['wall_dark'])
    make_building('logistics', P['orange'], P['orange_dark'], P['stone1'], P['stone2'])
    make_building('livestream', P['pink'], P['pink_dark'], P['wall'], P['wall_dark'], 'antenna')

    for name, img in buildings.items():
        img.save(os.path.join(OUT, f'bld-{name}.png'))
    print(f"Generated {len(buildings)} building sprites")

# ===========================================
# UI ICONS (32x32)
# ===========================================
def gen_ui_icons():
    ISIZ = 32
    icons = {}

    def make_icon(name, draw_fn):
        img = create_image(ISIZ, ISIZ)
        d = ImageDraw.Draw(img)
        draw_fn(d, ISIZ)
        icons[name] = img

    def icon_coin(d, s):
        cx, cy = s//2, s//2
        for dx in range(-6, 7):
            for dy in range(-6, 7):
                if dx*dx + dy*dy <= 36:
                    c = P['yellow'] if dx*dx+dy*dy < 25 else P['yellow_dark']
                    d.point((cx+dx, cy+dy), fill=c)
        d.point((cx, cy), fill=P['yellow_dark'])

    def icon_grain(d, s):
        for dy in range(20):
            d.point((s//2, s-4-dy), fill=P['wheat_stalk'])
        for i in range(-2, 3):
            d.point((s//2+i, 6), fill=P['wheat_gold'])
            d.point((s//2+i, 7), fill=P['wheat_gold'])

    def icon_star(d, s):
        cx, cy = s//2, s//2
        pts = []
        for i in range(5):
            a = math.radians(i * 72 - 90)
            pts.append((cx + int(8*math.cos(a)), cy + int(8*math.sin(a))))
            a2 = math.radians(i * 72 - 90 + 36)
            pts.append((cx + int(4*math.cos(a2)), cy + int(4*math.sin(a2))))
        d.polygon(pts, fill=P['yellow'], outline=P['yellow_dark'])

    make_icon('coin', icon_coin)
    make_icon('grain', icon_grain)
    make_icon('star', icon_star)

    for name, img in icons.items():
        img.save(os.path.join(OUT, f'icon-{name}.png'))
    print(f"Generated {len(icons)} UI icons")

# ===========================================
# MAIN
# ===========================================
if __name__ == '__main__':
    print("SYNAPSE Sprite Generator v2.0")
    print("=" * 40)
    gen_terrain()
    gen_characters()
    gen_crops()
    gen_buildings()
    gen_ui_icons()

    # Update atlas
    atlas = {
        "characters": ["chief", "farmer", "tech", "sales", "delivery", "livestream", "inspector", "finance"],
        "crops": ["rice", "wheat", "tomato", "cabbage", "strawberry", "orange", "pepper", "lotus", "tea", "corn"],
        "buildings": ["village-hall", "market", "warehouse", "greenhouse", "weather-station", "lab", "training", "logistics", "livestream"],
        "terrains": ["grass", "dirt", "water", "paddy", "stone", "sand"],
        "charSize": {"frameW": 32, "frameH": 32, "cols": 3, "rows": 4},
        "cropSize": {"frameW": 32, "frameH": 32, "stages": 4},
        "buildingSize": 64,
        "terrainSize": 48,
        "style": "16-bit pixel art, Stardew Valley inspired, warm tones",
        "palette": "consistent earth/nature colors with high saturation"
    }
    with open(os.path.join(OUT, 'atlas.json'), 'w') as f:
        json.dump(atlas, f, indent=2)

    print("\nAll sprites generated successfully!")
    print(f"Output: {OUT}")
