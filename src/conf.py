from environs import Env

env = Env()

app_name = 'NU cashier bot'

SKIP_UPDATES = False
TELEGRAM_TOKEN = env('BOT_TOKEN')

ADMIN_IDS = env.list('ADMIN_IDS')


EMOJI = {
    1: "🛒",
    2: "📲",
    3: "🔴",
    4: "🟢",
    5: "👋",
    6: "",
    7: "",
    8: "",
    9: "",
    10: ""
}
