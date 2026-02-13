import asyncio
import logging
import os
from bleak import BleakClient

# --- НАСТРОЙКИ ---
ADDRESS = "D8:A9:8B:7D:58:E5"
UART_RX_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
CHUNK_SIZE = 20
LOGS_DIR = 'logs'

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
    """Вспомогательная функция для отправки одной строки."""
    logging.info(f"Отправка строки: '{line_text}'")
    
    # Добавляем перенос строки
    data_to_send = (line_text + "\n").encode('utf-8')

    try:
        for i in range(0, len(data_to_send), CHUNK_SIZE):
            chunk = data_to_send[i:i + CHUNK_SIZE]
            await client.write_gatt_char(UART_RX_CHAR_UUID, chunk, response=False)
            await asyncio.sleep(0.05) # Чуть увеличил паузу между пакетами для надежности
    except Exception as e:
        logging.error(f"Ошибка при отправке строки '{line_text}': {e}")
        raise

async def send_list_via_bluetooth(today_games_list: list):
    """
    Основная функция модуля.
    """
    logging.info(f"Попытка подключения к устройству {ADDRESS}...")
    try:
        async with BleakClient(ADDRESS) as client:
            if not client.is_connected:
                logging.error("Не удалось подключиться к устройству.")
                return
            
            logging.info("Устройство успешно подключено! Ожидание инициализации...")
            
            # !!! ВАЖНОЕ ИЗМЕНЕНИЕ !!!
            # Ждем 2.5 секунды после подключения, чтобы Arduino была готова слушать
            await asyncio.sleep(2.5) 
            
            # 1. Отправка команды очистки экрана
            logging.info("Отправка команды очистки экрана (CLS)...")
            await _send_line(client, "CLS")
            
            # Ждем, пока экран реально очистится (черный прямоугольник)
            await asyncio.sleep(8.0) 

            # 2. Отправка списка
            logging.info("Начало отправки списка...")
            for line in today_games_list:
                line = line.strip()
                if not line:
                    continue
                
                await _send_line(client, line)
                # Пауза между строками, чтобы успеть прочитать/отрисовать
                await asyncio.sleep(3)
            
            logging.info("Список успешно отправлен!")

    except Exception as e:
        logging.error(f"Произошла критическая ошибка: {e}")
    finally:
        logging.info("Работа программы завершена.")
