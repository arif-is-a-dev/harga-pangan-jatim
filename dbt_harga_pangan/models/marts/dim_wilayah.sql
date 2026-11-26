-- ============================================================
-- dim_wilayah
-- Satu baris per wilayah, dengan jenisnya (Kota / Kabupaten / Provinsi).
-- ============================================================

select distinct
    kode_wilayah,
    nama_wilayah,
    case
        when kode_wilayah = 'jatim'          then 'Provinsi'
        when nama_wilayah like 'Kota %'      then 'Kota'
        when nama_wilayah like 'Kabupaten %' then 'Kabupaten'
        else 'Lainnya'
    end as jenis_wilayah
from {{ ref('stg_harga_harian') }}
