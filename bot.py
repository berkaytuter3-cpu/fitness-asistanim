import telebot
import requests
import json

# Şifrelerimizi bağlıyoruz
TOKEN = "8967109165:AAH7BdP28D7UHVZ7TcuS8szYuae3yctNutM"
SUPABASE_URL = "https://cyienwazvmnlbxsondwq.supabase.co"
SUPABASE_KEY = "sb_publishable_kNTUKDuw29M43goDPsFzcw_W7Y4EvFL"

bot = telebot.TeleBot(TOKEN)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    hosgeldin = (
        "💪 Merhaba Berkay! Fitness Asistanına hoş geldin.\n\n"
        "Şu komutlarla veri kaydedebilirsin:\n"
        "👉 `/kilo 75.5` -> Kilonu kaydeder.\n"
        "👉 `/kardiyo Bisiklet 20 250` -> Kardiyo kaydeder.\n"
        "👉 `/ant BenchPress 4 10 60` -> Antrenman kaydeder."
    )
    bot.reply_to(message, hosgeldin)

@bot.message_handler(commands=['kilo'])
def save_kilo(message):
    try:
        kilo_degeri = float(message.text.split()[1])
        data = {"kilo": kilo_degeri}
        response = requests.post(f"{SUPABASE_URL}/rest/v1/kilo_takip", headers=HEADERS, data=json.dumps(data))
        if response.status_code in [200, 201]:
            bot.reply_to(message, f"✅ Başarıyla kaydedildi! Bugünkü kilon: {kilo_degeri} kg.")
        else:
            bot.reply_to(message, "❌ Veri tabanına kaydedilirken bir hata oluştu.")
    except:
        bot.reply_to(message, "⚠️ Hatalı kullanım! Örnek: `/kilo 75.5` şeklinde yazmalısın.")

@bot.message_handler(commands=['kardiyo'])
def save_kardiyo(message):
    try:
        parcalar = message.text.split()
        tur = parcalar[1]
        sure = int(parcalar[2])
        kalori = int(parcalar[3])
        data = {"tur": tur, "sure": sure, "kalori": kalori}
        response = requests.post(f"{SUPABASE_URL}/rest/v1/kardiyo_takip", headers=HEADERS, data=json.dumps(data))
        if response.status_code in [200, 201]:
            bot.reply_to(message, f"🏃‍♂️ Kardiyo kaydedildi: {tur}, {sure} dk, {kalori} kcal.")
        else:
            bot.reply_to(message, "❌ Bir hata oluştu.")
    except:
        bot.reply_to(message, "⚠️ Hatalı kullanım! Örnek: `/kardiyo Bisiklet 25 300`")

@bot.message_handler(commands=['ant'])
def save_antrenman(message):
    try:
        parcalar = message.text.split()
        hareket = parcalar[1]
        set_s = int(parcalar[2])
        tekrar = int(parcalar[3])
        agirlik = float(parcalar[4])
        data = {"hareket_adi": hareket, "set_sayisi": set_s, "tekrar_sayisi": tekrar, "agirlik": agirlik}
        response = requests.post(f"{SUPABASE_URL}/rest/v1/antrenman_takip", headers=HEADERS, data=json.dumps(data))
        if response.status_code in [200, 201]:
            bot.reply_to(message, f"🏋️‍♂️ {hareket} kaydedildi! {set_s}x{tekrar} - {agirlik}kg.")
        else:
            bot.reply_to(message, "❌ Bir hata oluştu.")
    except:
        bot.reply_to(message, "⚠️ Hatalı kullanım! Örnek: `/ant Squat 4 10 80`")

bot.infinity_polling()
