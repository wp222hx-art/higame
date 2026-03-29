#!/bin/bash
# validate-rotation.sh — 检查种植计划是否违反轮作规则
# 触发时机：新增/修改种植计划文件时

PLAN_FILE="$1"

if [ -z "$PLAN_FILE" ]; then
  echo "用法: validate-rotation.sh <种植计划文件>"
  exit 0
fi

# 检查是否为种植数据文件
if [[ ! "$PLAN_FILE" =~ data/planting/ ]]; then
  exit 0
fi

echo "=== 轮作合规检查 ==="

# 检查文件是否为有效JSON
if command -v jq &>/dev/null && [ -f "$PLAN_FILE" ]; then
  if ! jq empty "$PLAN_FILE" 2>/dev/null; then
    echo "❌ 阻断：种植计划文件不是有效的 JSON 格式"
    exit 2
  fi
  
  # 检查必填字段
  for field in plot_id crop variety area plant_date; do
    if ! jq -e ".$field" "$PLAN_FILE" &>/dev/null; then
      echo "⚠️ 警告：缺少字段 '$field'"
    fi
  done
  
  # 检查茄科连作
  CROP=$(jq -r '.crop // empty' "$PLAN_FILE" 2>/dev/null)
  PLOT_ID=$(jq -r '.plot_id // empty' "$PLAN_FILE" 2>/dev/null)
  
  SOLANACEAE=("tomato" "pepper" "eggplant" "potato" "番茄" "辣椒" "茄子" "马铃薯")
  
  for s in "${SOLANACEAE[@]}"; do
    if [[ "$CROP" == "$s" ]]; then
      echo "⚠️ 注意：$CROP 是茄科作物，请确认前茬不是茄科（不可连作）"
      # 实际系统会查询历史记录进行自动校验
      break
    fi
  done
fi

echo "✅ 轮作检查完成"
exit 0
