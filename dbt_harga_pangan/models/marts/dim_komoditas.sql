-- ============================================================
-- dim_komoditas
-- Satu baris per komoditas. Nama, kategori, dan satuan diambil
-- dari data paling baru, karena situs kadang mengubah penulisannya.
-- ============================================================

with diberi_nomor_urut as (

    select
        id_komoditas,
        nama_komoditas,
        kategori,
        satuan,
        row_number() over (
            partition by id_komoditas
            order by tanggal desc, waktu_scrape desc
        ) as urutan_terbaru
    from {{ ref('stg_harga_harian') }}

)

select
    id_komoditas,
    nama_komoditas,
    kategori,
    satuan
from diberi_nomor_urut
where urutan_terbaru = 1
