#!/bin/bash

# --- Конфигурация ---
TARGET_HOST="laptop"
MAX_VOLUME=70
SSH_TIMEOUT=5

# Получаем текущее время для логов
timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

echo "[$(timestamp)] Запуск проверки громкости для $TARGET_HOST..."

# 1. Проверяем доступность хоста (чтобы ssh не висел, если ноут выключен)
# Используем quiet режим ssh для проверки соединения
ssh -q -o BatchMode=yes -o ConnectTimeout=$SSH_TIMEOUT $TARGET_HOST exit
if [ $? -ne 0 ]; then
    echo "[$(timestamp)] Хост $TARGET_HOST недоступен или выключен. Пропуск."
    exit 0
fi

# 2. Формируем удаленную команду
# Мы используем EOF (Here-Doc) внутри переменной, чтобы не мучаться с экранированием кавычек.
# Переменные внутри 'REMOTE_SCRIPT' не раскрываются локально (благодаря 'EOF'),
# они выполнятся на ноутбуке.

read -r -d '' REMOTE_SCRIPT << 'EOF'
    # Находим сокет PulseAudio/PipeWire
    export XDG_RUNTIME_DIR="/run/user/$(id -u)"
    
    # Получаем текущую громкость (берем первый канал, убираем пробелы и проценты)
    CURRENT_RAW=$(pactl get-sink-volume @DEFAULT_SINK@ | head -n1 | cut -d/ -f2 | tr -d " %")
    
    # Защита от пустой строки (если вдруг формат вывода изменится)
    CURRENT=${CURRENT_RAW:-0}

    # Логика ассистента: сравниваем
    if [ "$CURRENT" -gt 70 ]; then
        pactl set-sink-volume @DEFAULT_SINK@ 70%
        echo "CHANGED: Громкость была $CURRENT%, снижена до 70%."
    else
        echo "OK: Громкость ($CURRENT%) уже в норме."
    fi
EOF

# 3. Выполняем
# Передаем скрипт через аргумент bash -s для чистоты
ssh -o ConnectTimeout=$SSH_TIMEOUT "$TARGET_HOST" "bash -s" <<< "$REMOTE_SCRIPT"

echo "[$(timestamp)] Готово."
