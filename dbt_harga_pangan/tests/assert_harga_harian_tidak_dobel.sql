-- Tes: satu wilayah + satu komoditas hanya boleh punya satu harga per tanggal.
-- Tes lulus kalau query ini TIDAK mengembalikan baris apa pun.

select
    tanggal,
    kode_wilayah,
    id_komoditas,
    count(*) as jumlah_baris
from {{ ref('fct_harga_harian') }}
group by tanggal, kode_wilayah, id_komoditas
having count(*) > 1
