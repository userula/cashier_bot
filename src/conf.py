from environs import Env

env = Env()

app_name = 'NU cashier bot'

SKIP_UPDATES = False
# TELEGRAM_TOKEN = env('BOT_TOKEN')
TELEGRAM_TOKEN = "1239266158:AAF9ES_M4vvKF2zv7pIZCZAtruMfjAPHHj4"

ADMIN_IDS = env.list('ADMIN_IDS')


EMOJI = {
    "cart": "🛒",
    "phone": "📲",
    "red": "🔴",
    "green": "🟢",
    "handshake": "👋",
    "catalog": "🛍",
    "add": "📍",
    8: "",
    9: "",
    10: ""
}
