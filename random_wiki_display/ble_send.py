import asyncio
import logging
import os
import textwrap  # Добавили для красивого разбиения текста
from bleak import BleakClient

# --- НАСТРОЙКИ ---
ADDRESS = "D8:A9:8B:7D:58:E5"
UART_RX_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
BLE_CHUNK_SIZE = 20  # Размер пакета Bluetooth (MTU)
LOGS_DIR = 'logs'

# Максимальная длина строки для Arduino (чтобы не переполнить буфер Serial)
# Рекомендую 60-80 символов. Если экран узкий, ставь под ширину экрана (например, 20 или 40)
ARDUINO_BUFFER_SAFE_LIMIT = 60 

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'bluetooth_sender.log')),
        logging.StreamHandler()
    ]
)

async def _send_line(client, line_text):
    """Отправляет одну логическую строку, разбивая её на BLE-пакеты."""
    logging.info(f"Отправка строки: '{line_text}'")
    
    # Добавляем перенос строки - сигнал для Arduino, что команда закончена
    data_to_send = (line_text + "\n").encode('utf-8')

    try:
        # Разбиваем на пакеты по 20 байт для протокола BLE
        for i in range(0, len(data_to_send), BLE_CHUNK_SIZE):
            chunk = data_to_send[i:i + BLE_CHUNK_SIZE]
            await client.write_gatt_char(UART_RX_CHAR_UUID, chunk, response=False)
            await asyncio.sleep(0.05) 
    except Exception as e:
        logging.error(f"Ошибка при отправке пакетов строки '{line_text}': {e}")
        raise

async def send_list_via_bluetooth(data_list: list):
    """
    Принимает список [Заголовок, Длинный_Текст].
    Разбивает Длинный_Текст на короткие строки и отправляет всё на устройство.
    """
    logging.info(f"Попытка подключения к устройству {ADDRESS}...")
    
    # --- ПОДГОТОВКА ДАННЫХ (Разбиваем длинный текст) ---
    lines_to_send = []
    
    if data_list:
        # 1. Заголовок добавляем как есть (предполагаем, что он короткий)
        lines_to_send.append(data_list[0])
        
        # 2. Если есть текст (второй элемент), разбиваем его
        if len(data_list) > 1 and data_list[1]:
            raw_text = data_list[1]
            # textwrap.wrap разбивает текст на список строк, не разрывая слова
            wrapped_lines = textwrap.wrap(raw_text, width=ARDUINO_BUFFER_SAFE_LIMIT)
            lines_to_send.extend(wrapped_lines)
    
    logging.info(f"Итоговый список для отправки (разбит на {len(lines_to_send)} строк): {lines_to_send}")

    try:
        async with BleakClient(ADDRESS) as client:
            if not client.is_connected:
                logging.error("Не удалось подключиться к устройству.")
                return
            
            logging.info("Устройство успешно подключено! Ожидание инициализации...")
            await asyncio.sleep(2.5) 
            
            # 1. Отправка команды очистки экрана
            logging.info("Отправка команды очистки экрана (CLS)...")
            await _send_line(client, "CLS")
            
            # Ждем отрисовку очистки
            await asyncio.sleep(8) # Можно чуть уменьшить, если 8 сек много

            # 2. Отправка подготовленных строк
            logging.info("Начало отправки контента...")
            
            for line in lines_to_send:
                line = line.strip()
                if not line:
                    continue
                
                await _send_line(client, line)
                
                # Задержка, чтобы Arduino успела прочитать буфер, 
                # вывести строку на экран/терминал и очистить память.
                # Для длинного текста лучше дать чуть больше времени.
                await asyncio.sleep(1.5) 
            
            logging.info("Всё успешно отправлено!")

    except Exception as e:
        logging.error(f"Произошла критическая ошибка: {e}")
    finally:
        logging.info("Работа программы завершена.")
