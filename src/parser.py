# ============================================================
# parser.py
# Mengubah HTML tabel harga menjadi daftar baris data yang rapi.
#
# Bentuk tabel di situs:
#   - Baris KATEGORI : ada nomor ("01"), tanpa harga. Contoh: "BERAS"
#   - Baris KOMODITAS: punya <span data-commodity-id="...">. Contoh: "Beras Premium"
#   - Kadang komoditas punya nomor sendiri tanpa kategori (contoh "07 Jagung Pipilan Kering")
#   - Ada juga sub-judul tanpa nomor dan tanpa span (contoh "Kental Manis") -> dilewati
# ============================================================

from bs4 import BeautifulSoup


def ubah_teks_harga_ke_angka(teks_harga):
    """
    Mengubah teks harga gaya Indonesia menjadi angka bulat.
    Contoh: "16.166" -> 16166
    Harga "0", "-", atau kosong dianggap tidak ada data -> None.
    """
    teks_bersih = teks_harga.strip()

    # Hapus titik pemisah ribuan.
    teks_bersih = teks_bersih.replace(".", "")

    # Kalau bukan angka (misalnya "-" atau kosong), anggap tidak ada data.
    if teks_bersih.isdigit() == False:
        return None

    harga_angka = int(teks_bersih)

    # Situs menulis 0 kalau pasar tidak melaporkan harga.
    if harga_angka == 0:
        return None

    return harga_angka


def baca_tabel_harga(teks_html, tanggal_teks, kode_wilayah, nama_wilayah):
    """
    Membaca HTML dan mengembalikan list berisi dictionary, satu per komoditas.

    Setiap dictionary punya kunci:
      tanggal, kode_wilayah, nama_wilayah, id_komoditas, nama_komoditas,
      kategori, satuan, harga_rp
    """
    daftar_baris_hasil = []

    halaman = BeautifulSoup(teks_html, "html.parser")
    semua_baris_tabel = halaman.find_all("tr")

    # Kategori yang sedang aktif (berubah setiap ketemu baris kategori baru).
    kategori_sekarang = None

    for baris_tabel in semua_baris_tabel:
        semua_kolom = baris_tabel.find_all("td")

        # Baris judul tabel (<th>) tidak punya <td>, jadi dilewati.
        if len(semua_kolom) < 5:
            continue

        teks_nomor = semua_kolom[0].get_text(strip=True)
        kolom_nama = semua_kolom[1]
        span_komoditas = kolom_nama.find("span", attrs={"data-commodity-id": True})

        # ---- Kasus A: baris tanpa span = kategori atau sub-judul ----
        if span_komoditas is None:
            if teks_nomor != "":
                # Ada nomor -> ini kategori baru, contoh "BERAS"
                kategori_sekarang = kolom_nama.get_text(strip=True).upper()
            # Tidak ada nomor -> sub-judul seperti "Kental Manis", lewati saja.
            continue

        # ---- Kasus B: baris komoditas ----
        nama_komoditas = span_komoditas.get_text(strip=True)
        id_komoditas = int(span_komoditas["data-commodity-id"])

        # Komoditas yang punya nomor sendiri tidak punya kategori induk,
        # jadi kategorinya adalah namanya sendiri.
        if teks_nomor != "":
            kategori_untuk_baris_ini = nama_komoditas.upper()
            kategori_sekarang = None
        else:
            kategori_untuk_baris_ini = kategori_sekarang

        satuan = semua_kolom[2].get_text(strip=True).lower()

        # Kolom ke-5 (indeks 4) = HARGA SEKARANG.
        # Kolom HARGA KEMARIN tidak kita simpan, karena bisa dihitung
        # sendiri dari data hari sebelumnya.
        teks_harga_sekarang = semua_kolom[4].get_text(strip=True)
        harga_rupiah = ubah_teks_harga_ke_angka(teks_harga_sekarang)

        baris_data = {
            "tanggal": tanggal_teks,
            "kode_wilayah": kode_wilayah,
            "nama_wilayah": nama_wilayah,
            "id_komoditas": id_komoditas,
            "nama_komoditas": nama_komoditas,
            "kategori": kategori_untuk_baris_ini,
            "satuan": satuan,
            "harga_rp": harga_rupiah,
        }
        daftar_baris_hasil.append(baris_data)

    return daftar_baris_hasil
