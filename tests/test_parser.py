# ============================================================
# test_parser.py
# Menguji parser dengan potongan HTML asli dari situs (Surabaya, 25 Nov 2026).
# Jalankan dari folder project:  python -m pytest tests
# ============================================================

import os
import sys

# Supaya file di folder src/ bisa di-import.
FOLDER_TES = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(FOLDER_TES), "src"))

from parser import baca_tabel_harga, ubah_teks_harga_ke_angka  # noqa: E402


def baca_html_contoh():
    lokasi_file = os.path.join(FOLDER_TES, "fixtures", "sample_surabaya.html")
    with open(lokasi_file, "r", encoding="utf-8") as file_html:
        return file_html.read()


def cari_baris_berdasarkan_nama(daftar_baris, nama_dicari):
    for baris_data in daftar_baris:
        if baris_data["nama_komoditas"] == nama_dicari:
            return baris_data
    return None


def test_ubah_teks_harga_ke_angka():
    assert ubah_teks_harga_ke_angka("16.166") == 16166
    assert ubah_teks_harga_ke_angka("128.333") == 128333
    assert ubah_teks_harga_ke_angka("0") is None
    assert ubah_teks_harga_ke_angka("-") is None
    assert ubah_teks_harga_ke_angka("") is None


def test_jumlah_komoditas():
    daftar_baris = baca_tabel_harga(baca_html_contoh(), "2026-11-25", "surabayakota", "Kota Surabaya")
    # Baris kategori (BERAS, CABE, ...) dan sub-judul (Kental Manis) tidak ikut dihitung.
    assert len(daftar_baris) == 8


def test_harga_dan_kategori_beras():
    daftar_baris = baca_tabel_harga(baca_html_contoh(), "2026-11-25", "surabayakota", "Kota Surabaya")
    beras_premium = cari_baris_berdasarkan_nama(daftar_baris, "Beras Premium")
    assert beras_premium["id_komoditas"] == 2
    assert beras_premium["kategori"] == "BERAS"
    assert beras_premium["satuan"] == "kg"
    assert beras_premium["harga_rp"] == 16166


def test_harga_sekarang_bukan_harga_kemarin():
    daftar_baris = baca_tabel_harga(baca_html_contoh(), "2026-11-25", "surabayakota", "Kota Surabaya")
    cabe_keriting = cari_baris_berdasarkan_nama(daftar_baris, "Cabe Merah Keriting")
    assert cabe_keriting["harga_rp"] == 57166  # kemarin 55.000
    assert cabe_keriting["kategori"] == "CABE"


def test_komoditas_bernomor_sendiri():
    daftar_baris = baca_tabel_harga(baca_html_contoh(), "2026-11-25", "surabayakota", "Kota Surabaya")
    jagung = cari_baris_berdasarkan_nama(daftar_baris, "Jagung Pipilan Kering")
    assert jagung["kategori"] == "JAGUNG PIPILAN KERING"


def test_sub_judul_tidak_mengganti_kategori():
    daftar_baris = baca_tabel_harga(baca_html_contoh(), "2026-11-25", "surabayakota", "Kota Surabaya")
    susu_bendera = cari_baris_berdasarkan_nama(daftar_baris, "Susu Kental Manis Merk Bendera")
    assert susu_bendera["kategori"] == "SUSU"


def test_harga_kosong_menjadi_none():
    daftar_baris = baca_tabel_harga(baca_html_contoh(), "2026-11-25", "surabayakota", "Kota Surabaya")
    minyak_sederhana = cari_baris_berdasarkan_nama(daftar_baris, "Minyak Goreng Kemasan Sederhana")
    assert minyak_sederhana["harga_rp"] is None
