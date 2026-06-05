import streamlit as st
import datetime
import requests
import pandas as pd
import telebot
from threading import Thread
import google.generativeai as genai
import json
import re

# Şifreler ve Ayarlar
TOKEN = "8967109165:AAH7BdP28D7UHVZ7TcuS8szYuae3yctNutM"
SUPABASE_URL = "https://cyienwazvmnlbxsondwq.supabase.co"
SUPABASE_KEY = "sb_publishable_kNTUKDuw29M43goDPsFzcw_W7Y4EvFL"
GEMINI_KEY = "AQ.Ab8RN6I3gJDC9O7zcPLv2Bjx-QslZceTh6YkdmbechU7do2v1Q" # Senin gönderdiğin anahtar

# Yapay Zeka Kurulumu
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --- TELEGRAM BOT KISMI (YAPAY ZEKA ENTEGRELİ) ---
def botu_baslat():
    try:
        bot = telebot.TeleBot(TOKEN)

        @bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            hosgeldin = (
                "💪 Berkay! Yapay Zeka Fitness Koçun göreve hazır.\n\n"
                "Artık bota komut yazmak zorunda değilsin! Benimle tıpkı gerçek bir koç gibi normal cümlelerle konuşabilirsin.\n\n"
                "Örnek: 'Koç bugün tartıldım 80 kiloyum, sonra salonda 4 set 12 tekrar 60 kilo bench bastım, üstüne 20 dk koştum' yaz, gerisini bana bırak!"
            )
            bot.reply_to(message, hosgeldin)

        @bot.message_handler(func=lambda message: True)
        def handle_ai_message(message):
            user_text = message.text
            
            # Yapay zekaya veriyi ayıklaması ve cevap vermesi için talimat veriyoruz
            prompt = f"""
            Sen Berkay'ın kişisel fitness ve bodybuilding koçusun. Samimi, motive edici, hafif sert ve profesyonel bir üslubun var.
            Berkay sana bir mesaj gönderdi. Bu mesajdan eğer varsa antrenman, kilo veya kardiyo verilerini ayıklaman gerekiyor.
            
            Kullanıcının Mesajı: "{user_text}"
            
            GÖREV 1: Mesajın içindeki fitness verilerini SADECE aşağıdaki JSON formatında çıkar. Eğer veri yoksa boş bırak (null veya []).
            {{
                "kilo": null veya sayı (örn: 82.5),
                "kardiyo": null veya {{ "tur": "Kosu", "sure": 20, "kalori": 250 }},
                "antrenman": null veya [ {{ "hareket_adi": "BenchPress", "set_sayisi": 4, "tekrar_sayisi": 10, "agirlik": 80 }} ]
            }}
            Not: JSON formatında asla Türkçe karakter barındırma (KosuBandi, Squat vb. yap).
            
            GÖREV 2: Berkay'a bir fitness koçu gibi samimi, motive edici ve sorduğu soruları yanıtlayan bir cevap yaz.
            
            ÇIKTI FORMATI: Aşağıdaki şablonu BİREBİR koru. JSON ve CEVAP arasına '---' koy.
            
            JSON:
            (Buraya sadece oluşturduğun JSON gelecek)
            ---
            CEVAP:
            (Buraya Berkay'a vereceğin koçluk cevabı gelecek)
            """
            
            try:
                response = model.generate_content(prompt)
                ai_output = response.text
                
                # Çıktıyı parçala
                parcalar = ai_output.split("---")
                json_part = parcalar[0].replace("JSON:", "").strip()
                cevap_part = parcalar[1].replace("CEVAP:", "").strip()
                
                # Veritabanına kaydetme işlemleri
                data_json = json.loads(json_part)
                kayit_mesaji = ""
                
                # Kilo Kaydı
                if data_json.get("kilo"):
                    k_data = {"kilo": float(data_json["kilo"])}
                    requests.post(f"{SUPABASE_URL}/rest/v1/kilo_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json=k_data)
                    kayit_mesaji += f"\n📊 Kilo kaydedildi: {data_json['kilo']} kg"
                    
                # Kardiyo Kaydı
                if data_json.get("kardiyo"):
                    kard_data = data_json["kardiyo"]
                    requests.post(f"{SUPABASE_URL}/rest/v1/kardiyo_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json=kard_data)
                    kayit_mesaji += f"\n🏃‍♂️ Kardiyo kaydedildi: {kard_data['tur']}"
                    
                # Antrenman Kaydı
                if data_json.get("antrenman"):
                    for ant in data_json["antrenman"]:
                        requests.post(f"{SUPABASE_URL}/rest/v1/antrenman_takip", headers={**HEADERS, "Prefer": "return=minimal"}, json=ant)
                    kayit_mesaji += f"\n🏋️‍♂️ Antrenman logları veri tabanına işlendi!"

                # Sonucu kullanıcıya gönder
                tam_cevap = cevap_part
                if kayit_mesaji:
                    tam_cevap += f"\n\n🚨 *Sistem Notu:* {kayit_mesaji}"
                    
                bot.reply_to(message, tam_cevap, parse_mode="Markdown")
                
            except Exception as e:
                bot.reply_to(message, "Koç şu an yoğun, birazdan tekrar dener misin? (Sistem veya şifre hatası oluştu.)")

        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except:
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



