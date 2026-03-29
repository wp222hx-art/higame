#!/bin/bash
# validate-brand-assets.sh — 检查品牌资产文件命名和规格
# 触发时机：新增品牌资产文件时

ASSET_FILE="$1"

if [ -z "$ASSET_FILE" ]; then
  echo "用法: validate-brand-assets.sh <资产文件路径>"
  exit 0
fi

if [[ ! "$ASSET_FILE" =~ assets/brand/ ]]; then
  exit 0
fi

echo "=== 品牌资产规范检查 ==="

FILENAME=$(basename "$ASSET_FILE")

# 检查文件名是否全小写+下划线
if [[ "$FILENAME" =~ [A-Z] ]]; then
  echo "⚠️ 警告：文件名包含大写字母 '$FILENAME'"
  echo "   品牌资产文件名应使用小写字母和下划线"
fi

if [[ "$FILENAME" =~ [[:space:]] ]]; then
  echo "❌ 阻断：文件名包含空格 '$FILENAME'"
  echo "   请使用下划线替代空格"
  exit 2
fi

# 检查图片类型
if [[ "$FILENAME" =~ \.(png|jpg|jpeg|gif|webp)$ ]]; then
  echo "✅ 图片文件格式正确"
elif [[ "$FILENAME" =~ \.(ai|svg|eps|pdf)$ ]]; then
  echo "✅ 矢量/设计文件格式正确"
else
  echo "⚠️ 注意：非标准品牌资产格式，请确认"
fi

echo "✅ 品牌资产检查完成"
exit 0
