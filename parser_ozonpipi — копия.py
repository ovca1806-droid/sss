
import json
import random
import re
import time
import html
from html.parser import HTMLParser
import winsound

import random
import time

import curl_cffi

from urllib.parse import urlparse, parse_qs
from uuid import uuid4
from pathlib import Path


# ============================================================
# НАСТРОЙКИ
# ============================================================

API_URL = "https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2"

CATEGORY_URL = "https://www.ozon.ru/search/?text=Unihertz+%D0%A1%D0%BC%D0%B0%D1%80%D1%82%D1%84%D0%BE%D0%BD+12%2F256+%D0%93%D0%91%2C+Mini-SIM%2C+%D1%87%D0%B5%D1%80%D0%BD%D1%8B%D0%B9+%D0%BC%D0%B0%D1%82%D0%BE%D0%B2%D1%8B%D0%B9++%D0%A1+14+%D0%BD%D0%BE%D1%8F%D0%B1%D1%80%D1%8F&from_global=true"

category_urls = [
    "https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=new",
    "https://www.ozon.ru/category/kompyutery-i-komplektuyushchie-15690/?sorting=new",
    "https://www.ozon.ru/category/umnyy-dom-15849/?sorting=new",
    "https://www.ozon.ru/category/noutbuki-planshety-i-elektronnye-knigi-8730/?sorting=new",
    "https://www.ozon.ru/category/foto-i-videokamery-15623/?sorting=new",
    "https://www.ozon.ru/category/televizory-i-videotehnika-15527/?sorting=new",
    "https://www.ozon.ru/category/igrovye-pristavki-i-kompyutery-15800/?sorting=new",
    "https://www.ozon.ru/category/umnyy-dom-i-bezopasnost-15835/?sorting=new",
    "https://www.ozon.ru/category/ofisnaya-tehnika-15770/?sorting=new",
    "https://www.ozon.ru/category/audiotehnika-15543/?sorting=new",
    "https://www.ozon.ru/category/aksessuary-dlya-elektroniki-15879/?sorting=new",
    "https://www.ozon.ru/category/kompyuternye-komplektuyushchie-15709/?sorting=new",
    "https://www.ozon.ru/category/navigatory-15685/?sorting=new",
    "https://www.ozon.ru/category/zhenskaya-odezhda-7501/?sorting=new",
    "https://www.ozon.ru/category/sredstva-dlya-uhoda-za-odezhdoy-7757/?sorting=new",
    "https://www.ozon.ru/category/spetsodezhda-i-sredstva-individualnoy-zashchity-10189/?sorting=new",
    "https://www.ozon.ru/category/muzhskaya-odezhda-7542/?sorting=new",
    "https://www.ozon.ru/category/zhenskaya-obuv-7640/?sorting=new",
    "https://www.ozon.ru/category/muzhskaya-obuv-7658/?sorting=new",
    "https://www.ozon.ru/category/sredstva-dlya-uhoda-za-obuvyu-7763/?sorting=new",
    "https://www.ozon.ru/category/posuda-i-kuhonnye-prinadlezhnosti-14501/?sorting=new",
    "https://www.ozon.ru/category/tsvety-i-rasteniya-14884/?sorting=new",
    "https://www.ozon.ru/category/suveniry-15061/?sorting=new",
    "https://www.ozon.ru/category/tekstil-15078/?sorting=new",
    "https://www.ozon.ru/category/hozyaystvennye-tovary-14593/?sorting=new",
    "https://www.ozon.ru/category/tovary-dlya-prazdnikov-14793/?sorting=new",
    "https://www.ozon.ru/category/osveshchenie-15096/?sorting=new",
    "https://www.ozon.ru/category/hranenie-veshchey-14759/?sorting=new",
    "https://www.ozon.ru/category/dekor-i-interer-15044/?sorting=new",
    "https://www.ozon.ru/category/aksessuary-dlya-vannoy-14594/?sorting=new",
    "https://www.ozon.ru/category/tovary-dlya-dachi-14633/?sorting=new",
    "https://www.ozon.ru/category/tovary-dlya-bani-i-sauny-14860/?sorting=new",
    "https://www.ozon.ru/category/tovary-dlya-shkoly-7182/?sorting=new",
    "https://www.ozon.ru/category/igrushki-i-igry-7108/?sorting=new",
    "https://www.ozon.ru/category/uhod-za-volosami-6584/?sorting=new",
    "https://www.ozon.ru/category/nogti-6526/?sorting=new",
    "https://www.ozon.ru/category/detskaya-kosmetika-35584/?sorting=new",
    "https://www.ozon.ru/category/uhod-za-litsom-6559/?sorting=new",
    "https://www.ozon.ru/category/parfyumeriya-6662/?sorting=new",
    "https://www.ozon.ru/category/apparatnaya-kosmetologiya-6325/?sorting=new",
    "https://www.ozon.ru/category/darsonvali-6329/?sorting=new",
    "https://www.ozon.ru/category/uhod-za-telom-6637/?sorting=new",
    "https://www.ozon.ru/category/zagar-i-zashchita-ot-solntsa-6651/?sorting=new",
    "https://www.ozon.ru/category/makiyazh-6501/?sorting=new",
    "https://www.ozon.ru/category/muzhskaya-kosmetika-35504/?sorting=new",
    "https://www.ozon.ru/category/krupnaya-bytovaya-tehnika-10501/?sorting=new",
    "https://www.ozon.ru/category/tehnika-dlya-doma-10647/?sorting=new",
    "https://www.ozon.ru/category/tehnika-dlya-krasoty-i-zdorovya-10737/?sorting=new",
    "https://www.ozon.ru/category/tehnika-dlya-kuhni-10523/?sorting=new",
    "https://www.ozon.ru/category/klimaticheskaya-tehnika-10711/?sorting=new",
    "https://www.ozon.ru/category/tehnika-dlya-obshchepita-35374/?sorting=new",
    "https://www.ozon.ru/category/sportivnoe-pitanie-11650/?sorting=new",
    "https://www.ozon.ru/category/skeytbording-11075/?sorting=new",
    "https://www.ozon.ru/category/trenazhery-i-fitnes-11638/?sorting=new",
    "https://www.ozon.ru/category/velosipedy-ekipirovka-i-zapchasti-11001/?sorting=new",
    "https://www.ozon.ru/category/beg-11847/?sorting=new",
    "https://www.ozon.ru/category/vodnyy-sport-i-otdyh-na-vode-34408/?sorting=new",
    "https://www.ozon.ru/category/fitnes-i-yoga-38647/?sorting=new",
    "https://www.ozon.ru/category/instrumenty-dlya-remonta-i-stroitelstva-9856/?sorting=new",
    "https://www.ozon.ru/category/otdelochnye-materialy-9721/?sorting=new",
    "https://www.ozon.ru/category/otoplenie-10198/?sorting=new",
    "https://www.ozon.ru/category/rashodnye-materialy-i-osnastka-dlya-instrumentov-10110/?sorting=new",
    "https://www.ozon.ru/category/stroitelnye-i-otdelochnye-materialy-9701/?sorting=new",
    "https://www.ozon.ru/category/santehnika-i-vodosnabzhenie-10255/?sorting=new",
    "https://www.ozon.ru/category/sredstva-individualnoy-zashchity-33126/?sorting=new",
    "https://www.ozon.ru/category/vodosnabzhenie-31846/?sorting=new",
    "https://www.ozon.ru/category/silovaya-tehnika-i-oborudovanie-31810/?sorting=new",
    "https://www.ozon.ru/category/kraski-laki-i-rastvoriteli-9804/?sorting=new",
    "https://www.ozon.ru/category/chay-kofe-kakao-9370/?sorting=new",
    "https://www.ozon.ru/category/masla-sousy-spetsii-30701/?sorting=new",
    "https://www.ozon.ru/category/konditerskie-izdeliya-9378/?sorting=new",
    "https://www.ozon.ru/category/makarony-krupy-muka-30699/?sorting=new",
    "https://www.ozon.ru/category/konservatsiya-9413/?sorting=new",
    "https://www.ozon.ru/category/sneki-suhariki-chipsy-9355/?sorting=new",
    "https://www.ozon.ru/category/dlya-koshek-12347/?sorting=new",
    "https://www.ozon.ru/category/veterinarnaya-apteka-12387/?sorting=new",
    "https://www.ozon.ru/category/turizm-i-otdyh-na-prirode-11424/?sorting=new",
    "https://www.ozon.ru/category/rybalka-33152/?sorting=new",
    "https://www.ozon.ru/category/avtozvuk-8733/?sorting=new",
    "https://www.ozon.ru/category/masla-i-avtohimiya-8514/?sorting=new",
    "https://www.ozon.ru/category/avtoaksessuary-i-oborudovanie-8608/?sorting=new",
    "https://www.ozon.ru/category/uhod-za-avtomobilem-8523/?sorting=new",
    "http://ozon.ru/category/elektronika-dlya-avto-8751/?sorting=new",
    "https://www.ozon.ru/category/avtomobilnye-instrumenty-8576/?sorting=new",
    "https://www.ozon.ru/category/shkafy-komody-polki-15036/?sorting=new",
    "https://www.ozon.ru/category/mebel-dlya-spalni-15009/?sorting=new",
    "https://www.ozon.ru/category/kompyuternaya-i-ofisnaya-mebel-38449/?sorting=new",
    "https://www.ozon.ru/category/mebel-dlya-kuhni-15008/?sorting=new",
    "https://www.ozon.ru/category/stoly-stulya-i-kresla-15027/?sorting=new",
    "https://www.ozon.ru/category/rukodelie-13586/?sorting=new",
    "https://www.ozon.ru/category/risovanie-13528/?sorting=new",
    "https://www.ozon.ru/category/modelirovanie-13738/?sorting=new",
    "https://www.ozon.ru/category/nastolnye-i-kartochnye-igry-13506/?sorting=new",
    "https://www.ozon.ru/category/raskrashivanie-i-rospis-13524/?sorting=new",
    "https://www.ozon.ru/category/sozdanie-kartin-fotoramok-otkrytok-13567/?sorting=new",
    "https://www.ozon.ru/category/muzykalnye-instrumenty-13917/?sorting=new",
    "https://www.ozon.ru/category/koltsa-yuvelirnye-50002/?sorting=new",
    "https://www.ozon.ru/category/braslety-yuvelirnye-50011/?sorting=new",
    "https://www.ozon.ru/category/sergi-yuvelirnye-50003/?sorting=new",
    "https://www.ozon.ru/category/zhenskie-aksessuary-17000/?sorting=new",
    "https://www.ozon.ru/category/muzhskie-aksessuary-17063/?sorting=new",
    "https://www.ozon.ru/category/puteshestviya-8511/?sorting=new",
    "https://www.ozon.ru/category/playstation-31719/?sorting=new",
    "https://www.ozon.ru/category/pc-31718/?sorting=new",
    "https://www.ozon.ru/category/igrovaya-atributika-1672/?sorting=new",
    "https://www.ozon.ru/category/igrovye-naushniki-15827/?sorting=new",
    "https://www.ozon.ru/category/geympady-15823/?sorting=new",
    "https://www.ozon.ru/category/aksessuary-dlya-igrovyh-pristavok-15810/?delivery=4&sorting=new",
    "https://www.ozon.ru/category/pismennye-prinadlezhnosti-18015/?sorting=new",
    "https://www.ozon.ru/category/demonstratsionnye-doski-18095/?sorting=new",
    "https://www.ozon.ru/category/kartridzhi-dlya-lazernyh-printerov-31686/?sorting=new",
    "https://www.ozon.ru/category/ofisnye-prinadlezhnosti-30107/?sorting=new",
    "https://www.ozon.ru/category/bytovaya-himiya-36861/?sorting=new",
    "https://www.ozon.ru/category/lichnaya-gigiena-6310/?sorting=new",
]

USER_COOKIE = ""
COOKIE_FILE = Path(__file__).with_name("ozon_cookies.txt")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"

BLOCKS_TO_LOAD = 4

seen_products = set()

def load_cookies():
    if not COOKIE_FILE.exists():
        raise FileNotFoundError(
            f"Не найден файл с cookies: {COOKIE_FILE}"
        )

    cookie_text = COOKIE_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if not cookie_text:
        raise ValueError("Файл ozon_cookies.txt пуст")

    cookies = {}

    for cookie in cookie_text.split(";"):
        if "=" not in cookie:
            continue

        name, value = cookie.strip().split("=", 1)
        cookies[name] = value

    if not cookies:
        raise ValueError("Не удалось прочитать cookies")

    return cookies

def check_login_status(page_html):
    login_button = re.search(
        r'<button\b[^>]*>.*?Войти.*?</button>',
        page_html,
        re.IGNORECASE | re.DOTALL
    )

    return login_button is None

# ============================================================
# ИЗВЛЕЧЕНИЕ NEXT PAGE ИЗ HTML
# ============================================================

def extract_next_page(page_html):
    match = re.search(
        r'<div id="state-infiniteVirtualPaginator-[^"]+"[^>]*data-state=\'(.*?)\'',
        page_html,
        re.DOTALL
    )

    if not match:
        print("[-] Пагинатор не найден")
        return None

    state_text = html.unescape(match.group(1))

    try:
        state = json.loads(state_text)
    except json.JSONDecodeError as err:
        print(f"[-] Ошибка чтения пагинатора: {err}")
        return None

    return state.get("nextPage")

def extract_initial_products(page_html):
    match = re.search(
        r'<div id="state-tileGridDesktop-[^"]+"[^>]*data-state=\'(.*?)\'',
        page_html,
        re.DOTALL
    )

    if not match:
        print("[-] Начальный блок товаров в HTML не найден")
        return None

    state_text = html.unescape(match.group(1))

    try:
        state = json.loads(state_text)
    except json.JSONDecodeError as err:
        print(f"[-] Ошибка чтения начального блока: {err}")
        return None

    print(
        f"[+] Начальный блок найден: "
        f"{len(state.get('items', []))} карточек"
    )

    return {
        "widgetStates": {
            "initial-tileGridDesktop": json.dumps(
                state,
                ensure_ascii=False
            )
        }
    }

# ============================================================
# ЗАГРУЗКА ОДНОГО ДОПОЛНИТЕЛЬНОГО БЛОКА ЧЕРЕЗ API
# ============================================================

def load_next_page(session, next_page, category_url, page_view_id):

    query = parse_qs(urlparse(next_page).query)
    parent_id = query.get("start_page_id", [None])[0]

    if not parent_id:
        print("[-] В nextPage отсутствует start_page_id")
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

        if response.status_code == 403:
            print("[-] API вернул 403. Пауза 10 минут.")
            time.sleep(600)
            return None

        if response.status_code != 200:
            print(f"[-] API вернул статус {response.status_code}")
            return None

        data = response.json()

        if not isinstance(data, dict):
            print("[-] API вернул неожиданный формат данных")
            return None

        return data

    except (json.JSONDecodeError, ValueError) as err:
        print(f"[-] Не удалось прочитать JSON API: {err}")
        return None

    except Exception as err:
        print(f"[-] Ошибка запроса API: {err}")
        return None


def find_review_badge(item):
    badge = (
        item.get("tileImage", {})
            .get("leftBottomBadgeV2", {})
    )

    automatization_id = (
        badge.get("common", {})
             .get("testInfo", {})
             .get("automatizationId")
    )

    if automatization_id == "badge-topAuthor":
        return badge.get("text", "Плашка «Топ-автор»")

    return None

# ============================================================
# ПАРСИНГ ТОВАРОВ
# ============================================================

def parse_ozon_products(json_data):

    widget_states = json_data.get("widgetStates", {})

    for state_id, state_text in widget_states.items():

        if not (
                state_id.startswith("tileGridDesktop-")
                or state_id == "initial-tileGridDesktop"
        ):
            continue

        try:
            state = json.loads(state_text)
        except (json.JSONDecodeError, TypeError):
            continue

        for item in state.get("items", []):

            product_id = str(item.get("id") or item.get("sku") or "")

            if not product_id or product_id in seen_products:
                continue

            seen_products.add(product_id)

            badge = find_review_badge(item)

            if not badge:
                continue

            name = ""
            price = ""
            old_price = ""
            rating = ""
            reviews = ""

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

            product_url = item.get("action", {}).get("link", "")

            if product_url.startswith("/"):
                product_url = "https://www.ozon.ru" + product_url

            images = item.get("tileImage", {}).get("items", [])
            image_url = ""

            if images:
                image_url = images[0].get("image", {}).get("link", "")

            print("\n" + "=" * 45)
            print("[+] НАЙДЕН ТОВАР С ПЛАШКОЙ ЗА ОБЗОР!")
            print("Плашка:", badge)
            print("ID:", product_id)
            print("Название:", name)
            print("Цена:", price)
            print("Старая цена:", old_price)
            print("Рейтинг:", rating)
            print("Отзывы:", reviews)
            print("Ссылка:", product_url)
            print("Изображение:", image_url)
            print("=" * 45)

            winsound.Beep(1300, 100)


# ============================================================
# ЗАГРУЗКА ЧЕТЫРЁХ ДОПОЛНИТЕЛЬНЫХ БЛОКОВ
# ============================================================

def load_additional_blocks(session, next_page, category_url):

    page_view_id = str(uuid4())

    if not next_page:
        print("[-] Не удалось получить первую ссылку nextPage")
        return

    for block_num in range(1, BLOCKS_TO_LOAD + 1):

        print(f"\n[*] Получаем дополнительный блок {block_num}/{BLOCKS_TO_LOAD}")

        data = load_next_page(
            session,
            next_page,
            category_url,
            page_view_id
        )

        if data is None:
            print("[-] Загрузка блока прервана")
            break

        parse_ozon_products(data)

        next_page = data.get("nextPage")

        if not next_page:
            print("[*] Следующих блоков больше нет")
            break

        if block_num < BLOCKS_TO_LOAD:
            time.sleep(random.uniform(1, 2))


# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================

def main():

    print("[*] Мониторинг Ozon запущен")

    with curl_cffi.requests.Session() as session:

        session.cookies.update(load_cookies())

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

            random.shuffle(category_urls)
            print("\nНовый круг проверки категорий")

            for index, category_url in enumerate(category_urls):
                print(f"\nПроверяем категорию: {category_url}")

                try:
                    response = session.get(
                        CATEGORY_URL,
                        timeout=20
                    )

                    if response.status_code == 403:
                        print("[-] Ozon вернул 403. Пауза 10 минут.")
                        time.sleep(600)
                        continue

                    if response.status_code != 200:
                        print(f"[-] Ошибка страницы: {response.status_code}")
                        time.sleep(30)
                        continue

                    print("[+] HTML страницы получен")

                    if not check_login_status(page_html):
                        print("⚠️ Вы не авторизованы в Ozon! Проверьте ozon_cookies.txt.")
                        time.sleep(120)
                        return 0

                    # Сначала парсим первоначальные товары из HTML
                    initial_data = extract_initial_products(response.text)

                    if initial_data:
                        parse_ozon_products(initial_data)

                    next_page = extract_next_page(response.text)

                    if not next_page:
                        print("[-] Не удалось извлечь nextPage")
                        time.sleep(60)
                        continue

                    print("[+] nextPage извлечён")

                    load_additional_blocks(
                        session,
                        next_page,
                        CATEGORY_URL
                    )

                except Exception as err:
                    print(f"[-] Ошибка основного цикла: {err}")

                finally:
                    # Пауза между категориями, но не после последней
                    if index < len(category_urls) - 1:
                        delay = random.uniform(1, 2)
                        print(f"Пауза перед следующей категорией: {delay:.1f} сек.")
                        time.sleep(delay)

            round_delay = random.uniform(2, 5)

            print(f"\nВсе категории проверены. Следующий круг через {delay:.1f} сек.")

            time.sleep(round_delay)


if __name__ == "__main__":
    main()
