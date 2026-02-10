import requests
from bs4 import BeautifulSoup

def get_random_wiki_fact(max_chars=180):
    url = "https://ru.wikipedia.org/wiki/Служебная:Случайная_страница"
    
    # Википедия требует User-Agent, иначе вернет 403 Forbidden
    headers = {
        'User-Agent': 'ALYX_Agent/1.0 (educational project; python-requests)'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Проверка на ошибки сети
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Получаем заголовок (h1)
        title_tag = soup.find(id="firstHeading")
        title = title_tag.text.strip() if title_tag else "Без названия"
        
        # 2. Ищем первый нормальный абзац текста
        # Ищем внутри основного контента
        content_div = soup.find('div', id='mw-content-text')
        excerpt = ""
        
        if content_div:
            # Парсим параграфы
            paragraphs = content_div.select('.mw-parser-output > p')
            for p in paragraphs:
                text = p.text.strip()
                # Пропускаем пустые абзацы или координаты
                if text and len(text) > 20: 
                    excerpt = text
                    break
        
        # 3. Формируем итоговый текст и обрезаем
        # Сначала собираем полную строку
        full_text = f"{title}\n{excerpt}"
        
        # Если вышли за лимит, обрезаем и ставим многоточие
        if len(full_text) > max_chars:
            # Оставляем место под троеточие (3 символа)
            full_text = full_text[:max_chars-3] + "..."
            
        # 4. Считаем остаток
        remaining_chars = max_chars - len(full_text)
        
        # Возвращаем список: [Текст, Остаток символов]
        return [full_text, remaining_chars]

    except Exception as e:
        return [f"Ошибка получения данных: {e}", 0]

# --- Тест для ALYX ---
if __name__ == "__main__":
    result = get_random_wiki_fact()
    print(f"Результат (List): {result}")
    print("-" * 20)
    print(f"Вывод:\n{result[0]}")
    print(f"\nСвободного места: {result[1]}")
