
import json
import html
from pathlib import Path

from curl_cffi import requests
from curl_cffi import CurlMime

import tempfile
import os
import hmac


BASE_DIR = Path(__file__).parent
TOKEN_FILE = BASE_DIR / "tg_token.txt"
USERS_FILE = BASE_DIR / "telegram_users.json"

PASSWORD_FILE = BASE_DIR / "tg_pass.txt"


class TelegramBot:

    def __init__(self):
        if not TOKEN_FILE.exists():
            raise FileNotFoundError(
                f"Не найден файл токена: {TOKEN_FILE}"
            )

        self.token = TOKEN_FILE.read_text(
            encoding="utf-8"
        ).strip()

        if not self.token:
            raise ValueError("Файл telegram_token.txt пуст")

        if not PASSWORD_FILE.exists():
            raise FileNotFoundError(
                f"Не найден файл пароля: {PASSWORD_FILE}"
            )

        self.password = PASSWORD_FILE.read_text(
            encoding="utf-8"
        ).strip()

        if not self.password:
            raise ValueError("Файл telegram_password.txt пуст")

        self.api_url = (
            f"https://api.telegram.org/bot{self.token}"
        )

        # Отдельная сессия для Telegram.
        # Ozon cookies сюда не передаются.
        self.session = requests.Session()

        self.state = {
            "users": [],
            "offset": 0
        }

        self.load_users()

    def load_users(self):
        if USERS_FILE.exists():
            try:
                self.state = json.loads(
                    USERS_FILE.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                print("[Telegram] Не удалось прочитать список пользователей")

        self.state.setdefault("users", [])
        self.state.setdefault("offset", 0)

    def save_users(self):
        USERS_FILE.write_text(
            json.dumps(
                self.state,
                ensure_ascii=False,
                indent=4
            ),
            encoding="utf-8"
        )

    def api_request(self, method, params=None):
        try:
            response = self.session.post(
                f"{self.api_url}/{method}",
                data=params or {},
                timeout=20
            )

            result = response.json()

            if not result.get("ok"):
                print(
                    f"[Telegram] Ошибка {method}: "
                    f"{result.get('description')}"
                )

            return result

        except Exception as err:
            print(f"[Telegram] Ошибка соединения: {err}")
            return None

    def check_updates(self):
        result = self.api_request(
            "getUpdates",
            {
                "offset": self.state["offset"],
                "timeout": 0,
                "allowed_updates": json.dumps(["message"])
            }
        )

        if not result or not result.get("ok"):
            return

        for update in result.get("result", []):

            self.state["offset"] = update["update_id"] + 1

            message = update.get("message", {})
            chat = message.get("chat", {})

            # Работаем только с личными чатами
            if chat.get("type") != "private":
                continue

            chat_id = chat.get("id")
            text = message.get("text", "").strip()

            if not chat_id or not text:
                continue

            command = text.split()[0].split("@")[0].lower()


            if command == "/start":

                if chat_id in self.state["users"]:
                    answer = "Ты уже авторизован и получаешь уведомления."
                else:
                    answer = (
                        "Привет! Для получения уведомлений "
                        "введи пароль доступа к боту."
                    )

                self.api_request(
                    "sendMessage",
                    {
                        "chat_id": chat_id,
                        "text": answer
                    }
                )

            elif command == "/stop":

                if chat_id in self.state["users"]:
                    self.state["users"].remove(chat_id)
                    self.save_users()

                self.api_request(
                    "sendMessage",
                    {
                        "chat_id": chat_id,
                        "text": "Уведомления отключены. Для повторного доступа введи /start."
                    }
                )

            elif chat_id not in self.state["users"]:

                if hmac.compare_digest(text, self.password):

                    self.state["users"].append(chat_id)
                    self.save_users()

                    print(
                        f"[Telegram] Пользователь {chat_id} "
                        "успешно авторизован"
                    )

                    self.api_request(
                        "sendMessage",
                        {
                            "chat_id": chat_id,
                            "text": (
                                "✅ Пароль принят!\n\n"
                                "Ты добавлен в белый список "
                                "и теперь будешь получать уведомления "
                                "о новых товарах."
                            )
                        }
                    )

                else:
                    self.api_request(
                        "sendMessage",
                        {
                            "chat_id": chat_id,
                            "text": (
                                "❌ Неверный пароль. "
                                "Попробуй ещё раз."
                            )
                        }
                    )

            self.save_users()

        self.save_users()

    def send_product(
            self,
            product_id,
            name,
            price,
            badge,
            product_url,
            image_url,
            ozon_session=None
    ):
        if not self.state["users"]:
            print("[Telegram] Нет пользователей для рассылки")
            return

        caption = (
            f"🏷 Плашка: {badge}\n"
            f"📦 Название: {name}\n"
            f"🆔 Артикул: {product_id}\n"
            f"💰 Цена: {price or 'Не указана'}\n\n"
            f"🔗 {product_url}"
        )

        image_path = None

        # Скачиваем изображение через сессию Ozon
        if image_url and ozon_session:
            try:
                image_response = ozon_session.get(
                    image_url,
                    timeout=20
                )

                image_response.raise_for_status()

                with tempfile.NamedTemporaryFile(
                        suffix=".jpg",
                        delete=False
                ) as temp_file:
                    temp_file.write(image_response.content)
                    image_path = temp_file.name

            except Exception as err:
                print(
                    f"[Telegram] Ошибка загрузки изображения: {err}"
                )

        try:
            for chat_id in self.state["users"]:

                if image_path:
                    try:
                        with open(image_path, "rb") as photo:
                            multipart = CurlMime()

                            try:
                                multipart.addpart(
                                    name="photo",
                                    content_type="image/jpeg",
                                    filename="photo.jpg",
                                    data=photo.read()
                                )

                                response = self.session.post(
                                    f"{self.api_url}/sendPhoto",
                                    data={
                                        "chat_id": chat_id,
                                        "caption": caption
                                    },
                                    multipart=multipart,
                                    timeout=30
                                )

                            finally:
                                multipart.close()

                        result = response.json()

                        if result.get("ok"):
                            print(
                                f"[Telegram] Товар {product_id} "
                                f"отправлен с фотографией"
                            )
                            continue

                        print(
                            f"[Telegram] Ошибка sendPhoto: "
                            f"{result.get('description')}"
                        )

                    except Exception as err:
                        print(f"[Telegram] Ошибка отправки фото: {err}")

                # Если фотографию отправить не удалось
                self.api_request(
                    "sendMessage",
                    {
                        "chat_id": chat_id,
                        "text": caption
                    }
                )

        finally:
            # Удаляем временную фотографию
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

    def send_login_required(self, category_url=None):
        message = (
            "⚠️ **Потеряна авторизация на Ozon!**\n\n"
            "Парсер обнаружил кнопку «Войти» на странице.\n"
            "Необходимо обновить cookies в файле "
            "ozon_cookies.txt и перезапустить парсер."
        )

        if category_url:
            message += f"\n\nПроверяемая категория:\n{category_url}"

        for chat_id in self.state["users"]:
            self.api_request(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )

        print("[Telegram] Отправлено уведомление о потере авторизации")

    def close(self):
        self.session.close()
