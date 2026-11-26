# ============================================================
# export_marts.py
# Menyalin tabel hasil dbt dari data/warehouse.duckdb menjadi file
# Parquet di data/marts/. File inilah yang dibaca dashboard Streamlit,
# jadi dashboard tidak perlu menjalankan dbt sendiri.
#
# Cara pakai (dari folder project, setelah dbt build):
#   python scripts/export_marts.py
# ============================================================

import os

import duckdb

FOLDER_PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOKASI_WAREHOUSE = os.path.join(FOLDER_PROJECT, "data", "warehouse.duckdb")
FOLDER_MARTS = os.path.join(FOLDER_PROJECT, "data", "marts")

# Tabel yang diekspor. Kunci = nama tabel di DuckDB, nilai = nama file.
DAFTAR_TABEL_EKSPOR = {
    "main_marts.mart_dashboard_harian": "harga_harian.parquet",
    "main_marts.mart_harga_mingguan": "harga_mingguan.parquet",
    "main_marts.mart_lonjakan_harga": "lonjakan_harga.parquet",
}


def main():
    os.makedirs(FOLDER_MARTS, exist_ok=True)

    # read_only supaya tidak mengganggu file database.
    koneksi = duckdb.connect(LOKASI_WAREHOUSE, read_only=True)

    for nama_tabel, nama_file in DAFTAR_TABEL_EKSPOR.items():
        lokasi_file = os.path.join(FOLDER_MARTS, nama_file)

        # DuckDB membutuhkan garis miring "/" di path, juga di Windows.
        lokasi_file_untuk_duckdb = lokasi_file.replace("\\", "/")

        perintah_sql = (
            "COPY (SELECT * FROM " + nama_tabel + " ORDER BY ALL) "
            "TO '" + lokasi_file_untuk_duckdb + "' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )
        koneksi.execute(perintah_sql)

        jumlah_baris = koneksi.execute("SELECT COUNT(*) FROM " + nama_tabel).fetchall()[0][0]
        ukuran_kb = round(os.path.getsize(lokasi_file) / 1024)
        print("Ekspor", nama_tabel, "->", nama_file, "(", jumlah_baris, "baris,", ukuran_kb, "KB )")

    koneksi.close()


if __name__ == "__main__":
    main()
