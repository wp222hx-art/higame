#!/usr/bin/env python3
"""
Ghibli Sprite Sheet Converter
Converts a 5-row × 3-col high-res reference sprite sheet to the game's 4×3 (96×128) format.

Reference sheet format (5 rows × 3 cols):
  Row 0: Front/Down view (facing camera)
  Row 1: Front-Right diagonal
  Row 2: Right side view  
  Row 3: Back/Up view (facing away)
  Row 4: Left/Back-Left diagonal

Game format (4 rows × 3 cols, 32×32 per frame):
  Row 0: Down    (front facing)
  Row 1: Left
  Row 2: Up      (back facing)
  Row 3: Right

Usage:
  python convert_ghibli_sprite.py <input_spritesheet.png> <output_sprite.png>
"""

import sys
import os
import numpy as np
from PIL import Image, ImageOps

def remove_background_rembg(input_path):
    """Remove background using rembg AI model."""
    from rembg import remove
    
    img = Image.open(input_path)
    arr = np.array(img)
    H, W = arr.shape[:2]
    ROWS, COLS = 5, 3
    cell_h, cell_w = H // ROWS, W // COLS
    
    result = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    cells = {}
    
    for r in range(ROWS):
        for c in range(COLS):
            y0, x0 = r * cell_h, c * cell_w
            cell = img.crop((x0, y0, x0 + cell_w, y0 + cell_h))
            clean_cell = remove(cell)
            cells[(r, c)] = clean_cell
            result.paste(clean_cell, (x0, y0))
    
    return result, cells, cell_h, cell_w

def get_bbox(cell_img, crop_bottom_pct=0, alpha_threshold=20):
    """Get bounding box of opaque pixels."""
    arr = np.array(cell_img)
    ch, cw = arr.shape[:2]
    
    if crop_bottom_pct > 0:
        cutoff = int(ch * (1 - crop_bottom_pct))
        arr_work = arr[:cutoff, :, :]
    else:
        arr_work = arr
    
    mask = arr_work[:,:,3] > alpha_threshold
    if not mask.any():
        return None
    
    rows_with = np.any(mask, axis=1)
    cols_with = np.any(mask, axis=0)
    rmin, rmax = np.where(rows_with)[0][[0, -1]]
    cmin, cmax = np.where(cols_with)[0][[0, -1]]
    return (int(cmin), int(rmin), int(cmax)+1, int(rmax)+1)

def build_game_sheet(cells, frame_size=32):
    """Build the 4×3 game sprite sheet."""
    sheet = Image.new('RGBA', (frame_size * 3, frame_size * 4), (0, 0, 0, 0))
    
    # Direction mapping: game_row -> (ref_row, mirror, crop_bottom_pct)
    directions = {
        0: (0, False, 0),      # Down = Front (Row 0)
        1: (4, False, 0),      # Left = Left diagonal (Row 4)
        2: (3, False, 0.40),   # Up = Back (Row 3), crop bottom 40%
        3: (4, True, 0),       # Right = Mirror of Left
    }
    
    for game_row, (ref_row, mirror, crop_pct) in directions.items():
        bboxes = []
        for col in range(3):
            cell = cells[(ref_row, col)]
            bb = get_bbox(cell, crop_bottom_pct=crop_pct)
            bboxes.append(bb)
        
        valid_bboxes = [bb for bb in bboxes if bb is not None]
        if not valid_bboxes:
            continue
            
        max_w = max(bb[2]-bb[0] for bb in valid_bboxes)
        max_h = max(bb[3]-bb[1] for bb in valid_bboxes)
        max_dim = frame_size - 2
        shared_scale = min(max_dim / max_w, max_dim / max_h)
        
        for col in range(3):
            bbox = bboxes[col]
            if not bbox:
                continue
            
            cell = cells[(ref_row, col)]
            cropped = cell.crop(bbox)
            
            if mirror:
                cropped = ImageOps.mirror(cropped)
            
            cw, ch = cropped.size
            new_w = max(1, int(cw * shared_scale))
            new_h = max(1, int(ch * shared_scale))
            
            resized = cropped.resize((new_w, new_h), Image.LANCZOS)
            
            frame = Image.new('RGBA', (frame_size, frame_size), (0, 0, 0, 0))
            ox = (frame_size - new_w) // 2
            oy = frame_size - new_h - 1
            frame.paste(resized, (ox, oy), resized)
            
            sheet.paste(frame, (col * frame_size, game_row * frame_size), frame)
    
    return sheet

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input_spritesheet.png> <output_sprite.png>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    print(f"Processing: {input_path}")
    print("Step 1: Removing background with AI model...")
    clean_sheet, cells, cell_h, cell_w = remove_background_rembg(input_path)
    
    print("Step 2: Building game sprite sheet (96×128)...")
    sheet = build_game_sheet(cells)
    
    print(f"Step 3: Saving to {output_path}")
    sheet.save(output_path)
    
    # Stats
    arr = np.array(sheet)
    opaque = np.count_nonzero(arr[:,:,3] > 128)
    total = arr.shape[0] * arr.shape[1]
    print(f"Done! Fill rate: {100*opaque/total:.1f}%, Size: {sheet.size[0]}×{sheet.size[1]}")

if __name__ == '__main__':
    main()
