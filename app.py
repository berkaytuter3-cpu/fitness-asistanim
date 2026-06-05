import streamlit as st
import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Fitness Asistanım", page_icon="💪", layout="wide")

st.title("💪 Kişisel Fitness Takip Paneli")
st.markdown("Fitness hayatını düzene sokacak kişisel merkezin.")
st.write("---")

st.sidebar.header("👤 Profilim")
st.sidebar.info("Veri tabanı bağlandığında anlık kilonuz burada görünecek.")

sekme1, sekme2, sekme3, sekme4 = st.tabs([
    "🏋️‍♂️ Antrenman & Tekrar", "🏃‍♂️ Kardiyo", "🍎 Beslenme", "📈 Kilo Takibi"
])

with sekme1:
    st.header("Bugünkü Antrenman Durumu")
    hareket = st.text_input("Egzersiz Adı (Örn: Squat)", placeholder="Egzersiz yaz...")
    col1, col2 = st.columns(2)
    with col1:
        set_sayisi = st.number_input("Set Sayısı", min_value=1, value=4)
    with col2:
        tekrar_sayisi = st.number_input("Tekrar Sayısı", min_value=1, value=10)
    agirlik = st.number_input("Ağırlık (kg)", min_value=0.0, value=60.0)
    if st.button("Antrenmanı Kaydet"):
        st.success(f"{hareket} kaydedildi!")

with sekme2:
    st.header("Kardiyo Seansı Ekle")
    kardiyo_tipi = st.selectbox("Kardiyo Türü", ["Koşu Bandı", "Bisiklet", "Elliptical", "Yürüyüş"])
    sure = st.number_input("Süre (Dakika)", min_value=1, value=20)
    if st.button("Kardiyoyu Kaydet"):
        st.success(f"{kardiyo_tipi} başarıyla eklendi!")

with sekme3:
    st.header("Günlük Beslenme ve Makrolar")
    kalori = st.number_input("Alınan Kalori (kcal)", min_value=0, value=2000)
    if st.button("Beslenmeyi Kaydet"):
        st.success("Beslenme verileri kaydedildi!")

with sekme4:
    st.header("Kilo ve Gelişim Takibi")
    guncel_kilo = st.number_input("Bugünkü Kilonuz (kg)", min_value=30.0, value=75.0)
    if st.button("Kiloyu Kaydet"):
        st.success(f"Kilo kaydedildi!")
