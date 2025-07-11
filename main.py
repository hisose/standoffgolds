import telebot, json, time
from telebot import types

# 📌 Твой токен
TOKEN = "7867278635:AAEf-D_t3yky1WAM8W-4Gr3aCMMDQr-YOmI"
CHANNELS = ['@nftbazaNFT', '@standofgoldse']
bot = telebot.TeleBot(TOKEN)

# 💾 Загрузка базы
def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)

data = load_data()

# ✅ Проверка подписки
def is_subscribed(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

# 💬 /start
@bot.message_handler(commands=['start'])
def start(msg):
    uid = str(msg.from_user.id)
    ref = msg.text[7:] if len(msg.text.split()) > 1 else None

    if uid not in data:
        data[uid] = {"balance": 0, "ref": ref, "bonus": 0}
        save_data(data)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Подписаться", url="https://t.me/" + CHANNELS[0][1:]))
    markup.add(types.InlineKeyboardButton("✅ Проверить подписку", callback_data="verify"))
    bot.send_message(uid, "Добро пожаловать в STANDOFF GOLDS! Подпишитесь и нажмите кнопку ниже для получения голды.", reply_markup=markup)

# 🤖 Проверка подписки
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = str(call.from_user.id)
    if call.data == "verify":
        if is_subscribed(call.from_user.id):
            if data[uid]["balance"] == 0:
                data[uid]["balance"] += 5
                ref = data[uid].get("ref")
                if ref and ref in data:
                    data[ref]["balance"] += 10.5
                    bot.send_message(ref, f"👥 Приглашённый друг подписался! +10.5 голды.")
                save_data(data)
                bot.send_message(uid, "✅ Подписка подтверждена! +5 голды.")
            else:
                bot.send_message(uid, "Вы уже получили бонус 💰")
        else:
            bot.send_message(uid, "❌ Вы не подписались на оба канала.")

# 💰 /balance
@bot.message_handler(commands=['balance'])
def balance(msg):
    uid = str(msg.from_user.id)
    bal = data.get(uid, {}).get("balance", 0)
    bot.send_message(uid, f"💰 Ваш баланс: {bal} голды")

# 🎁 /bonus — раз в день
@bot.message_handler(commands=['bonus'])
def bonus(msg):
    uid = str(msg.from_user.id)
    now = int(time.time())
    last = data.get(uid, {}).get("bonus", 0)

    if now - last >= 86400:
        gain = 1 + int((time.time() * 1000) % 5)
        data[uid]["balance"] += gain
        data[uid]["bonus"] = now
        save_data(data)
        bot.send_message(uid, f"🎁 Вы получили {gain} голды за бонус!")
    else:
        remaining = 86400 - (now - last)
        hours = int(remaining / 3600)
        bot.send_message(uid, f"🕒 Бонус доступен через {hours}ч.")

# 🎯 /promo — ввод промо-кода
@bot.message_handler(commands=['promo'])
def promo(msg):
    code = msg.text.split(' ')[1] if len(msg.text.split()) > 1 else None
    uid = str(msg.from_user.id)
    if code == "GOLD100":
        data[uid]["balance"] += 100
        save_data(data)
        bot.send_message(uid, "🎉 Промо-код активирован! +100 голды.")
    else:
        bot.send_message(uid, "❌ Неверный промо-код.")

# 👑 /admin — доступ для тебя
@bot.message_handler(commands=['admin'])
def admin(msg):
    if msg.from_user.id == 786727863:  # Твой ID
        text = "\n".join([f"{u}: {d['balance']} голды" for u, d in data.items()])
        bot.send_message(msg.chat.id, f"📊 Игроки:\n{text}")
    else:
        bot.send_message(msg.chat.id, "🚫 Нет доступа")

# ▶️ Запуск
bot.polling(none_stop=True)
