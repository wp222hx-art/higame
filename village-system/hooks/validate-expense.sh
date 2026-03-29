#!/bin/bash
# validate-expense.sh — 检查支出记录是否有合规的审批
# 触发时机：新增支出记录时

EXPENSE_FILE="$1"

if [ -z "$EXPENSE_FILE" ]; then
  echo "用法: validate-expense.sh <支出记录文件>"
  exit 0
fi

if [[ ! "$EXPENSE_FILE" =~ data/finance/ ]]; then
  exit 0
fi

echo "=== 支出审批合规检查 ==="

if command -v jq &>/dev/null && [ -f "$EXPENSE_FILE" ]; then
  AMOUNT=$(jq -r '.amount // 0' "$EXPENSE_FILE" 2>/dev/null)
  APPROVER=$(jq -r '.approved_by // empty' "$EXPENSE_FILE" 2>/dev/null)
  
  AMOUNT_INT=${AMOUNT%.*}
  
  if [ "$AMOUNT_INT" -gt 5000 ] 2>/dev/null && [ -z "$APPROVER" ]; then
    echo "❌ 阻断：支出金额 ¥${AMOUNT} 超过5000元，需要 operations-director 审批"
    exit 2
  fi
  
  if [ "$AMOUNT_INT" -gt 20000 ] 2>/dev/null; then
    if [[ "$APPROVER" != *"village-chief"* ]]; then
      echo "❌ 阻断：支出金额 ¥${AMOUNT} 超过20000元，需要 village-chief 审批"
      exit 2
    fi
  fi
  
  if [ "$AMOUNT_INT" -gt 50000 ] 2>/dev/null; then
    echo "⚠️ 重大支出提醒：¥${AMOUNT}，请确认已通过村民代表会议"
  fi
fi

echo "✅ 支出审批检查完成"
exit 0
