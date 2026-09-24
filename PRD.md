# PRD — AspectSentix

**Aspect-Based Sentiment Analyzer untuk Seller Gadget UMKM**

| | |
|---|---|
| **Versi** | 1.0 (Draft) |
| **Tanggal** | 2026-09-14 |
| **Program** | Capstone Project — IBM SkillsBuild University Education × Hacktiv8 |
| **Track** | Track 1 · Langflow |
| **Penulis** | Syahril |
| **Status** | 🟡 Draft — menunggu implementasi |

---

## 1. Ringkasan Eksekutif

**AspectSentix** adalah AI Agent berbasis Langflow yang menganalisis ulasan produk gadget berbahasa Indonesia dan menghasilkan **sentimen per-aspek** (bukan satu sentimen global) beserta rekomendasi perbaikan berprioritas untuk seller UMKM.

Alih-alih memberi tahu seller bahwa rating produknya 4.3, AspectSentix menjawab pertanyaan yang sebenarnya penting: *aspek mana yang bikin rating itu turun, dan apa yang harus diperbaiki dulu?*

---

## 2. Problem Statement

Seller gadget UMKM menerima ratusan ulasan per bulan, tetapi hanya melihat **rating bintang agregat**. Rating 4.3 tidak memberi tahu apakah masalahnya ada di **pengiriman**, **garansi**, **baterai**, atau **keaslian produk**. Akibatnya seller menebak-nebak saat memperbaiki kualitas, dan sering memperbaiki hal yang salah.

Sentimen global juga menyamarkan kelemahan: satu ulasan bisa memuji layar tetapi mengeluh soal baterai — model sentimen tunggal akan meratakan keduanya menjadi satu label.

### 2.1 Yang Terdampak

| Pihak | Dampak |
|---|---|
| **Seller gadget UMKM** (1–5 orang, tanpa tim data) | Tidak punya alat untuk memahami ratusan ulasan; keputusan perbaikan berbasis tebakan |
| **Pembeli** | Kualitas produk tidak membaik karena keluhan tidak diterjemahkan jadi aksi |
| **Tim support marketplace** | Kebanjiran keluhan yang akarnya bisa dicegah di level seller |

### 2.2 Mengapa Penting

- Gadget adalah kategori **bernilai tinggi dan rawan sengketa** (garansi, keaslian, kesesuaian spesifikasi).
- UMKM mendominasi penjual di marketplace Indonesia, namun hampir tidak ada yang punya analis data.
- Perbaikan aspek yang tepat sasaran langsung menaikkan rating → berdampak langsung ke penjualan.
- Analisis sentimen berbahasa Indonesia masih sedikit; yang ada umumnya bukan per-aspek.

---

## 3. Tujuan & Dampak yang Diharapkan

1. Seller tahu **aspek mana** yang paling merugikan rating, bukan hanya angka rating.
2. Seller mendapat **rekomendasi konkret berprioritas** — apa yang harus dikerjakan minggu ini.
3. Seller bisa membedakan **keluhan sistemik** (pola berulang) dari **insiden tunggal**.
4. Ulasan yang tidak bisa dinilai dengan yakin **di-flag untuk verifikasi manusia**, bukan ditebak.
5. Proses yang tadinya butuh jam membaca manual menjadi **hitungan menit**.

---

## 4. Target Pengguna

**Persona utama — "Rina, Seller Gadget UMKM"**
- Usia 25–40, menjalankan toko aksesoris & gadget di Tokopedia/Shopee
- 1–3 orang tim, merangkap packing, CS, dan admin
- Melek digital tapi **bukan** data analyst — tidak bisa Python, tidak punya dashboard
- Punya 200–2.000 ulasan/bulan yang tidak pernah dibaca semua
- Kebutuhan: *"kasih tahu saya apa yang harus dibenerin, jangan kasih saya tabel"*

---

## 5. Ruang Lingkup

### ✅ In Scope
- Analisis ulasan dari **file CSV** (kolom `review`, `rating`)
- Kategori produk: **laptop, handphone, tablet, aksesoris gadget**
- Analisis **multi-aspek** dengan sentimen + skor + bukti kutipan
- Deteksi ulasan janggal (rating tidak cocok dengan isi sentimen)
- Output laporan naratif berbahasa Indonesia

### ❌ Out of Scope (v1.0)
- Integrasi API marketplace secara real-time
- Dashboard web / UI di luar Playground Langflow
- Analisis gambar pada ulasan
- Multi-bahasa selain Indonesia
- Autentikasi & multi-user

---

## 6. Definisi Aspek

Delapan kategori aspek tetap (closed taxonomy) — dibuat tetap agar output konsisten dan bisa dibandingkan antar-ulasan:

| Aspek | Cakupan |
|---|---|
| `product_quality` | Material, build quality, daya tahan, kesesuaian deskripsi |
| `performance` | Kecepatan, fungsi, fitur, kinerja teknis |
| `battery` | Daya tahan baterai, kecepatan charging |
| `shipping` | Kecepatan kirim, ketepatan estimasi, kurir |
| `packaging` | Kondisi paket, keamanan bungkus, kerapian |
| `price` | Harga vs nilai, value for money, potongan |
| `warranty` | Garansi, klaim, purna jual |
| `cs_service` | Respons seller, keramahan, penyelesaian masalah |
| `authenticity` | Keaslian produk, segel, kesesuaian spesifikasi |

> Catatan: `authenticity` krusial untuk gadget — keluhan "barang palsu/rekondisi" sering muncul dan berdampak besar.

---

## 7. Arsitektur Sistem

### 7.1 Alur Tingkat Tinggi

```
INPUT                  PROSES                                  OUTPUT
─────────────────────────────────────────────────────────────────────────────
CSV ulasan   →   Tahap 1: Normalisasi & Ekstraksi Aspek   →
                 Tahap 2: Skoring Sentimen per Aspek      →   Laporan
                 Tahap 3: Agregasi & Rekomendasi          →   untuk Seller
```

### 7.2 Detail Flow Langflow

```
[Read File]  gadget_reviews.csv
      ↓ message
[Prompt Template 1 — Normalisasi & Ekstraksi Aspek]   ← {text}
      ↓ prompt
[9Router LLM #1]   (temperature = 0.0)
      ↓ message (JSON array)
[Structured Output Parser]
      ↓
[Prompt Template 2 — Skoring Sentimen]                ← {aspects_json}
      ↓ prompt
[9Router LLM #2]   (temperature = 0.0)
      ↓ message (JSON array)
[Prompt Template 3 — Agregasi & Rekomendasi]          ← {sentiment_json}
      ↓ prompt
[9Router LLM #3]   (temperature = 0.7)
      ↓ message
[Chat Output]
```

### 7.3 Daftar Komponen

| # | Komponen | Peran | Konfigurasi |
|---|---|---|---|
| 1 | Read File | Load CSV ulasan | upload `gadget_reviews.csv` |
| 2 | Prompt Template 1 | Instruksi ekstraksi aspek | var `{text}` |
| 3 | 9Router LLM #1 | Ekstraksi aspek | `temperature=0.0`, `combo=Sak_Kapokmu` |
| 4 | Structured Output Parser | Validasi JSON | schema array of objects |
| 5 | Prompt Template 2 | Instruksi skoring | var `{aspects_json}` |
| 6 | 9Router LLM #2 | Skoring sentimen | `temperature=0.0` |
| 7 | Prompt Template 3 | Instruksi rekomendasi | var `{sentiment_json}` |
| 8 | 9Router LLM #3 | Komposisi laporan | `temperature=0.7` |
| 9 | Chat Output | Tampilkan hasil | — |
| 10 | Sticky Notes | Identitas (nama + universitas) | — |

### 7.4 Konfigurasi 9Router LLM

Komponen custom milik pengguna (`NineRouterLLM`), output tunggal bertipe `Message`.

| Field | Nilai | Alasan |
|---|---|---|
| `combo` | `Sak_Kapokmu` | Combo default; alternatif: `Good`, `gc/gemini-2.5-flash`, `kr/qwen3-coder-next` |
| `base_url` | `http://localhost:20128/v1` | Endpoint 9Router lokal |
| `api_key` | dari env `CUSTOM_ENDPOINT_API_KEY` | Jangan di-hardcode |
| `max_tokens` | `2048` | Cukup untuk output JSON per tahap |
| `temperature` | `0.0` (tahap 1 & 2), `0.7` (tahap 3) | JSON butuh deterministik; narasi butuh variasi |

---

## 8. Spesifikasi Prompt

### 8.1 Prompt Template 1 — Normalisasi & Ekstraksi Aspek

```
Anda analis data ulasan e-commerce berbahasa Indonesia.
Normalisasi variasi ejaan kata gaul/singkatan, lalu ekstrak ASPEK
yang dibahas dari tiap ulasan ke kategori tetap:
[product_quality, performance, battery, shipping, packaging,
 price, warranty, cs_service, authenticity].
Output HANYA JSON array, tiap elemen:
{"review_id": <idx>, "aspects": ["...", "..."]}
Jika tidak ada aspek terdeteksi, kirim array kosong.

Ulasan:
{text}
```

### 8.2 Prompt Template 2 — Skoring Sentimen per Aspek

```
Untuk setiap pasangan (review_id, aspek) di bawah ini, tentukan:
- sentiment: positive | negative | neutral
- confidence: 0.0-1.0
- evidence: kutipan langsung dari ulasan yang mendukung

Input:
{aspects_json}

Output HANYA JSON array:
[{"review_id": <idx>, "aspect": "...", "sentiment": "...",
  "confidence": 0.x, "evidence": "..."}]
```

### 8.3 Prompt Template 3 — Agregasi & Rekomendasi

```
Kamu adalah konsultan operasional UMKM gadget.
Berikut hasil skoring aspek per ulasan. Buat laporan untuk seller yang:
1. Rangkum distribusi sentimen per aspek (jumlah positif/negatif/netral)
2. Sebutkan 3 kekuatan produk
3. Sebutkan 3 kelemahan terbanyak + solusi praktis
4. Flag ulasan dengan confidence < 0.7 (perlu verifikasi manusia)
5. Rekomendasikan prioritas perbaikan minggu ini

Gaya: Bahasa Indonesia formal, friendly, actionable. Bullet points boleh.

Data:
{sentiment_json}
```

---

## 9. Spesifikasi Data

| Item | Detail |
|---|---|
| **Sumber** | [`revanmd/indonesian-dataset-SA-ML`](https://github.com/revanmd/indonesian-dataset-SA-ML) |
| **Isi sumber** | Review produk Lazada & Shopee, >3 juta ulasan, 63.000 file CSV, 200+ kategori |
| **Skema sumber** | `review,rating` (rating 1–5) |
| **Kategori dipakai** | `laptop`, `handphone`, `tablet` |
| **Metode sampling** | Stratified per rating (1–5) agar ulasan negatif terwakili |
| **Ukuran sampel** | 300 ulasan (100 per kategori) |
| **File output** | `aspectsentix/dataset/gadget_reviews.csv` |
| **Skema output** | `review, rating, category` |
| **Script** | `aspectsentix/build_dataset.py` (reproducible, seed=42) |

### 9.1 Hasil Sampling (terverifikasi)

| Kategori | Pool "kaya" | Pool "pendek" | Diambil |
|---|---|---|---|
| laptop | 20.861 | 4.597 | 100 |
| handphone | 29.261 | 6.064 | 100 |
| tablet | 30.816 | 8.322 | 100 |

- **Distribusi rating:** tepat 20 ulasan per rating (1–5) per kategori → total 60 per rating
- **Panjang ulasan:** min 4 · median 67 · max 998 karakter
- **Edge case disengaja:** 15 ulasan < 15 karakter (emoji-only, satu kata) → bahan uji ketahanan

### 9.2 Komposisi per Kategori

Tiap kategori = **95 ulasan kaya** (≥15 karakter, mengandung sinyal aspek) + **5 ulasan pendek** sebagai edge case yang sengaja disertakan. Rasio ini membuat analisis punya cukup bahan, sekaligus membuktikan flow tidak hancur saat diberi input tidak berguna.

### 9.3 Catatan Kualitas Data

Penulis dataset secara eksplisit menyatakan data **belum di-preprocess** dan menyebut 7 fenomena yang perlu ditangani:

1. Simbol
2. Kode gambar (emoji)
3. Kata gaul
4. Kata tidak baku
5. Huruf berulang (`mantappp`, `WKWKWK`)
6. Angka
7. Tanda baca

> 🎯 **Ini justru peluang.** Layer normalisasi di Prompt Template 1 dirancang khusus untuk mengatasi masalah yang diakui penulis dataset — ini bagian yang jarang dikerjakan orang lain dan jadi pembeda utama dari sample project.

---

## 10. Nilai Beda dari Sample Project

PPT mensyaratkan use case **dan** dataset berbeda dari tiga sample (Customer Feedback Sentiment Analyzer, Expense Analyzer, CV Information Extractor). Pemenuhannya:

| # | Pembeda | Nilai Juri yang Disasar |
|---|---|---|
| 1 | **ABSA multi-aspek** — sample hanya satu sentimen global | Creativity & Innovation |
| 2 | **Layer normalisasi bahasa gaul Indonesia** — mengatasi kelemahan yang diakui penulis dataset | Creativity & Innovation, Completeness |
| 3 | **Cross-validation rating vs sentimen** — deteksi ulasan janggal / potensi fake review | Creativity & Innovation |
| 4 | **Rekomendasi berprioritas** — output actionable, bukan sekadar ringkasan | Background & Impact |
| 5 | **Dataset bahasa Indonesia asli** dari marketplace lokal (Lazada/Shopee) | Background & Impact |
| 6 | **Pipeline LLM 3 tahap** dengan kontrak JSON antar-tahap | System Design & Architecture |
| 7 | **Confidence score + flag verifikasi manusia** | Responsible AI (nilai plus) |

---

## 11. Persyaratan Non-Fungsional

| Aspek | Persyaratan |
|---|---|
| **Bahasa output** | Bahasa Indonesia formal, mudah dipahami non-teknis |
| **Konsistensi format** | JSON valid di tahap 1 & 2; laporan naratif di tahap 3 |
| **Determinisme** | `temperature=0` pada tahap ekstraksi & skoring |
| **Transparansi** | Setiap label sentimen disertai kutipan bukti (`evidence`) |
| **Kesadaran keterbatasan** | Ulasan ber-confidence rendah di-flag, tidak dipaksa dilabeli |
| **Portabilitas** | Berjalan di Langflow lokal dengan 9Router; tanpa dependensi cloud eksternal |
| **Keamanan** | API key dibaca dari environment variable, tidak di-hardcode |

---

## 12. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Context limit (juta ulasan) | Flow gagal | Sampling 300 ulasan |
| Output LLM tidak konsisten antar-tahap | Pipeline putus | Structured Output Parser + `temperature=0` + few-shot |
| Bahasa gaul/singkatan salah tafsir | Sentimen keliru | Layer normalisasi khusus di Tahap 1 |
| Ulasan negatif terlalu sedikit | Analisis bias positif | Stratified sampling per rating |
| Aspek di luar 9 kategori | Aspek terlewat | Instruksi fallback + review berkala daftar aspek |
| Halusinasi pada ulasan ambigu | Label salah | Field `confidence` + flag verifikasi manusia |

---

## 13. Metrik Keberhasilan

| Metrik | Target |
|---|---|
| Semua komponen terhubung & flow berjalan end-to-end | ✅ Wajib |
| Output JSON valid di tahap 1 & 2 | 100% run |
| Aspek terdeteksi per ulasan | ≥ 1 aspek untuk ≥ 90% ulasan |
| Ulasan ber-confidence rendah ter-flag dengan benar | Terlihat di laporan |
| Laporan akhir dapat dipahami non-teknis | Review manual |
| Waktu eksekusi per run (300 ulasan) | < 3 menit |

---

## 14. Rencana Iterasi Prompt (Bukti untuk Juri)

Kriteria penilaian menyebut *"ada bukti iterasi"*. Dokumentasikan versi awal vs final:

| Versi | Perubahan | Alasan |
|---|---|---|
| v0.1 | Satu prompt monolitik (ringkas + sentimen + rekomendasi sekaligus) | Baseline |
| v0.2 | Dipecah 3 tahap terpisah | Output monolitik tidak konsisten & sulit divalidasi |
| v0.3 | Ditambah taksonomi 9 aspek tetap | Aspek bebas bikin hasil tidak bisa dibandingkan |
| v0.4 | Ditambah layer normalisasi bahasa gaul | Banyak kata tidak baku salah ditafsirkan |
| v0.5 | Ditambah `confidence` + `evidence` | Output tidak bisa diaudit |
| v1.0 | Ditambah flag verifikasi manusia + rekomendasi prioritas | Perlu kejujuran soal keterbatasan + output actionable |

> 📸 Screenshot tiap versi prompt untuk lampiran submission.

---

## 15. Ide Pengembangan ke Depan

**Judul: ReviewRadar Pro — Dashboard Monitoring Ulasan Real-Time untuk Seller Marketplace**

Pengembangan dari AspectSentix dengan tambahan:
- **Integrasi API marketplace** — tarik ulasan otomatis, tanpa upload CSV manual
- **Analisis berkelanjutan** — pantau tren sentimen per-aspek antar waktu
- **Alert otomatis** — notifikasi saat aspek tertentu (mis. `shipping`) mengalami lonjakan sentimen negatif
- **Benchmarking kompetitor** — bandingkan aspek produk sendiri vs produk pesaing di kategori sama
- **Rekomendasi prediktif** — prediksi dampak perbaikan aspek terhadap rating keseluruhan
- **Multi-bahasa** — perluas ke ulasan berbahasa campuran (Indonesia–Inggris–daerah)

---

## 16. Checklist Implementasi

### Fase 1 — Data
- [ ] Sparse-checkout kategori `laptop`, `handphone`, `tablet` dari repo dataset
- [ ] Sampling stratified ~300 ulasan (proporsional per rating 1–5)
- [ ] Gabung jadi `aspectsentix/dataset/gadget_reviews.csv` (`review, rating, category`)
- [ ] Sanity check: tidak ada baris kosong, encoding UTF-8

### Fase 2 — Setup
- [ ] Pastikan 9Router jalan di `http://localhost:20128/v1`
- [ ] Set env `CUSTOM_ENDPOINT_API_KEY`
- [ ] Konfirmasi komponen `NineRouterLLM` terdaftar di Langflow
- [ ] Buat flow baru di Langflow

### Fase 3 — Build
- [ ] Pasang Read File → upload CSV
- [ ] Pasang Prompt Template 1 + 9Router LLM #1 + Structured Output Parser
- [ ] Pasang Prompt Template 2 + 9Router LLM #2
- [ ] Pasang Prompt Template 3 + 9Router LLM #3
- [ ] Pasang Chat Output
- [ ] Hubungkan semua edge, cek tipe port cocok
- [ ] Tambah Sticky Notes berisi nama & universitas

### Fase 4 — Test & Iterasi
- [ ] Run Flow, cek output tahap 1 (JSON valid?)
- [ ] Cek output tahap 2 (semua aspek terskor?)
- [ ] Cek output tahap 3 (laporan masuk akal & actionable?)
- [ ] Dokumentasikan iterasi prompt (tabel Bagian 14)
- [ ] Test edge case: ulasan kosong, ulasan emoji-only, ulasan sangat pendek

### Fase 5 — Dokumentasi & Submit
- [ ] Screenshot Main Flow Canvas
- [ ] Screenshot Playground
- [ ] Screenshot tiap Prompt Template (3 buah)
- [ ] Export `.json` dari Langflow
- [ ] Upload `.json` ke Google Drive
- [ ] Isi 14 item form submission
- [ ] Submit ke https://bit.ly/ibm-sesi3

---

## 17. Lampiran — Isi Form Submission

Siap copy-paste ke form:

| Field | Isi |
|---|---|
| **Judul Project** | AspectSentix — Aspect-Based Sentiment Analyzer untuk Seller Gadget UMKM |
| **Problem** | Seller gadget UMKM menerima ratusan ulasan per bulan tetapi hanya melihat rating bintang agregat. Rating 4.3 tidak memberi tahu apakah masalahnya di pengiriman, garansi, baterai, atau keaslian produk, sehingga seller menebak-nebak saat memperbaiki kualitas. |
| **Yang Terdampak** | Seller gadget UMKM (1–5 orang, tanpa tim data) di Tokopedia/Shopee/Lazada, serta pembeli yang tidak mendapat perbaikan kualitas karena keluhan tidak diterjemahkan menjadi aksi. |
| **Mengapa Penting** | Gadget adalah kategori bernilai tinggi dan rawan sengketa (garansi, keaslian, spesifikasi). UMKM mendominasi penjual marketplace namun hampir tidak ada yang punya analis data. Perbaikan aspek yang tepat sasaran langsung menaikkan rating dan penjualan. |
| **Tujuan / Dampak** | Membuat seller tahu aspek mana yang paling merugikan rating, mendapat rekomendasi konkret berprioritas, dan mampu membedakan keluhan sistemik dari insiden tunggal — sehingga proses yang tadinya butuh jam membaca manual menjadi hitungan menit. |
| **Pendekatan / Teknik** | Saya menerapkan Aspect-Based Sentiment Analysis (ABSA) — sentimen dihitung per-aspek, bukan satu label global. Flow dibangun sebagai pipeline LLM 3 tahap dengan kontrak JSON antar-tahap (Structured Output Parser) agar output konsisten. Tahap pertama menormalisasi bahasa gaul dan singkatan khas ulasan Indonesia, lalu mengekstrak aspek ke taksonomi 9 kategori tetap. Tahap kedua menilai sentimen, confidence, dan kutipan bukti per aspek. Tahap ketiga mengagregasi hasil menjadi rekomendasi berprioritas. Ulasan ber-confidence rendah di-flag untuk verifikasi manusia. |
| **Input** | File CSV berisi ulasan produk gadget berbahasa Indonesia dari marketplace (kolom: review, rating, category) — ~300 ulasan dari kategori laptop, handphone, tablet, dan aksesoris. |
| **Proses** | Ulasan dibaca, dinormalisasi, lalu aspeknya diekstrak ke 9 kategori tetap. Setiap aspek diberi sentimen (positif/netral/negatif), skor keyakinan, dan kutipan bukti. Hasilnya diagregasi menjadi distribusi sentimen per aspek dan diterjemahkan menjadi rekomendasi perbaikan berprioritas untuk seller. |
| **Output** | Laporan naratif berbahasa Indonesia untuk seller: distribusi sentimen per aspek, 3 kekuatan produk, 3 kelemahan terbanyak beserta solusinya, daftar ulasan yang perlu diverifikasi manusia, dan prioritas perbaikan minggu ini. |
| **Ide Pengembangan ke Depan** | ReviewRadar Pro — Dashboard Monitoring Ulasan Real-Time untuk Seller Marketplace: integrasi API marketplace untuk analisis berkelanjutan tanpa upload manual, alert otomatis saat aspek tertentu mengalami lonjakan sentimen negatif, benchmarking terhadap produk pesaing, dan rekomendasi prediktif atas dampak perbaikan aspek terhadap rating keseluruhan. |

---

*Dokumen ini merangkap sebagai desain teknis dan sumber isi form submission.*
