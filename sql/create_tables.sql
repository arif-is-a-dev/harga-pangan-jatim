-- ============================================================
-- Tabel mentah (lapisan "raw").
-- Satu baris = harga satu komoditas, di satu wilayah, pada satu tanggal.
-- Kunci utama mencegah data dobel kalau pipeline dijalankan ulang.
-- ============================================================

CREATE TABLE IF NOT EXISTS raw_harga_harian (
    tanggal         DATE         NOT NULL,
    kode_wilayah    VARCHAR(40)  NOT NULL,
    nama_wilayah    VARCHAR(100) NOT NULL,
    id_komoditas    INTEGER      NOT NULL,
    nama_komoditas  VARCHAR(150) NOT NULL,
    kategori        VARCHAR(100),
    satuan          VARCHAR(40),
    harga_rp        INTEGER,               -- NULL = pasar tidak melaporkan harga
    waktu_scrape    TIMESTAMP    NOT NULL,
    PRIMARY KEY (tanggal, kode_wilayah, id_komoditas)
);
