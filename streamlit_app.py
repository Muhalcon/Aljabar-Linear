import streamlit as st

st.set_page_config(page_title="Hill Cipher Plus", page_icon="🔐", layout="centered")

st.title("🔐 Hill Cipher +++")
st.caption("4 input string, 2 tombol (Encrypt/Decrypt), 2 output.")

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def char_to_num(char):
    return ord(char.upper()) - ord('A')

def num_to_char(num):
    return chr((num % 26) + ord('A'))

def generate_key_matrix(key_string):
    key_string = key_string.replace(" ", "").upper()
    if len(key_string) < 9:
        raise ValueError("Key harus memiliki minimal 9 karakter.")
    matrix = []
    iterator = 0
    for i in range(3):
        row = []
        for j in range(3):
            row.append(char_to_num(key_string[iterator]))
            iterator += 1
        matrix.append(row)
    return matrix

def vector_multiply(key_matrix, text_vector):
    result_vector = []
    for i in range(3):
        val = 0
        for j in range(3):
            val += key_matrix[i][j] * text_vector[j]
        result_vector.append(val % 26)
    return result_vector

def determinan_3x3_kofaktor(matriks, padded_plaintext):
    if len(matriks) != 3 or any(len(baris) != 3 for baris in matriks):
        raise ValueError("Input harus berupa matriks ukuran 3x3.")
    a, b, c = matriks[0][0], matriks[0][1], matriks[0][2]
    minor_a = (matriks[1][1] * matriks[2][2]) - (matriks[1][2] * matriks[2][1])
    minor_b = (matriks[1][0] * matriks[2][2]) - (matriks[1][2] * matriks[2][0])
    minor_c = (matriks[1][0] * matriks[2][1]) - (matriks[1][1] * matriks[2][0])
    det = (a * minor_a) - (b * minor_b) + (c * minor_c)
    det_mod_26 = (det % 26 + 26) % 26
    if len(padded_plaintext) < 3:
        raise ValueError("Plaintext terlalu pendek untuk dianalisis 3 huruf terakhir.")
    last_three_chars = padded_plaintext[-3:]
    last_three_nums = [char_to_num(c) for c in last_three_chars]
    total_genap = sum(1 for num in last_three_nums if num % 2 == 0)
    second_char = padded_plaintext[1].upper() if len(padded_plaintext) > 1 else 'A'
    if total_genap <= 1:
        return f"R{second_char}N"
    elif total_genap == 2:
        return f"QO{second_char}"
    else:
        return f"{second_char}UT"

def hill_encrypt_plus(plaintext: str, key: str, padding_char: str = "X"):
    pt = plaintext.replace(" ", "").upper()
    if not pt:
        return "", None
    if not padding_char or len(padding_char) != 1 or not padding_char.isalpha():
        padding_char = "X"
    while len(pt) % 3 != 0:
        pt += padding_char.upper()
    try:
        key_matrix = generate_key_matrix(key)
    except ValueError as e:
        return f"Error: {e}", None
    ct = ""
    for i in range(0, len(pt), 3):
        block = pt[i:i+3]
        vec = [char_to_num(c) for c in block]
        enc_vec = vector_multiply(key_matrix, vec)
        ct += "".join(num_to_char(n) for n in enc_vec)
    extra = determinan_3x3_kofaktor(key_matrix, pt)
    return ct + extra, key_matrix

def _matrix_inverse_mod_26(mat):
    a,b,c = mat[0]
    d,e,f = mat[1]
    g,h,i = mat[2]
    det = (a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g))
    det_mod = det % 26
    def egcd(a,b):
        if a==0: return b,0,1
        g,y,x = egcd(b%a,a)
        return g, x - (b//a)*y, y
    def modinv(a,m=26):
        a%=m
        g,x,_ = egcd(a,m)
        if g!=1:
            raise ValueError("Determinant tidak invertible mod 26")
        return x % m
    inv_det = modinv(det_mod)
    cof = [
        [(e*i - f*h), -(d*i - f*g), (d*h - e*g)],
        [-(b*i - c*h), (a*i - c*g), -(a*h - b*g)],
        [(b*f - c*e), -(a*f - c*d), (a*e - b*d)]
    ]
    adj = [[cof[r][c] for r in range(3)] for c in range(3)]
    inv = [[(adj[r][c] * inv_det) % 26 for c in range(3)] for r in range(3)]
    return inv

def hill_decrypt_plus(ciphertext: str, key: str):
    ct = ciphertext.replace(" ", "").upper()
    if len(ct) < 6:
        return "", None
    core = ct[:-3]
    try:
        key_matrix = generate_key_matrix(key)
    except ValueError as e:
        return f"Error: {e}", None
    try:
        inv_key = _matrix_inverse_mod_26(key_matrix)
    except ValueError as e:
        return f"Error: {e}", key_matrix
    if len(core) % 3 != 0:
        return "Error: panjang ciphertext inti tidak kelipatan 3", key_matrix
    pt_nums = []
    for i in range(0, len(core), 3):
        block = core[i:i+3]
        vec = [char_to_num(c) for c in block]
        dec_vec = []
        for r in range(3):
            val = 0
            for c in range(3):
                val += inv_key[r][c] * vec[c]
            dec_vec.append(val % 26)
        pt_nums.extend(dec_vec)
    plaintext = "".join(num_to_char(n) for n in pt_nums)
    plaintext = plaintext.rstrip('X')
    return plaintext, key_matrix

# ========================= INPUTS =========================
colA, colB = st.columns(2)
with colA:
    key_input = st.text_input("Key (min 9 huruf)")
    padding_char = st.text_input("Padding Character", value="X", max_chars=1)
with colB:
    plaintext_input = st.text_area("Plaintext (Encrypt)", height=150)
    ciphertext_input = st.text_area("Ciphertext (Decrypt)", height=150)

if 'encrypt_result' not in st.session_state:
    st.session_state.encrypt_result = ""
if 'decrypt_result' not in st.session_state:
    st.session_state.decrypt_result = ""
if 'key_matrix' not in st.session_state:
    st.session_state.key_matrix = None

colE, colD = st.columns(2)
with colE:
    if st.button("Encrypt"):
        if not key_input:
            st.error("Masukkan key.")
        else:
            enc, km = hill_encrypt_plus(plaintext_input, key_input, padding_char)
            st.session_state.encrypt_result = enc
            st.session_state.key_matrix = km
with colD:
    if st.button("Decrypt"):
        if not key_input:
            st.error("Masukkan key.")
        else:
            dec, km = hill_decrypt_plus(ciphertext_input, key_input)
            st.session_state.decrypt_result = dec
            st.session_state.key_matrix = km if km else st.session_state.key_matrix

# ========================= OUTPUTS =========================
st.subheader("Hasil")
colR1, colR2 = st.columns(2)
with colR1:
    st.text_area("Ciphertext (Output)", value=st.session_state.encrypt_result, height=150)
    if st.session_state.encrypt_result:
        st.download_button("Download Ciphertext", st.session_state.encrypt_result, file_name="ciphertext.txt")
with colR2:
    st.text_area("Plaintext (Output)", value=st.session_state.decrypt_result, height=150)
    if st.session_state.decrypt_result:
        st.download_button("Download Plaintext", st.session_state.decrypt_result, file_name="plaintext.txt")

if st.session_state.key_matrix:
    st.markdown("### Key Matrix")
    st.table(st.session_state.key_matrix)
