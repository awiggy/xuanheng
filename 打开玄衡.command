#!/bin/zsh

PROJECT_DIR="${0:A:h}"
SERVICE_URL="http://127.0.0.1:4173"
LOG_DIR="$PROJECT_DIR/.xuanheng"

mkdir -p "$LOG_DIR"

if /usr/bin/curl -fsS "$SERVICE_URL/api/history" >/dev/null 2>&1; then
  /usr/bin/open "$SERVICE_URL/#/home"
  exit 0
fi

PYTHON_BIN="$(command -v python3)"
if [[ -z "$PYTHON_BIN" ]]; then
  /usr/bin/osascript -e 'display alert "无法启动 Luma" message "没有找到 Python 3。" as critical'
  exit 1
fi

cd "$PROJECT_DIR" || exit 1
printf '\nLuma 正在启动，请保持此窗口开启。\n关闭本窗口会停止本地网站。\n\n'

(
  for _ in {1..40}; do
    if /usr/bin/curl -fsS "$SERVICE_URL/api/history" >/dev/null 2>&1; then
      /usr/bin/open "$SERVICE_URL/#/home"
      exit 0
    fi
    sleep 0.25
  done
  /usr/bin/osascript -e 'display alert "Luma 服务未能启动" message "请把此终端窗口中的错误信息交给开发者。" as critical'
) &

exec "$PYTHON_BIN" "$PROJECT_DIR/server.py"
