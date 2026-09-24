# Form Submission — Capstone Project (IBM SkillsBuild × Hacktiv8)

> Siap copy-paste langsung ke Google Form: https://bit.ly/ibm-sesi3
> Dicatat: 2026-09-14

---

## Judul Topic / Use Case

**Other:**

```
AspectSentix - Aspect-Based Sentiment Analyzer untuk Seller Gadget UMKM
```

---

## Problem Statement

Jelaskan permasalahan utama yang ingin Anda selesaikan. Sertakan konteks, siapa yang terdampak, dan mengapa masalah ini penting untuk diselesaikan.

Seller gadget UMKM di marketplace Indonesia (Tokopedia/Shopee/Lazada) menerima ratusan ulasan pelanggan setiap bulan, tetapi hanya bisa melihat rating bintang agregat. Rating 4,3 tidak memberi tahu apakah masalahnya di pengiriman, keaslian barang, kualitas produk, atau layanan CS — sehingga seller menebak-nebak saat melakukan perbaikan, dan sering memperbaiki hal yang salah. Yang terdampak: seller UMKM (tim 1–5 orang tanpa analis data) dan pembeli yang kualitas layanannya tidak membaik. Masalah ini penting karena gadget adalah kategori bernilai tinggi dan rawan sengketa (garansi, keaslian, spesifikasi); satu aspek yang berdarah bisa menjatuhkan rating dan penjualan, sementara ulasan berbahasa Indonesia (kata gaul, singkatan) sulit dianalisis tool sentimen generik.

---

## Target Users

Jelaskan siapa pengguna utama dari solusi Anda. Sebutkan karakteristik, kebutuhan, dan konteks penggunaan mereka.

Utama: seller gadget UMKM di marketplace Indonesia — tim kecil 1–5 orang, merangkap packing/CS/admin, melek digital tapi bukan data analyst (tidak bisa Python, tidak punya dashboard). Kebutuhan: tahu aspek spesifik mana yang harus diperbaiki dari ratusan ulasan yang tidak sempat dibaca semua, dalam bahasa yang mudah dipahami, bukan tabel mentah. Konteks penggunaan: mengunggah file CSV ulasan bulanan ke playground agent, lalu bertanya sesuai kebutuhan (misal "fokus ke masalah pengiriman") untuk mendapat laporan singkat berisi prioritas perbaikan minggu ini.

---

## Potential Impact

Jelaskan bagaimana solusi berbasis AI yang Anda buat dapat menyelesaikan permasalahan yang diangkat, serta manfaat yang dihasilkan bagi pengguna atau stakeholder.

Agent mengubah ratusan ulasan mentah menjadi laporan aspek-per-aspek dalam hitungan menit: distribusi sentimen (positif/negatif/netral per aspek), 3 kekuatan, 3 kelemahan + solusi praktis, daftar ulasan yang perlu verifikasi manusia, dan prioritas perbaikan berurutan dampak. Manfaat: keputusan perbaikan berbasis data bukan tebakan (misal: temuan bahwa "ketidaksesuaian barang dengan deskripsi" adalah keluhan terbesar → aksi audit foto & double-check varian sebelum packing), waktu analisa turun dari berjam-jam membaca manual menjadi ~30 detik, dan keluhan sistemik dapat dibedakan dari insiden tunggal sebelum merusak rating.

---

## Apakah kamu memiliki improvisasi dalam project yang kamu buat?

**Pilihan:**

```
Menggunakan template yang ada dengan tambahan improvisasi
```

**Jika ya, jelaskan improvisasi atau modifikasi yang kamu lakukan:**

Saya memulai dari pola template Read File → Prompt Template → LLM → Chat Output, lalu memodifikasinya cukup jauh: (1) Pipeline ABSA 3 tahap dengan kontrak JSONL antar-tahap — bukan analisis sentimen tunggal seperti template; (2) menyisipkan komponen Type Convert agar CSV terbaca sebagai teks untuk prompt; (3) menambahkan Chat Input sebagai "lensa fokus" sehingga user bisa bertanya (mis. "analisis pengiriman saja") dan laporan menyesuaikan pertanyaan; (4) prompt dirancang ulang dengan taksonomi 9 aspek tetap untuk ulasan berbahasa Indonesia (normalisasi kata gaul/singkatan) plus instruksi self-check aritmetika agar angka agregasi konsisten; (5) field confidence pada tahap skoring sehingga ulasan ambigu di-flag untuk verifikasi manusia, bukan dipaksa berlabel.

---

## Penjelasan singkat alur sistem (input → proses → output)

**Input:** File CSV berisi 90 ulasan produk gadget berbahasa Indonesia (kolom: review, rating, category) + pertanyaan fokus dari user (opsional).

**Proses:** (1) Read File memuat CSV, Type Convert mengubah tabel menjadi teks; (2) 9Router LLM #1 menormalisasi kata gaul lalu mengekstrak aspek tiap ulasan ke taksonomi 9 kategori (JSONL); (3) 9Router LLM #2 menilai sentimen per aspek dengan confidence + bukti kutipan (JSONL); (4) 9Router LLM #3 mengagregasi hasil skoring menjadi laporan, dengan pertanyaan user sebagai lensa fokus.

**Output:** Laporan naratif Bahasa Indonesia: tabel distribusi sentimen per aspek, 3 kekuatan produk, 3 kelemahan + solusi praktis, daftar ulasan berkeyakinan rendah yang perlu dicek manusia, dan prioritas perbaikan minggu ini.

---

## Potensi Pengembangan Lanjutan

*(Optional)*

Beberapa arah pengembangan yang saya rencanakan untuk AspectSentix:

1. Integrasi API marketplace (Tokopedia/Shopee) agar ulasan tertarik otomatis setiap hari, tanpa perlu upload CSV manual.

2. Monitoring berkelanjutan dengan penyimpanan hasil analisis antar-waktu, sehingga seller bisa melihat tren: apakah keluhan pengiriman membaik setelah perbaikan, atau justru memburuk.

3. Alert otomatis ketika suatu aspek mengalami lonjakan sentimen negatif, misalnya ambang batas "lebih dari 30% ulasan negatif menyebut authenticity dalam 7 hari" memicu notifikasi ke seller.

4. Benchmarking kompetitor: menganalisis ulasan produk pesaing di kategori yang sama untuk menemukan celur aspek yang menjadi kelemahan kompetitor namun menjadi kekuatan produk kita.

5. Peningkatan akurasi agregasi dengan memindahkan penghitungan statistik dari LLM ke komponen kode deterministik, sehingga tabel distribusi tidak lagi berpotensi berbeda antar-run, dan LLM fokus pada tugas narasi & rekomendasi.

6. Ekspansi domain ke kategori produk lain (fashion, skincare, makanan) dengan taksonomi aspek yang disesuaikan per kategori, serta dukungan ulasan berbahasa daerah/campuran.

---

## Apakah muncul potensi ide project lain?

*(Optional)*

**Judul Use Case Baru: Review-to-Ticket — Otomasi Penanganan Keluhan Marketplace**

Agent yang meneruskan hasil analisis sentimen per-aspek menjadi tiket tindakan otomatis. Ketika ulasan negatif dengan confidence tinggi terdeteksi pada aspek tertentu (misalnya pengiriman atau garansi), agen menyusun draf respons seller, membuat checklist QC untuk tim gudang, dan menyiapkan usulan kompensasi (voucher/retur) sesuai kebijakan toko — sehingga siklus "ulasan masuk sampai keluhan tertangani" berjalan tanpa manusia kecuali untuk kasus berkeyakinan rendah.

**Judul Use Case Baru: UMKM Copilot — Asisten Operasional Harian Seller**

Perluasan dari sekadar analisis ulasan menjadi asisten serbaguna untuk seller UMKM: analisis data penjualan dari CSV (margin, produk laris, stok mati), riset kompetitor, hingga pembuatan deskripsi produk berbasis kata kunci dari ulasan pelanggan — memakai arsitektur pipeline multi-tahap yang sama dengan AspectSentix.

---

*Cara pakai: salin isi masing-masing bagian ke field yang sesuai di Google Form. Untuk field "Jika ya, jelaskan..." dan "Penjelasan singkat alur sistem", pastikan tidak melebihi batas karakter form.*
