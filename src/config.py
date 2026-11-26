# ============================================================
# config.py
# Semua pengaturan project dikumpulkan di sini supaya mudah diubah.
# ============================================================

import os

# ------------------------------------------------------------
# 1. Alamat sumber data (SISKAPERBAPO - Disperindag Jatim)
# ------------------------------------------------------------
# Halaman tabel harga mengirim POST ke alamat ini dengan 3 isian:
#   tanggal  -> format "YYYY-MM-DD"
#   kabkota  -> kode wilayah, misalnya "surabayakota" (kosong = rata-rata provinsi)
#   pasar    -> id pasar (kosong = semua pasar di wilayah itu)
URL_TABEL_HARGA = "https://siskaperbapo.jatimprov.go.id/harga/tabel.nodesign"

# Identitas scraper. Sopan untuk memberi tahu server siapa yang mengakses.
USER_AGENT_SCRAPER = (
    "Mozilla/5.0 (compatible; harga-pangan-jatim/1.0; "
    "+https://github.com/arif-is-a-dev/harga-pangan-jatim)"
)

# Jeda antar request (detik) supaya tidak membebani server pemerintah.
JEDA_ANTAR_REQUEST_DETIK = 1.5

# Berapa kali mencoba ulang kalau request gagal.
JUMLAH_PERCOBAAN_ULANG = 3

# Batas waktu menunggu jawaban server (detik).
BATAS_WAKTU_REQUEST_DETIK = 30

# ------------------------------------------------------------
# 2. Daftar wilayah (kode dari dropdown "Area" di situs)
# ------------------------------------------------------------
# Kunci = kode yang dikirim ke server, Nilai = nama yang mudah dibaca.
# Kode "" (string kosong) artinya rata-rata Provinsi Jawa Timur.
DAFTAR_WILAYAH = {
    "": "Provinsi Jawa Timur",
    "bangkalankab": "Kabupaten Bangkalan",
    "banyuwangikab": "Kabupaten Banyuwangi",
    "blitarkab": "Kabupaten Blitar",
    "bojonegorokab": "Kabupaten Bojonegoro",
    "bondowosokab": "Kabupaten Bondowoso",
    "gresikkab": "Kabupaten Gresik",
    "jemberkab": "Kabupaten Jember",
    "jombangkab": "Kabupaten Jombang",
    "kedirikab": "Kabupaten Kediri",
    "lamongankab": "Kabupaten Lamongan",
    "lumajangkab": "Kabupaten Lumajang",
    "madiunkab": "Kabupaten Madiun",
    "magetankab": "Kabupaten Magetan",
    "malangkab": "Kabupaten Malang",
    "mojokertokab": "Kabupaten Mojokerto",
    "nganjukkab": "Kabupaten Nganjuk",
    "ngawikab": "Kabupaten Ngawi",
    "pacitankab": "Kabupaten Pacitan",
    "pamekasankab": "Kabupaten Pamekasan",
    "pasuruankab": "Kabupaten Pasuruan",
    "ponorogokab": "Kabupaten Ponorogo",
    "probolinggokab": "Kabupaten Probolinggo",
    "sampangkab": "Kabupaten Sampang",
    "sidoarjokab": "Kabupaten Sidoarjo",
    "situbondokab": "Kabupaten Situbondo",
    "sumenepkab": "Kabupaten Sumenep",
    "trenggalekkab": "Kabupaten Trenggalek",
    "tubankab": "Kabupaten Tuban",
    "tulungagungkab": "Kabupaten Tulungagung",
    "batukota": "Kota Batu",
    "blitarkota": "Kota Blitar",
    "kedirikota": "Kota Kediri",
    "madiunkota": "Kota Madiun",
    "malangkota": "Kota Malang",
    "mojokertokota": "Kota Mojokerto",
    "pasuruankota": "Kota Pasuruan",
    "probolinggokota": "Kota Probolinggo",
    "surabayakota": "Kota Surabaya",
}

# Di database, kode kosong kurang enak dibaca, jadi provinsi kita beri kode "jatim".
KODE_WILAYAH_PROVINSI_DI_DATABASE = "jatim"

# ------------------------------------------------------------
# 3. Lokasi penyimpanan
# ------------------------------------------------------------
# Folder project (satu tingkat di atas folder src/)
FOLDER_PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CSV mentah per tanggal disimpan di sini (lapisan "raw").
FOLDER_DATA_MENTAH = os.path.join(FOLDER_PROJECT, "data", "raw")

# Alamat database. Kalau variabel lingkungan DATABASE_URL diisi
# (misalnya alamat PostgreSQL Supabase), itu yang dipakai.
# Kalau tidak diisi, pakai file SQLite lokal supaya mudah dicoba.
ALAMAT_DATABASE_DEFAULT = "sqlite:///" + os.path.join(FOLDER_PROJECT, "data", "harga_pangan.db")
ALAMAT_DATABASE = os.environ.get("DATABASE_URL", "")

# Kalau DATABASE_URL kosong (misalnya secret belum diisi), pakai SQLite lokal.
if ALAMAT_DATABASE.strip() == "":
    ALAMAT_DATABASE = ALAMAT_DATABASE_DEFAULT
