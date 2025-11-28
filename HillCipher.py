import math

# =======================================================================
# KONFIGURASI GLOBAL
# =======================================================================
VOCAB = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MOD = len(VOCAB)  # 36

# =======================================================================
# BAGIAN 1: FUNGSI UTILITAS & MATEMATIKA
# =======================================================================

def char_to_num(char):
    char = char.upper()
    if char in VOCAB:
        return VOCAB.index(char)
    return 0

def num_to_char(num):
    return VOCAB[num % MOD]

def mod_inverse(a, m):
    try:
        return pow(a, -1, m)
    except ValueError:
        return None 

def get_determinant(m):
    a, b, c = m[0][0], m[0][1], m[0][2]
    minor_a = (m[1][1] * m[2][2]) - (m[1][2] * m[2][1])
    minor_b = (m[1][0] * m[2][2]) - (m[1][2] * m[2][0])
    minor_c = (m[1][0] * m[2][1]) - (m[1][1] * m[2][0])
    det = (a * minor_a) - (b * minor_b) + (c * minor_c)
    return (det % MOD + MOD) % MOD

def get_matrix_inverse(m):
    det = get_determinant(m)
    inv_det = mod_inverse(det, MOD)
    if inv_det is None: return None

    adj = [[0]*3 for _ in range(3)]
    adj[0][0] =  ((m[1][1]*m[2][2]) - (m[1][2]*m[2][1]))
    adj[0][1] = -((m[1][0]*m[2][2]) - (m[1][2]*m[2][0]))
    adj[0][2] =  ((m[1][0]*m[2][1]) - (m[1][1]*m[2][0]))
    adj[1][0] = -((m[0][1]*m[2][2]) - (m[0][2]*m[2][1]))
    adj[1][1] =  ((m[0][0]*m[2][2]) - (m[0][2]*m[2][0]))
    adj[1][2] = -((m[0][0]*m[2][1]) - (m[0][1]*m[2][0]))
    adj[2][0] =  ((m[0][1]*m[1][2]) - (m[0][2]*m[1][1]))
    adj[2][1] = -((m[0][0]*m[1][2]) - (m[0][2]*m[1][0]))
    adj[2][2] =  ((m[0][0]*m[1][1]) - (m[0][1]*m[1][0]))

    inv_matrix = []
    for r in range(3):
        row = []
        for c in range(3):
            val = (adj[c][r] * inv_det) % MOD
            row.append(val)
        inv_matrix.append(row)
    return inv_matrix

def generate_key_matrix(key_string):
    clean_key = "".join([c for c in key_string.upper() if c in VOCAB])
    while len(clean_key) < 9: clean_key += "0"
    
    matrix = []
    iterator = 0
    for i in range(3):
        row = []
        for j in range(3):
            row.append(char_to_num(clean_key[iterator]))
            iterator += 1
        matrix.append(row)
    return matrix, clean_key

def matrix_to_string(matrix):
    res = ""
    for r in range(3):
        for c in range(3):
            res += num_to_char(matrix[r][c])
    return res

# --- BAGIAN INI YANG HILANG DARI KODE ANDA ---
def fix_matrix_logic(matrix):
    """
    Fungsi 'Auto-Heal' Cerdas:
    Mencoba memperbaiki matriks dengan mengubah elemen diagonal.
    Jika mengubah pojok kanan bawah (m[2][2]) mentok, 
    coba ubah tengah (m[1][1]), lalu pojok kiri atas (m[0][0]).
    """
    # Tahap 1: Coba ubah elemen pojok kanan bawah
    for _ in range(37):
        if math.gcd(get_determinant(matrix), MOD) == 1:
            return matrix
        matrix[2][2] = (matrix[2][2] + 1) % MOD

    # Tahap 2: Jika masih gagal, ubah elemen tengah
    for _ in range(37):
        if math.gcd(get_determinant(matrix), MOD) == 1:
            return matrix
        matrix[1][1] = (matrix[1][1] + 1) % MOD

    # Tahap 3: Opsi terakhir, ubah elemen awal
    for _ in range(37):
        if math.gcd(get_determinant(matrix), MOD) == 1:
            return matrix
        matrix[0][0] = (matrix[0][0] + 1) % MOD

    return None 
# --------------------------------------------

# =======================================================================
# BAGIAN 2: LOGIKA ENKRIPSI & DEKRIPSI
# =======================================================================

def proses_enkripsi(plaintext, key):
    # 1. Validasi Input
    clean_text = "".join([c for c in plaintext.upper() if c in VOCAB])
    
    if not clean_text: 
        return "ERROR: Plaintext kosong atau karakter tidak valid.", None, None, key, "Error"
    
    while len(clean_text) % 3 != 0: 
        clean_text += "0"
    
    # 2. Persiapan Kunci & AUTO-FIX
    key_matrix, clean_key = generate_key_matrix(key)
    det = get_determinant(key_matrix)
    
    status_msg = "Normal"
    final_used_key = clean_key

    if math.gcd(det, MOD) != 1:
        # Panggil fungsi fix yang sudah didefinisikan di atas
        key_matrix = fix_matrix_logic(key_matrix)
        
        if key_matrix is None:
            return "ERROR: Gagal memperbaiki kunci secara otomatis.", None, None, key, "Error"
        
        final_used_key = matrix_to_string(key_matrix)
        det = get_determinant(key_matrix)
        status_msg = "Otomatis"

    # 3. Hill Cipher Core
    hill_results = []
    for i in range(0, len(clean_text), 3):
        vec = [char_to_num(c) for c in clean_text[i:i+3]]
        res_vec = [0, 0, 0]
        for r in range(3):
            for c in range(3):
                res_vec[r] += key_matrix[r][c] * vec[c]
            res_vec[r] %= MOD
        hill_results.extend(res_vec)

    # 4. Analisis 3 Karakter Terakhir (Twist)
    last_3_nums = [char_to_num(c) for c in clean_text[-3:]]
    total_genap = sum(1 for n in last_3_nums if n % 2 == 0)

    # 5. Modifikasi Hasil
    final_nums = []
    flag = ''
    log_operasi = ""
    
    if total_genap <= 1:
        final_nums = [(n + det) % MOD for n in hill_results]
        flag = 'A'
        log_operasi = f"Penambahan (+{det})"
    elif total_genap == 2:
        final_nums = [(n - det) % MOD for n in hill_results]
        flag = 'S'
        log_operasi = f"Pengurangan (-{det})"
    elif total_genap >= 3:
        final_nums = [(n * det) % MOD for n in hill_results]
        flag = 'M'
        log_operasi = f"Perkalian (x{det})"

    ciphertext = "".join([num_to_char(n) for n in final_nums]) + flag
    
    # Return 5 values: Hasil, Matriks, Log Info, Kunci Akhir, Status
    return ciphertext, key_matrix, log_operasi, final_used_key, status_msg


def proses_dekripsi(ciphertext, key):
    clean_cipher = ciphertext.replace(" ", "").upper()
    if len(clean_cipher) < 2: 
        return "ERROR: Ciphertext terlalu pendek.", None

    flag = clean_cipher[-1]
    actual_cipher = clean_cipher[:-1]

    key_matrix, _ = generate_key_matrix(key)
    det = get_determinant(key_matrix)
    inv_matrix = get_matrix_inverse(key_matrix)

    if inv_matrix is None:
        return "ERROR: Matriks Kunci tidak valid. Gunakan kunci hasil Auto-Fix.", key_matrix

    cipher_nums = [char_to_num(c) for c in actual_cipher]
    processed_nums = []

    if flag == 'A':
        processed_nums = [(n - det) % MOD for n in cipher_nums]
    elif flag == 'S':
        processed_nums = [(n + det) % MOD for n in cipher_nums]
    elif flag == 'M':
        inv_det = mod_inverse(det, MOD)
        if inv_det is None: return "ERROR: Gagal mendekripsi operasi perkalian.", key_matrix
        processed_nums = [(n * inv_det) % MOD for n in cipher_nums]
    else:
        return "ERROR: Flag tidak dikenal.", key_matrix

    plaintext = ""
    for i in range(0, len(processed_nums), 3):
        vec = processed_nums[i:i+3]
        res_vec = [0, 0, 0]
        for r in range(3):
            for c in range(3):
                res_vec[r] += inv_matrix[r][c] * vec[c]
            res_vec[r] %= MOD
        plaintext += "".join([num_to_char(n) for n in res_vec])
    
    plaintext = plaintext.rstrip('0')
    return plaintext, key_matrix