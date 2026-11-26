<<<<<<< HEAD
# 🌶️ Pipeline Harga Pangan Jawa Timur

Pipeline ETL otomatis yang mengambil **harga harian bahan pokok di 38 kabupaten/kota Jawa Timur** (plus rata-rata provinsi) dari [SISKAPERBAPO](https://siskaperbapo.jatimprov.go.id) milik Disperindag Jatim, lalu menyimpannya ke database untuk analisis tren dan deteksi lonjakan harga.

> Status: 🚧 Tahap 1 (Extract & Load) selesai. Tahap 2 (transformasi dbt) dan tahap 3 (dashboard) menyusul.

## Kenapa project ini?

Harga cabai, bawang, dan beras bisa naik tajam dalam hitungan hari, dan kenaikannya tidak sama di setiap daerah. Data resminya tersedia, tetapi hanya bisa dilihat per hari dan per wilayah di situs. Project ini mengumpulkannya secara otomatis supaya bisa dianalisis sebagai deret waktu.

## Arsitektur

```
SISKAPERBAPO (HTML)
      │  POST /harga/tabel.nodesign  (tanggal, kabkota)
      ▼
scraper.py ──► parser.py ──► load_to_database.py
 (Extract)     (Transform)      │
                                ├──► data/raw/YYYY-MM-DD.csv   (arsip mentah)
                                └──► PostgreSQL / SQLite       (tabel raw_harga_harian)
                                          │
                                          ▼
                                   dbt models (tahap 2)  ──►  Dashboard (tahap 3)

Dijadwalkan setiap hari 13:00 WIB oleh GitHub Actions.
```

## Data

Tabel `raw_harga_harian`. Satu baris = satu komoditas × satu wilayah × satu tanggal.

| Kolom | Contoh |
|---|---|
| tanggal | 2026-11-25 |
| kode_wilayah | surabayakota |
| nama_wilayah | Kota Surabaya |
| id_komoditas | 37 |
| nama_komoditas | Cabe Merah Keriting |
| kategori | CABE |
| satuan | kg |
| harga_rp | 57166 (NULL kalau tidak dilaporkan) |
| waktu_scrape | 2026-11-25 13:02:11 |

Sekitar 39 wilayah × ±70 komoditas ≈ **2.700 baris per hari**.

## Cara menjalankan

```bash
pip install -r requirements.txt

# Ambil data hari ini untuk semua wilayah (±1-2 menit)
python src/run_pipeline.py

# Satu tanggal, wilayah tertentu
python src/run_pipeline.py --tanggal 2026-11-25 --wilayah surabayakota malangkota

# Backfill rentang tanggal
python src/run_pipeline.py --mulai 2026-10-01 --selesai 2026-11-25

# Tes parser
python -m pytest tests
```

Tanpa pengaturan apa pun, data masuk ke SQLite `data/harga_pangan.db`. Untuk PostgreSQL (misalnya Supabase), isi variabel lingkungan `DATABASE_URL`:

```bash
# Windows (PowerShell)
$env:DATABASE_URL="postgresql://postgres:PASSWORD@db.xxxx.supabase.co:5432/postgres"
# Linux / Mac
export DATABASE_URL="postgresql://postgres:PASSWORD@db.xxxx.supabase.co:5432/postgres"
```

## Keputusan desain

- **Idempoten**: kunci utama `(tanggal, kode_wilayah, id_komoditas)` + `ON CONFLICT DO UPDATE`, jadi pipeline aman dijalankan ulang tanpa data dobel.
- **Dua lapisan penyimpanan**: CSV mentah per hari (mudah diaudit, ikut ter-commit ke repo) dan database untuk query.
- **Harga 0 → NULL**: situs menulis 0 kalau pasar tidak melapor. Menyimpannya sebagai 0 akan merusak rata-rata.
- **Sopan ke server**: jeda 1,5 detik antar request, retry dengan jeda bertambah, User-Agent jelas.
- **Parser diuji** dengan potongan HTML asli, supaya kalau struktur situs berubah, tes langsung gagal.

## Roadmap

- [x] Scraper + parser + load ke database
- [x] Jadwal harian GitHub Actions
- [ ] Backfill data ke belakang
- [ ] dbt: model staging, rata-rata mingguan, deteksi lonjakan (> 2 standar deviasi)
- [ ] Dashboard Looker Studio / Metabase
- [ ] Alert Telegram saat ada lonjakan

## Sumber data

Sistem Informasi Ketersediaan dan Perkembangan Harga Bahan Pokok (SISKAPERBAPO), Dinas Perindustrian dan Perdagangan Provinsi Jawa Timur. Data dipakai untuk tujuan edukasi dan analisis.
=======
# harga-pangan-jatim
>>>>>>> 561136819d6e7b66cfbb9ce7115acad1538401f4
