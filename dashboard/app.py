# ============================================================
# app.py - Dashboard Harga Pangan Jawa Timur
#
# Menjalankan di laptop (dari folder project):
#   streamlit run dashboard/app.py
#
# Data dibaca dari data/marts/*.parquet yang dibuat oleh
# scripts/export_marts.py setelah dbt build.
# ============================================================

import os
from datetime import timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------
# 1. Pengaturan halaman
# ------------------------------------------------------------
st.set_page_config(
    page_title="Harga Pangan Jawa Timur",
    page_icon="🌶️",
    layout="wide",
)

FOLDER_DASHBOARD = os.path.dirname(os.path.abspath(__file__))
FOLDER_MARTS = os.path.join(os.path.dirname(FOLDER_DASHBOARD), "data", "marts")

KODE_PROVINSI = "jatim"
KOMODITAS_AWAL = "Cabe Rawit Merah"
WILAYAH_AWAL = ["Provinsi Jawa Timur", "Kota Surabaya", "Kota Malang", "Kabupaten Jember"]


# ------------------------------------------------------------
# 2. Membaca data (disimpan di cache supaya tidak dibaca ulang
#    setiap kali pengguna mengklik sesuatu)
# ------------------------------------------------------------
@st.cache_data(ttl=3600)
def baca_data_harian():
    lokasi_file = os.path.join(FOLDER_MARTS, "harga_harian.parquet")
    data_harian = pd.read_parquet(lokasi_file)
    data_harian["tanggal"] = pd.to_datetime(data_harian["tanggal"])
    return data_harian


@st.cache_data(ttl=3600)
def baca_data_lonjakan():
    lokasi_file = os.path.join(FOLDER_MARTS, "lonjakan_harga.parquet")
    data_lonjakan = pd.read_parquet(lokasi_file)
    data_lonjakan["tanggal"] = pd.to_datetime(data_lonjakan["tanggal"])
    return data_lonjakan


def format_rupiah(angka):
    """Contoh: 57166 -> 'Rp57.166'"""
    if pd.isna(angka):
        return "-"
    teks_angka = "{:,.0f}".format(angka)
    teks_angka = teks_angka.replace(",", ".")
    return "Rp" + teks_angka


data_harian = baca_data_harian()
data_lonjakan = baca_data_lonjakan()

tanggal_terbaru = data_harian["tanggal"].max()
tanggal_terlama = data_harian["tanggal"].min()

# ------------------------------------------------------------
# 3. Sidebar: pilihan pengguna
# ------------------------------------------------------------
st.sidebar.header("Filter")

# Daftar komoditas diurutkan berdasarkan kategori lalu nama.
daftar_komoditas_unik = data_harian[["kategori", "nama_komoditas"]].drop_duplicates()
daftar_komoditas_unik = daftar_komoditas_unik.sort_values(["kategori", "nama_komoditas"])
daftar_nama_komoditas = list(daftar_komoditas_unik["nama_komoditas"])

indeks_komoditas_awal = 0
if KOMODITAS_AWAL in daftar_nama_komoditas:
    indeks_komoditas_awal = daftar_nama_komoditas.index(KOMODITAS_AWAL)

komoditas_dipilih = st.sidebar.selectbox(
    "Komoditas", daftar_nama_komoditas, index=indeks_komoditas_awal
)

daftar_nama_wilayah = sorted(data_harian["nama_wilayah"].unique())
wilayah_dipilih = st.sidebar.multiselect(
    "Wilayah (untuk grafik tren)", daftar_nama_wilayah, default=WILAYAH_AWAL
)

rentang_tanggal = st.sidebar.date_input(
    "Rentang tanggal",
    value=(tanggal_terlama.date(), tanggal_terbaru.date()),
    min_value=tanggal_terlama.date(),
    max_value=tanggal_terbaru.date(),
)

# date_input mengembalikan 1 tanggal saat pengguna baru memilih tanggal awal.
if len(rentang_tanggal) == 2:
    tanggal_mulai = pd.Timestamp(rentang_tanggal[0])
    tanggal_selesai = pd.Timestamp(rentang_tanggal[1])
else:
    tanggal_mulai = tanggal_terlama
    tanggal_selesai = tanggal_terbaru

st.sidebar.caption(
    "Sumber: SISKAPERBAPO, Disperindag Jawa Timur. "
    "Diperbarui otomatis setiap hari."
)

# Data untuk komoditas yang dipilih saja
data_komoditas = data_harian[data_harian["nama_komoditas"] == komoditas_dipilih]
satuan_komoditas = data_komoditas["satuan"].iloc[0]

# ------------------------------------------------------------
# 4. Judul
# ------------------------------------------------------------
st.title("🌶️ Harga Pangan Jawa Timur")
st.caption(
    "Harga eceran harian bahan pokok di 38 kabupaten/kota. Data terakhir: "
    + tanggal_terbaru.strftime("%d %B %Y")
    + " · periode "
    + tanggal_terlama.strftime("%d %b %Y")
    + " – "
    + tanggal_terbaru.strftime("%d %b %Y")
)

# ------------------------------------------------------------
# 5. Kartu ringkasan (KPI)
# ------------------------------------------------------------
data_provinsi = data_komoditas[data_komoditas["kode_wilayah"] == KODE_PROVINSI]
data_provinsi = data_provinsi.sort_values("tanggal")

harga_provinsi_terbaru = None
selisih_7_hari_persen = None
if len(data_provinsi) > 0:
    baris_terbaru = data_provinsi.iloc[-1]
    harga_provinsi_terbaru = baris_terbaru["harga_rp"]

    tanggal_7_hari_lalu = baris_terbaru["tanggal"] - timedelta(days=7)
    data_7_hari_lalu = data_provinsi[data_provinsi["tanggal"] <= tanggal_7_hari_lalu]
    if len(data_7_hari_lalu) > 0:
        harga_7_hari_lalu = data_7_hari_lalu.iloc[-1]["harga_rp"]
        selisih_7_hari_persen = 100 * (harga_provinsi_terbaru - harga_7_hari_lalu) / harga_7_hari_lalu

# Harga hari terakhir di semua kab/kota (tanpa baris provinsi)
data_hari_terakhir = data_komoditas[
    (data_komoditas["tanggal"] == tanggal_terbaru)
    & (data_komoditas["kode_wilayah"] != KODE_PROVINSI)
]
data_hari_terakhir = data_hari_terakhir.sort_values("harga_rp")

tanggal_awal_7_hari = tanggal_terbaru - timedelta(days=6)
lonjakan_7_hari = data_lonjakan[data_lonjakan["tanggal"] >= tanggal_awal_7_hari]

kolom_kpi_1, kolom_kpi_2, kolom_kpi_3, kolom_kpi_4 = st.columns(4)

if selisih_7_hari_persen is None:
    teks_delta = None
else:
    teks_delta = "{:+.1f}% dari 7 hari lalu".format(selisih_7_hari_persen)

kolom_kpi_1.metric(
    "Rata-rata Jatim (/" + satuan_komoditas + ")",
    format_rupiah(harga_provinsi_terbaru),
    teks_delta,
    delta_color="inverse",  # harga naik = merah
)

if len(data_hari_terakhir) > 0:
    baris_termurah = data_hari_terakhir.iloc[0]
    baris_termahal = data_hari_terakhir.iloc[-1]
    kolom_kpi_2.metric("Termahal hari ini", format_rupiah(baris_termahal["harga_rp"]))
    kolom_kpi_2.caption("📍 " + baris_termahal["nama_wilayah"])
    kolom_kpi_3.metric("Termurah hari ini", format_rupiah(baris_termurah["harga_rp"]))
    kolom_kpi_3.caption("📍 " + baris_termurah["nama_wilayah"])
else:
    kolom_kpi_2.metric("Termahal hari ini", "-")
    kolom_kpi_3.metric("Termurah hari ini", "-")

kolom_kpi_4.metric("Lonjakan harga, 7 hari terakhir", str(len(lonjakan_7_hari)) + " kejadian")
kolom_kpi_4.caption("Semua komoditas dan wilayah")

# ------------------------------------------------------------
# 6. Tab-tab utama
# ------------------------------------------------------------
tab_tren, tab_wilayah, tab_lonjakan, tab_tentang = st.tabs(
    ["📈 Tren harga", "🗺️ Perbandingan wilayah", "🚨 Lonjakan harga", "ℹ️ Tentang"]
)

# ---- Tab 1: Tren harga ----
with tab_tren:
    st.subheader("Tren harga " + komoditas_dipilih)

    data_tren = data_komoditas[data_komoditas["nama_wilayah"].isin(wilayah_dipilih)]
    data_tren = data_tren[
        (data_tren["tanggal"] >= tanggal_mulai) & (data_tren["tanggal"] <= tanggal_selesai)
    ]

    if len(wilayah_dipilih) == 0:
        st.info("Pilih minimal satu wilayah di sidebar.")
    elif len(data_tren) == 0:
        st.info("Tidak ada data untuk pilihan ini.")
    else:
        grafik_tren = px.line(
            data_tren.sort_values("tanggal"),
            x="tanggal",
            y="harga_rp",
            color="nama_wilayah",
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={
                "tanggal": "Tanggal",
                "harga_rp": "Harga (Rp/" + satuan_komoditas + ")",
                "nama_wilayah": "Wilayah",
            },
        )
        grafik_tren.update_layout(hovermode="x unified", legend_title_text="", height=460)
        st.plotly_chart(grafik_tren, use_container_width=True)
        st.caption("Titik yang hilang berarti pasar di wilayah itu tidak melaporkan harga pada hari tersebut.")

# ---- Tab 2: Perbandingan antar wilayah ----
with tab_wilayah:
    st.subheader(
        "Harga " + komoditas_dipilih + " per kabupaten/kota, " + tanggal_terbaru.strftime("%d %B %Y")
    )

    if len(data_hari_terakhir) == 0:
        st.info("Belum ada data hari terakhir untuk komoditas ini.")
    else:
        grafik_wilayah = px.bar(
            data_hari_terakhir,
            x="harga_rp",
            y="nama_wilayah",
            orientation="h",
            color="selisih_dari_provinsi_persen",
            color_continuous_scale="RdYlGn_r",
            color_continuous_midpoint=0,
            labels={
                "harga_rp": "Harga (Rp/" + satuan_komoditas + ")",
                "nama_wilayah": "",
                "selisih_dari_provinsi_persen": "Selisih dari<br>rata-rata Jatim (%)",
            },
        )
        tinggi_grafik = 22 * len(data_hari_terakhir) + 120
        grafik_wilayah.update_layout(height=tinggi_grafik)
        st.plotly_chart(grafik_wilayah, use_container_width=True)
        st.caption("Warna merah = lebih mahal dari rata-rata Jawa Timur, hijau = lebih murah.")

# ---- Tab 3: Lonjakan harga ----
with tab_lonjakan:
    st.subheader("Lonjakan harga yang terdeteksi")
    st.markdown(
        "Lonjakan = harga hari itu **naik minimal 10%** dan **z-score ≥ 2** "
        "dibanding 30 hari sebelumnya di wilayah yang sama."
    )

    data_lonjakan_periode = data_lonjakan[
        (data_lonjakan["tanggal"] >= tanggal_mulai) & (data_lonjakan["tanggal"] <= tanggal_selesai)
    ]

    hanya_komoditas_dipilih = st.checkbox("Hanya tampilkan " + komoditas_dipilih, value=False)
    if hanya_komoditas_dipilih:
        data_lonjakan_periode = data_lonjakan_periode[
            data_lonjakan_periode["nama_komoditas"] == komoditas_dipilih
        ]

    if len(data_lonjakan_periode) == 0:
        st.info("Tidak ada lonjakan pada periode dan pilihan ini.")
    else:
        # Grafik ringkasan di atas, tabel detail di bawah (lebar penuh).
        jumlah_per_komoditas = data_lonjakan_periode.groupby("nama_komoditas").size()
        jumlah_per_komoditas = jumlah_per_komoditas.reset_index(name="jumlah_kejadian")
        jumlah_per_komoditas = jumlah_per_komoditas.sort_values("jumlah_kejadian").tail(10)

        grafik_jumlah = px.bar(
            jumlah_per_komoditas,
            x="jumlah_kejadian",
            y="nama_komoditas",
            orientation="h",
            labels={"jumlah_kejadian": "Jumlah kejadian", "nama_komoditas": ""},
            title="10 komoditas paling sering melonjak",
        )
        grafik_jumlah.update_layout(height=380)
        st.plotly_chart(grafik_jumlah, use_container_width=True)

        tabel_lonjakan = data_lonjakan_periode.sort_values(
            ["tanggal", "kenaikan_dari_rata_rata_persen"], ascending=[False, False]
        )
        tabel_lonjakan = tabel_lonjakan[
            [
                "tanggal",
                "nama_wilayah",
                "nama_komoditas",
                "harga_rp",
                "rata_rata_30_hari_rp",
                "kenaikan_dari_rata_rata_persen",
                "z_score",
            ]
        ]
        st.dataframe(
            tabel_lonjakan,
            hide_index=True,
            use_container_width=True,
            height=420,
            column_config={
                "tanggal": st.column_config.DateColumn("Tanggal", format="DD MMM YYYY"),
                "nama_wilayah": "Wilayah",
                "nama_komoditas": "Komoditas",
                "harga_rp": st.column_config.NumberColumn("Harga (Rp)", format="localized"),
                "rata_rata_30_hari_rp": st.column_config.NumberColumn("Rata-rata 30 hari (Rp)", format="localized"),
                "kenaikan_dari_rata_rata_persen": st.column_config.NumberColumn("Naik (%)", format="%.1f"),
                "z_score": st.column_config.NumberColumn("Z-score", format="%.2f"),
            },
        )

# ---- Tab 4: Tentang ----
with tab_tentang:
    st.subheader("Tentang dashboard ini")
    st.markdown(
        """
Dashboard ini adalah tahap akhir dari pipeline data **harga-pangan-jatim**:

1. **Extract**: scraper Python mengambil tabel harga harian dari
   [SISKAPERBAPO](https://siskaperbapo.jatimprov.go.id) untuk 38 kabupaten/kota + rata-rata provinsi.
2. **Load**: data mentah disimpan sebagai CSV harian di repo.
3. **Transform**: dbt + DuckDB membersihkan data, membuat tabel dimensi & fakta,
   ringkasan mingguan, dan deteksi lonjakan harga, lengkap dengan tes kualitas data.
4. **Serve**: hasil dbt diekspor ke Parquet dan ditampilkan di dashboard ini.

Pipeline berjalan otomatis setiap hari, dan dashboard ikut diperbarui setiap kali data baru masuk ke GitHub.

**Catatan data:** harga 0 atau kosong berarti pasar tidak melapor, sehingga tidak ditampilkan.
Harga yang tidak masuk akal (di bawah Rp100, biasanya salah input di sumber) disaring.
        """
    )
    st.caption("Dibuat oleh Arif Raharjo · github.com/arif-is-a-dev/harga-pangan-jatim")
