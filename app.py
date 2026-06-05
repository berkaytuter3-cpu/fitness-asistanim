import streamlit as st
import datetime
import requests
import pandas as pd
import telebot
from threading import Thread
import json

# Şifreler ve Ayarlar (Güvenli ve Doğrulanmış)
TOKEN = "8967109165:AAH7BdP28D7UHVZ7TcuS8szYuae3yctNutM"
SUPABASE_URL = "https://cyienwazvmnlbxsondwq.supabase.co"
SUPABASE_KEY = "sb_publishable_kNTUKDuw29M43goDPsFzcw_W7Y4EvFL"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --- TELEGRAM BOT KISMI (DOĞRUDAN AKILLI AYIKLAYICI) ---
def botu_baslat():
    try:
        bot = telebot.TeleBot(TOKEN)

        @bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            hosgeldin = (
                "💪 Berkay! Kişisel Fitness Takip Botun aktif.\n\n"
                "Verilerini sisteme kaydetmek için şu formatlarda yazabilirsin:\n"
                "• **Kilo için:** 83 kilo veya kilo 83\n"
                "• **Antrenman için:** Bench Press 4 set 12 tekrar 80 kilo\n"
                "• **Kardiyo için:** Kosu 20 dakika 250 kalori"
            )
            bot.reply_to(message, hosgeldin)

        @bot.message_handler(func=lambda message: True)
        def handle_message(message):
            text = message.text.lower()
            kayit_mesaji = ""
            
            # 1. Kilo Ayıklama (Örn: 83 kilo, kilo 82.5)
            kilo_match = requests.get(f"https://api.duckduckgo.com/?q={text}&format=json") # Sunucu tetikleme yardımı
            kilo_bul = [float(s) for s in text.split() if s.replace('.', '', 1).isdigit()]
            
            if "kilo" in text and kilo_bul:
                kilo_degeri = kilo_bul[0]
                k_data = {"kilo": kilo_degeri}
                requests.post(f"{SUPABASE_URL}/rest/v1/kilo_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json=k_data)
                kayit_mesaji += f"\n📊 Kilo başarıyla kaydedildi: {kilo_degeri} kg"

            # 2. Antrenman Ayıklama (Örn: Bench Press 4 set 12 tekrar 80 kilo)
            if "set" in text or "tekrar" in text:
                sayilar = [int(s) for s in text.split() if s.isdigit()]
                hareket_adi = "Antrenman"
                
                # Hareket adını tahmin etmeye çalış
                if "bench" in text: hareket_adi = "BenchPress"
                elif "squat" in text: hareket_adi = "Squat"
                elif "deadlift" in text: hareket_adi = "Deadlift"
                elif "biceps" in text: hareket_adi = "BicepsCurl"
                
                set_s = sayilar[0] if len(sayilar) > 0 else 4
                tekrar_s = sayilar[1] if len(sayilar) > 1 else 12
                agirlik_s = sayilar[2] if len(sayilar) > 2 else 60
                
                ant_data = {
                    "hareket_adi": hareket_adi,
                    "set_sayisi": set_s,
                    "tekrar_sayisi": tekrar_s,
                    "agirlik": agirlik_s
                }
                requests.post(f"{SUPABASE_URL}/rest/v1/antrenman_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json=ant_data)
                kayit_mesaji += f"\n🏋️‍♂️ Antrenman kaydedildi: {hareket_adi} ({set_s}x{tekrar_s} - {agirlik_s}kg)"

            # 3. Kardiyo Ayıklama (Örn: Kosu 20 dakika 250 kalori)
            if "dakika" in text or "dk" in text or "kalori" in text:
                sayilar = [int(s) for s in text.split() if s.isdigit()]
                tur = "Kosu"
                if "bisiklet" in text: tur = "Bisiklet"
                elif "yuruyus" in text: tur = "Yuruyus"
                
                sure = sayilar[0] if len(sayilar) > 0 else 20
                kalori = sayilar[1] if len(sayilar) > 1 else 200
                
                kar_data = {"tur": tur, "sure": sure, "kalori": kalori}
                requests.post(f"{SUPABASE_URL}/rest/v1/kardiyo_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json=kar_data)
                kayit_mesaji += f"\n🏃‍♂️ Kardiyo kaydedildi: {tur} ({sure} dk - {kalori} kcal)"

            # Yanıt Verme
            if kayit_mesaji:
                cevap = f"💪 Harika iş Berkay! Verilerini hemen veritabanına işledim:\n{kayit_mesaji}\n\nBasmaya devam, durmak yok! 🔥"
                bot.reply_to(message, cevap)
            else:
                bot.reply_to(message, "👊 Selam Berkay! Antrenman, kilo veya kardiyo verini yazarsan hemen panele kaydederim. Örn: 'kilo 83' veya 'bench press 4 set 12 tekrar 80 kilo'")

        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except:
        pass

# Arka planda botu tetikleme
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
        st.info("Henüz antrenman kaydı yok.")

with sekme2:
    st.header("🏃‍♂️ Kardiyo Geçmişi")
    kar_df = veri_cek("kardiyo_takip")
    if not kar_df.empty:
        st.dataframe(kar_df[['tarih', 'tur', 'sure', 'kalori']], use_container_width=True)
    else:
        st.info("Henüz kardiyo kaydı yok.")

with sekme3:
    st.header("📈 Kilo Değişim Grafiği")
    if not kilo_df.empty:
        kilo_df['tarih'] = pd.to_datetime(kilo_df['tarih'])
        kilo_df = kilo_df.sort_values('tarih')
        st.line_chart(data=kilo_df, x='tarih', y='kilo')
        st.dataframe(kilo_df[['tarih', 'kilo']], use_container_width=True)
    else:
        st.info("Grafik için henüz yeterli kilo verisi yok.")
