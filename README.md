# 🌶️ Pipeline Harga Pangan Jawa Timur

Pipeline ETL otomatis yang mengambil **harga harian bahan pokok di 38 kabupaten/kota Jawa Timur** (plus rata-rata provinsi) dari [SISKAPERBAPO](https://siskaperbapo.jatimprov.go.id) milik Disperindag Jatim, lalu menyimpannya ke database untuk analisis tren dan deteksi lonjakan harga.

> ✅ Pipeline lengkap: scraping harian → dbt + DuckDB → dashboard Streamlit.
>
> 🔗 **Dashboard live:** (https://harga-pangan-jatim.streamlit.app/)

![Dashboard](docs/dashboard.png)

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
                     dbt + DuckDB (data/warehouse.duckdb)
                     staging ──► dim / fct ──► mart_mingguan, mart_lonjakan
                                          │
                                          ▼
                     scripts/export_marts.py ──► data/marts/*.parquet
                                          │
                                          ▼
                     Dashboard Streamlit (dashboard/app.py)

Dijadwalkan setiap hari dari komputer lokal (Windows Task Scheduler).
GitHub Actions menjalankan tes parser di setiap push.
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

Sekitar 39 wilayah × ±70 komoditas ≈ **2.700 baris per hari**. Per 26 Nov 2026 sudah terkumpul **87 hari (1 Sep – 26 Nov 2026), ±225 ribu baris mentah**, dan ±190 ribu baris bersih setelah harga kosong disaring.

## Transformasi (dbt)

Model dbt ada di `dbt_harga_pangan/` dan membaca CSV mentah langsung lewat DuckDB, jadi tidak perlu server database.

| Model | Isi |
|---|---|
| `stg_harga_harian` | Data bersih: tipe kolom benar, harga kosong/tidak masuk akal dibuang, baris dobel diambil yang terbaru |
| `dim_wilayah` | 39 wilayah + jenisnya (Kota / Kabupaten / Provinsi) |
| `dim_komoditas` | 67 komoditas dengan nama, kategori, dan satuan terbaru |
| `fct_harga_harian` | Harga harian + perubahan dari hari sebelumnya, rata-rata 7 hari, dan selisih dari rata-rata provinsi |
| `mart_harga_mingguan` | Rata-rata, min, dan max per minggu untuk grafik tren |
| `mart_lonjakan_harga` | Hari ketika harga melonjak (lihat metode di bawah) |

```bash
cd dbt_harga_pangan
dbt build --profiles-dir .      # membuat semua tabel + menjalankan 19 tes kualitas data
```

**Metode deteksi lonjakan.** Sebuah hari ditandai sebagai lonjakan jika:
1. z-score harga hari itu ≥ 2, dibanding rata-rata dan standar deviasi **30 hari sebelumnya** (hari itu sendiri tidak ikut dihitung), **dan**
2. harganya naik **minimal 10%** dari rata-rata 30 hari itu.

Syarat kedua ditambahkan setelah melihat data asli. Dengan z-score saja, muncul 6.083 "lonjakan", dan hampir setengahnya kenaikannya di bawah 5%. Penyebabnya, banyak harga yang datar berminggu-minggu sehingga standar deviasinya hampir nol, dan kenaikan Rp100 pun menghasilkan z-score besar. Dengan dua syarat, hasilnya menjadi 2.076 lonjakan yang didominasi komoditas yang memang bergejolak: cabai merah besar, kubis, tomat, dan cabai keriting.

**Tes kualitas data** (`dbt build`): kunci unik, relasi antar tabel, nilai yang diizinkan, tidak ada harga dobel per hari, dan peringatan untuk harga mentah yang tidak masuk akal. Tes terakhir menemukan contoh nyata: minyak goreng tercatat **Rp6** di Kab. Madiun pada 16 Nov 2026, kemungkinan salah input di sumber. Baris seperti ini disaring di staging, tetapi tetap dicatat sebagai peringatan.

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

## Dashboard

`dashboard/app.py` (Streamlit) membaca `data/marts/*.parquet` dan menampilkan:

- **Ringkasan**: rata-rata harga Jatim + perubahan 7 hari, wilayah termahal/termurah, jumlah lonjakan 7 hari terakhir
- **Tren harga** harian per wilayah untuk komoditas yang dipilih
- **Perbandingan wilayah**: harga di 38 kab/kota hari ini, diwarnai menurut selisih dari rata-rata provinsi
- **Lonjakan harga**: komoditas yang paling sering melonjak + tabel detail

```bash
streamlit run dashboard/app.py
```

Dashboard di-deploy ke Streamlit Community Cloud dari repo ini. Setiap kali pipeline harian push data baru, dashboard ikut diperbarui.

## Penjadwalan harian (Windows)

`scripts/jalankan_harian.bat` menjalankan pipeline, memperbarui model dbt, mengekspor data dashboard, lalu commit dan push. Log tersimpan di `logs/pipeline.log`.

Daftarkan ke Task Scheduler sekali saja (Command Prompt, dari folder project):

```bat
schtasks /create /tn "HargaPanganJatim" /tr "\"%cd%\scripts\jalankan_harian.bat\"" /sc daily /st 13:00
```

Linux/Mac bisa memakai cron: `0 13 * * * cd /path/ke/repo && python src/run_pipeline.py && git add data/raw && git commit -m data && git push`

## Keputusan desain

- **Idempoten**: kunci utama `(tanggal, kode_wilayah, id_komoditas)` + `ON CONFLICT DO UPDATE`, jadi pipeline aman dijalankan ulang tanpa data dobel.
- **Dua lapisan penyimpanan**: CSV mentah per hari (mudah diaudit, ikut ter-commit ke repo) dan database untuk query.
- **Harga 0 → NULL**: situs menulis 0 kalau pasar tidak melapor. Menyimpannya sebagai 0 akan merusak rata-rata.
- **Sopan ke server**: jeda 1,5 detik antar request, retry dengan jeda bertambah, User-Agent jelas.
- **Parser diuji** dengan potongan HTML asli, supaya kalau struktur situs berubah, tes langsung gagal.
- **Scraping dijalankan lokal, bukan di GitHub Actions**: percobaan pertama di GitHub Actions mendapat HTTP 403 untuk setiap request, sementara request yang sama dari jaringan Indonesia berhasil. Situs tampaknya membatasi akses dari luar negeri. Karena itu jadwal harian dipindah ke Task Scheduler di komputer lokal, yang lalu meng-commit CSV ke repo, dan GitHub Actions dipakai untuk CI (tes parser).

## Roadmap

- [x] Scraper + parser + load ke database
- [x] Jadwal harian (Task Scheduler) + CI di GitHub Actions (tes parser + `dbt build` di data asli)
- [x] Backfill data ke belakang (mulai 1 Sep 2026)
- [x] dbt: model staging, dim/fct, rata-rata mingguan, deteksi lonjakan + tes kualitas data
- [x] Dashboard Streamlit
- [ ] Alert Telegram saat ada lonjakan

## Sumber data

Sistem Informasi Ketersediaan dan Perkembangan Harga Bahan Pokok (SISKAPERBAPO), Dinas Perindustrian dan Perdagangan Provinsi Jawa Timur. Data dipakai untuk tujuan edukasi dan analisis.
