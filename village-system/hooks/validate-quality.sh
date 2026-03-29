#!/bin/bash
# validate-quality.sh — 检查质量检测报告的完整性
# 触发时机：新增质量检测报告时

REPORT_FILE="$1"

if [ -z "$REPORT_FILE" ]; then
  echo "用法: validate-quality.sh <检测报告文件>"
  exit 0
fi

if [[ ! "$REPORT_FILE" =~ data/quality/ ]]; then
  exit 0
fi

echo "=== 质量检测报告验证 ==="

if command -v jq &>/dev/null && [ -f "$REPORT_FILE" ]; then
  if ! jq empty "$REPORT_FILE" 2>/dev/null; then
    echo "❌ 阻断：检测报告不是有效的 JSON 格式"
    exit 2
  fi
  
  # 检查必填字段
  REQUIRED_FIELDS=("sample_id" "product_name" "sample_date" "test_items" "result" "conclusion")
  MISSING=0
  
  for field in "${REQUIRED_FIELDS[@]}"; do
    if ! jq -e ".$field" "$REPORT_FILE" &>/dev/null; then
      echo "❌ 缺少必填字段：$field"
      MISSING=1
    fi
  done
  
  if [ $MISSING -eq 1 ]; then
    echo "❌ 阻断：检测报告缺少必填字段"
    exit 2
  fi
  
  # 检查农残是否超标
  CONCLUSION=$(jq -r '.conclusion // empty' "$REPORT_FILE" 2>/dev/null)
  if [[ "$CONCLUSION" == *"不合格"* ]] || [[ "$CONCLUSION" == *"超标"* ]]; then
    echo "🔴 严重警告：检测结果不合格！已通知 quality-director"
    echo "   相关产品必须停止出货直至复检合格"
  fi
fi

echo "✅ 质量报告验证完成"
exit 0
