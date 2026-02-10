#!/bin/bash

# 1. Магия: определяем директорию, в которой лежит этот скрипт
# Даже если скрипт запущен из крона или через симлинк, это вернет правильный путь к папке проекта.
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# 2. Переходим в директорию проекта (чтобы скрипт видел .env и json-файлы)
cd "$PROJECT_DIR"

# 3. Определяем путь к Python внутри venv
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
SCRIPT_FILE="isthereanydeal.py"  # Твой основной файл

# 4. Проверка: существует ли виртуальное окружение?
if [ ! -f "$VENV_PYTHON" ]; then
    echo "$(date) - ОШИБКА: Не найдено виртуальное окружение env ($VENV_PYTHON)" >> cron_errors.log
    exit 1
fi

# 5. Запуск Python скрипта
# Мы вызываем python из venv напрямую — это автоматически подтягивает все библиотеки.
# ">> cron.log 2>&1" перенаправляет и вывод, и ошибки в лог-файл в папке проекта.
"$VENV_PYTHON" "$SCRIPT_FILE" >> cron_output.log 2>&1

