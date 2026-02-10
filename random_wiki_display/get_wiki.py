import requests
from bs4 import BeautifulSoup
from ble_send import send_list_via_bluetooth
import asyncio

def clean_typography(text):
    """
    Заменяет сложные типографские символы на простые ASCII (или близкие к ним),
    которые переварит простой шрифт Arduino.
    """
    if not text:
        return ""
        
    replacements = {
        # Тире и дефисы
        '—': '-',    # Длинное тире (em dash)
        '–': '-',    # Среднее тире (en dash)
        '−': '-',    # Минус
        
        # Кавычки
        '«': '"',    # Елочки левые
        '»': '"',    # Елочки правые
        '“': '"',    # Лапки левые
        '”': '"',    # Лапки правые
        '‘': "'",    # Одинарная левая
        '’': "'",    # Одинарная правая
        
        # Пробелы и спецсимволы
        '\xa0': ' ', # Неразрывный пробел (часто встречается в Вики)
        '…': '...',  # Символ троеточия (один знак -> три знака)
        '\u0301': '', # Знак ударения (бывает над буквами)
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def get_random_wiki_fact(max_chars=220):
    url = "https://ru.wikipedia.org/wiki/Служебная:Случайная_страница"
    
    headers = {
        'User-Agent': 'ALYX_Agent/1.0 (educational project; python-requests)'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Получаем заголовок
        title_tag = soup.find(id="firstHeading")
        raw_title = title_tag.text.strip() if title_tag else "Без названия"
        
        # --- ЧИСТИМ ЗАГОЛОВОК СРАЗУ ---
        title = clean_typography(raw_title)
        
        # 2. Ищем текст
        content_div = soup.find('div', id='mw-content-text')
        excerpt = ""
        
        if content_div:
            paragraphs = content_div.select('.mw-parser-output > p')
            for p in paragraphs:
                raw_text = p.text.strip()
                # Сначала проверяем длину "грязного" текста, чтобы не обрабатывать мусор
                if raw_text and len(raw_text) > 20:
                    # --- ЧИСТИМ ТЕКСТ ---
                    clean_text = clean_typography(raw_text)
                    excerpt = clean_text
                    break
        
        # 3. Логика обрезки (теперь работаем только с очищенным текстом)
        
        # Если заголовок слишком длинный
        if len(title) >= max_chars:
            title = title[:max_chars-3] + "..."
            return [title, ""]

        remaining_space = max_chars - len(title) - 1
        
        final_text = ""
        
        if excerpt:
            if len(excerpt) > remaining_space:
                if remaining_space > 3:
                    final_text = excerpt[:remaining_space-3] + "..."
                else:
                    final_text = "" 
            else:
                final_text = excerpt

        return [title, final_text]

    except Exception as e:
        return ["Ошибка Вики", str(e)[:100]]

async def main():
    # Ставим лимит побольше, раз у нас теперь есть разбиение на чанки в ble_send
    result = get_random_wiki_fact(500) 
    
    print(f"Заголовок: {result[0]}")
    print(f"Текст: {result[1]}")
    print("-" * 20)
    
    if result:
        await send_list_via_bluetooth(result)
    else:
        print("Список пуст.")
    
if __name__ == "__main__":
    asyncio.run(main())
