import requests
import telebot

BOT_TOKEN = 'ваш_телеграм_токен' # @BotFather

bot = telebot.TeleBot(BOT_TOKEN)

user_state = {}

def check_server_status(url):
    try:
        response = requests.get(url, timeout=15)
        return response.status_code
    except requests.RequestException:
        return None

@bot.message_handler(commands=['start'])
def request_url(message):
    chat_id = message.chat.id
    user_state[chat_id] = "waiting_for_url"
    bot.send_message(chat_id, "Введите URL сайта (protocol://domain_name):")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_url")
def process_url(message):
    chat_id = message.chat.id
    url = message.text.strip()
    status_code = check_server_status(url)

    if status_code is None:
        alert_message = "❌ Ошибка!: Сервер недоступен."
    else:
        status_range = get_status_range(status_code)
        alert_message = f"{status_range}\nСтатус-код ответа: {status_code}\nURL: {url}"

        bot.send_message(chat_id=chat_id, text=alert_message)

    user_state[chat_id] = "waiting_for_another_url"
    bot.send_message(chat_id, "Хотите проверить другой URL? Введите URL или нажмите /cancel для выхода.")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_another_url")
def process_another_url(message):
    chat_id = message.chat.id
    if message.text.lower() == "/cancel":
        bot.send_message(chat_id, "Работа бота остановлена. Нажмите /start чтобы перезапустить бота.")
        del user_state[chat_id]
    else:
        process_url(message)

def get_status_range(status_code):
    if 100 <= status_code <= 199:
        return "🟣 Информационный (1xx)"
    elif 200 <= status_code <= 299:
        return "🟢 Успешно (2xx)"
    elif 300 <= status_code <= 399:
        return "🟡 Перенаправление (3xx)"
    elif 400 <= status_code <= 499:
        return "🔴 Ошибка клиента (4xx)"
    elif 500 <= status_code <= 599:
        return "🔴 Ошибка сервера (5xx)"
    else:
        return "❓ Неизвестный статус-код"

def main():
    bot.polling()

if __name__ == "__main__":
    main()