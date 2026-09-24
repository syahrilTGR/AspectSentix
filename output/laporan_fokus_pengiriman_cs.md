# Laporan Analisis Sentimen Ulasan — Fokus: Pengiriman & Layanan Pelanggan

## 1. Distribusi Sentimen per Aspek

| Aspek | Positif | Negatif | Netral | Total |
|---|---|---|---|---|
| Shipping | 13 | 12 | 0 | 25 |
| CS Service | 8 | 4 | 0 | 12 |
| Packaging | 7 | 1 | 0 | 8 |
| Product Quality | 20 | 24 | 2 | 46 |
| Authenticity | 5 | 13 | 0 | 18 |
| Performance | 2 | 4 | 0 | 6 |
| Price | 4 | 1 | 1 | 6 |
| Battery | 0 | 2 | 0 | 2 |
| Warranty | 0 | 1 | 1 | 2 |
| **Total** | **59** | **62** | **4** | **125** |

*Total pasangan (ulasan, aspek) = 125 baris.*

**Sorotan aspek fokus:**
- **Shipping (25 pasangan):** hampir seimbang — 13 positif vs 12 negatif. Masalah utama: keterlambatan pengiriman dan order dibatalkan sepihak.
- **CS Service (12 pasangan):** mayoritas positif (8), namun keluhan negatif menyangkut respons lambat dan ketidaksesuaian pesanan.

---

## 2. Tiga Kekuatan Utama Produk

1. **Pengiriman cepat & tepat waktu** — banyak ulasan memuji kecepatan kirim (ulasan 4, 6, 36, 46, 73).
2. **Keramahan kurir & respons seller** — kurir dinilai ramah dan seller responsif (ulasan 6, 24, 32, 39, 76).
3. **Kemasan aman saat pengiriman** — packing rapi dan aman (ulasan 32, 36, 38).

---

## 3. Tiga Kelemahan Terbanyak + Solusi Praktis

### a. Pengiriman Lambat (12 ulasan negatif)
Keluhan: estimasi terlampaui, hampir 2 minggu, order dicancel sepihak (ulasan 7, 9, 29, 30, 37, 56, 63, 71, 79, 80).
- **Solusi:** Aktifkan notifikasi proaktif saat keterlambatan >1 hari; siapkan stok di gudang kota tujuan; jika stok kosong, tawarkan opsi penggantian/refund sebelum estimasi berakhir.

### b. Respons CS Lambat / Tidak Empatik (4 ulasan negatif)
Keluhan: "chat seller jawabnya msh dikonveksi", kurir tidak konfirmasi serah terima (ulasan 30, 63, 84, 10).
- **Solusi:** Tetapkan SLA balas chat <15 menit pada jam kerja; template jawaban untuk pertanyaan stok/ongkir; wajibkan kurir konfirmasi sebelum menyerahkan barang.

### c. Pesanan Tidak Dicek Sebelum Kirim (13 ulasan authenticity negatif)
Keluhan: warna/model/kapasitas berbeda dari pesanan (ulasan 10, 23, 26, 44, 48, 57, 66, 67, 71, 74, 84, 86, 91).
- **Solusi:** Checklist QC 2-langkah (warna + varian + kelengkapan) sebelum packing; foto barang sebelum kirim sebagai bukti; beri label varian pada paket.

---

## 4. Ulasan Berkeyakinan Rendah (Perlu Verifikasi Manusia)

Kriteria: keyakinan <0.6.

Daftar ID: **1, 2, 20, 28, 59, 63, 64, 87** — total **8 ulasan**.

| ID | Aspek | Alasan |
|---|---|---|
| 1 | Shipping, CS Service | Konteks "saran dipercepat" tidak spesifik |
| 2 | Packaging | Kalimat tidak lengkap, makna ambigu |
| 20 | CS Service | "thanks lazada" terlalu umum (c=0.5) |
| 28 | Warranty | Pertanyaan, belum tentu keluhan |
| 59 | Price | Netral, kemungkinan bukan keluhan |
| 63 | Product Quality | "sampai dengan selamat" tapi konteks keluhan kurir |
| 64 | Shipping | Ada kata "agak lama" tapi dilabeli positif |
| 87 | Product Quality | "Lmynlah" ambigu (c=0.3) |

---

## 5. Prioritas Perbaikan Minggu Ini (Fokus Pengiriman & CS)

Diurutkan dari yang paling berdampak:

1. **Percepat & pantau pengiriman** — 12 keluhan negatif, dampak langsung ke rating. Siapkan stok di gudang terdekat; kirim notifikasi proaktif keterlambatan.
2. **Audit serah terima oleh kurir** — pastikan konfirmasi ke penerima sebelum barang diserahkan (ulasan 63).
3. **Percepat respons CS/Seller** — terapkan SLA <15 menit + template balasan (ulasan 30).
4. **QC varian & kelengkapan sebelum kirim** — kurangi salah kirim warna/model yang memicu keluhan CS (ulasan 10, 84, 86).
5. **Tangani order yang berisiko batal** — hubungi pembeli lebih awal agar tidak dibatalkan sepihak (ulasan 79).

---

*Catatan: Analisis difokuskan pada aspek pengiriman dan layanan pelanggan, namun seluruh data skoring tetap dihitung untuk distribusi sentimen. Ulasan tanpa aspek (ID 3, 8, 18, 19, 22, 75, 82, 88, 90) tidak dihitung dalam tabel.*