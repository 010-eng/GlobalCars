import re
import html
import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN", "8784709823:AAHvkau9rkZdePQKscELM8swzaLeuxxbSbo")
MANAGER_ID = int(os.environ.get("MANAGER_ID", "-1004472275042"))  # ← ID вашей группы (отрицательное число) или личный Telegram ID
MANAGER_USERNAME = "Boris_GlobalAuto"

# Метка бота — если этот же код запущен несколько раз под разными токенами
# (разные боты), но заявки шлются в один и тот же чат менеджера, эта метка
# подставляется в каждое сообщение о заявке, чтобы было видно, с какого
# именно бота она пришла. Меняется через переменную окружения BOT_LABEL —
# менять код для этого не нужно, для каждого бота просто свой BOT_LABEL.
BOT_LABEL = os.environ.get("BOT_LABEL", "Global Auto")
CHANNEL_LINK = "https://t.me/asiabazarkr"
REVIEWS_LINK = "https://t.me/asiabazarotzivi"

BACK = '⬅️ Назад'
SKIP = '⏭ Пропустить'
CONTACT_VIA_TG_BTN = '📱 Связаться со мной в Telegram'

DELIVERY_COST = {
    '🇨🇳 Китай': 120000,
    '🇰🇷 Корея': 150000,
    '🇯🇵 Япония': 180000,
    '🇪🇺 Европа': 200000,
}
CUSTOMS_RATE = {
    '🚗 До 2.0 л (легковой)': 0.15,
    '🚙 2.0–3.0 л (легковой)': 0.20,
    '🚘 Внедорожник/кроссовер': 0.20,
    '🚐 Свыше 3.0 л': 0.30,
}
SERVICE_FEE = 80000
COUNTRIES = ['🇨🇳 Китай', '🇰🇷 Корея', '🇯🇵 Япония', '🇪🇺 Европа']
BUDGETS = [
    '💵 До 1 млн ₽',
    '💰 1–1.5 млн ₽',
    '📈 1.5–2 млн ₽',
    '💎 2–3 млн ₽',
    '👑 3–5 млн ₽',
    '🏆 От 5 млн ₽',
]
BODIES = ['🚗 Седан', '🚙 Внедорожник', '🚘 Кроссовер', '🚐 Минивэн']
CALC_BODIES = ['🚗 До 2.0 л (легковой)', '🚙 2.0–3.0 л (легковой)', '🚘 Внедорожник/кроссовер', '🚐 Свыше 3.0 л']
CITIES = ['Москва', 'Санкт-Петербург', 'Владивосток', 'Новосибирск', 'Екатеринбург', 'Казань', 'Краснодар']
CUSTOM_CITY_BTN = '✏️ Свой вариант'
WEBSITE_LINK = "https://globalcarpro.ru"

FAQ = {
    '🚚 Как происходит доставка автомобиля?': (
        'После покупки автомобиль отправляется морским или ж/д транспортом до ближайшего к Вам порта/терминала, '
        'проходит растаможку, а затем доставляется автовозом до Вашего города.\n\n'
        '⏱ Средние сроки: Китай — 2–3 недели, Корея — 3–4 недели, Япония — 4–6 недель.'
    ),
    '💰 Из чего складывается цена автомобиля?': (
        'Итоговая стоимость под ключ включает:\n'
        '🚗 Цену самого автомобиля\n'
        '🚢 Логистику до России\n'
        '📋 Таможенные платежи и сборы\n'
        '🔧 Наши услуги за подбор и сопровождение\n\n'
        'Точный расчёт можно получить в разделе «💰 Расчёт стоимости под ключ».'
    ),
    '📊 Нужно ли платить НДС? Можно ли вернуть НДС?': (
        'При пригоне автомобиля из Кореи через нашу компанию в ряде случаев возможна дополнительная '
        'экономия за счёт возврата НДС.\n\n'
        '⚠️ Точная сумма и условия рассчитываются индивидуально по каждому автомобилю — '
        'уточните расчёт у менеджера.'
    ),
    '💳 Можно ли купить автомобиль в рассрочку?': (
        'Да! Через нашу компанию можно оформить авто-кредит под минимальные проценты.\n\n'
        '🏦 Банки-партнёры: Т-Банк, Альфа-Банк, ВТБ, Газпромбанк, ПСБ, Сбербанк, ОТП Банк\n'
        '💵 Минимальный первоначальный взнос: <b>от 350 000 ₽</b>\n'
        '✅ Простое и быстрое оформление\n\n'
        'Точные условия по ставке и сроку зависят от банка и Вашей ситуации — уточните у менеджера.'
    ),
    '🛡 Страхуется ли автомобиль во время доставки?': (
        'Да, при транспортировке автомобиль может быть застрахован от повреждений в пути — это дополнительная опция, '
        'которую можно подключить при оформлении. Уточните детали у менеджера.'
    ),
    '🔧 Трудно ли найти запчасти на пригнанный авто?': (
        'На популярные модели (Toyota, Kia, Hyundai, Haval, Geely и др.) запчасти в России найти несложно — '
        'по ним развита сеть поставщиков и аналогов. По редким моделям поможем сориентироваться перед покупкой.'
    ),
    '📄 Есть ли гарантия, что авто соответствует описанию?': (
        'Мы проверяем техническое состояние и историю автомобиля перед покупкой (пробег, ДТП, юридическая чистота) '
        'и предоставляем Вам эту информацию до принятия решения — чтобы Вы точно знали, что покупаете.'
    ),
}

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

import csv
import json
import requests
import threading
from datetime import datetime

# Папка для файлов, которые бот сам создаёт и меняет во время работы
# (список пользователей для рассылки, CSV-лог кликов).
#
# ВАЖНО: на хостингах вроде Railway/Heroku/Render диск контейнера эфемерный —
# при каждом редеплое файловая система пересобирается заново из git, и все
# файлы, созданные ботом во время работы (не из репозитория), стираются.
# Чтобы users.json и clicks_log.csv переживали редеплой, подключите постоянный
# диск (например, Railway Volume) и укажите его путь в переменной окружения
# DATA_DIR (например, DATA_DIR=/data). Если переменная не задана — файлы, как
# и раньше, будут лежать рядом со скриптом (и стираться при редеплое).
DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(DATA_DIR, exist_ok=True)

# Локальный CSV-лог кликов пользователей.
LOG_FILE = os.path.join(DATA_DIR, "clicks_log.csv")

# URL вашего собственного Google Apps Script (см. инструкцию по настройке).
GOOGLE_SCRIPT_URL = os.environ.get(
    "GOOGLE_SCRIPT_URL",
    "https://script.google.com/macros/s/AKfycbwVSlp-vTX6_LpYrR8fGrP8FllhE1qWV6oZYldSNsQZhadKbE7ogYw-COKIMY4zaWk/exec"
)

# Файл со списком всех, кто хоть раз писал боту — нужен для рассылки (/broadcast).
USERS_FILE = os.path.join(DATA_DIR, "users.json")
_users_lock = threading.Lock()


def save_user_id(user_id):
    """Сохраняет Telegram ID пользователя в локальный файл, чтобы потом можно было
    сделать рассылку командой /broadcast. Дубликаты не добавляются."""
    with _users_lock:
        users = set()
        if os.path.isfile(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    users = set(json.load(f))
            except Exception:
                users = set()
        if user_id not in users:
            users.add(user_id)
            try:
                with open(USERS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(list(users), f)
            except Exception as e:
                print(f"Не удалось сохранить список пользователей: {e}")


def load_user_ids():
    """Возвращает список всех сохранённых Telegram ID."""
    if os.path.isfile(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _post_to_sheet(payload, error_prefix):
    """Реальная отправка запроса — выполняется в отдельном потоке,
    чтобы не задерживать ответ бота пользователю."""
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"{error_prefix}: {e}")


def log_step(m, scenario, step, is_new_session=False):
    """Отправляет в лист 'Аналитика' отметку о том, что пользователь дошёл до этого шага,
    а также то, что он ввёл/выбрал непосредственно перед этим (m.text).
    is_new_session=True ставится на первом шаге сценария (новый заход в анкету).
    Не блокирует бота — запрос уходит в фоновом потоке."""
    payload = {
        "type": "step",
        "bot_label": BOT_LABEL,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": m.from_user.first_name or "",
        "username": m.from_user.username or "",
        "telegram_id": m.from_user.id,
        "scenario": scenario,
        "step": step,
        "is_new_session": is_new_session,
        "user_input": (m.text or "")[:200],
    }
    threading.Thread(target=_post_to_sheet, args=(payload, "Не удалось отправить шаг в таблицу"), daemon=True).start()


def send_lead(m, lead_type, data):
    """Отправляет в лист 'Заявки' полностью заполненную заявку.
    Не блокирует бота — запрос уходит в фоновом потоке."""
    mark_lead_submitted(m.chat.id)
    payload = {
        "type": "lead",
        "bot_label": BOT_LABEL,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lead_type": lead_type,
        "name": data.get('name', ''),
        "phone": data.get('phone', ''),
        "country": data.get('country', ''),
        "budget": data.get('budget', ''),
        "body": data.get('body', ''),
        "brand": data.get('brand', ''),
        "city": data.get('city', ''),
        "telegram_id": m.from_user.id,
        "username": m.from_user.username or "",
    }
    threading.Thread(target=_post_to_sheet, args=(payload, "Не удалось отправить заявку в таблицу"), daemon=True).start()

def log_click(m):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Дата и время", "Имя", "Telegram ID", "Что нажал"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            m.from_user.first_name or "",
            m.from_user.id,
            m.text or ""
        ])

@bot.middleware_handler(update_types=["message"])
def log_all_messages(bot_instance, message):
    log_click(message)

user_data = {}
calc_data = {}
quick_data = {}

# Chat ID тех, кто уже оставил заявку (полную или быструю) — им больше не шлём
# отложенные пуши серии.
lead_submitted = set()
_lead_lock = threading.Lock()


def mark_lead_submitted(chat_id):
    with _lead_lock:
        lead_submitted.add(chat_id)


def has_lead(chat_id):
    with _lead_lock:
        return chat_id in lead_submitted


def kb(options, with_back=True, row_width=2, option_style=None, extra=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
    if options:
        markup.add(*[types.KeyboardButton(opt) for opt in options])
    if extra:
        markup.add(*[types.KeyboardButton(opt) if isinstance(opt, str) else opt for opt in extra])
    if with_back:
        markup.add(types.KeyboardButton(BACK))
    return markup


MORE_MENU_BTN = '⋯ Ещё'
CALL_ME_BTN = '📞 Позвонить мне'
CONTACT_METHODS = [CONTACT_VIA_TG_BTN, CALL_ME_BTN]


def main_menu():
    # Максимально простой главный экран: один явный приоритетный шаг (оставить
    # заявку) + связь с менеджером напрямую. Всё остальное — в разделе "Ещё",
    # чтобы не отвлекать лида, который пришёл с рекламы, от целевого действия.
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton('📝 Оставить заявку'))
    markup.add(types.KeyboardButton('💬 Связаться с менеджером'))
    markup.add(types.KeyboardButton(MORE_MENU_BTN))
    return markup


def more_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton('🔍 Подобрать автомобиль'))
    markup.add(types.KeyboardButton('💰 Расчёт стоимости под ключ'))
    markup.add(types.KeyboardButton('⭐ Отзывы'), types.KeyboardButton('📢 Канал'))
    markup.add(types.KeyboardButton('🌐 Наш сайт'), types.KeyboardButton('💡 Популярные вопросы'))
    markup.add(types.KeyboardButton('🏢 О компании'))
    markup.add(types.KeyboardButton(BACK))
    return markup


def contact_method_kb(with_back=True):
    return kb(CONTACT_METHODS, with_back=with_back, row_width=1)


def link_buttons():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='📞 Связаться с менеджером', url=f'https://t.me/{MANAGER_USERNAME}'))
    markup.add(types.InlineKeyboardButton(text='📢 Канал', url=CHANNEL_LINK))
    markup.add(types.InlineKeyboardButton(text='⭐ Отзывы', url=REVIEWS_LINK))
    markup.add(types.InlineKeyboardButton(text='🌐 Наш сайт', url=WEBSITE_LINK))
    return markup


def manager_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text='💬 Написать менеджеру сейчас',
        url=f'https://t.me/{MANAGER_USERNAME}'
    ))
    return markup


def show_main_menu(chat_id, text='Выберите, что хотите сделать 👇'):
    bot.send_message(chat_id, text, reply_markup=main_menu())


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WELCOME_PHOTO = os.path.join(BASE_DIR, "welcome.jpg")

# ===== Серия отложенных пушей после /start: 5 мин / 1ч / 4ч / 10ч / 24ч =====
# Каждый пуш отменяется, если пользователь к этому моменту уже оставил заявку
# (полную анкету или быструю заявку) — см. has_lead().
# Картинку и текст для каждого пуша присылаете отдельно, по очереди — пока
# используются заглушки (кроме 5-минутного, там уже стоит присланный текст/фото).

PUSH_5MIN_DELAY = 5 * 60
PUSH_1H_DELAY = 1 * 60 * 60
PUSH_4H_DELAY = 4 * 60 * 60
PUSH_10H_DELAY = 10 * 60 * 60
PUSH_24H_DELAY = 24 * 60 * 60

PUSH_5MIN_PHOTO = os.path.join(BASE_DIR, "reminder.jpg")
PUSH_1H_PHOTO = os.path.join(BASE_DIR, "push_1h.jpg")
PUSH_4H_PHOTO = os.path.join(BASE_DIR, "push_4h.jpg")
PUSH_10H_PHOTO = os.path.join(BASE_DIR, "push_10h.jpg")
PUSH_24H_PHOTO = os.path.join(BASE_DIR, "push_24h.jpg")


def _send_photo_push(chat_id, photo_path, caption, error_label):
    try:
        with open(photo_path, 'rb') as photo:
            bot.send_photo(chat_id, photo, caption=caption, reply_markup=broadcast_keyboard())
    except FileNotFoundError:
        bot.send_message(chat_id, caption, reply_markup=broadcast_keyboard())
    except Exception as e:
        print(f"Не удалось отправить пуш ({error_label}): {e}")


def send_push_5min(chat_id):
    caption = (
        '🔥 <b>Акционные варианты с горящей ценой</b>\n\n'
        'Сейчас доступны Mazda CX-5 до 160 л.с. по особенно выгодной стоимости для пригона в Россию.\n\n'
        'Такие предложения появляются ограниченно и зависят от наличия автомобилей у поставщиков.\n\n'
        'Оставьте несколько данных — мы бесплатно рассчитаем итоговую стоимость под ключ до вашего города '
        'и покажем вашу экономию относительно рынка РФ.'
    )
    _send_photo_push(chat_id, PUSH_5MIN_PHOTO, caption, '5 мин')


def send_push_1h(chat_id):
    caption = (
        '💰 <b>Дополнительная экономия — и подготовка автомобиля к выдаче</b>\n\n'
        'При покупке автомобиля через нас в ряде случаев возможна дополнительная экономия за счёт '
        'налоговых льгот, что помогает снизить итоговую стоимость.\n\n'
        'А перед выдачей автомобиль можно полностью подготовить: детейлинг, русификация и другие необходимые работы.\n\n'
        'Заполните короткую заявку — рассчитаем стоимость автомобиля с учётом возможной экономии и '
        'доступных вариантов подготовки.'
    )
    _send_photo_push(chat_id, PUSH_1H_PHOTO, caption, '1ч')


def send_push_4h(chat_id):
    caption = (
        '💳 <b>Не нужно оплачивать всю стоимость автомобиля сразу</b>\n\n'
        'При заказе автомобиля через нас оплата проходит поэтапно — в 3 платежа по мере прохождения '
        'основных этапов сделки.\n\n'
        'Это позволяет распределить расходы и не вносить всю сумму за автомобиль в самом начале.\n\n'
        'Оставьте короткую заявку — бесплатно подберём варианты под ваш бюджет и рассчитаем полную '
        'стоимость до вашего города.'
    )
    _send_photo_push(chat_id, PUSH_4H_PHOTO, caption, '4ч')


def send_push_10h(chat_id):
    caption = (
        '🚗 <b>Подберём автомобиль, который действительно выгодно привезти</b>\n\n'
        'Наши менеджеры учитывают мощность до 160 л.с., состояние авто и особенности ввоза, чтобы '
        'подобрать оптимальный вариант под ваш бюджет.'
    )
    _send_photo_push(chat_id, PUSH_10H_PHOTO, caption, '10ч')


def send_push_24h(chat_id):
    caption = (
        '🏢 <b>Личная консультация в наших офисах в Москве</b>\n\n'
        'Обсудите с менеджером подбор и покупку автомобиля лично — от выбора подходящего варианта '
        'до расчёта стоимости.'
    )
    _send_photo_push(chat_id, PUSH_24H_PHOTO, caption, '24ч')


def schedule_lead_push(chat_id, delay_seconds, send_func):
    def _check_and_send():
        if not has_lead(chat_id):
            send_func(chat_id)

    timer = threading.Timer(delay_seconds, _check_and_send)
    timer.daemon = True
    timer.start()


@bot.message_handler(commands=['start'])
def start(m):
    save_user_id(m.from_user.id)
    log_step(m, 'Старт', '🚀 Команда /start', is_new_session=True)
    caption = (
        '✨ <b>Global Auto — премиальный пригон автомобилей под ключ</b>\n\n'
        'Индивидуальный подбор, точный расчёт стоимости и полное сопровождение сделки — '
        'от выбора автомобиля до его передачи Вам в городе.\n\n'
        '📝 Оставьте заявку — персональный менеджер бесплатно подготовит расчёт под Ваш запрос. '
        'Обычно отвечаем в течение 10–15 минут.'
    )
    try:
        with open(WELCOME_PHOTO, 'rb') as photo:
            bot.send_photo(m.chat.id, photo, caption=caption, reply_markup=main_menu())
    except FileNotFoundError:
        bot.send_message(m.chat.id, caption, reply_markup=main_menu())

    schedule_lead_push(m.chat.id, PUSH_5MIN_DELAY, send_push_5min)
    schedule_lead_push(m.chat.id, PUSH_1H_DELAY, send_push_1h)
    schedule_lead_push(m.chat.id, PUSH_4H_DELAY, send_push_4h)
    schedule_lead_push(m.chat.id, PUSH_10H_DELAY, send_push_10h)
    schedule_lead_push(m.chat.id, PUSH_24H_DELAY, send_push_24h)


# ========== 1. ПОДБОР АВТО (полная анкета) ==========

@bot.message_handler(func=lambda m: m.text in ['🔍 Подобрать авто', '🔍 Подобрать автомобиль', '🔍 Подобрать другой автомобиль'])
def ask_country(m):
    log_step(m, 'Подбор авто', 'Шаг 1/7: старт (страна)', is_new_session=True)
    bot.send_message(m.chat.id, '📍 <b>Шаг 1 из 7</b>\n\nИз какой страны Вы хотели бы приобрести автомобиль? 🌏', reply_markup=kb(COUNTRIES))
    bot.register_next_step_handler(m, handle_country)


def handle_country(m):
    if m.text == BACK:
        show_main_menu(m.chat.id)
        return
    if m.text not in COUNTRIES:
        bot.send_message(m.chat.id, '⚠️ Пожалуйста, выберите вариант с помощью кнопок.')
        bot.register_next_step_handler(m, handle_country)
        return
    user_data[m.chat.id] = {'country': m.text}
    ask_budget(m)


def ask_budget(m):
    log_step(m, 'Подбор авто', 'Шаг 2/7: бюджет')
    bot.send_message(m.chat.id, '📍 <b>Шаг 2 из 7</b>\n\nУкажите, пожалуйста, Ваш бюджет 💰', reply_markup=kb(BUDGETS, row_width=1))
    bot.register_next_step_handler(m, handle_budget)


def handle_budget(m):
    if m.text == BACK:
        ask_country(m)
        return
    if m.text not in BUDGETS:
        bot.send_message(m.chat.id, '⚠️ Пожалуйста, выберите вариант с помощью кнопок.')
        bot.register_next_step_handler(m, handle_budget)
        return
    user_data[m.chat.id]['budget'] = m.text
    ask_body(m)


def ask_body(m):
    log_step(m, 'Подбор авто', 'Шаг 3/7: кузов')
    bot.send_message(m.chat.id, '📍 <b>Шаг 3 из 7</b>\n\nКакой кузов Вас интересует? 🚗', reply_markup=kb(BODIES, extra=[SKIP]))
    bot.register_next_step_handler(m, handle_body)


def handle_body(m):
    if m.text == BACK:
        ask_budget(m)
        return
    if m.text == SKIP:
        user_data[m.chat.id]['body'] = 'Не важно'
        ask_brand(m)
        return
    if m.text not in BODIES:
        bot.send_message(m.chat.id, '⚠️ Пожалуйста, выберите вариант с помощью кнопок.')
        bot.register_next_step_handler(m, handle_body)
        return
    user_data[m.chat.id]['body'] = m.text
    ask_brand(m)


def ask_brand(m):
    log_step(m, 'Подбор авто', 'Шаг 4/7: марка')
    bot.send_message(
        m.chat.id,
        '📍 <b>Шаг 4 из 7</b>\n\nКакую марку Вы рассматриваете? 🚙\nНапример: Haval, Kia, Toyota',
        reply_markup=kb([], with_back=True, extra=[SKIP])
    )
    bot.register_next_step_handler(m, handle_brand)


def handle_brand(m):
    if m.text == BACK:
        ask_body(m)
        return
    if m.text == SKIP:
        user_data[m.chat.id]['brand'] = 'Не важно'
        ask_city(m)
        return
    user_data[m.chat.id]['brand'] = m.text
    ask_city(m)


def ask_city(m):
    log_step(m, 'Подбор авто', 'Шаг 5/7: город')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*CITIES)
    markup.add(CUSTOM_CITY_BTN)
    markup.add(types.KeyboardButton(BACK))
    bot.send_message(m.chat.id, '📍 <b>Шаг 5 из 7</b>\n\nВ какой город доставить автомобиль? Выберите из списка или укажите свой:', reply_markup=markup)
    bot.register_next_step_handler(m, handle_city)


def handle_city(m):
    if m.text == BACK:
        ask_brand(m)
        return
    if m.text == CUSTOM_CITY_BTN:
        bot.send_message(m.chat.id, 'Введите название Вашего города:', reply_markup=kb([], with_back=True))
        bot.register_next_step_handler(m, handle_custom_city)
        return
    user_data[m.chat.id]['city'] = m.text
    ask_contact_method(m)


def handle_custom_city(m):
    if m.text == BACK:
        ask_city(m)
        return
    user_data[m.chat.id]['city'] = m.text.strip()
    ask_contact_method(m)


def resolve_phone(m):
    """Проверяет ввод: либо валидный номер, либо связь в Telegram."""
    text = (m.text or '').strip()
    if text == CONTACT_VIA_TG_BTN:
        if m.from_user.username:
            return f"не указан — писать в Telegram: @{m.from_user.username}", True
        return f"не указан — писать в Telegram (ID: {m.from_user.id})", True
    if re.fullmatch(r'(\+7|8)\d{10}', text):
        return text, True
    return None, False


def ask_contact_method(m):
    log_step(m, 'Подбор авто', 'Шаг 6/7: способ связи')
    bot.send_message(
        m.chat.id,
        '✅ <b>Подбор почти готов.</b>\n\n'
        'Как удобнее отправить Вам варианты автомобилей и расчёт стоимости?',
        reply_markup=contact_method_kb()
    )
    bot.register_next_step_handler(m, handle_contact_method)


def handle_contact_method(m):
    if m.text == BACK:
        ask_city(m)
        return
    if m.text == CONTACT_VIA_TG_BTN:
        phone, _ = resolve_phone(m)
        user_data[m.chat.id]['phone'] = phone
        ask_name(m)
        return
    if m.text == CALL_ME_BTN:
        ask_phone(m)
        return
    bot.send_message(m.chat.id, '⚠️ Выберите удобный способ связи с помощью кнопок.')
    bot.register_next_step_handler(m, handle_contact_method)


def ask_name(m):
    log_step(m, 'Подбор авто', 'Шаг 7/7: имя')
    bot.send_message(
        m.chat.id,
        'Остался последний шаг 🙂\n\nКак к Вам обращаться?',
        reply_markup=kb([], with_back=True)
    )
    bot.register_next_step_handler(m, check_name)


def check_name(m):
    if m.text == BACK:
        ask_contact_method(m)
        return
    name = m.text.strip()
    if re.fullmatch(r'[А-Яа-яЁёA-Za-z\s\-]{2,50}', name):
        user_data[m.chat.id]['name'] = name
        finish_full_request(m)
    else:
        bot.send_message(m.chat.id, '⚠️ Имя должно содержать только буквы. Попробуйте ещё раз:', reply_markup=kb([], with_back=True))
        bot.register_next_step_handler(m, check_name)


def ask_phone(m):
    log_step(m, 'Подбор авто', 'Шаг 6/7: телефон')
    bot.send_message(
        m.chat.id,
        'Введите номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX.\n\n'
        'Если передумали — можно выбрать связь в Telegram.',
        reply_markup=kb([], with_back=True, extra=[CONTACT_VIA_TG_BTN])
    )
    bot.register_next_step_handler(m, check_phone)


def check_phone(m):
    if m.text == BACK:
        ask_contact_method(m)
        return
    phone, valid = resolve_phone(m)
    if valid:
        user_data[m.chat.id]['phone'] = phone
        ask_name(m)
    else:
        bot.send_message(
            m.chat.id,
            '⚠️ Неверный формат. Введите номер +7XXXXXXXXXX или нажмите «Связаться со мной в Telegram».',
            reply_markup=kb([], with_back=True, extra=[CONTACT_VIA_TG_BTN])
        )
        bot.register_next_step_handler(m, check_phone)


def finish_full_request(m):
    d = user_data[m.chat.id]
    name_safe = html.escape(d['name'])
    brand_safe = html.escape(d['brand'])
    city_safe = html.escape(d['city'])

    text = (
        f'🔔 Новая заявка (полная анкета)! [{BOT_LABEL}]\n\n'
        f"👤 Имя: {name_safe}\n"
        f"📱 Контакт: {d['phone']}\n"
        f"🆔 Telegram ID: {m.from_user.id}\n"
        f"👤 Username: @{m.from_user.username if m.from_user.username else 'нет username'}\n"
        f"🌏 Страна: {d['country']}\n"
        f"💰 Бюджет: {d['budget']}\n"
        f"🚗 Кузов: {d['body']}\n"
        f"🏷 Марка: {brand_safe}\n"
        f"🏙 Город: {city_safe}"
    )
    bot.send_message(MANAGER_ID, text)
    log_step(m, 'Подбор авто', 'Завершил анкету ✅')
    send_lead(m, 'Полная анкета', d)

    bot.send_message(
        m.chat.id,
        f'✅ <b>{name_safe}, заявка принята!</b>\n\n'
        'Ваш запрос уже получил менеджер. Обычно отвечаем за 10–15 минут.\n\n'
        'Пока ожидаете, можно посмотреть реальные автомобили и отзывы:',
        reply_markup=link_buttons()
    )
    show_main_menu(m.chat.id, 'Что ещё хотите посмотреть? 👇')


# ========== 2. БЫСТРАЯ ЗАЯВКА (1 шаг: номер телефона в один тап) ==========
# Имя не спрашиваем отдельным вопросом — берём first_name из профиля Telegram
# (он есть в каждом сообщении). Телефон получаем через нативную кнопку
# "Поделиться номером" (request_contact) — это одно нажатие, без набора текста.
# Если человек не хочет делиться номером напрямую — вместо ручного ввода
# предлагаем связаться в Telegram (по @username/ID), это тоже 1 тап.

def lead_name_from_profile(m):
    name = (m.from_user.first_name or '').strip()
    return name if name else 'Клиент'


def phone_request_kb():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton('📲 Поделиться номером', request_contact=True))
    markup.add(types.KeyboardButton(CONTACT_VIA_TG_BTN))
    markup.add(types.KeyboardButton(BACK))
    return markup


@bot.message_handler(func=lambda m: m.text in ['⚡ Быстрая заявка', '📝 Оставить заявку'])
def quick_ask_name(m):
    log_step(m, 'Быстрая заявка', 'Шаг 1/1: телефон', is_new_session=True)
    quick_data[m.chat.id] = {'name': lead_name_from_profile(m)}
    bot.send_message(
        m.chat.id,
        '📲 Нажмите кнопку ниже, чтобы поделиться номером телефона — это займёт одно нажатие.',
        reply_markup=phone_request_kb()
    )
    bot.register_next_step_handler(m, quick_check_phone)


def quick_check_phone(m):
    if m.text == BACK:
        show_main_menu(m.chat.id)
        return

    d = quick_data.setdefault(m.chat.id, {'name': lead_name_from_profile(m)})

    phone = None
    contact = getattr(m, 'contact', None)
    if contact is not None:
        raw_phone = contact.phone_number or ''
        phone = raw_phone if raw_phone.startswith('+') else f'+{raw_phone}'
    else:
        resolved, valid = resolve_phone(m)
        if valid:
            phone = resolved

    if phone:
        d['phone'] = phone
        name_safe = html.escape(d['name'])

        text = (
            f'⚡ Новая БЫСТРАЯ заявка! [{BOT_LABEL}]\n\n'
            f"👤 Имя: {name_safe}\n"
            f"📱 Телефон: {d['phone']}\n"
            f"🆔 Telegram ID: {m.from_user.id}\n"
            f"👤 Username: @{m.from_user.username if m.from_user.username else 'нет username'}"
        )
        bot.send_message(MANAGER_ID, text)
        log_step(m, 'Быстрая заявка', 'Завершил анкету ✅')
        send_lead(m, 'Быстрая заявка', d)

        bot.send_message(
            m.chat.id,
            f'✅ <b>{name_safe}, заявка принята!</b>\n\n'
            'Ваш персональный менеджер уже получил заявку и свяжется с Вами в ближайшее время.',
            reply_markup=manager_button()
        )
        show_main_menu(m.chat.id)
    else:
        bot.send_message(
            m.chat.id,
            '⚠️ Не получилось распознать номер. Нажмите «Поделиться номером» или введите номер в формате +7XXXXXXXXXX.',
            reply_markup=phone_request_kb()
        )
        bot.register_next_step_handler(m, quick_check_phone)


# ========== 3. РАСЧЁТ СТОИМОСТИ ПОД КЛЮЧ ==========

@bot.message_handler(func=lambda m: m.text == '💰 Расчёт стоимости под ключ')
def calc_ask_country(m):
    log_step(m, 'Расчёт стоимости', 'Шаг 1/3: страна', is_new_session=True)
    bot.send_message(m.chat.id, '📍 <b>Шаг 1 из 3</b>\n\nИз какой страны рассматриваете автомобиль? 🌏', reply_markup=kb(COUNTRIES))
    bot.register_next_step_handler(m, calc_handle_country)


def calc_handle_country(m):
    if m.text == BACK:
        show_main_menu(m.chat.id)
        return
    if m.text not in DELIVERY_COST:
        bot.send_message(m.chat.id, '⚠️ Пожалуйста, выберите страну с помощью кнопок.')
        bot.register_next_step_handler(m, calc_handle_country)
        return
    calc_data[m.chat.id] = {'country': m.text}
    calc_ask_price(m)


def calc_ask_price(m):
    log_step(m, 'Расчёт стоимости', 'Шаг 2/3: цена')
    bot.send_message(
        m.chat.id,
        '📍 <b>Шаг 2 из 3</b>\n\nВведите примерную стоимость автомобиля на месте, в рублях (только число, например: 1500000)',
        reply_markup=kb([], with_back=True)
    )
    bot.register_next_step_handler(m, calc_handle_price)


def calc_handle_price(m):
    if m.text == BACK:
        calc_ask_country(m)
        return
    price_raw = m.text.strip().replace(' ', '')
    if not price_raw.isdigit():
        bot.send_message(m.chat.id, '⚠️ Введите, пожалуйста, только число, например: 1500000', reply_markup=kb([], with_back=True))
        bot.register_next_step_handler(m, calc_handle_price)
        return
    calc_data[m.chat.id]['price'] = int(price_raw)
    calc_ask_body(m)


def calc_ask_body(m):
    log_step(m, 'Расчёт стоимости', 'Шаг 3/3: кузов')
    bot.send_message(m.chat.id, '📍 <b>Шаг 3 из 3</b>\n\nВыберите тип кузова / объём двигателя 🚗', reply_markup=kb(CALC_BODIES))
    bot.register_next_step_handler(m, calc_handle_body)


def calc_handle_body(m):
    if m.text == BACK:
        calc_ask_price(m)
        return
    if m.text not in CUSTOMS_RATE:
        bot.send_message(m.chat.id, '⚠️ Пожалуйста, выберите вариант с помощью кнопок.')
        bot.register_next_step_handler(m, calc_handle_body)
        return

    d = calc_data[m.chat.id]
    price = d['price']
    country = d['country']
    delivery = DELIVERY_COST[country]
    customs = int(price * CUSTOMS_RATE[m.text])
    total = price + delivery + customs + SERVICE_FEE

    text = (
        '📊 Примерный расчёт стоимости под ключ:\n\n'
        f"🚗 Стоимость автомобиля: {price:,} ₽\n".replace(',', ' ')
        + f"🚢 Доставка из {country.split(' ')[1]}: ~{delivery:,} ₽\n".replace(',', ' ')
        + f"📋 Растаможка: ~{customs:,} ₽\n".replace(',', ' ')
        + f"🔧 Наши услуги: {SERVICE_FEE:,} ₽\n\n".replace(',', ' ')
        + f"💰 <b>Итого под ключ: ~{total:,} ₽</b>\n\n".replace(',', ' ')
        + '⚠️ Точная сумма зависит от конкретной модели, года выпуска и точного объёма двигателя.'
    )
    bot.send_message(m.chat.id, text, reply_markup=manager_button())
    log_step(m, 'Расчёт стоимости', 'Получил расчёт ✅')
    show_main_menu(m.chat.id)


@bot.message_handler(func=lambda m: m.text == MORE_MENU_BTN)
def show_more_menu(m):
    bot.send_message(m.chat.id, 'Дополнительные разделы 👇', reply_markup=more_menu())

# ========== 4. КАНАЛ ==========

@bot.message_handler(func=lambda m: m.text == '📢 Канал')
def show_channel(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='📢 Перейти в канал', url=CHANNEL_LINK))
    bot.send_message(m.chat.id, 'Актуальные автомобили и новости — в нашем канале:', reply_markup=markup)


# ========== 5. СВЯЗАТЬСЯ С МЕНЕДЖЕРОМ ==========

@bot.message_handler(func=lambda m: m.text in ['📞 Связаться с менеджером', '💬 Связаться с менеджером'])
def contact_manager(m):
    bot.send_message(m.chat.id, '👇', reply_markup=manager_button())


# ========== 6. ОТЗЫВЫ ==========

@bot.message_handler(func=lambda m: m.text == '⭐ Отзывы')
def show_reviews(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='⭐ Смотреть отзывы', url=REVIEWS_LINK))
    bot.send_message(m.chat.id, 'Отзывы наших клиентов:', reply_markup=markup)


# ========== 7. О КОМПАНИИ ==========

@bot.message_handler(func=lambda m: m.text == '🏢 О компании')
def about_company(m):
    bot.send_message(
        m.chat.id,
        '🏢 <b>Global Auto — пригон авто</b>\n\n'
        '📅 Работаем с <b>2015 года</b> из Владивостока. За 10 лет помогли <b>2 500+</b> клиентам '
        'по всей России купить автомобиль напрямую у зарубежных поставщиков.\n\n'
        '<b>Как мы работаем:</b>\n'
        '🎯 Подбираем под ваш бюджет и задачи\n'
        '🔍 Проверяем историю и состояние авто\n'
        '📋 Оформляем все документы и растаможку\n'
        '🚚 Доставляем до вашего города под ключ\n\n'
        '📍 Офис: Владивосток, ул. Маковского, 11\n'
        '📞 Телефон: 8 (800) 300-80-33 (бесплатно по РФ)',
        reply_markup=main_menu()
    )


# ========== 8. НАШ САЙТ ==========

@bot.message_handler(func=lambda m: m.text == '🌐 Наш сайт')
def show_website(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='🌐 Перейти на сайт', url=WEBSITE_LINK))
    bot.send_message(m.chat.id, 'Подробнее о том, как мы работаем — на нашем сайте:', reply_markup=markup)


# ========== 9. ПОПУЛЯРНЫЕ ВОПРОСЫ ==========

STILL_QUESTIONS_BTN = '❓ Остались вопросы?'


def faq_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*list(FAQ.keys()))
    markup.add(types.KeyboardButton(STILL_QUESTIONS_BTN))
    markup.add(types.KeyboardButton(BACK))
    bot.send_message(chat_id, '💡 Выберите интересующий вопрос:', reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == '💡 Популярные вопросы')
def show_faq(m):
    faq_menu(m.chat.id)


@bot.message_handler(func=lambda m: m.text in FAQ)
def answer_faq(m):
    bot.send_message(m.chat.id, FAQ[m.text])
    faq_menu(m.chat.id)


@bot.message_handler(func=lambda m: m.text == STILL_QUESTIONS_BTN)
def still_questions(m):
    bot.send_message(
        m.chat.id,
        'Не нашли ответ на свой вопрос? 🤔\n\nНапишите напрямую нашему менеджеру — он ответит на всё, что Вас интересует!',
        reply_markup=manager_button()
    )
    faq_menu(m.chat.id)


# Общий обработчик "Назад" — срабатывает, когда кнопка нажата вне пошаговых анкет
# (например, в разделе FAQ), и просто возвращает в главное меню.
@bot.message_handler(func=lambda m: m.text == BACK)
def fallback_back(m):
    show_main_menu(m.chat.id)


@bot.message_handler(commands=['reply'])
def reply_to_client(m):
    if m.chat.id != MANAGER_ID:
        return

    parts = m.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(
            m,
            '⚠️ Использование:\n<code>/reply telegram_id текст сообщения</code>\n\n'
            'Пример:\n<code>/reply 8069140702 Здравствуйте! Мы получили Вашу заявку...</code>'
        )
        return

    _, raw_id, text = parts
    try:
        target_id = int(raw_id)
    except ValueError:
        bot.reply_to(m, '⚠️ Telegram ID должен быть числом. Пример: /reply 8069140702 Ваш текст')
        return

    try:
        bot.send_message(target_id, text)
        bot.reply_to(m, f'✅ Сообщение отправлено клиенту ({target_id}).')
    except Exception as e:
        bot.reply_to(m, f'❌ Не удалось отправить сообщение: {e}')

import time

# Рассылка сообщения всем, кто хоть раз писал боту. Использовать в рабочей группе:
# /broadcast текст сообщения
def broadcast_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('💬 Связаться с менеджером', url=f'https://t.me/{MANAGER_USERNAME}'))
    markup.add(types.InlineKeyboardButton('📝 Оставить заявку', callback_data='start_quick_request'))
    return markup


@bot.callback_query_handler(func=lambda call: call.data == 'start_quick_request')
def handle_broadcast_quick_request(call):
    call.message.from_user = call.from_user  # чтобы анкета и логирование шли от имени реального пользователя
    bot.answer_callback_query(call.id)
    quick_ask_name(call.message)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(m):
    if m.chat.id != MANAGER_ID:
        return  # рассылку можно запускать только из рабочей группы

    text = m.text.partition(' ')[2].strip()
    if not text:
        bot.reply_to(m, '⚠️ Использование:\n<code>/broadcast текст сообщения для всех</code>')
        return

    user_ids = load_user_ids()
    if not user_ids:
        bot.reply_to(m, '⚠️ Пока нет ни одного сохранённого пользователя для рассылки.')
        return

    bot.reply_to(m, f'🚀 Начинаю рассылку {len(user_ids)} пользователям...')

    def _run_broadcast():
        sent, failed = 0, 0
        for uid in user_ids:
            try:
                bot.send_message(uid, text, reply_markup=broadcast_keyboard())
                sent += 1
            except Exception:
                failed += 1
            time.sleep(0.05)  # небольшая пауза, чтобы не упереться в лимиты Telegram
        bot.send_message(MANAGER_ID, f'✅ Рассылка завершена.\n📤 Доставлено: {sent}\n🚫 Не доставлено: {failed}')

    threading.Thread(target=_run_broadcast, daemon=True).start()


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"⚠️ Бот упал с ошибкой, перезапуск через 5 секунд: {e}")
            time.sleep(5)
            continue
