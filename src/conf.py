from environs import Env

env = Env()

app_name = 'NU cashier bot'

SKIP_UPDATES = False

TELEGRAM_TOKEN = env('BOT_TOKEN')

ADMIN_IDS = env.list('ADMIN_IDS')


EMOJI = {
    "cart": "🛒",
    "phone": "📲",
    "red": "🔴",
    "green": "🟢",
    "handshake": "👋",
    "catalog": "🛍",
    "add": "📍",
    "address": "🏠",
    "user": "👤",
    "order": "📦"
}
