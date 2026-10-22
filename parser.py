import re
from datetime import datetime

# Daftar kata kunci kategori
CATEGORY_KEYWORDS = {
    "Makanan & Minuman": ["makan", "nasi", "kopi", "cafe", "mie", "minum", "jajan", "snack", "sarapan", "lunch", "dinner", "ayam", "bakso", "gorengan"],
    "Transportasi": ["bensin", "pertalite", "pertamax", "gojek", "grab", "maxim", "parkir", "tol", "angkot", "bus", "service motor", "oli"],
    "Belanja / Kebutuhan": ["sabun", "shampoo", "odol", "indomaret", "alfamart", "skincare", "baju", "celana", "laundry", "listrik", "pulsa", "kuota", "wifi"],
    "Pendidikan / Kuliah": ["buku", "fotocopy", "print", "spp", "instiki", "kursus", "seminar", "alat tulis"],
    "Hiburan & Langganan": ["spotify", "netflix", "youtube", "game", "steam", "nonton", "bioskop", "topup"],
    "Pemasukan": ["gaji", "transfer", "dapat uang", "uang saku", "freelance", "kiriman", "jual", "bonus", "hadiah"]
}

def parse_transaction(text: str) -> dict:
    """
    Ekstrak tipe (pemasukan/pengeluaran), nominal, kategori, dan deskripsi dari teks natural.
    Contoh: 'makan siang nasi padang 25rb' -> {tipe: 'Pengeluaran', nominal: 25000, kategori: 'Makanan & Minuman', keterangan: 'makan siang nasi padang'}
    """
    raw_text = text.strip()
    lower_text = raw_text.lower()

    # 1. Deteksi Nominal
    # Pola: 25rb, 25k, 25.000, 25000, 2.5jt, dll.
    nominal = 0
    nominal_pattern = r'(\d+(?:[.,]\d+)?)\s*(rb|k|ribu|jt|juta)?\b'
    match = re.search(nominal_pattern, lower_text)

    if match:
        num_str = match.group(1).replace(',', '.')
        multiplier_str = match.group(2)
        try:
            val = float(num_str)
            if multiplier_str in ['rb', 'k', 'ribu']:
                val *= 1000
            elif multiplier_str in ['jt', 'juta']:
                val *= 1000000
            elif '.' in match.group(1) and not multiplier_str:
                # Menangani pemisah ribuan standar Indonesia misal 25.000
                val = float(match.group(1).replace('.', ''))
            nominal = int(val)
        except ValueError:
            nominal = 0

    # 2. Deteksi Tipe (Pemasukan vs Pengeluaran)
    income_indicators = ["gaji", "dapat", "transfer masuk", "kiriman", "terima", "uang saku", "freelance", "bonus", "pemasukan", "masuk"]
    is_income = any(word in lower_text for word in income_indicators)
    tipe = "Pemasukan" if is_income else "Pengeluaran"

    # 3. Deteksi Kategori
    kategori = "Lain-lain"
    if is_income:
        kategori = "Pemasukan"
    else:
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if cat == "Pemasukan":
                continue
            if any(kw in lower_text for kw in keywords):
                kategori = cat
                break

    # 4. Keterangan / Deskripsi (bersihkan teks nominal agar rapi)
    clean_desc = re.sub(nominal_pattern, '', raw_text).strip()
    clean_desc = re.sub(r'\s+', ' ', clean_desc)
    if not clean_desc:
        clean_desc = raw_text

    # 5. Format Tanggal
    now = datetime.now()
    tanggal_str = now.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "tanggal": tanggal_str,
        "tipe": tipe,
        "kategori": kategori,
        "nominal": nominal,
        "keterangan": clean_desc,
        "original_text": raw_text
    }
