-- Tes: mencatat harga mentah yang tidak masuk akal (di bawah Rp100 atau
-- di atas Rp2.000.000). Contoh nyata: minyak goreng tercatat Rp6 di
-- Kab. Madiun, 16 Nov 2026 (salah input di sumber).
--
-- Baris seperti ini sudah disaring di stg_harga_harian, jadi tes ini
-- hanya "warn": tidak menghentikan pipeline, tapi tetap terlihat di log
-- supaya kita tahu seberapa sering sumber data salah input.

{{ config(severity = 'warn') }}

select *
from read_csv('{{ var("raw_csv_path") }}', header = true)
where harga_rp is not null
  and (harga_rp < 100 or harga_rp > 2000000)
