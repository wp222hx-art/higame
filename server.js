const express = require('express');
const { execSync, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = 3000;
const PROJECT_ROOT = __dirname;

// Ensure directories exist
const CUSTOM_SPRITES_DIR = path.join(__dirname, 'public', 'game', 'assets', 'sprites', 'custom');
const BUILTIN_SPRITES_DIR = path.join(__dirname, 'public', 'game', 'assets', 'sprites');
const CUSTOM_AGENTS_DIR = path.join(__dirname, 'data', 'custom-agents');
const UPLOAD_TMP_DIR = path.join(__dirname, 'data', 'tmp');
const MAP_ASSETS_DIR = path.join(__dirname, 'public', 'game', 'assets', 'map-custom');
const MAP_ASSETS_DATA = path.join(__dirname, 'data', 'map-assets.json');
const GAME_SAVE_PATH = path.join(__dirname, 'data', 'game-save.json');
[CUSTOM_SPRITES_DIR, CUSTOM_AGENTS_DIR, UPLOAD_TMP_DIR, MAP_ASSETS_DIR].forEach(d => {
  if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });
});

// ============================================================
// Built-in agent definitions (seeded into editor on first run)
// ============================================================
const BUILTIN_AGENTS = [
  { id: 'chief',     name: '村长',     icon: '🏛️', dept: '领导层', tier: 1, sprite: 'chief',     zone: 'village-hall', color: '#ffd740', skills: ['seasonal-plan','budget-review','resource-check'], description: '全村最高管理者，统筹规划村庄发展' },
  { id: 'agritech',  name: '农技总监', icon: '🔬', dept: '领导层', tier: 1, sprite: 'tech',      zone: 'lab',          color: '#ffd740', skills: ['soil-analysis','crop-plan','pest-alert','seed-select'], description: '农业技术总负责人，指导科学种植' },
  { id: 'ops',       name: '运营总监', icon: '📊', dept: '领导层', tier: 1, sprite: 'finance',   zone: 'village-hall', color: '#ffd740', skills: ['seasonal-plan','budget-review','cost-analysis','resource-check'], description: '运营管理负责人，协调各部门工作' },
  { id: 'plant-dir', name: '种植部长', icon: '🌱', dept: '种植部', tier: 2, sprite: 'farmer',    zone: 'fields-a',     color: '#00e676', skills: ['crop-plan','rotation-plan','seed-select','harvest-schedule'], description: '种植部门负责人，管理所有农田生产' },
  { id: 'soil',      name: '土壤专家', icon: '🧪', dept: '种植部', tier: 3, sprite: 'inspector', zone: 'fields-a',     color: '#00e676', skills: ['soil-analysis','fertilizer-plan'], description: '专注土壤质量检测和改良方案' },
  { id: 'meteo',     name: '气象师',   icon: '🌤️', dept: '种植部', tier: 3, sprite: 'tech',      zone: 'weather',      color: '#00e676', skills: ['weather-alert','irrigation-plan'], description: '气象数据分析，提供天气预警' },
  { id: 'seed',      name: '种子专家', icon: '🌾', dept: '种植部', tier: 3, sprite: 'farmer',    zone: 'fields-b',     color: '#00e676', skills: ['seed-select','crop-plan'], description: '优良品种筛选和培育' },
  { id: 'irrig',     name: '灌溉工程', icon: '💧', dept: '种植部', tier: 3, sprite: 'delivery',  zone: 'pond',         color: '#00e676', skills: ['irrigation-plan','resource-check'], description: '农田灌溉系统规划和维护' },
  { id: 'pest',      name: '病虫害专', icon: '🐛', dept: '种植部', tier: 3, sprite: 'inspector', zone: 'greenhouse',   color: '#00e676', skills: ['pest-alert','quality-check'], description: '病虫害监测预警和防治' },
  { id: 'mach',      name: '农机专家', icon: '🚜', dept: '种植部', tier: 3, sprite: 'delivery',  zone: 'fields-b',     color: '#00e676', skills: ['resource-check','team-planting'], description: '农业机械管理和调度' },
  { id: 'harvest',   name: '采收专家', icon: '🌾', dept: '种植部', tier: 3, sprite: 'farmer',    zone: 'fields-a',     color: '#00e676', skills: ['harvest-schedule','team-harvest','quality-check'], description: '最佳采收时机判断和组织采收' },
  { id: 'sales-dir', name: '销售部长', icon: '📦', dept: '销售部', tier: 2, sprite: 'sales',     zone: 'market',       color: '#ff9100', skills: ['market-analysis','pricing-strategy','channel-plan','launch-product'], description: '销售部门负责人，统筹市场工作' },
  { id: 'ecom',      name: '电商运营', icon: '📱', dept: '销售部', tier: 3, sprite: 'livestream', zone: 'livestream',   color: '#ff9100', skills: ['channel-plan','brand-build','livestream-plan'], description: '线上电商渠道运营管理' },
  { id: 'live',      name: '直播销售', icon: '🎬', dept: '销售部', tier: 3, sprite: 'livestream', zone: 'livestream',   color: '#ff9100', skills: ['livestream-plan','brand-build'], description: '直播带货策划和执行' },
  { id: 'price',     name: '定价分析', icon: '💹', dept: '销售部', tier: 3, sprite: 'finance',   zone: 'market',       color: '#ff9100', skills: ['pricing-strategy','cost-analysis','market-analysis'], description: '产品定价策略制定和调整' },
  { id: 'whole',     name: '批发专家', icon: '🏪', dept: '销售部', tier: 3, sprite: 'sales',     zone: 'warehouse',    color: '#ff9100', skills: ['channel-plan','team-sales'], description: '批发渠道开拓和维护' },
  { id: 'logi',      name: '物流专家', icon: '🚛', dept: '销售部', tier: 3, sprite: 'delivery',  zone: 'logistics',    color: '#ff9100', skills: ['resource-check','team-sales'], description: '物流配送方案和路线优化' },
  { id: 'brand',     name: '品牌部长', icon: '🎨', dept: '品牌部', tier: 2, sprite: 'livestream', zone: 'livestream',   color: '#f48fb1', skills: ['brand-build','livestream-plan','launch-product'], description: '品牌形象建设和推广' },
  { id: 'qual',      name: '质检部长', icon: '🔍', dept: '质检部', tier: 2, sprite: 'inspector', zone: 'lab',          color: '#ef5350', skills: ['quality-check','organic-audit','food-safety-review'], description: '产品质量把控和认证管理' },
  { id: 'fin',       name: '财务部长', icon: '💰', dept: '财务部', tier: 2, sprite: 'finance',   zone: 'village-hall', color: '#42a5f5', skills: ['budget-review','cost-analysis'], description: '财务管理和预算执行' },
  { id: 'rear',      name: '后勤部长', icon: '🏗️', dept: '后勤部', tier: 2, sprite: 'delivery',  zone: 'warehouse',    color: '#00bcd4', skills: ['resource-check','training-plan'], description: '后勤保障和物资管理' },
  { id: 'eco',       name: '生态部长', icon: '🌿', dept: '生态部', tier: 2, sprite: 'farmer',    zone: 'pond',         color: '#69f0ae', skills: ['organic-audit','rotation-plan','soil-analysis'], description: '生态环境保护和有机发展' },
];

function seedBuiltinAgents() {
  BUILTIN_AGENTS.forEach(agent => {
    const configPath = path.join(CUSTOM_AGENTS_DIR, `${agent.id}.json`);
    // Only seed if not already exists (user may have edited it)
    if (!fs.existsSync(configPath)) {
      const config = {
        ...agent,
        builtin: true,
        spriteUrl: `/game/assets/sprites/char-${agent.sprite}.png`,
        frameSize: 32,
        frameHeight: 32,
        scale: 2.2,
        createdAt: new Date().toISOString()
      };
      fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    }
  });
}

// Seed on startup
seedBuiltinAgents();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Village system main page redirect
app.get('/village', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'village.html'));
});

// Village guide page
app.get('/village/guide', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'village-guide.html'));
});

// Village simulation game
app.get('/village/game', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'game', 'index.html'));
});

// Character editor
app.get('/village/editor', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'game', 'editor.html'));
});

// Map editor
app.get('/village/map-editor', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'game', 'map-editor.html'));
});

// ============================================================
// Map Editor APIs
// ============================================================
const MAP_DATA_PATH = path.join(__dirname, 'data', 'map-data.json');

// GET map data
app.get('/api/editor/map', (req, res) => {
  try {
    if (fs.existsSync(MAP_DATA_PATH)) {
      const data = JSON.parse(fs.readFileSync(MAP_DATA_PATH, 'utf8'));
      res.json(data);
    } else {
      res.json({});
    }
  } catch (e) {
    res.json({});
  }
});

// POST save map data
app.post('/api/editor/map', (req, res) => {
  try {
    const mapData = req.body;
    if (!mapData || !mapData.terrain) {
      return res.status(400).json({ error: '无效的地图数据' });
    }
    // Add metadata
    mapData.savedAt = new Date().toISOString();
    fs.writeFileSync(MAP_DATA_PATH, JSON.stringify(mapData, null, 2));
    res.json({ success: true, message: '地图已保存' });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// Map Asset Management APIs
// ============================================================

// Helper: Read map assets registry
function readMapAssets() {
  try {
    if (fs.existsSync(MAP_ASSETS_DATA)) {
      return JSON.parse(fs.readFileSync(MAP_ASSETS_DATA, 'utf8'));
    }
  } catch (e) {}
  return { assets: [] };
}

// Helper: Write map assets registry
function writeMapAssets(data) {
  fs.writeFileSync(MAP_ASSETS_DATA, JSON.stringify(data, null, 2));
}

// GET: List all map assets
app.get('/api/editor/map-assets', (req, res) => {
  try {
    const data = readMapAssets();
    res.json(data.assets || []);
  } catch (e) {
    res.json([]);
  }
});

// POST: Upload a new map asset (terrain tile, building sprite, decoration, etc.)
app.post('/api/editor/map-assets', async (req, res) => {
  try {
    const parts = await parseMultipart(req);
    const imageFile = parts.image;
    const name = parts.name || 'Unnamed Asset';
    const category = parts.category || 'decoration'; // terrain, building, decoration, farmland, residential
    const tileW = parseInt(parts.tileWidth) || 32;
    const tileH = parseInt(parts.tileHeight) || 32;
    const frameCount = parseInt(parts.frameCount) || 1;
    const tags = parts.tags || '';

    if (!imageFile || !imageFile.data) {
      return res.status(400).json({ error: '未接收到图片文件' });
    }

    // Generate unique ID
    const assetId = 'ma-' + crypto.randomBytes(6).toString('hex');
    const ext = (imageFile.filename || '.png').split('.').pop() || 'png';
    const fileName = `${assetId}.${ext}`;
    const filePath = path.join(MAP_ASSETS_DIR, fileName);

    // Save file
    fs.writeFileSync(filePath, imageFile.data);

    // Get image dimensions using identify or fallback
    let imgWidth = 0, imgHeight = 0;
    try {
      const sizeInfo = execSync(`python3 -c "from PIL import Image; img=Image.open('${filePath}'); print(img.width, img.height)"`, { encoding: 'utf8', timeout: 5000 }).trim();
      const [w, h] = sizeInfo.split(' ').map(Number);
      imgWidth = w; imgHeight = h;
    } catch (_) {
      // Fallback: read PNG header
      try {
        const buf = fs.readFileSync(filePath);
        if (buf[0] === 0x89 && buf[1] === 0x50) { // PNG
          imgWidth = buf.readUInt32BE(16);
          imgHeight = buf.readUInt32BE(20);
        }
      } catch (__) {}
    }

    const asset = {
      id: assetId,
      name,
      category,
      fileName,
      url: `/game/assets/map-custom/${fileName}`,
      tileWidth: tileW,
      tileHeight: tileH,
      imgWidth,
      imgHeight,
      frameCount,
      tags: tags.split(',').map(t => t.trim()).filter(Boolean),
      createdAt: new Date().toISOString()
    };

    // Add to registry
    const data = readMapAssets();
    data.assets.push(asset);
    writeMapAssets(data);

    res.json({ success: true, asset });
  } catch (err) {
    console.error('Map asset upload error:', err.message);
    res.status(500).json({ error: err.message || '上传失败' });
  }
});

// PUT: Update map asset metadata
app.put('/api/editor/map-assets/:id', (req, res) => {
  try {
    const id = req.params.id;
    const updates = req.body;
    const data = readMapAssets();
    const idx = data.assets.findIndex(a => a.id === id);
    if (idx === -1) return res.status(404).json({ error: 'Asset not found' });

    // Merge updates (only metadata, not file)
    const allowed = ['name', 'category', 'tileWidth', 'tileHeight', 'frameCount', 'tags'];
    allowed.forEach(k => {
      if (updates[k] !== undefined) data.assets[idx][k] = updates[k];
    });
    data.assets[idx].updatedAt = new Date().toISOString();
    writeMapAssets(data);

    res.json({ success: true, asset: data.assets[idx] });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// DELETE: Remove a map asset
app.delete('/api/editor/map-assets/:id', (req, res) => {
  try {
    const id = req.params.id;
    const data = readMapAssets();
    const idx = data.assets.findIndex(a => a.id === id);
    if (idx === -1) return res.status(404).json({ error: 'Asset not found' });

    const asset = data.assets[idx];
    // Delete file
    const filePath = path.join(MAP_ASSETS_DIR, asset.fileName);
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);

    // Remove from registry
    data.assets.splice(idx, 1);
    writeMapAssets(data);

    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// POST: Upload tileset spritesheet, auto-split and classify tiles
app.post('/api/editor/tileset-split', async (req, res) => {
  try {
    const parts = await parseMultipart(req);
    const imageFile = parts.image;
    const mode = parts.mode || 'auto'; // 'auto' or 'uniform'
    const tileW = parseInt(parts.tileWidth) || 0;
    const tileH = parseInt(parts.tileHeight) || 0;

    if (!imageFile || !imageFile.data) {
      return res.status(400).json({ error: '未接收到图片文件' });
    }

    // Save uploaded tileset to temp
    const tsId = 'ts-' + crypto.randomBytes(6).toString('hex');
    const ext = (imageFile.filename || '.png').split('.').pop() || 'png';
    const tmpFile = path.join(UPLOAD_TMP_DIR, `${tsId}.${ext}`);
    fs.writeFileSync(tmpFile, imageFile.data);

    // Create output directory for split tiles
    const outDir = path.join(MAP_ASSETS_DIR, tsId);
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

    // Run Python tile splitter
    const scriptPath = path.join(__dirname, 'tools', 'split_tileset.py');
    let cmd;
    if (mode === 'uniform' && tileW > 0 && tileH > 0) {
      cmd = `python3 "${scriptPath}" "${tmpFile}" "${outDir}" ${tileW} ${tileH}`;
    } else {
      cmd = `python3 "${scriptPath}" "${tmpFile}" "${outDir}"`;
    }

    const result = execSync(cmd, { encoding: 'utf8', timeout: 30000 });
    const splitResult = JSON.parse(result);

    if (!splitResult.success) {
      return res.status(500).json({ error: splitResult.error || '分割失败' });
    }

    // Save the original tileset image for reference
    const tilesetFileName = `${tsId}-source.${ext}`;
    const tilesetPath = path.join(MAP_ASSETS_DIR, tilesetFileName);
    fs.copyFileSync(tmpFile, tilesetPath);

    // Update each tile's URL path
    splitResult.tiles.forEach(t => {
      t.url = `/game/assets/map-custom/${tsId}/${t.filename}`;
      t.tilesetId = tsId;
    });
    splitResult.tilesetId = tsId;
    splitResult.sourceUrl = `/game/assets/map-custom/${tilesetFileName}`;

    // Grid overlay URL
    if (splitResult.gridOverlay) {
      splitResult.gridOverlayUrl = `/game/assets/map-custom/${tsId}/${splitResult.gridOverlay}`;
    }

    // Cleanup temp file
    try { fs.unlinkSync(tmpFile); } catch (_) {}

    res.json(splitResult);
  } catch (err) {
    console.error('Tileset split error:', err.message);
    res.status(500).json({ error: err.message || '处理失败' });
  }
});

// POST: Import split tiles into asset library (batch)
app.post('/api/editor/tileset-import', (req, res) => {
  try {
    const { tilesetId, tiles } = req.body;
    if (!tilesetId || !tiles || !tiles.length) {
      return res.status(400).json({ error: '缺少参数' });
    }

    const data = readMapAssets();
    const imported = [];

    // Collect existing asset names for dedup
    const existingNames = new Set(data.assets.map(a => a.name));
    const batchNames = new Set();

    tiles.forEach(t => {
      const assetId = 'ma-' + crypto.randomBytes(6).toString('hex');
      const srcFile = path.join(MAP_ASSETS_DIR, tilesetId, t.filename);
      if (!fs.existsSync(srcFile)) return;

      // Copy tile to flat assets directory
      const destFile = `${assetId}.png`;
      const destPath = path.join(MAP_ASSETS_DIR, destFile);
      fs.copyFileSync(srcFile, destPath);

      // Get dimensions
      let imgWidth = 0, imgHeight = 0;
      try {
        const sizeInfo = execSync(`python3 -c "from PIL import Image; img=Image.open('${destPath}'); print(img.width, img.height)"`, { encoding: 'utf8', timeout: 5000 }).trim();
        [imgWidth, imgHeight] = sizeInfo.split(' ').map(Number);
      } catch (_) {}

      // Deduplicate name: check both existing library and current batch
      let finalName = t.name || t.label || `Tile_${t.row}_${t.col}`;
      if (existingNames.has(finalName) || batchNames.has(finalName)) {
        let suffix = 2;
        while (existingNames.has(`${finalName}_${suffix}`) || batchNames.has(`${finalName}_${suffix}`)) suffix++;
        finalName = `${finalName}_${suffix}`;
      }
      batchNames.add(finalName);

      const asset = {
        id: assetId,
        name: finalName,
        category: t.category || 'decoration',
        fileName: destFile,
        url: `/game/assets/map-custom/${destFile}`,
        tileWidth: imgWidth,
        tileHeight: imgHeight,
        imgWidth, imgHeight,
        frameCount: 1,
        tags: t.tags || [],
        source: 'tileset-' + tilesetId,
        createdAt: new Date().toISOString()
      };

      data.assets.push(asset);
      imported.push(asset);
    });

    writeMapAssets(data);

    // Cleanup tileset split directory
    try {
      const splitDir = path.join(MAP_ASSETS_DIR, tilesetId);
      if (fs.existsSync(splitDir)) {
        fs.readdirSync(splitDir).forEach(f => fs.unlinkSync(path.join(splitDir, f)));
        fs.rmdirSync(splitDir);
      }
    } catch (_) {}

    res.json({ success: true, imported: imported.length, assets: imported });
  } catch (err) {
    console.error('Tileset import error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// PATCH: Rename a single asset
app.patch('/api/editor/map-assets/:id/rename', (req, res) => {
  try {
    const { name } = req.body;
    if (!name || !name.trim()) return res.status(400).json({ error: '名称不能为空' });
    const data = readMapAssets();
    const asset = data.assets.find(a => a.id === req.params.id);
    if (!asset) return res.status(404).json({ error: '素材不存在' });
    // Dedup check
    const trimmed = name.trim();
    const dup = data.assets.find(a => a.id !== req.params.id && a.name === trimmed);
    if (dup) return res.status(409).json({ error: `名称 "${trimmed}" 已被使用` });
    asset.name = trimmed;
    asset.updatedAt = new Date().toISOString();
    writeMapAssets(data);
    res.json({ success: true, asset });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST: Batch rename assets with prefix/pattern
app.post('/api/editor/map-assets/batch-rename', (req, res) => {
  try {
    const { ids, prefix, pattern } = req.body;
    if (!ids || !ids.length) return res.status(400).json({ error: '未选择素材' });
    const data = readMapAssets();
    let renamed = 0;
    const existingNames = new Set(data.assets.filter(a => !ids.includes(a.id)).map(a => a.name));
    const batchNames = new Set();
    ids.forEach((id, idx) => {
      const asset = data.assets.find(a => a.id === id);
      if (!asset) return;
      let newName;
      if (pattern) {
        // Pattern: {n}=number, {cat}=category, {old}=current name
        const catCn = {terrain:'地形',water:'水域',farmland:'农田',decoration:'装饰',building:'建筑'}[asset.category] || asset.category;
        newName = pattern
          .replace('{n}', String(idx + 1).padStart(2, '0'))
          .replace('{cat}', catCn)
          .replace('{old}', asset.name);
      } else if (prefix) {
        newName = `${prefix}${String(idx + 1).padStart(2, '0')}`;
      } else {
        return;
      }
      // Dedup
      if (existingNames.has(newName) || batchNames.has(newName)) {
        let s = 2;
        while (existingNames.has(`${newName}_${s}`) || batchNames.has(`${newName}_${s}`)) s++;
        newName = `${newName}_${s}`;
      }
      batchNames.add(newName);
      asset.name = newName;
      asset.updatedAt = new Date().toISOString();
      renamed++;
    });
    writeMapAssets(data);
    res.json({ success: true, renamed });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET: List built-in assets for the map editor
app.get('/api/editor/map-builtin-assets', (req, res) => {
  try {
    const builtinAssets = [];
    // Scan terrain sprites
    const terrainFiles = fs.readdirSync(BUILTIN_SPRITES_DIR).filter(f => f.startsWith('terrain-'));
    terrainFiles.forEach(f => {
      builtinAssets.push({
        id: 'builtin-' + f.replace('.png', ''),
        name: f.replace('terrain-', '').replace('.png', ''),
        category: 'terrain',
        fileName: f,
        url: `/game/assets/sprites/${f}`,
        builtin: true
      });
    });
    // Scan building sprites
    const buildingFiles = fs.readdirSync(BUILTIN_SPRITES_DIR).filter(f => f.startsWith('bld-'));
    buildingFiles.forEach(f => {
      builtinAssets.push({
        id: 'builtin-' + f.replace('.png', ''),
        name: f.replace('bld-', '').replace('.png', ''),
        category: 'building',
        fileName: f,
        url: `/game/assets/sprites/${f}`,
        builtin: true
      });
    });
    // Scan crop sprites
    const cropFiles = fs.readdirSync(BUILTIN_SPRITES_DIR).filter(f => f.startsWith('crop-'));
    cropFiles.forEach(f => {
      builtinAssets.push({
        id: 'builtin-' + f.replace('.png', ''),
        name: f.replace('crop-', '').replace('.png', ''),
        category: 'farmland',
        fileName: f,
        url: `/game/assets/sprites/${f}`,
        builtin: true
      });
    });
    res.json(builtinAssets);
  } catch (e) {
    res.json([]);
  }
});

// ============================================================
// Character Editor APIs
// ============================================================

// Simple multipart parser for file uploads (no multer dependency)
function parseMultipart(req) {
  return new Promise((resolve, reject) => {
    const contentType = req.headers['content-type'] || '';
    if (!contentType.includes('multipart/form-data')) {
      return reject(new Error('Not multipart'));
    }
    const boundary = contentType.split('boundary=')[1];
    if (!boundary) return reject(new Error('No boundary'));

    const chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', () => {
      const buffer = Buffer.concat(chunks);
      const parts = {};
      const boundaryBuf = Buffer.from('--' + boundary);
      let pos = 0;

      while (pos < buffer.length) {
        const start = buffer.indexOf(boundaryBuf, pos);
        if (start === -1) break;
        const nextStart = buffer.indexOf(boundaryBuf, start + boundaryBuf.length + 2);
        if (nextStart === -1) break;

        const part = buffer.slice(start + boundaryBuf.length + 2, nextStart - 2);
        const headerEnd = part.indexOf('\r\n\r\n');
        if (headerEnd === -1) { pos = nextStart; continue; }

        const headerStr = part.slice(0, headerEnd).toString();
        const body = part.slice(headerEnd + 4);

        const nameMatch = headerStr.match(/name="([^"]+)"/);
        const filenameMatch = headerStr.match(/filename="([^"]+)"/);
        if (nameMatch) {
          if (filenameMatch) {
            parts[nameMatch[1]] = { filename: filenameMatch[1], data: body };
          } else {
            parts[nameMatch[1]] = body.toString();
          }
        }
        pos = nextStart;
      }
      resolve(parts);
    });
    req.on('error', reject);
  });
}

// API: Process uploaded image into sprite sheet
app.post('/api/editor/process-sprite', async (req, res) => {
  try {
    const parts = await parseMultipart(req);
    const imageFile = parts.image;
    const frameSize = parseInt(parts.frameSize) || 0;  // 0 = auto-detect

    if (!imageFile || !imageFile.data) {
      return res.status(400).json({ error: '未接收到图片文件' });
    }

    // Save temp file
    const tmpId = crypto.randomBytes(8).toString('hex');
    const tmpInput = path.join(UPLOAD_TMP_DIR, `input_${tmpId}.png`);
    const tmpOutput = path.join(UPLOAD_TMP_DIR, `output_${tmpId}.png`);
    fs.writeFileSync(tmpInput, imageFile.data);

    // Process with Python script
    const scriptPath = path.join(PROJECT_ROOT, 'tools', 'process_sprite.py');
    const result = execSync(
      `python3 "${scriptPath}" "${tmpInput}" "${tmpOutput}" ${frameSize}`,
      { cwd: PROJECT_ROOT, timeout: 120000, encoding: 'utf8' }
    );

    let parsed;
    try {
      parsed = JSON.parse(result.trim());
    } catch (e) {
      // Try to find JSON in output (stderr may precede JSON)
      const lines = result.trim().split('\n');
      for (const line of lines) {
        try { parsed = JSON.parse(line); break; } catch (_) {}
      }
    }

    if (!parsed || parsed.error) {
      throw new Error(parsed?.error || '处理失败');
    }

    // Move output to a web-accessible temp location
    const spriteFileName = `temp_${tmpId}.png`;
    const spriteDest = path.join(CUSTOM_SPRITES_DIR, spriteFileName);
    fs.renameSync(tmpOutput, spriteDest);

    // Clean up input
    try { fs.unlinkSync(tmpInput); } catch (_) {}

    res.json({
      success: true,
      spriteUrl: `/game/assets/sprites/custom/${spriteFileName}`,
      frameSize: parsed.frameSize || frameSize,
      frameHeight: parsed.frameHeight || parsed.frameSize || frameSize,
      fillRate: parsed.fillRate,
      detectedLayout: parsed.detectedLayout || 'unknown',
      sheetSize: parsed.size || null
    });

  } catch (err) {
    console.error('Sprite processing error:', err.message);
    res.status(500).json({ error: err.message || '处理失败' });
  }
});

// API: Save agent configuration
app.post('/api/editor/save-agent', async (req, res) => {
  try {
    const parts = await parseMultipart(req);
    const spriteFile = parts.sprite;
    const agentData = JSON.parse(parts.agent);

    if (!agentData.id || !agentData.name) {
      return res.status(400).json({ error: '缺少必要信息' });
    }

    // Save sprite
    const spriteFileName = `char-${agentData.id}.png`;
    const spritePath = path.join(CUSTOM_SPRITES_DIR, spriteFileName);
    if (spriteFile && spriteFile.data) {
      fs.writeFileSync(spritePath, spriteFile.data);
    }

    // Save agent config
    const agentConfig = {
      ...agentData,
      spriteUrl: `/game/assets/sprites/custom/${spriteFileName}`,
      createdAt: new Date().toISOString()
    };
    const configPath = path.join(CUSTOM_AGENTS_DIR, `${agentData.id}.json`);
    fs.writeFileSync(configPath, JSON.stringify(agentConfig, null, 2));

    res.json({ success: true, agent: agentConfig });

  } catch (err) {
    console.error('Save agent error:', err.message);
    res.status(500).json({ error: err.message || '保存失败' });
  }
});

// API: List all agents (built-in + custom)
app.get('/api/editor/agents', (req, res) => {
  try {
    const files = fs.readdirSync(CUSTOM_AGENTS_DIR).filter(f => f.endsWith('.json'));
    const agents = files.map(f => {
      const content = fs.readFileSync(path.join(CUSTOM_AGENTS_DIR, f), 'utf8');
      return JSON.parse(content);
    }).sort((a, b) => {
      // Sort: builtin first (by tier then dept), then custom by date
      if (a.builtin && !b.builtin) return -1;
      if (!a.builtin && b.builtin) return 1;
      if (a.builtin && b.builtin) {
        if (a.tier !== b.tier) return a.tier - b.tier;
        return (a.dept || '').localeCompare(b.dept || '');
      }
      return 0;
    });
    res.json(agents);
  } catch (e) {
    res.json([]);
  }
});

// API: Get single agent
app.get('/api/editor/agents/:id', (req, res) => {
  try {
    const configPath = path.join(CUSTOM_AGENTS_DIR, `${req.params.id}.json`);
    if (!fs.existsSync(configPath)) return res.status(404).json({ error: 'Agent not found' });
    const content = fs.readFileSync(configPath, 'utf8');
    res.json(JSON.parse(content));
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Update an existing agent (PUT)
app.put('/api/editor/agents/:id', async (req, res) => {
  try {
    const id = req.params.id;
    const configPath = path.join(CUSTOM_AGENTS_DIR, `${id}.json`);
    if (!fs.existsSync(configPath)) return res.status(404).json({ error: 'Agent not found' });

    const contentType = req.headers['content-type'] || '';
    let agentData, spriteFile;

    if (contentType.includes('multipart/form-data')) {
      const parts = await parseMultipart(req);
      spriteFile = parts.sprite;
      agentData = JSON.parse(parts.agent);
    } else {
      agentData = req.body;
    }

    // Read existing config
    const existing = JSON.parse(fs.readFileSync(configPath, 'utf8'));

    // If sprite file provided, save it
    if (spriteFile && spriteFile.data) {
      const spriteFileName = `char-${id}.png`;
      const spritePath = path.join(CUSTOM_SPRITES_DIR, spriteFileName);
      fs.writeFileSync(spritePath, spriteFile.data);
      agentData.spriteUrl = `/game/assets/sprites/custom/${spriteFileName}`;
      agentData.sprite = id;
      agentData.builtin = false; // No longer builtin if sprite changed
    }

    // Merge update
    const updated = {
      ...existing,
      ...agentData,
      id: id,  // ID cannot change
      updatedAt: new Date().toISOString()
    };

    fs.writeFileSync(configPath, JSON.stringify(updated, null, 2));
    res.json({ success: true, agent: updated });

  } catch (err) {
    console.error('Update agent error:', err.message);
    res.status(500).json({ error: err.message || '更新失败' });
  }
});

// API: Delete an agent
app.delete('/api/editor/agents/:id', (req, res) => {
  try {
    const id = req.params.id;
    const configPath = path.join(CUSTOM_AGENTS_DIR, `${id}.json`);

    // Check if it exists
    if (fs.existsSync(configPath)) {
      const agent = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      fs.unlinkSync(configPath);

      // Only delete custom sprite (not built-in ones)
      if (!agent.builtin) {
        const spritePath = path.join(CUSTOM_SPRITES_DIR, `char-${id}.png`);
        if (fs.existsSync(spritePath)) fs.unlinkSync(spritePath);
      }
    }

    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Reset (re-seed) all built-in agents
app.post('/api/editor/agents/reset-builtin', (req, res) => {
  try {
    BUILTIN_AGENTS.forEach(agent => {
      const configPath = path.join(CUSTOM_AGENTS_DIR, `${agent.id}.json`);
      const config = {
        ...agent,
        builtin: true,
        spriteUrl: `/game/assets/sprites/char-${agent.sprite}.png`,
        frameSize: 32,
        frameHeight: 32,
        scale: 2.2,
        createdAt: new Date().toISOString()
      };
      fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    });
    res.json({ success: true, count: BUILTIN_AGENTS.length });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// --- API: Get all agents ---
app.get('/api/agents', (req, res) => {
  const agentsDir = path.join(PROJECT_ROOT, '.claude', 'agents');
  const agents = [];
  try {
    const files = fs.readdirSync(agentsDir).filter(f => f.endsWith('.md'));
    for (const file of files) {
      const content = fs.readFileSync(path.join(agentsDir, file), 'utf8');
      const frontmatter = parseFrontmatter(content);
      const body = content.replace(/^---[\s\S]*?---\n*/, '');
      const responsibilities = [];
      const respMatch = body.match(/### Key Responsibilities[\s\S]*?(?=###|$)/);
      if (respMatch) {
        const lines = respMatch[0].split('\n').filter(l => l.match(/^\d+\.\s/));
        lines.forEach(l => responsibilities.push(l.replace(/^\d+\.\s\*\*/, '').replace(/\*\*.*/, '').trim()));
      }
      agents.push({
        id: file.replace('.md', ''),
        name: frontmatter.name || file.replace('.md', ''),
        description: (frontmatter.description || '').replace(/^"|"$/g, ''),
        model: frontmatter.model || 'unknown',
        tools: frontmatter.tools || '',
        maxTurns: frontmatter.maxTurns || '',
        skills: frontmatter.skills || '',
        tier: getTier(frontmatter.model, frontmatter.name || file.replace('.md', '')),
        responsibilities: responsibilities.slice(0, 4)
      });
    }
    res.json(agents);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// --- API: Get all skills ---
app.get('/api/skills', (req, res) => {
  const skillsDir = path.join(PROJECT_ROOT, '.claude', 'skills');
  const skills = [];
  try {
    const dirs = fs.readdirSync(skillsDir).filter(d =>
      fs.statSync(path.join(skillsDir, d)).isDirectory()
    );
    for (const dir of dirs) {
      const skillFile = path.join(skillsDir, dir, 'SKILL.md');
      if (fs.existsSync(skillFile)) {
        const content = fs.readFileSync(skillFile, 'utf8');
        const frontmatter = parseFrontmatter(content);
        skills.push({
          id: dir,
          name: frontmatter.name || dir,
          description: (frontmatter.description || '').replace(/^"|"$/g, ''),
          category: getSkillCategory(dir)
        });
      }
    }
    res.json(skills);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// --- API: Get all rules ---
app.get('/api/rules', (req, res) => {
  const rulesDir = path.join(PROJECT_ROOT, '.claude', 'rules');
  const rules = [];
  try {
    const files = fs.readdirSync(rulesDir).filter(f => f.endsWith('.md'));
    for (const file of files) {
      const content = fs.readFileSync(path.join(rulesDir, file), 'utf8');
      const lines = content.split('\n');
      const title = lines.find(l => l.startsWith('# '))?.replace('# ', '') || file.replace('.md', '');
      const pathMatch = content.match(/Applies to.*?`([^`]+)`/i) || content.match(/Path.*?`([^`]+)`/i);
      rules.push({
        id: file.replace('.md', ''),
        title,
        path: pathMatch ? pathMatch[1] : file.replace('.md', '').replace(/-/g, '/'),
        content: content.substring(0, 500)
      });
    }
    res.json(rules);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// --- API: Get hooks list ---
app.get('/api/hooks', (req, res) => {
  const hooks = [
    { id: 'session-start', name: 'session-start.sh', trigger: 'SessionStart', desc: 'Load project context at session start', blocking: false },
    { id: 'detect-gaps', name: 'detect-gaps.sh', trigger: 'SessionStart', desc: 'Detect missing docs when code/prototypes exist', blocking: false },
    { id: 'validate-commit', name: 'validate-commit.sh', trigger: 'PreToolUse (Bash)', desc: 'Validate git commit: hardcoded values, JSON, design docs', blocking: true },
    { id: 'validate-push', name: 'validate-push.sh', trigger: 'PreToolUse (Bash)', desc: 'Warn on pushes to protected branches', blocking: true },
    { id: 'validate-assets', name: 'validate-assets.sh', trigger: 'PostToolUse (Write/Edit)', desc: 'Validate asset naming conventions and JSON format', blocking: false },
    { id: 'pre-compact', name: 'pre-compact.sh', trigger: 'PreCompact', desc: 'Save session state before context compression', blocking: false },
    { id: 'session-stop', name: 'session-stop.sh', trigger: 'Stop', desc: 'Log session summary for audit trail', blocking: false },
    { id: 'log-agent', name: 'log-agent.sh', trigger: 'SubagentStart', desc: 'Audit trail of all subagent invocations', blocking: false },
  ];
  res.json(hooks);
});

// --- API: Run a hook ---
app.post('/api/hooks/run', (req, res) => {
  const { hookId, stdin } = req.body;
  const hookFile = path.join(PROJECT_ROOT, '.claude', 'hooks', `${hookId}.sh`);
  if (!fs.existsSync(hookFile)) {
    return res.status(404).json({ error: 'Hook not found' });
  }
  try {
    const result = execSync(`echo '${(stdin || '').replace(/'/g, "'\\''")}' | bash "${hookFile}" 2>&1`, {
      cwd: PROJECT_ROOT,
      timeout: 10000,
      encoding: 'utf8'
    });
    res.json({ output: result, exitCode: 0 });
  } catch (e) {
    res.json({ output: e.stdout || e.stderr || e.message, exitCode: e.status || 1 });
  }
});

// --- API: Run statusline ---
app.post('/api/statusline', (req, res) => {
  const { input } = req.body;
  try {
    const result = execSync(`echo '${input.replace(/'/g, "'\\''")}' | bash .claude/statusline.sh 2>&1`, {
      cwd: PROJECT_ROOT,
      timeout: 5000,
      encoding: 'utf8'
    });
    res.json({ output: result.trim() });
  } catch (e) {
    res.json({ output: e.stdout || 'Error', exitCode: 1 });
  }
});

// --- API: Project stats ---
app.get('/api/stats', (req, res) => {
  try {
    const agentCount = fs.readdirSync(path.join(PROJECT_ROOT, '.claude', 'agents')).filter(f => f.endsWith('.md')).length;
    const skillCount = fs.readdirSync(path.join(PROJECT_ROOT, '.claude', 'skills')).filter(d =>
      fs.statSync(path.join(PROJECT_ROOT, '.claude', 'skills', d)).isDirectory()
    ).length;
    const ruleCount = fs.readdirSync(path.join(PROJECT_ROOT, '.claude', 'rules')).filter(f => f.endsWith('.md')).length;
    const hookCount = fs.readdirSync(path.join(PROJECT_ROOT, '.claude', 'hooks')).filter(f => f.endsWith('.sh')).length;
    const branch = execSync('git rev-parse --abbrev-ref HEAD 2>/dev/null', { cwd: PROJECT_ROOT, encoding: 'utf8' }).trim();
    const commits = execSync('git log --oneline -5 2>/dev/null', { cwd: PROJECT_ROOT, encoding: 'utf8' }).trim();
    res.json({ agentCount, skillCount, ruleCount, hookCount, branch, commits });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// Village Management System APIs
// ============================================================

// --- Village API: Get all agents ---
app.get('/api/village/agents', (req, res) => {
  const agentsDir = path.join(PROJECT_ROOT, 'village-system', 'agents');
  const agents = [];
  try {
    const files = fs.readdirSync(agentsDir).filter(f => f.endsWith('.md'));
    for (const file of files) {
      const content = fs.readFileSync(path.join(agentsDir, file), 'utf8');
      const frontmatter = parseFrontmatter(content);
      agents.push({
        id: file.replace('.md', ''),
        name: frontmatter.name || file.replace('.md', ''),
        description: (frontmatter.description || '').replace(/^"|"$/g, ''),
        model: frontmatter.model || 'unknown',
        tools: frontmatter.tools || '',
        maxTurns: frontmatter.maxTurns || '',
        tier: getVillageTier(frontmatter.name || file.replace('.md', '')),
        department: getVillageDept(file.replace('.md', ''))
      });
    }
    res.json(agents);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// --- Village API: Get all skills ---
app.get('/api/village/skills', (req, res) => {
  const skillsDir = path.join(PROJECT_ROOT, 'village-system', 'skills');
  const skills = [];
  try {
    const dirs = fs.readdirSync(skillsDir).filter(d =>
      fs.statSync(path.join(skillsDir, d)).isDirectory()
    );
    for (const dir of dirs) {
      const skillFile = path.join(skillsDir, dir, 'SKILL.md');
      if (fs.existsSync(skillFile)) {
        const content = fs.readFileSync(skillFile, 'utf8');
        const frontmatter = parseFrontmatter(content);
        skills.push({
          id: dir,
          name: frontmatter.name || dir,
          description: (frontmatter.description || '').replace(/^"|"$/g, ''),
          category: getVillageSkillCategory(dir)
        });
      }
    }
    res.json(skills);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// --- Village API: Get rules ---
app.get('/api/village/rules', (req, res) => {
  const rulesDir = path.join(PROJECT_ROOT, 'village-system', 'rules');
  const rules = [];
  try {
    const files = fs.readdirSync(rulesDir).filter(f => f.endsWith('.md'));
    for (const file of files) {
      const content = fs.readFileSync(path.join(rulesDir, file), 'utf8');
      const fm = parseFrontmatter(content);
      const title = content.split('\n').find(l => l.startsWith('# '))?.replace('# ', '') || file.replace('.md', '');
      rules.push({
        id: file.replace('.md', ''),
        title,
        path: fm.path || file.replace('.md', ''),
        content: content.substring(0, 500)
      });
    }
    res.json(rules);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// --- Village API: Get hooks ---
app.get('/api/village/hooks', (req, res) => {
  const hooks = [
    { id: 'validate-rotation', name: 'validate-rotation.sh', trigger: '种植计划提交', desc: '检查轮作合规性，阻止茄科连作', blocking: true },
    { id: 'validate-quality', name: 'validate-quality.sh', trigger: '检测报告提交', desc: '验证质量检测报告完整性和合规性', blocking: true },
    { id: 'validate-pricing', name: 'validate-pricing.sh', trigger: '定价变更', desc: '检查定价是否在合理毛利区间', blocking: false },
    { id: 'weather-alert-trigger', name: 'weather-alert-trigger.sh', trigger: '天气数据更新', desc: '触发霜冻/高温/暴雨等农事预警', blocking: false },
    { id: 'validate-expense', name: 'validate-expense.sh', trigger: '支出记录提交', desc: '检查支出金额审批权限合规', blocking: true },
    { id: 'validate-brand-assets', name: 'validate-brand-assets.sh', trigger: '品牌资产上传', desc: '检查品牌文件命名规范和格式', blocking: false },
  ];
  res.json(hooks);
});

// --- Village API: Run a hook ---
app.post('/api/village/hooks/run', (req, res) => {
  const { hookId, testData } = req.body;
  const hookFile = path.join(PROJECT_ROOT, 'village-system', 'hooks', `${hookId}.sh`);
  if (!fs.existsSync(hookFile)) {
    return res.status(404).json({ error: 'Hook not found' });
  }
  try {
    // Create temp test file if test data provided
    let tempFile = '';
    let cleanupCmd = '';
    if (testData) {
      const testDir = `/tmp/village_test_${Date.now()}`;
      const testFilePath = `${testDir}/${testData.path || 'test.json'}`;
      execSync(`mkdir -p $(dirname ${testFilePath})`, { encoding: 'utf8' });
      fs.writeFileSync(testFilePath, JSON.stringify(testData.content || {}));
      tempFile = testFilePath;
      cleanupCmd = `rm -rf ${testDir}`;
    }
    
    const result = execSync(`bash "${hookFile}" "${tempFile}" 2>&1`, {
      cwd: PROJECT_ROOT,
      timeout: 10000,
      encoding: 'utf8'
    });
    if (cleanupCmd) execSync(cleanupCmd);
    res.json({ output: result, exitCode: 0 });
  } catch (e) {
    res.json({ output: e.stdout || e.stderr || e.message, exitCode: e.status || 1 });
  }
});

// --- Village API: Read a doc file ---
app.get('/api/village/doc/:category/:file', (req, res) => {
  const { category, file } = req.params;
  let filePath;
  if (category === '_root') {
    filePath = path.join(PROJECT_ROOT, 'village-system', 'docs', file + '.md');
  } else {
    filePath = path.join(PROJECT_ROOT, 'village-system', 'docs', category, file + '.md');
  }
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'Doc not found' });
  }
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    res.json({ content });
  } catch(e) {
    res.status(500).json({ error: e.message });
  }
});

// --- Village API: Read the usage guide ---
app.get('/api/village/usage-guide', (req, res) => {
  const guidePath = path.join(PROJECT_ROOT, 'village-system', 'docs', 'usage-guide.md');
  if (!fs.existsSync(guidePath)) {
    return res.status(404).json({ error: 'Guide not found' });
  }
  try {
    const content = fs.readFileSync(guidePath, 'utf8');
    res.json({ content });
  } catch(e) {
    res.status(500).json({ error: e.message });
  }
});

// --- Village API: Simulate a skill workflow ---
app.post('/api/village/simulate', (req, res) => {
  const { scenario } = req.body;
  // Return a simulated multi-agent workflow based on scenario
  const simulations = {
    'crop-plan': {
      title: '年度种植方案规划',
      steps: [
        { agent: 'planting-director', icon: '🌱', action: '接收任务', detail: '种植部长收到规划请求，开始协调调研' },
        { agent: 'soil-expert', icon: '🧪', action: '土壤检测', detail: '取样 12 个点位，pH 6.2，有机质 2.8%，土壤状况良好', delay: 800 },
        { agent: 'meteorologist', icon: '🌤️', action: '气候分析', detail: '年均温 18°C，无霜期 280 天，雨季 5-8 月', delay: 600 },
        { agent: 'pricing-analyst', icon: '💹', action: '市场调研', detail: '草莓行情看涨(+15%)，辣椒供应过剩(-8%)，柑橘稳定', delay: 1000 },
        { agent: 'seed-expert', icon: '🌾', action: '品种推荐', detail: '推荐红颜草莓(大棚)、湘研辣椒(旱地)、脐橙(山地)', delay: 500 },
        { agent: 'finance-director', icon: '💰', action: '预算核算', detail: '方案A投入55万/利润65万，方案B投入85万/利润95万', delay: 700 },
        { agent: 'planting-director', icon: '📋', action: '方案生成', detail: '生成 3 套对比方案（稳健/增长/创新），推荐增长型方案B', delay: 400 }
      ]
    },
    'product-launch': {
      title: '产品上市销售',
      steps: [
        { agent: 'harvest-expert', icon: '🌾', action: '采收确认', detail: '草莓大棚预计下周采收，产量 2000斤/周' },
        { agent: 'food-safety-inspector', icon: '🔍', action: '质量检测', detail: '抽检 5 批次，农残未检出 ✅，糖度 12.5°Brix', delay: 800 },
        { agent: 'pricing-analyst', icon: '💰', action: '定价策略', detail: '批发15元/斤，电商29.9元/500g，直播35.9元/kg', delay: 600 },
        { agent: 'sales-director', icon: '📦', action: '渠道分配', detail: '批发40%、电商30%、直播20%、采摘10%', delay: 500 },
        { agent: 'ecommerce-operator', icon: '📱', action: '电商上架', detail: '抖音+拼多多同步上线，主图/详情页已就绪', delay: 700 },
        { agent: 'livestream-seller', icon: '🎬', action: '直播策划', detail: '每周三/五/日 3场直播，首场主打"田间直发"', delay: 600 },
        { agent: 'logistics-expert', icon: '🚛', action: '物流对接', detail: '顺丰冷链协议确认，次日达覆盖省内，首重5元', delay: 400 }
      ]
    },
    'emergency-weather': {
      title: '暴雨应急处理',
      steps: [
        { agent: 'meteorologist', icon: '🌧️', action: '预警触发', detail: '⚠️ 未来48小时持续暴雨，累计降雨量 120mm' },
        { agent: 'planting-director', icon: '📋', action: '损失评估', detail: '水稻灌浆期 80 亩高风险，蔬菜 30 亩需紧急处理', delay: 500 },
        { agent: 'machinery-expert', icon: '🚜', action: '抢收调度', detail: '调配 3 台收割机抢收成熟蔬菜 20 亩', delay: 600 },
        { agent: 'irrigation-engineer', icon: '💧', action: '排水防涝', detail: '开启所有排水沟闸门，确认 3 台水泵就位', delay: 400 },
        { agent: 'warehouse-expert', icon: '📦', action: '仓储准备', detail: '腾出 2 号仓库 50 立方，准备防潮物资', delay: 300 },
        { agent: 'finance-director', icon: '💰', action: '资金评估', detail: '应急储备金剩余 3.2 万，本次预估支出 8000 元', delay: 500 }
      ]
    },
    'pest-outbreak': {
      title: '病虫害爆发处理',
      steps: [
        { agent: 'pest-control-expert', icon: '🐛', action: '虫害确认', detail: '100亩水稻发现稻飞虱，密度超标 3 倍，紧急处理' },
        { agent: 'pest-control-expert', icon: '💊', action: '用药方案', detail: '推荐吡虫啉+灯诱组合，生物+化学双管齐下', delay: 600 },
        { agent: 'planting-director', icon: '✅', action: '方案审批', detail: '审核通过，预估费用 8000 元，在应急预算内', delay: 400 },
        { agent: 'machinery-expert', icon: '🚁', action: '设备调度', detail: '调配 2 台植保无人机，预计 2 天完成 100 亩', delay: 500 },
        { agent: 'logistics-director', icon: '🏪', action: '物资采购', detail: '紧急采购吡虫啉 500 瓶，太阳能杀虫灯 20 套', delay: 700 },
        { agent: 'pest-control-expert', icon: '🔄', action: '效果复查', detail: '3 天后复查：虫口密度下降 85%，防治成功 ✅', delay: 800 }
      ]
    }
  };
  res.json(simulations[scenario] || { error: 'Unknown scenario' });
});

// --- Village API: Get docs structure ---
app.get('/api/village/docs', (req, res) => {
  const docsDir = path.join(PROJECT_ROOT, 'village-system', 'docs');
  const docs = {};
  try {
    const categories = fs.readdirSync(docsDir).filter(d => {
      const fullPath = path.join(docsDir, d);
      return fs.statSync(fullPath).isDirectory();
    });
    for (const cat of categories) {
      const catDir = path.join(docsDir, cat);
      const files = fs.readdirSync(catDir).filter(f => f.endsWith('.md'));
      docs[cat] = files.map(f => {
        const content = fs.readFileSync(path.join(catDir, f), 'utf8');
        const title = content.split('\n').find(l => l.startsWith('# '))?.replace('# ', '') || f;
        return { id: f.replace('.md', ''), title, filename: f };
      });
    }
    // Add architecture.md
    if (fs.existsSync(path.join(docsDir, 'architecture.md'))) {
      docs['_root'] = [{ id: 'architecture', title: '系统架构文档', filename: 'architecture.md' }];
    }
    res.json(docs);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// --- Village API: Get stats ---
app.get('/api/village/stats', (req, res) => {
  try {
    const agentCount = fs.readdirSync(path.join(PROJECT_ROOT, 'village-system', 'agents')).filter(f => f.endsWith('.md')).length;
    const skillCount = fs.readdirSync(path.join(PROJECT_ROOT, 'village-system', 'skills')).filter(d =>
      fs.statSync(path.join(PROJECT_ROOT, 'village-system', 'skills', d)).isDirectory()
    ).length;
    const ruleCount = fs.readdirSync(path.join(PROJECT_ROOT, 'village-system', 'rules')).filter(f => f.endsWith('.md')).length;
    const hookCount = fs.readdirSync(path.join(PROJECT_ROOT, 'village-system', 'hooks')).filter(f => f.endsWith('.sh')).length;
    const templateCount = fs.readdirSync(path.join(PROJECT_ROOT, 'village-system', 'templates')).filter(f => f.endsWith('.md')).length;
    
    let docCount = 0;
    const docsDir = path.join(PROJECT_ROOT, 'village-system', 'docs');
    const countMdFiles = (dir) => {
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        if (fs.statSync(fullPath).isDirectory()) countMdFiles(fullPath);
        else if (item.endsWith('.md')) docCount++;
      }
    };
    countMdFiles(docsDir);
    
    res.json({ agentCount, skillCount, ruleCount, hookCount, templateCount, docCount });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Village helpers
function getVillageTier(name) {
  const tier1 = ['village-chief', 'agri-tech-director', 'operations-director'];
  const tier2 = ['planting-director', 'sales-director', 'quality-director', 'finance-director', 'brand-director', 'logistics-director', 'ecology-director'];
  if (tier1.includes(name)) return 1;
  if (tier2.includes(name)) return 2;
  return 3;
}

function getVillageDept(name) {
  const depts = {
    'village-chief': '村级领导', 'agri-tech-director': '村级领导', 'operations-director': '村级领导',
    'planting-director': '种植部', 'soil-expert': '种植部', 'meteorologist': '种植部', 'seed-expert': '种植部',
    'irrigation-engineer': '种植部', 'pest-control-expert': '种植部', 'machinery-expert': '种植部', 'harvest-expert': '种植部',
    'sales-director': '销售部', 'ecommerce-operator': '销售部', 'livestream-seller': '销售部',
    'wholesale-expert': '销售部', 'logistics-expert': '销售部', 'pricing-analyst': '销售部',
    'brand-director': '品牌部', 'packaging-designer': '品牌部', 'agritourism-expert': '品牌部',
    'quality-director': '质检部', 'food-safety-inspector': '质检部', 'organic-certifier': '质检部',
    'finance-director': '财务部', 'accountant': '财务部', 'cost-analyst': '财务部',
    'logistics-director': '后勤部', 'warehouse-expert': '后勤部', 'land-planner': '后勤部', 'water-expert': '后勤部',
    'ecology-director': '生态部', 'trainer': '生态部'
  };
  return depts[name] || '其他';
}

function getVillageSkillCategory(name) {
  const cats = {
    'crop-plan': '种植管理', 'soil-analysis': '种植管理', 'pest-alert': '种植管理', 'irrigation-plan': '种植管理',
    'harvest-schedule': '种植管理', 'rotation-plan': '种植管理', 'seed-select': '种植管理', 'fertilizer-plan': '种植管理',
    'market-analysis': '销售管理', 'pricing-strategy': '销售管理', 'channel-plan': '销售管理', 'launch-product': '销售管理',
    'brand-build': '销售管理', 'livestream-plan': '销售管理',
    'seasonal-plan': '运营管理', 'budget-review': '运营管理', 'cost-analysis': '运营管理', 'resource-check': '运营管理',
    'weather-alert': '运营管理', 'training-plan': '运营管理',
    'quality-check': '质量认证', 'organic-audit': '质量认证', 'food-safety-review': '质量认证',
  };
  if (name.startsWith('team-')) return '团队协调';
  return cats[name] || '其他';
}

// Helpers
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const obj = {};
  match[1].split('\n').forEach(line => {
    const idx = line.indexOf(':');
    if (idx > 0) {
      const key = line.substring(0, idx).trim();
      const val = line.substring(idx + 1).trim();
      obj[key] = val;
    }
  });
  return obj;
}

function getTier(model, name) {
  const directors = ['creative-director', 'technical-director', 'producer'];
  const leads = ['game-designer', 'lead-programmer', 'art-director', 'audio-director', 'narrative-director', 'qa-lead', 'release-manager', 'localization-lead'];
  if (directors.includes(name)) return 1;
  if (leads.includes(name)) return 2;
  return 3;
}

function getSkillCategory(name) {
  const categories = {
    'design-review': 'Reviews', 'code-review': 'Reviews', 'balance-check': 'Reviews', 'asset-audit': 'Reviews', 'scope-check': 'Reviews', 'perf-profile': 'Reviews', 'tech-debt': 'Reviews',
    'sprint-plan': 'Production', 'milestone-review': 'Production', 'estimate': 'Production', 'retrospective': 'Production', 'bug-report': 'Production',
    'start': 'Project', 'project-stage-detect': 'Project', 'reverse-document': 'Project', 'gate-check': 'Project', 'map-systems': 'Project', 'design-system': 'Project', 'architecture-decision': 'Project', 'setup-engine': 'Project',
    'release-checklist': 'Release', 'launch-checklist': 'Release', 'changelog': 'Release', 'patch-notes': 'Release', 'hotfix': 'Release',
    'brainstorm': 'Creative', 'playtest-report': 'Creative', 'prototype': 'Creative', 'onboard': 'Creative', 'localize': 'Creative',
  };
  if (name.startsWith('team-')) return 'Team Orchestration';
  return categories[name] || 'Other';
}

// ============================================================
// Game Save / Load API — persists progress across devices
// ============================================================
const SAVE_SLOTS_DIR = path.join(__dirname, 'data', 'saves');
if (!fs.existsSync(SAVE_SLOTS_DIR)) fs.mkdirSync(SAVE_SLOTS_DIR, { recursive: true });

// POST /api/game/save — save game state
app.post('/api/game/save', (req, res) => {
  try {
    const state = req.body;
    if (!state || typeof state !== 'object') {
      return res.status(400).json({ error: '无效的存档数据' });
    }
    const slot = state.slot || 'auto';
    const saveData = {
      ...state,
      savedAt: new Date().toISOString(),
      version: 2
    };
    // Save to slot file
    const slotPath = path.join(SAVE_SLOTS_DIR, `save-${slot}.json`);
    fs.writeFileSync(slotPath, JSON.stringify(saveData, null, 2));
    // Also write to main save file for backward compat
    fs.writeFileSync(GAME_SAVE_PATH, JSON.stringify(saveData, null, 2));
    res.json({ success: true, slot, savedAt: saveData.savedAt });
  } catch (e) {
    console.error('Save error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// GET /api/game/load — load game state (optional ?slot=xxx)
app.get('/api/game/load', (req, res) => {
  try {
    const slot = req.query.slot || 'auto';
    const slotPath = path.join(SAVE_SLOTS_DIR, `save-${slot}.json`);
    // Try slot file first, then fallback to main save
    let savePath = fs.existsSync(slotPath) ? slotPath : GAME_SAVE_PATH;
    if (!fs.existsSync(savePath)) {
      return res.json({ found: false });
    }
    const raw = fs.readFileSync(savePath, 'utf8');
    const data = JSON.parse(raw);
    res.json({ found: true, data });
  } catch (e) {
    console.error('Load error:', e.message);
    res.json({ found: false, error: e.message });
  }
});

// GET /api/game/saves — list all save slots
app.get('/api/game/saves', (req, res) => {
  try {
    const files = fs.readdirSync(SAVE_SLOTS_DIR).filter(f => f.startsWith('save-') && f.endsWith('.json'));
    const saves = files.map(f => {
      try {
        const raw = JSON.parse(fs.readFileSync(path.join(SAVE_SLOTS_DIR, f), 'utf8'));
        return { slot: f.replace('save-', '').replace('.json', ''), savedAt: raw.savedAt, day: raw.day, year: raw.year, season: raw.season, gold: raw.gold };
      } catch { return null; }
    }).filter(Boolean);
    res.json(saves);
  } catch (e) {
    res.json([]);
  }
});

// DELETE /api/game/save/:slot — delete a save slot
app.delete('/api/game/save/:slot', (req, res) => {
  try {
    const slotPath = path.join(SAVE_SLOTS_DIR, `save-${req.params.slot}.json`);
    if (fs.existsSync(slotPath)) fs.unlinkSync(slotPath);
    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// HD 2.5D Asset Manifest API
// ============================================================
const HD_ASSETS_DIR = path.join(__dirname, 'public', 'game', 'assets');

app.get('/api/game/hd-assets', (req, res) => {
  try {
    const manifest = { terrain: {}, buildings: {}, decorations: {} };
    // Scan terrain
    const terrainDir = path.join(HD_ASSETS_DIR, 'hd-terrain');
    if (fs.existsSync(terrainDir)) {
      fs.readdirSync(terrainDir).filter(f => f.endsWith('.png')).forEach(f => {
        const name = f.replace('.png', '');
        manifest.terrain[name] = `/game/assets/hd-terrain/${f}`;
      });
    }
    // Scan buildings
    const buildingDir = path.join(HD_ASSETS_DIR, 'hd-buildings');
    if (fs.existsSync(buildingDir)) {
      fs.readdirSync(buildingDir).filter(f => f.endsWith('.png')).forEach(f => {
        const name = f.replace('.png', '');
        manifest.buildings[name] = `/game/assets/hd-buildings/${f}`;
      });
    }
    // Scan decorations
    const decoDir = path.join(HD_ASSETS_DIR, 'hd-decorations');
    if (fs.existsSync(decoDir)) {
      fs.readdirSync(decoDir).filter(f => f.endsWith('.png')).forEach(f => {
        const name = f.replace('.png', '');
        manifest.decorations[name] = `/game/assets/hd-decorations/${f}`;
      });
    }
    res.json(manifest);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// AI Asset Generation API (proxy for Banana Pro)
// ============================================================
app.post('/api/ai/generate-asset', (req, res) => {
  try {
    const { type, description, style } = req.body;
    if (!type || !description) {
      return res.status(400).json({ error: 'type and description required' });
    }
    // Return the prompt template for the client to use with the AI image generation
    // The actual generation happens client-side through the GenSpark platform
    const prompts = {
      terrain: `A seamless tileable game terrain tile of ${description} for a 2.5D isometric rural village simulation game. Beautiful hand-painted style with soft lighting, subtle shadows. Top-down view with slight isometric perspective. ${style || 'Warm sunlit atmosphere'}. Game asset, seamless texture, professional game art quality.`,
      building: `A beautiful 2.5D isometric ${description} building for a rural Chinese village simulation game. ${style || 'Traditional architecture style'}. Warm lighting, hand-painted game art style. Top-down isometric 45-degree view. White/transparent background. Game asset, isolated object, professional quality.`,
      decoration: `A beautiful 2.5D isometric ${description} for a village simulation game. Hand-painted game art style, warm natural lighting. Top-down isometric view. White/transparent background. Game asset, isolated object, professional quality.`
    };
    res.json({
      success: true,
      prompt: prompts[type] || prompts.decoration,
      type,
      description,
      tip: 'Use this prompt with Banana Pro image generation to create your custom asset'
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// Isometric 2.5D Asset Manifest API
// ============================================================
app.get('/api/game/iso-assets', (req, res) => {
  try {
    const manifest = { terrain: {}, buildings: {}, decorations: {}, baseMap: null };
    const scan = (sub, target) => {
      const dir = path.join(HD_ASSETS_DIR, sub);
      if (fs.existsSync(dir)) {
        fs.readdirSync(dir).filter(f => f.endsWith('.png')).forEach(f => {
          const name = f.replace('.png', '');
          if (name === 'base-map') { manifest.baseMap = `/game/assets/${sub}/${f}`; }
          else { target[name] = `/game/assets/${sub}/${f}`; }
        });
      }
    };
    scan('iso-terrain', manifest.terrain);
    scan('iso-buildings', manifest.buildings);
    scan('iso-decorations', manifest.decorations);
    res.json(manifest);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Claude Code Game Studios Dashboard running on http://0.0.0.0:${PORT}`);
});
