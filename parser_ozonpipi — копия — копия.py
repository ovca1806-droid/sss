import json
import random
import time
import curl_cffi

import time
from urllib.parse import urlparse, parse_qs
from uuid import uuid4

import re
import json
import html


def extract_next_page(page_html):
    # Находим HTML-блок с состоянием пагинатора
    match = re.search(
        r'<div id="state-infiniteVirtualPaginator-[^"]+"[^>]*data-state=\'(.*?)\'',
        page_html,
        re.DOTALL
    )

    if not match:
        print("[-] Блок infiniteVirtualPaginator не найден")
        return None

    state_text = html.unescape(match.group(1))

    try:
        state = json.loads(state_text)
    except json.JSONDecodeError as err:
        print(f"[-] Не удалось прочитать data-state как JSON: {err}")
        return None

    next_page = state.get("nextPage")

    if not next_page:
        print("[-] В пагинаторе нет nextPage")
        return None

    return next_page

API_URL = "https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2"

def load_next_page(session, next_page, category_url, page_view_id):

    query = parse_qs(urlparse(next_page).query)
    parent_id = query.get("start_page_id", [None])[0]

    if not parent_id:
        print("[-] Не найден start_page_id")
        return None

    headers = {
        "Accept": "application/json",
        "Referer": category_url,
        "x-o3-app-name": "dweb_client",
        "x-o3-parent-requestid": parent_id,
        "x-page-view-id": page_view_id,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    try:
        response = session.get(
            API_URL,
            params={"url": next_page},
            headers=headers,
            timeout=20
        )

        print(f"[API] Status: {response.status_code}")
        print("[API] Content-Type:", response.headers.get("Content-Type"))

        if response.status_code != 200:
            print("[-] Ответ API:", response.text[:500])
            return None

        data = response.json()

        print("[+] JSON успешно получен")
        print("[API] Ключи верхнего уровня:", list(data.keys()))

        # Временно сохраняем структуру ответа для диагностики
        with open("ozon_api_debug.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        print("[+] Ответ сохранён в ozon_api_debug.json")

        return data

    except Exception as err:
        print(f"[-] Ошибка запроса: {err}")
        return None

def load_four_blocks(session, initial_data, category_url):

    # Берём ссылку на следующую страницу из первоначального ответа
    next_page = initial_data.get("nextPage")

    # Идентификатор просмотра создаём один раз на категорию
    page_view_id = str(uuid4())

    if not next_page:
        print("[-] В первоначальном ответе отсутствует nextPage")
        return

    for page_num in range(1, 5):

        print(f"\n[*] Загружаем дополнительный блок {page_num}/4")

        time.sleep(2)

        data = load_next_page(
            session,
            next_page,
            category_url,
            page_view_id
        )

        if data is None:
            print("[-] Не удалось получить блок")
            break

        # Передаём полученный JSON твоему парсеру
        parse_ozon_products(data)

        # Получаем ссылку на следующую страницу
        next_page = data.get("nextPage")

        if not next_page:
            print("[!] Следующих страниц больше нет")
            break


SCROLL_DEPTH = 3

# Ссылки пишите в ОБЫЧНОМ ВИДЕ, прямо из адресной строки браузера:
CATEGORIES = [
    # --- ЭЛЕКТРОНИКА ---
    "https://www.ozon.ru/category/smartfony-15502/?sorting=new",
    #"https://www.ozon.ru/category/aksessuary-dlya-telefonov-15511/",
    #"https://www.ozon.ru/category/umnye-chasy-15516/",
    #"https://www.ozon.ru/category/fitnes-braslety-15519/"
]

# СЮДА ВСТАВЛЯЙТЕ ВАШИ ДАННЫЕ ИЗ БРАУЗЕРА (внутри кавычек):
USER_COOKIE = ""
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
# ================================================================

seen_products = set()


def parse_ozon_products(json_data: dict):
    for state_id, state_text in json_data.get("widgetStates", {}).items():

        # Нас интересуют блоки с товарной сеткой
        if not state_id.startswith("tileGridDesktop-"):
            continue

        try:
            state = json.loads(state_text)
        except json.JSONDecodeError:
            continue

        for item in state.get("items", []):
            product_id = str(item.get("id") or item.get("sku") or "")

            if not product_id or product_id in seen_products:
                continue

            seen_products.add(product_id)

            name = ""
            price = ""
            old_price = ""
            rating = ""
            reviews = ""

            # Название и цены находятся в mainState
            for block in item.get("mainState", []):
                block_type = block.get("type")
                block_data = block.get(block_type, {})

                if block_type == "textDS":
                    if block.get("id") == "name":
                        name = block_data.get("text", "")

                elif block_type == "priceV2":
                    for price_item in block_data.get("price", []):
                        text = price_item.get("text", "")
                        style = price_item.get("textStyle")

                        if style == "PRICE":
                            price = text
                        elif style == "ORIGINAL_PRICE":
                            old_price = text

                elif block_type == "labelListV2":
                    for label in block_data.get("items", []):
                        if label.get("type") != "text":
                            continue

                        text = label.get("text", {}).get("text", "")

                        if re.fullmatch(r"\d+[.,]\d+", text):
                            rating = text

                        elif re.search(r"отзыв", text, re.IGNORECASE):
                            reviews = text

            # Ссылка на товар
            product_url = item.get("action", {}).get("link", "")

            # Иногда ссылка находится в другом месте карточки
            if not product_url:
                product_url = ""

            if product_url and product_url.startswith("/"):
                product_url = "https://www.ozon.ru" + product_url

            # Первое изображение товара
            images = item.get("tileImage", {}).get("items", [])
            image_url = ""

            if images:
                image_url = images[0].get("image", {}).get("link", "")

            print("\n------------------------------")
            print("ID:", product_id)
            print("Название:", name)
            print("Цена:", price)
            print("Старая цена:", old_price)
            print("Рейтинг:", rating)
            print("Отзывы:", reviews)
            print("Ссылка:", product_url)
            print("Изображение:", image_url)


def debug_response(response):
    print("\n========== RESPONSE DEBUG ==========")
    print("Status:", response.status_code)
    print("URL:", response.url)
    print("Content-Type:", response.headers.get("Content-Type"))

    print("\nПервые 2000 символов ответа:")
    print(response.text[:2000])

    print("\nCookies после запроса:")
    for cookie in response.cookies.jar:
        print(cookie.name, "=", cookie.value)

    print("====================================\n")

def main():
    print("[*] Скрипт мониторинга Ozon «Топ-автор» запущен в безопасном режиме домашнего ПК...")

    # Работаем строго через requests.Session для поддержания CookieJar
    with curl_cffi.requests.Session() as session:
        # Важно: Загружаем стартовые куки методом обновления встроенного CookieJar сессии
        # Это позволяет curl_cffi перезаписывать их автоматически при ответе Set-Cookie
        session.cookies.update({
            k.strip(): v for cookie in USER_COOKIE.split(";") if "=" in cookie 
            for k, v in [cookie.strip().split("=", 1)]
        })

        session.headers.update({
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.9",
            "Referer": "https://ozon.ru/",
            "User-Agent": USER_AGENT,
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Ozon-App-Version": "web",
            "Platform": "web"
        })

        while True:
            current_round_categories = CATEGORIES.copy()
            random.shuffle(current_round_categories)

            print(f"\n[*] Начинаем новый круг проверок {len(current_round_categories)} категорий...")

            for cat_url in current_round_categories:
                params = {
                    "url": cat_url,
                    "layout_page_index": "1"
                }

                try:
                    response = session.get(cat_url, timeout=20)

                    print("\n========== PAGE DEBUG ==========")

                    print("Status:", response.status_code)
                    print("URL:", response.url)
                    print("Content-Type:", response.headers.get("Content-Type"))

                    print("\nПервые 1000 символов ответа:")
                    print(response.text[:1000])

                    print("================================\n")

                    html = response.text

                    for marker in ["nextPage", "paginator_token", "search_page_state", "widgetStates"]:
                        position = html.find(marker)

                        print(f"\nПоиск: {marker}")

                        if position == -1:
                            print("Не найдено")
                        else:
                            print("Найдено! Фрагмент:")
                            print(html[max(0, position - 200):position + 800])

                    #debug_response(response)

                    if response.status_code == 403:
                        print("[-] Ошибка 403. Доступ ограничен. Остужаем IP на 10 минут...")
                        time.sleep(600)
                        continue

                    if response.status_code != 200:
                        print(f"[-] Нестандартный ответ API: {response.status_code}")
                        continue

                    print("[+] Успешный ответ от сервера Ozon.")

                    next_page = extract_next_page(response.text)

                    if next_page:
                        page_view_id = str(uuid4())

                        data = load_next_page(
                            session,
                            next_page,
                            cat_url,
                            page_view_id
                        )

                        if data is not None:
                            print("[+] Первый дополнительный блок получен!")

                    #time.sleep(random.uniform(15, 30))

                    try:
                        json_data = response.json()

                        # Парсим первоначальные товары
                        parse_ozon_products(json_data)

                        # Загружаем ещё 4 блока
                        load_four_blocks(session, json_data, cat_url)
                    except json.JSONDecodeError:
                        print("[-] Ошибка декодирования JSON Ozon.")

                except Exception as err:
                    print(f"[-] Ошибка сети: {err}")

                time.sleep(random.uniform(15, 30))

            round_delay = random.uniform(60, 120)
            print(f"[*] Круг завершен. Сон перед новым кругом: {round_delay:.1f} сек.")
            time.sleep(round_delay)


if __name__ == "__main__":
    main()