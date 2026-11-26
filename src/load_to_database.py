# ============================================================
# load_to_database.py
# Menyimpan baris data ke CSV (arsip mentah) dan ke database.
# Database bisa SQLite (lokal) atau PostgreSQL (Supabase) - kode sama.
# ============================================================

import csv
import os
from datetime import datetime

from sqlalchemy import create_engine, text

import config


NAMA_KOLOM_DATA = [
    "tanggal",
    "kode_wilayah",
    "nama_wilayah",
    "id_komoditas",
    "nama_komoditas",
    "kategori",
    "satuan",
    "harga_rp",
    "waktu_scrape",
]


def simpan_ke_csv(daftar_baris, tanggal_teks):
    """
    Menyimpan semua baris satu tanggal ke data/raw/YYYY-MM-DD.csv.
    File lama dengan tanggal yang sama akan ditimpa.
    """
    os.makedirs(config.FOLDER_DATA_MENTAH, exist_ok=True)
    lokasi_file_csv = os.path.join(config.FOLDER_DATA_MENTAH, tanggal_teks + ".csv")

    with open(lokasi_file_csv, "w", newline="", encoding="utf-8") as file_csv:
        penulis_csv = csv.DictWriter(file_csv, fieldnames=NAMA_KOLOM_DATA)
        penulis_csv.writeheader()
        for baris_data in daftar_baris:
            penulis_csv.writerow(baris_data)

    return lokasi_file_csv


def siapkan_tabel_database(mesin_database):
    """Membuat tabel kalau belum ada, memakai file sql/create_tables.sql."""
    lokasi_file_sql = os.path.join(config.FOLDER_PROJECT, "sql", "create_tables.sql")
    with open(lokasi_file_sql, "r", encoding="utf-8") as file_sql:
        perintah_sql = file_sql.read()

    with mesin_database.begin() as koneksi:
        koneksi.execute(text(perintah_sql))


def simpan_ke_database(daftar_baris):
    """
    Memasukkan baris ke tabel raw_harga_harian.
    Kalau baris dengan kunci yang sama sudah ada, harganya diperbarui
    (jadi aman menjalankan pipeline berkali-kali di hari yang sama).
    """
    if len(daftar_baris) == 0:
        return 0

    # Pastikan folder data ada (dibutuhkan kalau pakai SQLite lokal).
    os.makedirs(os.path.join(config.FOLDER_PROJECT, "data"), exist_ok=True)

    mesin_database = create_engine(config.ALAMAT_DATABASE)
    siapkan_tabel_database(mesin_database)

    perintah_insert = text(
        """
        INSERT INTO raw_harga_harian (
            tanggal, kode_wilayah, nama_wilayah, id_komoditas, nama_komoditas,
            kategori, satuan, harga_rp, waktu_scrape
        )
        VALUES (
            :tanggal, :kode_wilayah, :nama_wilayah, :id_komoditas, :nama_komoditas,
            :kategori, :satuan, :harga_rp, :waktu_scrape
        )
        ON CONFLICT (tanggal, kode_wilayah, id_komoditas)
        DO UPDATE SET
            harga_rp = excluded.harga_rp,
            waktu_scrape = excluded.waktu_scrape
        """
    )

    with mesin_database.begin() as koneksi:
        koneksi.execute(perintah_insert, daftar_baris)

    return len(daftar_baris)


def tambahkan_waktu_scrape(daftar_baris):
    """Menambahkan kolom waktu_scrape (waktu sekarang) ke setiap baris."""
    waktu_sekarang_teks = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for baris_data in daftar_baris:
        baris_data["waktu_scrape"] = waktu_sekarang_teks
    return daftar_baris
