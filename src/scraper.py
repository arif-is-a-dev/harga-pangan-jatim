# ============================================================
# scraper.py
# Tugas file ini HANYA satu: mengambil HTML tabel harga dari situs.
# Membaca isi HTML dikerjakan oleh parser.py.
# ============================================================

import time

import requests

import config


def ambil_html_tabel_harga(tanggal_teks, kode_wilayah):
    """
    Mengambil HTML tabel harga untuk satu tanggal dan satu wilayah.

    tanggal_teks : string format "YYYY-MM-DD", contoh "2026-11-25"
    kode_wilayah : kode dari config.DAFTAR_WILAYAH, contoh "surabayakota"

    Mengembalikan teks HTML, atau None kalau semua percobaan gagal.
    """

    # Langkah 1: siapkan isian formulir, sama seperti yang dikirim browser.
    isian_formulir = {
        "tanggal": tanggal_teks,
        "kabkota": kode_wilayah,
        "pasar": "",  # kosong = semua pasar
    }

    # Langkah 2: siapkan header supaya server tahu siapa yang meminta.
    header_request = {
        "User-Agent": config.USER_AGENT_SCRAPER,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Langkah 3: coba kirim request, ulangi kalau gagal.
    nomor_percobaan = 1
    while nomor_percobaan <= config.JUMLAH_PERCOBAAN_ULANG:
        try:
            jawaban_server = requests.post(
                config.URL_TABEL_HARGA,
                data=isian_formulir,
                headers=header_request,
                timeout=config.BATAS_WAKTU_REQUEST_DETIK,
            )

            # Status 200 artinya berhasil.
            if jawaban_server.status_code == 200:
                return jawaban_server.text

            print(
                "  Peringatan: server menjawab status",
                jawaban_server.status_code,
                "untuk wilayah",
                kode_wilayah,
            )

        except requests.exceptions.RequestException as kesalahan:
            print("  Peringatan: request gagal untuk wilayah", kode_wilayah, "->", kesalahan)

        # Tunggu sebentar sebelum mencoba lagi (makin lama tiap percobaan).
        lama_tunggu_detik = 5 * nomor_percobaan
        print("  Mencoba lagi dalam", lama_tunggu_detik, "detik...")
        time.sleep(lama_tunggu_detik)
        nomor_percobaan = nomor_percobaan + 1

    # Semua percobaan gagal.
    return None
