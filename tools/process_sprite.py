#!/usr/bin/env python3
"""
SYNAPSE Character Sprite Processor
Converts an uploaded character image into a 4-direction walk animation sprite sheet.

Supports:
  - Already-complete 4×3 sprite sheets (any size, with or without transparency)
  - 5×3 reference sheets (remapped to 4×3)
  - Single character images (auto-generates 4 directions)

Input: Any character image or sprite sheet
Output: sprite sheet with 4 rows × 3 columns
  Row 0: Down (front) - 3 walk frames
  Row 1: Left - 3 walk frames
  Row 2: Up (back) - 3 walk frames
  Row 3: Right - 3 walk frames
"""

import sys
import os
import json
import numpy as np
from PIL import Image, ImageFilter

# ============================================================
# BACKGROUND REMOVAL
# ============================================================

def remove_background(img):
    """Remove background using rembg if available, otherwise use simple method."""
    try:
        from rembg import remove
        import io
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        result = remove(buf.read())
        return Image.open(io.BytesIO(result)).convert('RGBA')
    except ImportError:
        return simple_bg_remove(img)


def simple_bg_remove(img):
    """Simple background removal using flood fill from corners."""
    img = img.convert('RGBA')
    arr = np.array(img)
    h, w = arr.shape[:2]
    
    # Sample corner colors
    corners = [arr[0,0,:3], arr[0,w-1,:3], arr[h-1,0,:3], arr[h-1,w-1,:3]]
    bg_color = np.mean(corners, axis=0)
    
    # Create mask based on color distance from background
    diff = np.sqrt(np.sum((arr[:,:,:3].astype(float) - bg_color) ** 2, axis=2))
    mask = diff < 30
    arr[mask, 3] = 0
    return Image.fromarray(arr)


def remove_checker_background(img):
    """
    Remove baked-in checkerboard background from sprite sheets.
    Checkerboard patterns alternate between two similar gray tones
    in a regular grid pattern.
    """
    img = img.convert('RGBA')
    arr = np.array(img, dtype=np.float64)
    h, w = arr.shape[:2]
    
    # Check if image has real transparency already
    if np.sum(arr[:,:,3] == 0) > (h * w * 0.05):
        # Already has >5% transparent pixels, probably fine
        return img
    
    # Detect checkerboard: sample from corners where we expect no character
    # Take 4 corners, 20×20 each
    corner_size = min(20, h // 8, w // 8)
    if corner_size < 4:
        return img
    
    corners = [
        arr[0:corner_size, 0:corner_size, :3],                    # top-left
        arr[0:corner_size, w-corner_size:w, :3],                   # top-right
        arr[h-corner_size:h, 0:corner_size, :3],                   # bottom-left
        arr[h-corner_size:h, w-corner_size:w, :3],                 # bottom-right
    ]
    
    # Check if corners have a checkerboard pattern (two alternating colors)
    all_corner_pixels = np.vstack([c.reshape(-1, 3) for c in corners])
    
    # Find the two dominant colors using simple clustering
    mean_color = np.mean(all_corner_pixels, axis=0)
    above = all_corner_pixels[np.sum((all_corner_pixels - mean_color) ** 2, axis=1) > 0]
    
    if len(above) < 10:
        return img  # All same color, not a checkerboard
    
    # Two clusters: above and below mean brightness
    brightness = np.sum(all_corner_pixels, axis=1)
    median_brightness = np.median(brightness)
    dark_pixels = all_corner_pixels[brightness <= median_brightness]
    light_pixels = all_corner_pixels[brightness > median_brightness]
    
    if len(dark_pixels) < 5 or len(light_pixels) < 5:
        return img
    
    color_dark = np.mean(dark_pixels, axis=0)
    color_light = np.mean(light_pixels, axis=0)
    
    # Check if these two colors are close (both grayish) - typical checker pattern
    color_diff = np.sqrt(np.sum((color_dark - color_light) ** 2))
    if color_diff > 80:
        # Colors too different, probably not a checkerboard
        return img
    
    # Now remove all pixels that are close to either checker color
    pixel_colors = arr[:,:,:3]
    dist_dark = np.sqrt(np.sum((pixel_colors - color_dark) ** 2, axis=2))
    dist_light = np.sqrt(np.sum((pixel_colors - color_light) ** 2, axis=2))
    
    # Adaptive threshold: tighter for better precision
    threshold = max(20, color_diff * 0.6)
    checker_mask = (dist_dark < threshold) | (dist_light < threshold)
    
    # Apply: set checker pixels to transparent
    result = arr.astype(np.uint8)
    result[checker_mask, 3] = 0
    
    # Clean up edges with small blur on alpha to reduce jagged edges
    result_img = Image.fromarray(result)
    
    # Check if we removed a reasonable amount (not too much, not too little)
    removed_pct = np.sum(checker_mask) / (h * w) * 100
    if removed_pct < 5 or removed_pct > 90:
        # Either too little or too much removed, something is wrong
        return img
    
    return result_img


# ============================================================
# SPRITE SHEET DETECTION & PROCESSING
# ============================================================

def detect_sheet_layout(img):
    """
    Detect if image is a sprite sheet and return (cols, rows, cell_w, cell_h).
    Returns None if not a recognizable sheet.
    """
    w, h = img.size
    
    # Check 4×3 layout (our target format: 3 cols × 4 rows)
    if w >= 60 and h >= 80:
        cw3 = w / 3
        ch4 = h / 4
        ratio_4x3 = cw3 / ch4 if ch4 > 0 else 999
        if 0.7 < ratio_4x3 < 1.4:
            return (3, 4, int(round(cw3)), int(round(ch4)))
    
    # Check 5×3 layout (reference format: 3 cols × 5 rows)
    if w >= 200 and h >= 300:
        cw3 = w / 3
        ch5 = h / 5
        ratio_5x3 = cw3 / ch5 if ch5 > 0 else 999
        if 0.7 < ratio_5x3 < 1.4:
            return (3, 5, int(round(cw3)), int(round(ch5)))
    
    return None


def process_4x3_sheet(img, target_frame_size=0):
    """
    Process an already-formatted 4×3 sprite sheet.
    - Remove checkerboard/background from each cell
    - Optionally resize to target_frame_size (0 = keep original)
    - Returns (sheet, actual_frame_size)
    """
    img = img.convert('RGBA')
    w, h = img.size
    src_fw = w / 3
    src_fh = h / 4
    
    # First, remove any baked-in checkerboard background
    clean = remove_checker_background(img)
    
    # If still no transparency, try per-cell background removal
    clean_arr = np.array(clean)
    transparent_pct = np.sum(clean_arr[:,:,3] == 0) / (w * h) * 100
    if transparent_pct < 5:
        # Per-cell removal
        cells_clean = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        for row in range(4):
            for col in range(3):
                x0 = int(col * src_fw)
                y0 = int(row * src_fh)
                x1 = int((col + 1) * src_fw)
                y1 = int((row + 1) * src_fh)
                cell = img.crop((x0, y0, x1, y1))
                cell_clean = remove_background(cell)
                cells_clean.paste(cell_clean, (x0, y0))
        clean = cells_clean
    
    # Determine actual frame size
    actual_fw = int(round(src_fw))
    actual_fh = int(round(src_fh))
    
    if target_frame_size > 0 and target_frame_size != actual_fw:
        # Resize to target frame size
        new_w = target_frame_size * 3
        new_h = target_frame_size * 4
        clean = clean.resize((new_w, new_h), Image.LANCZOS)
        actual_fw = target_frame_size
        actual_fh = target_frame_size
    
    return clean, actual_fw


def process_5x3_sheet(img, target_frame_size=0):
    """Process a 5×3 reference sheet into 4×3 game format."""
    img = img.convert('RGBA')
    w, h = img.size
    cw, ch = w // 3, h // 5
    
    # Remove background from each cell
    cells = {}
    for row in range(5):
        for col in range(3):
            cell = img.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))
            cells[(row, col)] = remove_background(cell)
    
    # Use target or derive from source
    frame_size = target_frame_size if target_frame_size > 0 else max(32, min(cw, ch))
    
    mapping = {
        0: [(0, 0), (0, 1), (0, 2)],   # Down <- Row 0
        1: [(4, 0), (4, 1), (4, 2)],   # Left <- Row 4
        2: [(3, 0), (3, 1), (3, 2)],   # Up <- Row 3
    }
    
    sheet = Image.new('RGBA', (frame_size * 3, frame_size * 4), (0, 0, 0, 0))
    
    for game_row, src_cells in mapping.items():
        for col, (sr, sc) in enumerate(src_cells):
            cell = cells[(sr, sc)]
            arr = np.array(cell)
            opaque = arr[:, :, 3] > 20
            if not opaque.any():
                continue
            
            rows_op = np.any(opaque, axis=1)
            cols_op = np.any(opaque, axis=0)
            rmin, rmax = np.where(rows_op)[0][[0, -1]]
            cmin, cmax = np.where(cols_op)[0][[0, -1]]
            
            content = cell.crop((cmin, rmin, cmax + 1, rmax + 1))
            content_w, content_h = content.size
            
            scale = min((frame_size - 2) / content_w, (frame_size - 2) / content_h)
            nw, nh = int(content_w * scale), int(content_h * scale)
            content = content.resize((nw, nh), Image.LANCZOS)
            
            frame = Image.new('RGBA', (frame_size, frame_size), (0, 0, 0, 0))
            x = (frame_size - nw) // 2
            y = frame_size - nh
            frame.paste(content, (x, y), content)
            sheet.paste(frame, (col * frame_size, game_row * frame_size))
    
    # Row 3 (Right) = mirror of Row 1 (Left)
    for col in range(3):
        left_frame = sheet.crop((col * frame_size, 1 * frame_size, (col + 1) * frame_size, 2 * frame_size))
        right_frame = left_frame.transpose(Image.FLIP_LEFT_RIGHT)
        sheet.paste(right_frame, (col * frame_size, 3 * frame_size))
    
    return sheet, frame_size


# ============================================================
# SINGLE IMAGE -> WALK ANIMATION
# ============================================================

def create_walk_frames(char_img, frame_size=32):
    """Generate 4-direction × 3-frame walk sprite sheet from a single character image."""
    char_img = char_img.convert('RGBA')
    arr = np.array(char_img)
    opaque = arr[:, :, 3] > 20
    if not opaque.any():
        return Image.new('RGBA', (frame_size * 3, frame_size * 4), (0, 0, 0, 0))
    
    rows = np.any(opaque, axis=1)
    cols = np.any(opaque, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    cropped = char_img.crop((cmin, rmin, cmax + 1, rmax + 1))
    cw, ch = cropped.size
    
    target_h = int(frame_size * 0.9)
    scale = target_h / ch
    target_w = int(cw * scale)
    if target_w > frame_size * 0.85:
        target_w = int(frame_size * 0.85)
        scale = target_w / cw
        target_h = int(ch * scale)
    
    base = cropped.resize((target_w, target_h), Image.LANCZOS)
    
    def make_frame(img, offset_x=0, offset_y=0):
        frame = Image.new('RGBA', (frame_size, frame_size), (0, 0, 0, 0))
        iw, ih = img.size
        x = (frame_size - iw) // 2 + offset_x
        y = frame_size - ih + offset_y
        frame.paste(img, (x, y), img)
        return frame
    
    frames = []
    
    # ROW 0: DOWN (Front)
    frames.append([make_frame(base), make_frame(base, 1, -1), make_frame(base, -1, -1)])
    
    # ROW 1: LEFT
    lw = max(1, int(target_w * 0.82))
    left_base = base.resize((lw, target_h), Image.LANCZOS)
    l0 = make_frame(left_base, -1)
    l1 = make_frame(left_base, -2, -1)
    l2 = make_frame(left_base, 0, -1)
    frames.append([l0, l1, l2])
    
    # ROW 2: UP (Back)
    back_arr = np.array(base.copy())
    opaque_mask = back_arr[:, :, 3] > 20
    back_arr[opaque_mask, :3] = np.clip(back_arr[opaque_mask, :3].astype(int) - 15, 0, 255).astype(np.uint8)
    back_base = Image.fromarray(back_arr)
    frames.append([make_frame(back_base), make_frame(back_base, 1, -1), make_frame(back_base, -1, -1)])
    
    # ROW 3: RIGHT (Mirror of Left)
    frames.append([f.transpose(Image.FLIP_LEFT_RIGHT) for f in frames[1]])
    
    sheet = Image.new('RGBA', (frame_size * 3, frame_size * 4), (0, 0, 0, 0))
    for row in range(4):
        for col in range(3):
            sheet.paste(frames[row][col], (col * frame_size, row * frame_size))
    
    return sheet


# ============================================================
# MAIN
# ============================================================

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: process_sprite.py <input_image> <output_path> [frame_size]"}))
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    frame_size = int(sys.argv[3]) if len(sys.argv) > 3 else 0  # 0 = auto
    
    try:
        img = Image.open(input_path).convert('RGBA')
        w, h = img.size
        
        # Step 1: Detect layout
        layout = detect_sheet_layout(img)
        
        if layout:
            cols, rows, cell_w, cell_h = layout
            sys.stderr.write(f"Detected {cols}x{rows} sheet, cell={cell_w}x{cell_h}\n")
            
            if rows == 4 and cols == 3:
                # Already a 4×3 sheet
                result, actual_fs = process_4x3_sheet(img, frame_size)
            elif rows == 5 and cols == 3:
                # 5×3 reference sheet
                target_fs = frame_size if frame_size > 0 else 64
                result, actual_fs = process_5x3_sheet(img, target_fs)
            else:
                result, actual_fs = None, frame_size
        else:
            result = None
            actual_fs = frame_size if frame_size > 0 else 32
        
        if result is None:
            # Single character image
            if frame_size <= 0:
                frame_size = 32
            clean = remove_background(img)
            result = create_walk_frames(clean, frame_size)
            actual_fs = frame_size
        
        # Save
        result.save(output_path)
        
        # Compute actual frame size from output
        out_fw = result.width // 3
        out_fh = result.height // 4
        
        arr = np.array(result)
        opaque_count = int(np.sum(arr[:, :, 3] > 20))
        total = arr.shape[0] * arr.shape[1]
        
        print(json.dumps({
            "success": True,
            "size": [result.width, result.height],
            "frameSize": out_fw,
            "frameHeight": out_fh,
            "fillRate": round(opaque_count / total * 100, 1),
            "outputPath": output_path,
            "detectedLayout": f"{layout[0]}x{layout[1]}" if layout else "single"
        }))
        
    except Exception as e:
        import traceback
        sys.stderr.write(traceback.format_exc())
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()
