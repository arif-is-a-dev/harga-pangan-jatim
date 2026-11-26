-- ============================================================
-- mart_dashboard_harian
-- Tabel siap pakai untuk dashboard: fakta harian + nama wilayah
-- dan komoditas, supaya dashboard tidak perlu melakukan join.
-- ============================================================

select
    fakta.tanggal,
    fakta.kode_wilayah,
    wilayah.nama_wilayah,
    wilayah.jenis_wilayah,
    fakta.id_komoditas,
    komoditas.nama_komoditas,
    komoditas.kategori,
    komoditas.satuan,
    fakta.harga_rp,
    fakta.harga_sebelumnya_rp,
    fakta.perubahan_harian_persen,
    fakta.rata_rata_7_hari_rp,
    fakta.harga_provinsi_rp,
    fakta.selisih_dari_provinsi_persen
from {{ ref('fct_harga_harian') }} as fakta
left join {{ ref('dim_wilayah') }} as wilayah
    on wilayah.kode_wilayah = fakta.kode_wilayah
left join {{ ref('dim_komoditas') }} as komoditas
    on komoditas.id_komoditas = fakta.id_komoditas
