import streamlit as st
import datetime
import requests
import pandas as pd
import telebot
from threading import Thread

# Şifreler ve Ayarlar
TOKEN = "8967109165:AAH7BdP28D7UHVZ7TcuS8szYuae3yctNutM"
SUPABASE_URL = "https://cyienwazvmnlbxsondwq.supabase.co"
SUPABASE_KEY = "sb_publishable_kNTUKDuw29M43goDPsFzcw_W7Y4EvFL"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --- TELEGRAM BOT KISMI ---
def botu_baslat():
    try:
        bot = telebot.TeleBot(TOKEN)

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
                res = requests.post(f"{SUPABASE_URL}/rest/v1/kilo_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json=data)
                if res.status_code in [200, 201]:
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
                res = requests.post(f"{SUPABASE_URL}/rest/v1/kardiyo_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json=data)
                if res.status_code in [200, 201]:
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
                data = {"hareket_adi": hareket, "set_sayisi": set_s, "tekrar_sayisi": tekrar, "agirlik": ag规律}
                data = {"hareket_adi": hareket, "set_sayisi": set_s, "tekrar_sayisi": tekrar, "agirlik": agirlik}
                res = requests.post(f"{SUPABASE_URL}/rest/v1/antrenman_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json=data)
                if res.status_code in [200, 201]:
                    bot.reply_to(message, f"🏋️‍♂️ {hareket} kaydedildi! {set_s}x{tekrar} - {agirlik}kg.")
                else:
                    bot.reply_to(message, "❌ Bir hata oluştu.")
            except:
                bot.reply_to(message, "⚠️ Hatalı kullanım! Örnek: `/ant Squat 4 10 80`")

        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        pass

# Botu arka planda bir kereye mahsus çalıştırıyoruz
if "bot_calisiyor" not in st.session_state:
    st.session_state["bot_calisiyor"] = True
    Thread(target=botu_baslat, daemon=True).start()

# --- STREAMLIT WEB ARAYÜZ KISMI ---
st.set_page_config(page_title="Fitness Asistanım", page_icon="💪", layout="wide")
st.title("💪 Kişisel Fitness Takip Paneli")
st.write("---")

def veri_cek(tablo_adi):
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/{tablo_adi}?order=id.desc", headers=HEADERS)
        if res.status_code == 200:
            return pd.DataFrame(res.json())
    except:
        pass
    return pd.DataFrame()

st.sidebar.header("👤 Profilim")
kilo_df = veri_cek("kilo_takip")
if not kilo_df.empty:
    son_kilo = kilo_df.iloc[0]['kilo']
    st.sidebar.metric(label="Anlık Kilonuz", value=f"{son_kilo} kg")
else:
    st.sidebar.info("Henüz kilo kaydı bulunamadı.")

sekme1, sekme2, sekme3 = st.tabs(["🏋️‍♂️ Antrenman Geçmişi", "🏃‍♂️ Kardiyo Geçmişi", "📈 Kilo Gelişimi"])

with sekme1:
    st.header("🏋️‍♂️ Antrenman Logları")
    ant_df = veri_cek("antrenman_takip")
    if not ant_df.empty:
        st.dataframe(ant_df[['tarih', 'hareket_adi', 'set_sayisi', 'tekrar_sayisi', 'agirlik']], use_container_width=True)
    else:
        st.info("Henüz antrenman kaydı yok. Telegram botundan ekleyebilirsin!")

with sekme2:
    st.header("🏃‍♂️ Kardiyo Geçmişi")
    kar_df = veri_cek("kardiyo_takip")
    if not kar_df.empty:
        st.dataframe(kar_df[['tarih', 'tur', 'sure', 'kalori']], use_container_width=True)
    else:
        st.info("Henüz kardiyo kaydı yok. Telegram botundan ekleyebilirsin!")

with sekme3:
    st.header("📈 Kilo Değişim Grafiği")
    if not kilo_df.empty:
        kilo_df['tarih'] = pd.to_datetime(kilo_df['tarih'])
        kilo_df = kilo_df.sort_values('tarih')
        st.line_chart(data=kilo_df, x='tarih', y='kilo')
        st.dataframe(kilo_df[['tarih', 'kilo']], use_container_width=True)
    else:
        st.info("Grafik için henüz yeterli kilo verisi yok.")


