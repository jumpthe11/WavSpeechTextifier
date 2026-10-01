import streamlit as st
import os
import tkinter as tk
from tkinter import filedialog
from voiceline_renamer import process_audio_files
from transcribers import PROVIDERS

# Streamlit sayfa ayarları
st.set_page_config(page_title="WavSpeechTextifier", page_icon="🎙️", layout="centered")

def select_folder():
    """Tkinter kullanarak klasör seçme penceresi açar."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title="Ses Dosyalarının Bulunduğu Klasörü Seçin")
    root.destroy()
    return folder_path

# CSS ile özel tasarım
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
    }
    .success-text {
        color: #00cc66;
    }
    .error-text {
        color: #ff4c4c;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ WavSpeechTextifier")
st.markdown("Yapay zeka (Whisper) kullanarak **.wav** ses dosyalarınızı otomatik olarak dinler ve metne dönüştürerek yeniden adlandırır.")

# Durum yönetimi (State)
if 'folder_path' not in st.session_state:
    st.session_state.folder_path = ""
if 'logs' not in st.session_state:
    st.session_state.logs = []

# Klasör Seçimi
st.subheader("1. Klasör Seçimi")
col1, col2 = st.columns([3, 1])
with col1:
    folder_input = st.text_input("Klasör Yolu:", value=st.session_state.folder_path, placeholder="Örn: C:\\Sesler\\Karakter1")
with col2:
    st.markdown("<br>", unsafe_allow_html=True) # Boşluk
    if st.button("📁 Gözat"):
        selected = select_folder()
        if selected:
            st.session_state.folder_path = selected
            st.rerun()

# Klasör yolu input'tan manuel olarak da değiştirilebilir
st.session_state.folder_path = folder_input

# Ayarlar
st.subheader("2. Ayarlar")
col3, col4 = st.columns(2)

with col3:
    provider = st.selectbox("Sağlayıcı (Provider):", options=list(PROVIDERS.keys()), index=0)
    device = st.selectbox("İşlemci (Device):", options=["cpu", "cuda"], index=0, help="Ekran kartı kullanmak için cuda seçin (CUDA yüklüyse).")

with col4:
    model_name = st.selectbox("Model:", options=["tiny.en", "small.en", "medium.en", "large-v3", "tiny", "small", "medium", "large"], index=1, help="İngilizce için .en modelleri daha iyi ve hızlıdır.")
    language = st.text_input("Dil Kodu:", value="en", help="İngilizce için 'en', Türkçe için 'tr' yazın.")

max_length = st.slider("Maksimum Dosya Adı Uzunluğu:", min_value=10, max_value=150, value=80)

# İşlem Başlatma
st.subheader("3. İşlemi Başlat")

start_button = st.button("🚀 Sesleri Metne Çevir ve Yeniden Adlandır", type="primary")

progress_bar = st.progress(0)
status_text = st.empty()
log_container = st.empty()

if start_button:
    if not st.session_state.folder_path or not os.path.isdir(st.session_state.folder_path):
        st.error("Lütfen geçerli bir klasör yolu seçin!")
    else:
        st.session_state.logs = [] # Logları temizle
        
        success_count = [0]
        
        def progress_callback(current, total, original_name, new_name, status):
            progress = int((current / total) * 100)
            progress_bar.progress(progress)
            status_text.text(f"İşleniyor: {current}/{total} ({progress}%)")
            
            if status == "success":
                log_msg = f"✅ `{original_name}` -> `{new_name}`"
                success_count[0] += 1
            else:
                log_msg = f"❌ `{original_name}` hatası: {status}"
                
            st.session_state.logs.append(log_msg)
            
            # Logları son 15 satırı gösterecek şekilde güncelle
            log_container.markdown("\n".join(st.session_state.logs[-15:]))

        with st.spinner("Modeller yükleniyor ve işlem başlatılıyor... (Bu biraz sürebilir)"):
            try:
                process_audio_files(
                    directory_path=st.session_state.folder_path,
                    provider=provider,
                    model_name=model_name,
                    language=language,
                    device=device,
                    max_length=max_length,
                    progress_callback=progress_callback
                )
                
                if success_count[0] > 0:
                    st.success(f"🎉 İşlem tamamlandı! {success_count[0]} dosya başarıyla yeniden adlandırıldı.")
                    st.balloons()
                else:
                    st.error("Hiçbir dosya başarıyla işlenemedi. Lütfen hataları kontrol edin.")
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")
