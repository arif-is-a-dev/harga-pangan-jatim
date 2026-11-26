-- ============================================================
-- fct_harga_harian
-- Tabel fakta utama: harga per tanggal x wilayah x komoditas,
-- ditambah kolom bantu untuk analisis:
--   - harga hari sebelumnya dan persen perubahannya
--   - rata-rata 7 hari terakhir
--   - harga rata-rata provinsi di hari yang sama dan selisihnya
-- ============================================================

with harga as (

    select
        tanggal,
        kode_wilayah,
        id_komoditas,
        harga_rp
    from {{ ref('stg_harga_harian') }}

),

harga_provinsi as (

    select
        tanggal,
        id_komoditas,
        harga_rp as harga_provinsi_rp
    from harga
    where kode_wilayah = 'jatim'

),

dengan_kolom_waktu as (

    select
        harga.tanggal,
        harga.kode_wilayah,
        harga.id_komoditas,
        harga.harga_rp,

        -- Harga pada data sebelumnya (biasanya kemarin)
        lag(harga.harga_rp) over jendela_per_wilayah_komoditas
            as harga_sebelumnya_rp,

        -- Rata-rata 7 hari terakhir, termasuk hari ini
        avg(harga.harga_rp) over (
            partition by harga.kode_wilayah, harga.id_komoditas
            order by harga.tanggal
            range between interval 6 days preceding and current row
        ) as rata_rata_7_hari_rp

    from harga
    window jendela_per_wilayah_komoditas as (
        partition by harga.kode_wilayah, harga.id_komoditas
        order by harga.tanggal
    )

)

select
    dengan_kolom_waktu.tanggal,
    dengan_kolom_waktu.kode_wilayah,
    dengan_kolom_waktu.id_komoditas,
    dengan_kolom_waktu.harga_rp,
    dengan_kolom_waktu.harga_sebelumnya_rp,

    round(
        100.0 * (dengan_kolom_waktu.harga_rp - dengan_kolom_waktu.harga_sebelumnya_rp)
        / nullif(dengan_kolom_waktu.harga_sebelumnya_rp, 0),
        2
    ) as perubahan_harian_persen,

    round(dengan_kolom_waktu.rata_rata_7_hari_rp, 0) as rata_rata_7_hari_rp,

    harga_provinsi.harga_provinsi_rp,

    round(
        100.0 * (dengan_kolom_waktu.harga_rp - harga_provinsi.harga_provinsi_rp)
        / nullif(harga_provinsi.harga_provinsi_rp, 0),
        2
    ) as selisih_dari_provinsi_persen

from dengan_kolom_waktu
left join harga_provinsi
    on  harga_provinsi.tanggal = dengan_kolom_waktu.tanggal
    and harga_provinsi.id_komoditas = dengan_kolom_waktu.id_komoditas
