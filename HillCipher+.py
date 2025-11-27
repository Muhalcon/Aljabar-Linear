# =======================================================================
# BAGIAN 1: FUNGSI UTILITAS
# =======================================================================

# Konversi dari karakter ke angka
def char_to_num(char):
  return ord(char.upper()) - ord('A')

# Konversi dari angka ke karakter
def num_to_char(num):
  return chr((num % 26) + ord('A'))

# =======================================================================
# BAGIAN 2: FUNGSI HILL CIPHER ENKRIPSI
# =======================================================================

# Membuat matriks 3x3 dari 9 karakter pertama string input key.
def generate_key_matrix(key_string):
  # Menghapus spasi dan mengubah menjadi huruf besar
  key_string = key_string.replace(" ", "").upper()
  if len(key_string) < 9:
    raise ValueError("Key harus memiliki minimal 9 karakter.")
  
  # Membuat matriks 3x3
  matrix = []
  iterator = 0
  for i in range(3):
    row = []
    for j in range(3):
      row.append(char_to_num(key_string[iterator]))
      iterator += 1
    matrix.append(row)
    
  # Mengembalikan matriks 3x3
  return matrix

# Melakukan perkalian matriks (3x3) dengan vektor teks (3x1) mod 26.
def vector_multiply(key_matrix, text_vector):
  # Melakukan perkalian matriks
  result_vector = []
  for i in range(3): 
    val = 0
    for j in range(3):
      val += key_matrix[i][j] * text_vector[j]
    result_vector.append(val % 26)
    
  # Mengembalikan vektor hasil
  return result_vector

# Fungsi utama enkripsi Hill Cipher.
def hill_encrypt(plaintext, key):
  # Menghapus spasi dan mengubah menjadi huruf besar
  plaintext = plaintext.replace(" ", "").upper()
    
  # Padding
  while len(plaintext) % 3 != 0:
    plaintext += "X"

  # Membuat Matriks Kunci
  try:
    key_matrix = generate_key_matrix(key)
  except ValueError as e:
    return str(e), None, None

  # Enkripsi
  ciphertext = ""
  for i in range(0, len(plaintext), 3):
    block = plaintext[i:i+3]
    text_vector = [char_to_num(c) for c in block]
    encrypted_vector = vector_multiply(key_matrix, text_vector)
    ciphertext += "".join([num_to_char(n) for n in encrypted_vector])
    
  # Menambahkan string ekstra
  extra_string = determinan_3x3_kofaktor(key_matrix, plaintext)
  ciphertext = append_extra_string(ciphertext, extra_string)

  # Mengembalikan Ciphertext dan Matriks Kunci
  return ciphertext, key_matrix

# Menambahkan string ekstra ke ciphertext
def append_extra_string(ciphertext, extra_string):
  return ciphertext + extra_string


# =======================================================================
# BAGIAN 3: FUNGSI DETERMINAN KHUSUS (Dinamis berdasarkan 3 Huruf Akhir)
# =======================================================================

# Menghitung determinan matriks 3x3 (mod 26) dan memodifikasinya
# berdasarkan jumlah bilangan genap dari 3 huruf terakhir (setelah padding).
def determinan_3x3_kofaktor(matriks, padded_plaintext):
  # Validasi ukuran
  if len(matriks) != 3 or any(len(baris) != 3 for baris in matriks):
    raise ValueError("Input harus berupa matriks ukuran 3x3.")
        
  # Perhitungan Determinan (Kofaktor)
  a, b, c = matriks[0][0], matriks[0][1], matriks[0][2]
  minor_a = (matriks[1][1] * matriks[2][2]) - (matriks[1][2] * matriks[2][1])
  minor_b = (matriks[1][0] * matriks[2][2]) - (matriks[1][2] * matriks[2][0])
  minor_c = (matriks[1][0] * matriks[2][1]) - (matriks[1][1] * matriks[2][0])
  det = (a * minor_a) - (b * minor_b) + (c * minor_c)
    
  # Modulo 26 awal
  det_mod_26 = (det % 26 + 26) % 26
      
  # Validasi 3 Huruf Terakhir
  if len(padded_plaintext) < 3:
    raise ValueError("Plaintext terlalu pendek untuk dianalisis 3 huruf terakhir.")
        
  # Ambil 3 huruf terakhir
  last_three_chars = padded_plaintext[-3:]
  
  # Ubah 3 huruf akhir menjadi nilai numerik
  last_three_nums = [char_to_num(c) for c in last_three_chars]
    
  # Hitung jumlah bilangan genap (Even) dari 3 nilai numerik tersebut
  total_genap = sum(1 for num in last_three_nums if num % 2 == 0)
    
  # Ambil karakter kedua (indeks 1) untuk string tambahan
  second_char = padded_plaintext[1].upper()
    
  # 3. Tentukan Operasi dan String
  hasil_modifikasi = det_mod_26
  string_tambahan = ""
  
  # Modifikasi String
  if total_genap <= 1:
    # Total Genap = 1 -> Penambahan (+)
    hasil_modifikasi += det_mod_26
    string_tambahan = f"R{second_char}N"
  elif total_genap == 2:
    # Total Genap = 2 -> Pengurangan (-)
    hasil_modifikasi -= det_mod_26 
    string_tambahan = f"QO{second_char}"
  elif total_genap >= 3:
    # Total Genap = 3 -> Perkalian (*)
    hasil_modifikasi *= det_mod_26 
    string_tambahan = f"{second_char}UT"
        
  # Modulo 26 akhir
  hasil_modifikasi = (hasil_modifikasi % 26 + 26) % 26
  
  # Menambahkan string ekstra  
  return string_tambahan

# =======================================================================
# BAGIAN 4: DEMO EKSEKUSI
# =======================================================================

if __name__ == "__main__":
  # Input
  input_text = input("Masukkan Plaintext: ")
  input_key = input("Masukkan Key (min 9 karakter): ")
    
  # Eksekusi
  ciphertext, key_matrix_list = hill_encrypt(input_text, input_key)
  
  # Output  
  if key_matrix_list is not None:
    print(f"Ciphertext: {ciphertext}")