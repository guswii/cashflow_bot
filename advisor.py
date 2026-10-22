def get_smart_feedback(data: dict) -> str:
    """
    Memberikan feedback cerdas dan saran finansial berdasarkan transaksi yang baru dicatat.
    """
    tipe = data.get("tipe")
    nominal = data.get("nominal", 0)
    kategori = data.get("kategori", "Lain-lain")

    if tipe == "Pemasukan":
        if nominal >= 1000000:
            return "🎉 Mantap! Pemasukan cukup besar. Jangan lupa sisihkan minimal 20-30% untuk tabungan/dana darurat ya!"
        elif nominal >= 200000:
            return "💰 Rezeki masuk! Tetap pertahankan cashflow positif."
        else:
            return "✨ Pemasukan tercatat. Setiap rupiah tetap berarti!"

    # Evaluasi Pengeluaran
    if kategori == "Makanan & Minuman":
        if nominal > 100000:
            return "🍔 Pengeluaran makan cukup tinggi nih hari ini. Pertimbangkan untuk masak atau cari opsi lebih hemat besok ya."
        else:
            return "🍽️ Pengeluaran makan masih dalam batas wajar sehari-hari."
    elif kategori == "Hiburan & Langganan":
        return "🎮 Hiburan penting buat refreshing, tapi pastikan jatah pos hiburan bulan ini tidak overbudget ya!"
    elif kategori == "Transportasi":
        return "🚗 Kebutuhan mobilitas tercatat. Aman!"
    elif kategori == "Pendidikan / Kuliah":
        return "📚 Investasi untuk ilmu dan kuliah selalu bernilai baik. Semangat belajarnya!"
    else:
        if nominal > 250000:
            return "⚠️ Pengeluaran di atas Rp 250.000. Pastikan ini pengeluaran yang terencana ya."
        return "✅ Catatan tersimpan dengan rapi."
