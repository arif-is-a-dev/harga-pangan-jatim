-- ============================================================
-- mart_lonjakan_harga
-- Mendeteksi hari ketika harga jauh di atas kebiasaannya.
--
-- Caranya (z-score):
--   1. Hitung rata-rata dan standar deviasi harga 30 hari SEBELUM hari itu
--      (hari itu sendiri tidak ikut, supaya lonjakan tidak "menutupi dirinya")
--   2. z_score = (harga hari ini - rata-rata) / standar deviasi
--   3. Kalau z_score >= 2 DAN harga naik minimal 10% dari rata-rata,
--      hari itu ditandai sebagai lonjakan
--      (syarat 10% mencegah harga yang biasanya datar menghasilkan
--       z-score besar hanya karena naik sedikit)
-- ============================================================

with patokan as (

    select
        tanggal,
        kode_wilayah,
        id_komoditas,
        harga_rp,

        avg(harga_rp) over jendela_patokan         as rata_rata_patokan_rp,
        stddev_samp(harga_rp) over jendela_patokan as standar_deviasi_patokan_rp,
        count(harga_rp) over jendela_patokan       as jumlah_data_patokan

    from {{ ref('fct_harga_harian') }}
    window jendela_patokan as (
        partition by kode_wilayah, id_komoditas
        order by tanggal
        range between interval {{ var('jendela_hari_patokan') }} days preceding
                  and interval 1 day preceding
    )

),

dengan_z_score as (

    select
        *,
        (harga_rp - rata_rata_patokan_rp)
            / nullif(standar_deviasi_patokan_rp, 0) as z_score
    from patokan
    where jumlah_data_patokan >= {{ var('minimal_data_patokan') }}

)

select
    dengan_z_score.tanggal,
    dengan_z_score.kode_wilayah,
    wilayah.nama_wilayah,
    dengan_z_score.id_komoditas,
    komoditas.nama_komoditas,
    komoditas.kategori,
    dengan_z_score.harga_rp,
    round(dengan_z_score.rata_rata_patokan_rp, 0) as rata_rata_30_hari_rp,
    round(
        100.0 * (dengan_z_score.harga_rp - dengan_z_score.rata_rata_patokan_rp)
        / dengan_z_score.rata_rata_patokan_rp,
        2
    ) as kenaikan_dari_rata_rata_persen,
    round(dengan_z_score.z_score, 2) as z_score
from dengan_z_score
left join {{ ref('dim_wilayah') }}   as wilayah
    on wilayah.kode_wilayah = dengan_z_score.kode_wilayah
left join {{ ref('dim_komoditas') }} as komoditas
    on komoditas.id_komoditas = dengan_z_score.id_komoditas
where dengan_z_score.z_score >= {{ var('batas_z_score_lonjakan') }}
  and 100.0 * (dengan_z_score.harga_rp - dengan_z_score.rata_rata_patokan_rp)
      / dengan_z_score.rata_rata_patokan_rp >= {{ var('minimal_kenaikan_persen') }}
