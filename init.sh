#!/bin/bash

# --- ЦВЕТА ДЛЯ КРАСОТЫ (HACKER STYLE) ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- ОПРЕДЕЛЕНИЕ ПУТЕЙ ---
# Получаем абсолютный путь к папке, где лежит этот скрипт
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VENV_DIR="$PROJECT_DIR/venv"
RUN_SCRIPT="$PROJECT_DIR/run.sh"
REQ_FILE="$PROJECT_DIR/requirements.txt"
ENV_FILE="$PROJECT_DIR/.env"

echo -e "${GREEN}[*] Запуск автоматической установки FreeGames Notifier...${NC}"
echo -e "${YELLOW}[i] Директория проекта: $PROJECT_DIR${NC}"

# 1. ПРОВЕРКА .ENV
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}[!] Файл .env не найден!${NC}"
    echo "    Сначала создайте .env и добавьте туда API_KEY."
    echo "    Пример: cp .env.example .env"
    exit 1
else
    echo -e "${GREEN}[+] .env обнаружен.${NC}"
fi

# 2. СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[i] Виртуальное окружение (venv) уже существует. Пропускаю создание.${NC}"
else
    echo -e "${GREEN}[*] Создаю python venv...${NC}"
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}[!] Ошибка при создании venv. Убедитесь, что python3-venv установлен.${NC}"
        exit 1
    fi
     echo -e "${GREEN}[+] venv создан успешно.${NC}"
fi

# 3. УСТАНОВКА ЗАВИСИМОСТЕЙ
if [ -f "$REQ_FILE" ]; then
    echo -e "${GREEN}[*] Устанавливаю зависимости из requirements.txt...${NC}"
    "$VENV_DIR/bin/pip" install -r "$REQ_FILE"
    if [ $? -ne 0 ]; then
        echo -e "${RED}[!] Ошибка при установке зависимостей.${NC}"
        exit 1
    fi
    echo -e "${GREEN}[+] Зависимости установлены.${NC}"
else
    echo -e "${RED}[!] requirements.txt не найден! Нечего устанавливать.${NC}"
    exit 1
fi

# 4. НАСТРОЙКА ПРАВ ДОСТУПА
echo -e "${GREEN}[*] Выдаю права на выполнение скриптам...${NC}"
chmod +x "$RUN_SCRIPT" 2>/dev/null
chmod +x "$PROJECT_DIR/isthereanydeal.py" 2>/dev/null # или как называется твой главный скрипт
echo -e "${GREEN}[+] Права выданы: chmod +x run.sh${NC}"

# 5. ДОБАВЛЕНИЕ В CRON (САМОЕ ИНТЕРЕСНОЕ)
CRON_CMD="0 10 * * * $RUN_SCRIPT"

# Проверяем, есть ли уже такая задача, чтобы не плодить дубли
(crontab -l 2>/dev/null | grep -F "$RUN_SCRIPT") >/dev/null

if [ $? -eq 0 ]; then
    echo -e "${YELLOW}[i] Задача уже есть в crontab. Пропускаю добавление.${NC}"
else
    echo -e "${GREEN}[*] Добавляю задачу в планировщик Cron (каждый день в 10:00)...${NC}"
    # Берем старый кронтаб, добавляем нашу строку и скармливаем обратно в кронтаб
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[+] Успешно добавлено в crontab.${NC}"
    else
        echo -e "${RED}[!] Не удалось обновить crontab.${NC}"
        exit 1
    fi
fi

echo -e "\n${GREEN}=== УСТАНОВКА ЗАВЕРШЕНА ===${NC}"
echo -e "${GREEN}[+] Программа настроена и будет запускаться автоматически.${NC}"
echo -e "${YELLOW}[i] Чтобы проверить работу прямо сейчас, запустите: $RUN_SCRIPT${NC}"
