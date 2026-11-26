# ============================================================
# run_pipeline.py
# Pintu masuk utama: Extract -> Transform -> Load.
#
# Cara pakai (dari folder project):
#   python src/run_pipeline.py                         -> ambil data hari ini
#   python src/run_pipeline.py --tanggal 2026-11-25    -> ambil satu tanggal
#   python src/run_pipeline.py --mulai 2026-11-01 --selesai 2026-11-25   -> backfill
#   python src/run_pipeline.py --wilayah surabayakota malangkota         -> wilayah tertentu
# ============================================================

import argparse
import sys
import time
from datetime import date, datetime, timedelta, timezone

import config
from load_to_database import simpan_ke_csv, simpan_ke_database, tambahkan_waktu_scrape
from parser import baca_tabel_harga
from scraper import ambil_html_tabel_harga


def tanggal_hari_ini_wib():
    """Tanggal hari ini menurut jam WIB (UTC+7), karena server GitHub memakai UTC."""
    zona_wib = timezone(timedelta(hours=7))
    return datetime.now(zona_wib).date()


def buat_daftar_tanggal(tanggal_mulai, tanggal_selesai):
    """Membuat list tanggal dari tanggal_mulai sampai tanggal_selesai (termasuk keduanya)."""
    daftar_tanggal = []
    tanggal_sekarang = tanggal_mulai
    while tanggal_sekarang <= tanggal_selesai:
        daftar_tanggal.append(tanggal_sekarang)
        tanggal_sekarang = tanggal_sekarang + timedelta(days=1)
    return daftar_tanggal


def jalankan_untuk_satu_tanggal(tanggal_target, daftar_kode_wilayah):
    """Menjalankan seluruh pipeline untuk satu tanggal."""
    tanggal_teks = tanggal_target.strftime("%Y-%m-%d")
    print("=== Tanggal", tanggal_teks, "===")

    semua_baris_tanggal_ini = []
    jumlah_wilayah_gagal = 0

    for kode_wilayah in daftar_kode_wilayah:
        nama_wilayah = config.DAFTAR_WILAYAH[kode_wilayah]
        print("- Mengambil", nama_wilayah)

        # EXTRACT: ambil HTML dari situs
        teks_html = ambil_html_tabel_harga(tanggal_teks, kode_wilayah)
        if teks_html is None:
            jumlah_wilayah_gagal = jumlah_wilayah_gagal + 1
            continue

        # Kode kosong (provinsi) diganti "jatim" supaya jelas di database.
        kode_wilayah_untuk_database = kode_wilayah
        if kode_wilayah == "":
            kode_wilayah_untuk_database = config.KODE_WILAYAH_PROVINSI_DI_DATABASE

        # TRANSFORM: ubah HTML menjadi baris data
        baris_wilayah_ini = baca_tabel_harga(
            teks_html, tanggal_teks, kode_wilayah_untuk_database, nama_wilayah
        )
        print("  dapat", len(baris_wilayah_ini), "komoditas")
        semua_baris_tanggal_ini.extend(baris_wilayah_ini)

        # Jeda supaya sopan ke server.
        time.sleep(config.JEDA_ANTAR_REQUEST_DETIK)

    # Kalau tidak ada data sama sekali, jangan buat CSV kosong.
    if len(semua_baris_tanggal_ini) == 0:
        print("Tidak ada data yang berhasil diambil. CSV dan database tidak diubah.")
        print("Wilayah gagal:", jumlah_wilayah_gagal)
        return jumlah_wilayah_gagal

    # LOAD: simpan ke CSV dan database
    semua_baris_tanggal_ini = tambahkan_waktu_scrape(semua_baris_tanggal_ini)
    lokasi_csv = simpan_ke_csv(semua_baris_tanggal_ini, tanggal_teks)
    jumlah_tersimpan = simpan_ke_database(semua_baris_tanggal_ini)

    print("Selesai:", jumlah_tersimpan, "baris disimpan. CSV:", lokasi_csv)
    print("Wilayah gagal:", jumlah_wilayah_gagal)
    return jumlah_wilayah_gagal


def main():
    pembaca_argumen = argparse.ArgumentParser(description="Pipeline harga pangan Jawa Timur")
    pembaca_argumen.add_argument("--tanggal", help="Satu tanggal, format YYYY-MM-DD")
    pembaca_argumen.add_argument("--mulai", help="Tanggal awal backfill, format YYYY-MM-DD")
    pembaca_argumen.add_argument("--selesai", help="Tanggal akhir backfill, format YYYY-MM-DD")
    pembaca_argumen.add_argument(
        "--wilayah", nargs="+", help="Kode wilayah tertentu saja (default: semua 39 wilayah)"
    )
    argumen = pembaca_argumen.parse_args()

    # Tentukan tanggal yang mau diambil.
    if argumen.mulai and argumen.selesai:
        tanggal_mulai = date.fromisoformat(argumen.mulai)
        tanggal_selesai = date.fromisoformat(argumen.selesai)
        daftar_tanggal = buat_daftar_tanggal(tanggal_mulai, tanggal_selesai)
    elif argumen.tanggal:
        daftar_tanggal = [date.fromisoformat(argumen.tanggal)]
    else:
        daftar_tanggal = [tanggal_hari_ini_wib()]

    # Tentukan wilayah yang mau diambil.
    if argumen.wilayah:
        daftar_kode_wilayah = argumen.wilayah
    else:
        daftar_kode_wilayah = list(config.DAFTAR_WILAYAH.keys())

    total_wilayah_gagal = 0
    for tanggal_target in daftar_tanggal:
        total_wilayah_gagal = total_wilayah_gagal + jalankan_untuk_satu_tanggal(
            tanggal_target, daftar_kode_wilayah
        )

    # Kalau ada yang gagal, keluar dengan kode 1 supaya GitHub Actions menandai merah.
    if total_wilayah_gagal > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
