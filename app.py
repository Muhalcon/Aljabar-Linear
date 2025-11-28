import streamlit as st
import HillCipher as hc  # Mengimpor backend logika

# =======================================================================
# KONFIGURASI TAMPILAN
# =======================================================================
st.set_page_config(
    page_title="Aplikasi Kriptografi Hill Cipher", 
    page_icon="🔐", 
    layout="wide"
)

st.title("🔐 Hill Cipher Sakti (Alphanumeric)")
st.markdown("""
**Sistem Enkripsi Hill Cipher dengan Auto-Healing Key**. 
Jika kunci yang Anda masukkan matematisnya salah, sistem akan memperbaikinya otomatis.
Mendukung angka (0-9) dan huruf (A-Z).
""")

# =======================================================================
# INPUT USER
# =======================================================================
with st.container():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🔑 Konfigurasi Kunci")
        key_input = st.text_input(
            "Masukkan Kunci Rahasia", 
            value="GYBNQKURP",
            help="Sistem akan otomatis memperbaiki jika kunci invalid."
        )
        st.caption("Kamus Data: 0-9 lalu A-Z (Mod 36)")
        
    with col2:
        st.subheader("📝 Pesan Teks")
        input_text = st.text_area(
            "Input Text", 
            height=100, 
            placeholder="Ketik Plaintext untuk Enkripsi, atau Ciphertext untuk Dekripsi..."
        )

# Session State Variables
if 'hasil_teks' not in st.session_state: st.session_state.hasil_teks = ""
if 'matrix_display' not in st.session_state: st.session_state.matrix_display = None
if 'log_info' not in st.session_state: st.session_state.log_info = ""

# =======================================================================
# TOMBOL EKSEKUSI
# =======================================================================
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🔒 ENKRIPSI PESAN", type="primary", use_container_width=True):
        if not key_input or not input_text:
            st.error("Harap isi Kunci dan Teks terlebih dahulu!")
        else:
            # Panggil fungsi backend
            # Menerima 5 variabel return
            hasil, mat, log, final_key, status = hc.proses_enkripsi(input_text, key_input)
            
            if "ERROR" in hasil:
                st.error(hasil)
            else:
                st.session_state.hasil_teks = hasil
                st.session_state.matrix_display = mat
                
                # Cek apakah terjadi Auto-Fix
                if status == "Otomatis":
                    st.warning("⚠️ PERHATIAN: Kunci awal Anda tidak valid secara matematika (Determinan genap/faktor 36).")
                    st.info(f"Sistem telah memperbaiki kunci Anda menjadi: **{final_key}**")
                    st.success("Enkripsi berhasil dilakukan dengan KUNCI BARU di atas. Harap simpan kunci baru tersebut.")
                    st.session_state.log_info = f"Operasi Twist: {log} | Kunci: Diperbaiki Otomatis"
                else:
                    st.success("Enkripsi Berhasil!")
                    st.session_state.log_info = f"Operasi Twist: {log}"

with col_btn2:
    if st.button("🔓 DEKRIPSI PESAN", use_container_width=True):
        if not key_input or not input_text:
            st.error("Harap isi Kunci dan Teks terlebih dahulu!")
        else:
            # Panggil fungsi backend
            hasil, mat = hc.proses_dekripsi(input_text, key_input)
            
            if hasil and "ERROR" in hasil:
                st.error(hasil)
            else:
                st.session_state.hasil_teks = hasil
                st.session_state.matrix_display = mat
                st.session_state.log_info = "Dekripsi Sukses."
                st.success("Pesan berhasil dikembalikan ke aslinya.")

# =======================================================================
# OUTPUT DAN VISUALISASI
# =======================================================================
st.divider()

col_out1, col_out2 = st.columns([2, 1])

with col_out1:
    st.subheader("📄 Hasil Akhir")
    st.text_area("Output Data:", value=st.session_state.hasil_teks, height=150)
    if st.session_state.log_info:
        st.caption(f"Info Sistem: {st.session_state.log_info}")

with col_out2:
    st.subheader("🧮 Matriks Kunci")
    if st.session_state.matrix_display:
        mat = st.session_state.matrix_display
        det = hc.get_determinant(mat)
        
        st.table(mat)
        st.metric(label="Determinan (Mod 36)", value=det)
    else:
        st.text("Matriks akan muncul di sini.")