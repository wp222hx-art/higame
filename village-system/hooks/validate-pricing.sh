#!/bin/bash
# validate-pricing.sh — 检查定价是否在合理区间
# 触发时机：修改产品定价时

PRICING_FILE="$1"

if [ -z "$PRICING_FILE" ]; then
  echo "用法: validate-pricing.sh <定价文件>"
  exit 0
fi

if [[ ! "$PRICING_FILE" =~ data/sales/ ]]; then
  exit 0
fi

echo "=== 定价合理性检查 ==="

if command -v jq &>/dev/null && [ -f "$PRICING_FILE" ]; then
  if ! jq empty "$PRICING_FILE" 2>/dev/null; then
    echo "❌ 定价文件格式错误"
    exit 2
  fi
  
  # 检查是否有成本价和售价
  COST=$(jq -r '.cost_per_kg // empty' "$PRICING_FILE" 2>/dev/null)
  PRICE=$(jq -r '.price_per_kg // empty' "$PRICING_FILE" 2>/dev/null)
  
  if [ -n "$COST" ] && [ -n "$PRICE" ]; then
    # 使用 bc 或 awk 计算毛利率
    MARGIN=$(echo "$COST $PRICE" | awk '{if($2>0) printf "%.0f", (($2-$1)/$2)*100; else print "0"}')
    
    if [ "$MARGIN" -lt 0 ]; then
      echo "🔴 警告：定价低于成本！毛利率 ${MARGIN}%"
      echo "   请确认是否为促销价，如非促销需 sales-director 审批"
    elif [ "$MARGIN" -lt 10 ]; then
      echo "⚠️ 注意：毛利率偏低 (${MARGIN}%)，请确认定价策略"
    elif [ "$MARGIN" -gt 80 ]; then
      echo "⚠️ 注意：毛利率异常高 (${MARGIN}%)，请确认是否合理"
    else
      echo "✅ 毛利率 ${MARGIN}% — 在正常范围内"
    fi
  fi
fi

echo "✅ 定价检查完成"
exit 0
