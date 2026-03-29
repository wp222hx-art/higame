#!/usr/bin/env python3
"""
Tileset Auto-Splitter & Classifier v3
Advanced tile detection with:
- Intelligent checkered/transparent background removal
- Adaptive grid detection with gap merging
- Multi-feature tile classification (color, texture, edges, patterns)
- Also handles true transparency (RGBA alpha channel)
"""

import sys
import json
import os
from PIL import Image, ImageFilter
import numpy as np

def detect_bg_mask(data):
    """Detect checkered background using pattern analysis.
    Also handles true transparency (alpha channel).
    Returns a boolean mask where True = background pixel."""
    h, w = data.shape[:2]
    has_alpha = data.shape[2] == 4
    
    # If image already has real transparency, use alpha channel
    if has_alpha:
        alpha = data[:, :, 3]
        transparent = alpha < 20
        transparent_ratio = np.sum(transparent) / (h * w)
        if transparent_ratio > 0.05:
            # Real transparency exists, use it directly
            return transparent, (0.0, 0.0)
    
    rgb = data[:, :, :3].astype(np.int16)
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    max_diff = np.maximum(np.abs(r - g), np.maximum(np.abs(g - b), np.abs(r - b)))
    gray = (r + g + b) / 3.0
    
    # Sample corners to find background colors
    corners = []
    cs = min(40, h // 4, w // 4)
    for cy, cx in [(0, 0), (0, w-cs), (h-cs, 0), (h-cs, w-cs)]:
        region = data[cy:cy+cs, cx:cx+cs, :3]
        corners.append(region)
    
    corner_data = np.concatenate([c.reshape(-1, 3) for c in corners], axis=0).astype(np.int16)
    corner_gray = np.mean(corner_data, axis=1)
    corner_sat = np.max(corner_data, axis=1) - np.min(corner_data, axis=1)
    
    gray_mask_corners = corner_sat < 30
    if np.sum(gray_mask_corners) > 10:
        bg_grays = corner_gray[gray_mask_corners]
        median_g = np.median(bg_grays)
        low_grays = bg_grays[bg_grays < median_g]
        high_grays = bg_grays[bg_grays >= median_g]
        bg_low = np.median(low_grays) if len(low_grays) > 0 else 90
        bg_high = np.median(high_grays) if len(high_grays) > 0 else 177
    else:
        bg_low, bg_high = 90, 177
    
    is_gray = max_diff < 25
    near_low = np.abs(gray - bg_low) < 20
    near_high = np.abs(gray - bg_high) < 20
    bg_mask = is_gray & (near_low | near_high)
    
    # Also check for white/light gray uniform backgrounds
    white_bg = (r > 240) & (g > 240) & (b > 240)
    if np.sum(white_bg) / (h * w) > 0.3:
        bg_mask = bg_mask | white_bg
    
    return bg_mask, (float(bg_low), float(bg_high))


def detect_grid(bg_mask):
    """Detect tile grid by finding rows/columns dominated by background."""
    h, w = bg_mask.shape
    
    row_bg_ratio = np.mean(bg_mask, axis=1)
    col_bg_ratio = np.mean(bg_mask, axis=0)
    
    def find_content_ranges(bg_ratio, length, min_size=15):
        """Find ranges of content (non-bg) pixels with adaptive threshold."""
        # Try different thresholds - lower is stricter
        for threshold in [0.55, 0.5, 0.45, 0.6, 0.7]:
            content = bg_ratio < threshold
            ranges = []
            in_range = False
            start = 0
            for i in range(length):
                if content[i]:
                    if not in_range:
                        start = i
                        in_range = True
                else:
                    if in_range:
                        if i - start >= min_size:
                            ranges.append((start, i - 1))
                        in_range = False
            if in_range and length - start >= min_size:
                ranges.append((start, length - 1))
            if len(ranges) >= 2:
                return ranges
        return ranges
    
    tile_rows = find_content_ranges(row_bg_ratio, h, min_size=12)
    tile_cols = find_content_ranges(col_bg_ratio, w, min_size=12)
    
    def merge_close(ranges, gap=5):
        if not ranges:
            return ranges
        merged = [list(ranges[0])]
        for s, e in ranges[1:]:
            if s - merged[-1][1] <= gap:
                merged[-1][1] = e
            else:
                merged.append([s, e])
        return [tuple(r) for r in merged]
    
    tile_rows = merge_close(tile_rows)
    tile_cols = merge_close(tile_cols)
    
    return tile_rows, tile_cols


def extract_tile(data, bg_mask, y1, y2, x1, x2):
    """Extract a tile, converting bg to transparency with edge anti-aliasing."""
    region = data[y1:y2+1, x1:x2+1].copy()
    bg_region = bg_mask[y1:y2+1, x1:x2+1]
    
    h, w = region.shape[:2]
    result = np.zeros((h, w, 4), dtype=np.uint8)
    result[:, :, :3] = region[:, :, :3]
    result[:, :, 3] = np.where(bg_region, 0, 255).astype(np.uint8)
    
    # Smooth edges: semi-transparent border pixels
    from scipy.ndimage import binary_dilation, binary_erosion
    try:
        inner = binary_erosion(~bg_region, iterations=1)
        border = (~bg_region) & (~inner)
        result[:, :, 3] = np.where(border, 180, result[:, :, 3]).astype(np.uint8)
    except:
        pass
    
    return Image.fromarray(result, 'RGBA')


def is_tile_empty(tile_data, threshold=0.08):
    """Check if tile is mostly empty."""
    if tile_data.shape[2] == 4:
        opaque = np.sum(tile_data[:, :, 3] > 64) / (tile_data.shape[0] * tile_data.shape[1])
        return opaque < threshold
    return False


def compute_texture_features(tile_data, mask):
    """Compute texture complexity features for better classification."""
    h, w = tile_data.shape[:2]
    if h < 4 or w < 4:
        return 0, 0, 0
    
    gray = np.mean(tile_data[:, :, :3].astype(np.float32), axis=2)
    
    # Edge detection (gradient magnitude)
    gx = np.abs(np.diff(gray, axis=1))
    gy = np.abs(np.diff(gray, axis=0))
    edge_h = np.mean(gx[mask[:, :-1]]) if np.sum(mask[:, :-1]) > 0 else 0
    edge_v = np.mean(gy[mask[:-1, :]]) if np.sum(mask[:-1, :]) > 0 else 0
    edge_strength = (edge_h + edge_v) / 2.0
    
    # Texture variance (local standard deviation)
    try:
        from PIL import ImageFilter
        gray_img = Image.fromarray(gray.astype(np.uint8))
        blurred = np.array(gray_img.filter(ImageFilter.GaussianBlur(3))).astype(np.float32)
        local_var = np.mean(np.abs(gray - blurred)[mask]) if np.sum(mask) > 0 else 0
    except:
        local_var = np.std(gray[mask]) if np.sum(mask) > 0 else 0
    
    # Line detection: horizontal/vertical regularity
    # Structured objects (buildings, paths) tend to have more straight lines
    h_lines = 0
    v_lines = 0
    if h > 8 and w > 8:
        for row in range(2, h - 2, max(1, h // 8)):
            row_slice = gray[row, :][mask[row, :]]
            if len(row_slice) > 10:
                diffs = np.abs(np.diff(row_slice))
                # Count "flat" segments (potential lines)
                h_lines += np.sum(diffs < 5) / len(diffs)
        for col in range(2, w - 2, max(1, w // 8)):
            col_slice = gray[:, col][mask[:, col]]
            if len(col_slice) > 10:
                diffs = np.abs(np.diff(col_slice))
                v_lines += np.sum(diffs < 5) / len(diffs)
    
    regularity = (h_lines + v_lines) / max(1, (h // max(1, h // 8)) + (w // max(1, w // 8)))
    
    return float(edge_strength), float(local_var), float(regularity)


def analyze_shape(tile_data, mask):
    """Analyze shape features: compactness, symmetry, holes."""
    if np.sum(mask) < 20:
        return 0, 0, False
    
    h, w = mask.shape
    
    # Compactness: ratio of opaque area to bounding box area of opaque region
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not np.any(rows) or not np.any(cols):
        return 0, 0, False
    
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    bbox_area = (rmax - rmin + 1) * (cmax - cmin + 1)
    compactness = np.sum(mask) / max(1, bbox_area)
    
    # Symmetry (horizontal)
    left = mask[:, :w // 2]
    right = np.flip(mask[:, (w + 1) // 2:], axis=1)
    min_w = min(left.shape[1], right.shape[1])
    if min_w > 0:
        symmetry = np.mean(left[:, :min_w] == right[:, :min_w])
    else:
        symmetry = 0
    
    # Has interior holes (common in buildings/structures)
    from scipy.ndimage import binary_fill_holes
    try:
        filled = binary_fill_holes(mask)
        has_holes = np.sum(filled & ~mask) > (np.sum(mask) * 0.02)
    except:
        has_holes = False
    
    return float(compactness), float(symmetry), has_holes


def classify_tile(tile_data):
    """Enhanced tile classification with color, texture, shape analysis."""
    h, w = tile_data.shape[:2]
    
    mask = tile_data[:, :, 3] > 64 if tile_data.shape[2] == 4 else np.ones((h, w), dtype=bool)
    n_opaque = np.sum(mask)
    
    if n_opaque < 30:
        return 'decoration', 0.3, '装饰物', []
    
    opaque_ratio = n_opaque / (h * w)
    
    r = tile_data[:, :, 0][mask].astype(np.float32)
    g = tile_data[:, :, 1][mask].astype(np.float32)
    b = tile_data[:, :, 2][mask].astype(np.float32)
    
    avg_r, avg_g, avg_b = np.mean(r), np.mean(g), np.mean(b)
    std_r, std_g, std_b = np.std(r), np.std(g), np.std(b)
    brightness = (avg_r + avg_g + avg_b) / 3
    
    total = avg_r + avg_g + avg_b + 1
    r_ratio = avg_r / total
    g_ratio = avg_g / total
    b_ratio = avg_b / total
    
    saturation = max(avg_r, avg_g, avg_b) - min(avg_r, avg_g, avg_b)
    
    n = len(r)
    blue_pixels = np.sum((b > 120) & (b > r * 1.15) & (b > g * 0.85)) / n
    cyan_pixels = np.sum((b > 120) & (g > 120) & (r < 120)) / n
    green_pixels = np.sum((g > 90) & (g > r * 1.1) & (g > b * 1.1)) / n
    dark_green = np.sum((g > 60) & (g < 140) & (g > r * 1.2) & (b < 100)) / n
    brown_pixels = np.sum((r > 100) & (r > g * 0.85) & (g > b * 1.05) & (b < 140)) / n
    gray_pixels = np.sum((np.abs(r - g) < 20) & (np.abs(g - b) < 20) & (r > 70) & (r < 210)) / n
    dark_brown = np.sum((r > 70) & (r < 170) & (g > 40) & (g < 140) & (b < 110)) / n
    pink_pixels = np.sum((r > 160) & (b > 90) & (g < 160) & (r > g)) / n
    yellow_pixels = np.sum((r > 160) & (g > 140) & (b < 130) & (r > b * 1.3)) / n
    white_pixels = np.sum((r > 210) & (g > 210) & (b > 210)) / n
    red_pixels = np.sum((r > 150) & (r > g * 1.5) & (r > b * 1.5)) / n
    orange_pixels = np.sum((r > 180) & (g > 100) & (g < 170) & (b < 100)) / n
    purple_pixels = np.sum((r > 100) & (b > 100) & (g < 90) & (np.abs(r.astype(float) - b.astype(float)) < 60)) / n
    
    # Texture features
    edge_str, tex_var, regularity = compute_texture_features(tile_data, mask)
    
    # Shape features
    try:
        compactness, symmetry, has_holes = analyze_shape(tile_data, mask)
    except:
        compactness, symmetry, has_holes = 0.5, 0.5, False
    
    scores = {'terrain': 0, 'water': 0, 'farmland': 0, 'decoration': 0, 'building': 0}
    tags = []
    
    # ============ WATER ============
    if blue_pixels > 0.35 or (blue_pixels > 0.2 and cyan_pixels > 0.1):
        scores['water'] += 5
        tags.append('水域')
    elif blue_pixels > 0.15:
        scores['water'] += 3
        if green_pixels > 0.1:
            tags.append('河岸')
        else:
            tags.append('水体')
    elif blue_pixels > 0.08 and opaque_ratio > 0.7:
        scores['water'] += 1
    
    # Water with foam/waves (high blue + white)
    if blue_pixels > 0.2 and white_pixels > 0.05:
        scores['water'] += 2
        if '瀑布' not in tags:
            tags.append('浪花')
    
    # ============ GRASS / TERRAIN ============
    if green_pixels > 0.5:
        scores['terrain'] += 4
        tags.append('草地')
    elif green_pixels > 0.3:
        scores['terrain'] += 3
        tags.append('草地')
    elif green_pixels > 0.15:
        scores['terrain'] += 2
        tags.append('植被')
    
    # Dark green = dense vegetation / forest
    if dark_green > 0.3:
        scores['terrain'] += 1
        if '草地' not in tags and '植被' not in tags:
            tags.append('密林')
    
    # ============ DIRT / SAND / STONE ============
    if brown_pixels > 0.45 and blue_pixels < 0.08:
        scores['terrain'] += 4
        if avg_r > 155 and avg_g > 135:
            tags.append('沙地')
        elif avg_r > 120 and brightness > 100:
            tags.append('土路')
        else:
            tags.append('泥土')
    elif brown_pixels > 0.25 and blue_pixels < 0.1:
        scores['terrain'] += 2
        if '泥土' not in tags and '土路' not in tags:
            tags.append('泥土')
    
    if gray_pixels > 0.45 and saturation < 30:
        scores['terrain'] += 3
        tags.append('石头')
    elif gray_pixels > 0.3 and saturation < 40:
        scores['terrain'] += 1
        if regularity > 0.6:
            scores['building'] += 2
            tags.append('石砖')
        else:
            tags.append('碎石')
    
    # ============ FARMLAND ============
    if green_pixels > 0.12 and dark_brown > 0.12:
        scores['farmland'] += 4
        if green_pixels > dark_brown * 1.5:
            tags.append('作物')
        else:
            tags.append('耕地')
    elif dark_brown > 0.35 and green_pixels < 0.08:
        scores['farmland'] += 3
        tags.append('农田')
    
    # Rice paddy (water + green + brown)
    if blue_pixels > 0.08 and green_pixels > 0.1 and brown_pixels > 0.05:
        scores['farmland'] += 2
        scores['water'] += 1
        tags.append('水田')
    
    # Golden wheat / crop
    if avg_r > 145 and avg_g > 125 and avg_b < 105:
        if std_g < 45 and opaque_ratio > 0.5:
            scores['farmland'] += 3
            tags.append('麦田')
    
    # Green rows (planted crops)
    if green_pixels > 0.2 and brown_pixels > 0.15 and regularity > 0.5:
        scores['farmland'] += 2
        if '作物' not in tags:
            tags.append('种植')
    
    # ============ DECORATION ============
    if pink_pixels > 0.04:
        scores['decoration'] += 3
        tags.append('花卉')
    elif pink_pixels > 0.015:
        scores['decoration'] += 1
        tags.append('花朵')
    
    if yellow_pixels > 0.06 and green_pixels > 0.1:
        scores['decoration'] += 2
        tags.append('黄花')
    
    if purple_pixels > 0.05:
        scores['decoration'] += 2
        tags.append('紫花')
    
    if red_pixels > 0.05 and green_pixels > 0.1:
        scores['decoration'] += 2
        tags.append('红花')
    
    if orange_pixels > 0.05:
        scores['decoration'] += 1
        tags.append('果实')
    
    # Small partial objects
    if opaque_ratio < 0.35:
        scores['decoration'] += 4
        if not tags:
            tags.append('装饰')
    elif opaque_ratio < 0.55:
        scores['decoration'] += 2
    elif opaque_ratio < 0.7:
        scores['decoration'] += 1
    
    # Water features: lotus, lily pads, waterfall, bridge
    if blue_pixels > 0.12 and (pink_pixels > 0.015 or green_pixels > 0.08):
        if opaque_ratio < 0.75:
            scores['decoration'] += 3
            tags.append('水景')
    
    # ============ BUILDING ============
    if dark_brown > 0.25 and gray_pixels < 0.15 and opaque_ratio > 0.55:
        if saturation > 25:
            scores['building'] += 2
            tags.append('木制')
    
    # Structured objects (high regularity + compact)
    if regularity > 0.65 and compactness > 0.7 and opaque_ratio > 0.5:
        scores['building'] += 2
        if edge_str > 15:
            scores['building'] += 1
            if '结构' not in tags:
                tags.append('结构')
    
    # Bridge / wooden structure
    if dark_brown > 0.2 and (blue_pixels > 0.1 or opaque_ratio < 0.6):
        if regularity > 0.4:
            scores['building'] += 1
            if '桥' not in tags and '木制' not in tags:
                tags.append('桥梁')
    
    # Interior holes = building-like
    if has_holes and opaque_ratio > 0.5:
        scores['building'] += 1
    
    # ============ IRRIGATION ============
    if blue_pixels > 0.08 and green_pixels > 0.08 and brown_pixels > 0.06:
        scores['water'] += 2
        if '灌溉' not in tags and '水田' not in tags:
            tags.append('灌溉')
    
    # ============ PATH / ROAD ============
    if brown_pixels > 0.3 and opaque_ratio > 0.8 and edge_str < 12:
        if regularity > 0.5:
            scores['terrain'] += 1
            if '土路' not in tags and '小径' not in tags:
                tags.append('小径')
    
    # ============ DETERMINE BEST CATEGORY ============
    best_cat = max(scores, key=scores.get)
    best_score = scores[best_cat]
    
    # Handle ties
    top_cats = [k for k, v in scores.items() if v == best_score and v > 0]
    if len(top_cats) > 1:
        # Priority: water > farmland > terrain > building > decoration
        priority = {'water': 5, 'farmland': 4, 'building': 3, 'terrain': 2, 'decoration': 1}
        best_cat = max(top_cats, key=lambda c: priority.get(c, 0))
    
    confidence = min(1.0, best_score / 6.0)
    
    if best_score == 0:
        if brightness > 150 and saturation < 30:
            best_cat = 'terrain'
            tags = ['浅色地形']
        elif green_pixels > brown_pixels and green_pixels > blue_pixels:
            best_cat = 'terrain'
            tags = ['自然']
        elif blue_pixels > green_pixels and blue_pixels > brown_pixels:
            best_cat = 'water'
            tags = ['水域']
        else:
            best_cat = 'decoration'
            tags = ['未分类']
        confidence = 0.25
    
    # Deduplicate tags
    seen = set()
    unique_tags = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)
    
    # Generate a descriptive label from top 2 unique tags
    label = unique_tags[0] if unique_tags else best_cat
    
    return best_cat, confidence, label, unique_tags


def generate_grid_overlay(image_path, output_path, tile_rows, tile_cols, bg_mask):
    """Generate a grid overlay image showing detected tile boundaries."""
    img = Image.open(image_path).convert('RGBA')
    from PIL import ImageDraw
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for y1, y2 in tile_rows:
        draw.line([(0, y1), (img.width, y1)], fill=(0, 230, 118, 140), width=2)
        draw.line([(0, y2), (img.width, y2)], fill=(0, 230, 118, 140), width=2)
    
    for x1, x2 in tile_cols:
        draw.line([(x1, 0), (x1, img.height)], fill=(0, 230, 118, 140), width=2)
        draw.line([(x2, 0), (x2, img.height)], fill=(0, 230, 118, 140), width=2)
    
    result = Image.alpha_composite(img, overlay)
    result.save(output_path, 'PNG')


def split_tileset(image_path, output_dir, min_tile_size=20):
    """Auto-detect grid and split tileset."""
    img = Image.open(image_path).convert('RGBA')
    data = np.array(img)
    
    bg_mask, bg_tones = detect_bg_mask(data)
    tile_rows, tile_cols = detect_grid(bg_mask)
    
    if not tile_rows or not tile_cols:
        for ts in [128, 64, 96, 48, 32]:
            if img.width % ts == 0:
                tile_cols = [(x, x + ts - 1) for x in range(0, img.width, ts)]
                tile_rows = [(y, y + ts - 1) for y in range(0, img.height, ts) if y + ts <= img.height]
                break
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate grid overlay image
    try:
        overlay_path = os.path.join(output_dir, '_grid_overlay.png')
        generate_grid_overlay(image_path, overlay_path, tile_rows, tile_cols, bg_mask)
    except:
        overlay_path = None
    
    tiles = []
    # Auto-numbering counters per category for unique names
    cat_counters = {}
    # Track label usage for dedup
    name_counts = {}
    
    for ri, (y1, y2) in enumerate(tile_rows):
        for ci, (x1, x2) in enumerate(tile_cols):
            tile_img = extract_tile(data, bg_mask, y1, y2, x1, x2)
            tile_arr = np.array(tile_img)
            
            if is_tile_empty(tile_arr):
                continue
            
            category, confidence, label, tags = classify_tile(tile_arr)
            
            # Build unique name: category_num + descriptive feature
            cat_counters[category] = cat_counters.get(category, 0) + 1
            cat_num = cat_counters[category]
            cat_cn = {'terrain':'地形','water':'水域','farmland':'农田','decoration':'装饰','building':'建筑'}.get(category, category)
            # Combine first two distinct tags for richer name
            desc_parts = tags[:2] if len(tags) >= 2 else tags[:1]
            desc = '·'.join(desc_parts) if desc_parts else label
            unique_name = f"{cat_cn}{cat_num:02d}_{desc}"
            # Ensure truly unique
            if unique_name in name_counts:
                name_counts[unique_name] += 1
                unique_name = f"{unique_name}({name_counts[unique_name]})"
            else:
                name_counts[unique_name] = 1
            
            tile_id = f"tile_{ri}_{ci}"
            filename = f"{tile_id}.png"
            filepath = os.path.join(output_dir, filename)
            tile_img.save(filepath, 'PNG')
            
            tiles.append({
                'id': tile_id,
                'row': ri, 'col': ci,
                'x': int(x1), 'y': int(y1),
                'width': int(x2 - x1 + 1),
                'height': int(y2 - y1 + 1),
                'filename': filename,
                'category': category,
                'confidence': round(confidence, 2),
                'label': unique_name,
                'tags': tags,
            })
    
    result = {
        'success': True,
        'sourceWidth': img.width,
        'sourceHeight': img.height,
        'gridRows': len(tile_rows),
        'gridCols': len(tile_cols),
        'tileCount': len(tiles),
        'tiles': tiles,
        'gridInfo': {
            'rows': [(int(y1), int(y2)) for y1, y2 in tile_rows],
            'cols': [(int(x1), int(x2)) for x1, x2 in tile_cols],
        },
    }
    
    if overlay_path and os.path.exists(overlay_path):
        result['gridOverlay'] = os.path.basename(overlay_path)
    
    return result


def split_uniform(image_path, output_dir, tile_w, tile_h):
    """Split with user-specified tile size."""
    img = Image.open(image_path).convert('RGBA')
    data = np.array(img)
    bg_mask, _ = detect_bg_mask(data)
    
    cols = img.width // tile_w
    rows = img.height // tile_h
    
    os.makedirs(output_dir, exist_ok=True)
    
    tile_rows = [(ri * tile_h, (ri + 1) * tile_h - 1) for ri in range(rows)]
    tile_cols = [(ci * tile_w, (ci + 1) * tile_w - 1) for ci in range(cols)]
    
    try:
        overlay_path = os.path.join(output_dir, '_grid_overlay.png')
        generate_grid_overlay(image_path, overlay_path, tile_rows, tile_cols, bg_mask)
    except:
        overlay_path = None
    
    tiles = []
    cat_counters = {}
    name_counts = {}
    
    for ri in range(rows):
        for ci in range(cols):
            x1, y1 = ci * tile_w, ri * tile_h
            x2, y2 = x1 + tile_w - 1, y1 + tile_h - 1
            
            tile_img = extract_tile(data, bg_mask, y1, y2, x1, x2)
            tile_arr = np.array(tile_img)
            
            if is_tile_empty(tile_arr):
                continue
            
            category, confidence, label, tags = classify_tile(tile_arr)
            
            cat_counters[category] = cat_counters.get(category, 0) + 1
            cat_num = cat_counters[category]
            cat_cn = {'terrain':'地形','water':'水域','farmland':'农田','decoration':'装饰','building':'建筑'}.get(category, category)
            desc_parts = tags[:2] if len(tags) >= 2 else tags[:1]
            desc = '·'.join(desc_parts) if desc_parts else label
            unique_name = f"{cat_cn}{cat_num:02d}_{desc}"
            if unique_name in name_counts:
                name_counts[unique_name] += 1
                unique_name = f"{unique_name}({name_counts[unique_name]})"
            else:
                name_counts[unique_name] = 1
            
            tile_id = f"tile_{ri}_{ci}"
            filename = f"{tile_id}.png"
            tile_img.save(os.path.join(output_dir, filename), 'PNG')
            
            tiles.append({
                'id': tile_id,
                'row': ri, 'col': ci,
                'x': int(x1), 'y': int(y1),
                'width': tile_w, 'height': tile_h,
                'filename': filename,
                'category': category,
                'confidence': round(confidence, 2),
                'label': unique_name,
                'tags': tags,
            })
    
    result = {
        'success': True,
        'sourceWidth': img.width,
        'sourceHeight': img.height,
        'gridRows': rows, 'gridCols': cols,
        'tileCount': len(tiles),
        'tiles': tiles,
        'gridInfo': {
            'rows': [(int(y1), int(y2)) for y1, y2 in tile_rows],
            'cols': [(int(x1), int(x2)) for x1, x2 in tile_cols],
        },
    }
    
    if overlay_path and os.path.exists(overlay_path):
        result['gridOverlay'] = os.path.basename(overlay_path)
    
    return result


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({'error': 'Usage: split_tileset.py <image> <outdir> [tile_w tile_h]'}))
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if len(sys.argv) >= 5:
        result = split_uniform(image_path, output_dir, int(sys.argv[3]), int(sys.argv[4]))
    else:
        result = split_tileset(image_path, output_dir)
    
    print(json.dumps(result))
