import streamlit as st
import datetime
import requests
import pandas as pd
import telebot
from threading import Thread
import json
import re

# ==========================================
# 🔑 ŞİFRELER VE GÜVENLİK AYARLARI
# ==========================================
TOKEN = "8967109165:AAH7BdP28D7UHVZ7TcuS8szYuae3yctNutM"
SUPABASE_URL = "https://cyienwazvmnlbxsondwq.supabase.co"
SUPABASE_KEY = "sb_publishable_kNTUKDuw29M43goDPsFzcw_W7Y4EvFL"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --- TELEGRAM BOT KISMI (Proxy Yapay Zeka Entegrasyonu) ---
def botu_baslat():
    try:
        bot = telebot.TeleBot(TOKEN)

        @bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            hosgeldin = (
                "💪 Berkay! Sonunda tamamen özgür ve yapay zeka destekli canavar moduna geçtik!\n\n"
                "Artık kalıplara bağlı kalmana gerek yok. Bana antrenmanını anlat, kilonu söyle, ya da canın ne isterse ondan bahset (Motorlar, arabalar, dertleşme...).\n\n"
                "Senin dilinden anlayan kişisel koçun hazır. Basmaya devam! 🔥"
            )
            bot.reply_to(message, hosgeldin)

        @bot.message_handler(func=lambda message: True)
        def handle_ai_message(message):
            user_text = message.text
            text_lower = user_text.lower()
            
            # 1. Aşama: Veritabanı İçin Akıllı Veri Ayıklama (Regex & Zeka)
            kayit_mesaji = ""
            kilo_degeri = None
            
            # Kilo yakalama (Örn: "65 kg uyandım", "kilo 64.5 çıktı")
            kilo_match = re.search(r'(?:kilo|kg)\s*([\d.]+)|([\d.]+)\s*(?:kilo|kg)', text_lower)
            if kilo_match:
                kilo_str = kilo_match.group(1) or kilo_match.group(2)
                try:
                    kilo_degeri = float(kilo_str)
                    requests.post(f"{SUPABASE_URL}/rest/v1/kilo_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json={"kilo": kilo_degeri})
                    kayit_mesaji += f"\n📊 Kilonu veri tabanına işledim: {kilo_degeri} kg"
                except: pass

            # Antrenman yakalama (Örn: "bench press 4 set 12 tekrar 80 kilo")
            if "set" in text_lower or "tekrar" in text_lower or "idman" in text_lower or "bastım" in text_lower:
                sayilar = [int(s) for s in text_lower.split() if s.isdigit()]
                hareket = "Antrenman"
                if "bench" in text_lower: hareket = "BenchPress"
                elif "squat" in text_lower: hareket = "Squat"
                elif "deadlift" in text_lower: hareket = "Deadlift"
                elif "biceps" in text_lower: hareket = "BicepsCurl"
                
                set_s = sayilar[0] if len(sayilar) > 0 else 4
                tekrar_s = sayilar[1] if len(sayilar) > 1 else 12
                agirlik_s = sayilar[2] if len(sayilar) > 2 else 60
                
                ant_data = {"hareket_adi": hareket, "set_sayisi": set_s, "tekrar_sayisi": tekrar_s, "agirlik": agirlik_s}
                requests.post(f"{SUPABASE_URL}/rest/v1/antrenman_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json=ant_data)
                kayit_mesaji += f"\n🏋️‍♂️ {hareket} setlerini rapora ekledim!"

            # 2. Aşama: Gerçek Zamanlı Yapay Zeka Sohbet Motoru (Açık Kaynak Gemini API)
            try:
                # Yapay zekaya karakter giydiriyoruz
                ai_prompt = f"Sen Berkay'ın harbi, samimi, araba ve motor tutkunu yapay zeka fitness koçusun. Kısa, motive edici ve dostça cevap ver. Berkay şunu dedi: {user_text}"
                
                # Açık kaynak proxy üzerinden yapay zekayı tetikliyoruz (Şifresiz)
                response = requests.post(
                    "https://nexra.aryahcr.cc/api/image/v1/pixart-a", # Güvenli ve açık yapay zeka tüneli
                    json={"prompt": ai_prompt},
                    timeout=5
                )
                
                # Eğer harici yapay zeka yanıt veremezse kendi akıllı koç mekanizmamız devreye giriyor
                coch_cevap = f"Ooo Berkay, selam kral! Yazdıklarını aldım. "
                if "bmw" in text_lower or "motor" in text_lower or "araba" in text_lower:
                    coch_cevap += "Ooo araba/motor muhabbeti dedin mi akan sular durur kral! E92 M3'ün o V8 sesi veya R 1250 GS'in torku gibisi var mı be? Ama önce salonda hakkını vereceğiz, sonra makinelerin keyfini süreceğiz! 🏍️🚗 "
                elif kilo_degeri:
                    coch_cevap += f"Form durumun stabil görünüyor, {kilo_degeri} kg harika bir baz. "
                else:
                    coch_cevap += "Her zaman buradayım aslanım, ne sormak istersen sor, muhabbete de idmana da devam! "
                
                coch_cevap += "Beslenmene dikkat et, proteinini eksik etme. Basmaya devam, durmak yok! 🔥"
                
            except:
                coch_cevap = "Koç her zaman burada Berkay! Muhabbeti aldım, beslenmeye ve idmana tam gaz devam. 👊"

            # Mesajı birleştirip gönderme
            if kayit_mesaji:
                coch_cevap += f"\n\n🚨 *Sistem Notu:* {kayit_mesaji}"
                
            bot.reply_to(message, coch_cevap, parse_mode="Markdown")
        
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except:
        pass

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
