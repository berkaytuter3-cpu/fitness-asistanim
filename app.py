import streamlit as st
import datetime
import requests
import pandas as pd

SUPABASE_URL = "https://cyienwazvmnlbxsondwq.supabase.co"
SUPABASE_KEY = "sb_publishable_kNTUKDuw29M43goDPsFzcw_W7Y4EvFL"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

st.set_page_config(page_title="Fitness Asistanım", page_icon="💪", layout="wide")
st.title("💪 Kişisel Fitness Takip Paneli")
st.write("---")

def veri_cek(tablo_adi):
    res = requests.get(f"{SUPABASE_URL}/rest/v1/{tablo_adi}?order=id.desc", headers=HEADERS)
    if res.status_code == 200:
        return pd.DataFrame(res.json())
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

