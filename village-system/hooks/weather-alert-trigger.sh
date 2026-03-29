#!/bin/bash
# weather-alert-trigger.sh — 检查天气数据并触发农事提醒
# 触发时机：天气数据更新时

echo "=== 天气预警检查 ==="

WEATHER_FILE="$1"

if [ -n "$WEATHER_FILE" ] && [ -f "$WEATHER_FILE" ] && command -v jq &>/dev/null; then
  TEMP=$(jq -r '.temperature // empty' "$WEATHER_FILE" 2>/dev/null)
  RAIN=$(jq -r '.rainfall_mm // empty' "$WEATHER_FILE" 2>/dev/null)
  
  if [ -n "$TEMP" ]; then
    TEMP_INT=${TEMP%.*}
    if [ "$TEMP_INT" -le 0 ] 2>/dev/null; then
      echo "🔴 霜冻预警：温度 ${TEMP}°C，请启动防冻措施"
    elif [ "$TEMP_INT" -ge 38 ] 2>/dev/null; then
      echo "🔴 高温预警：温度 ${TEMP}°C，请启动防暑降温措施"
    fi
  fi
  
  if [ -n "$RAIN" ]; then
    RAIN_INT=${RAIN%.*}
    if [ "$RAIN_INT" -ge 50 ] 2>/dev/null; then
      echo "🔴 暴雨预警：预计降雨 ${RAIN}mm，请检查排水系统"
    elif [ "$RAIN_INT" -ge 25 ] 2>/dev/null; then
      echo "⚠️ 大雨提醒：预计降雨 ${RAIN}mm，注意防涝"
    fi
  fi
fi

echo "✅ 天气预警检查完成"
exit 0
