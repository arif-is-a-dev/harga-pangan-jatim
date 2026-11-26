-- ============================================================
-- mart_harga_mingguan
-- Ringkasan per minggu (mulai hari Senin) untuk grafik tren di dashboard.
-- ============================================================

select
    date_trunc('week', fakta.tanggal)::date   as awal_minggu,
    fakta.kode_wilayah,
    wilayah.nama_wilayah,
    wilayah.jenis_wilayah,
    fakta.id_komoditas,
    komoditas.nama_komoditas,
    komoditas.kategori,
    komoditas.satuan,
    round(avg(fakta.harga_rp), 0)             as rata_rata_harga_rp,
    min(fakta.harga_rp)                       as harga_terendah_rp,
    max(fakta.harga_rp)                       as harga_tertinggi_rp,
    count(*)                                  as jumlah_hari_ada_data
from {{ ref('fct_harga_harian') }} as fakta
left join {{ ref('dim_wilayah') }}   as wilayah
    on wilayah.kode_wilayah = fakta.kode_wilayah
left join {{ ref('dim_komoditas') }} as komoditas
    on komoditas.id_komoditas = fakta.id_komoditas
group by 1, 2, 3, 4, 5, 6, 7, 8
