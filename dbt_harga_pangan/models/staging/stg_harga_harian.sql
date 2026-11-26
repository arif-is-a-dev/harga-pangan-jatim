-- ============================================================
-- stg_harga_harian
-- Membaca semua CSV mentah lalu membersihkannya:
--   1. Tipe kolom dipastikan benar
--   2. Harga kosong (pasar tidak melapor) dan harga tidak masuk akal
--      (di bawah Rp100, biasanya salah input di sumber) dibuang
--   3. Kalau ada baris dobel, ambil hasil scrape paling baru
-- ============================================================

with data_mentah as (

    select *
    from read_csv(
        '{{ var("raw_csv_path") }}',
        header = true,
        columns = {
            'tanggal': 'DATE',
            'kode_wilayah': 'VARCHAR',
            'nama_wilayah': 'VARCHAR',
            'id_komoditas': 'INTEGER',
            'nama_komoditas': 'VARCHAR',
            'kategori': 'VARCHAR',
            'satuan': 'VARCHAR',
            'harga_rp': 'INTEGER',
            'waktu_scrape': 'TIMESTAMP'
        }
    )

),

data_dibersihkan as (

    select
        tanggal,
        trim(kode_wilayah)                as kode_wilayah,
        trim(nama_wilayah)                as nama_wilayah,
        id_komoditas,
        trim(nama_komoditas)              as nama_komoditas,
        upper(trim(kategori))             as kategori,
        lower(trim(satuan))               as satuan,
        harga_rp,
        waktu_scrape
    from data_mentah
    where harga_rp is not null
      and harga_rp >= 100

),

diberi_nomor_urut as (

    select
        *,
        row_number() over (
            partition by tanggal, kode_wilayah, id_komoditas
            order by waktu_scrape desc
        ) as urutan_terbaru
    from data_dibersihkan

)

select
    tanggal,
    kode_wilayah,
    nama_wilayah,
    id_komoditas,
    nama_komoditas,
    kategori,
    satuan,
    harga_rp,
    waktu_scrape
from diberi_nomor_urut
where urutan_terbaru = 1
