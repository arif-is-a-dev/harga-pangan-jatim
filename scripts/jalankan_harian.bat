@echo off
REM ============================================================
REM jalankan_harian.bat
REM Dipanggil oleh Windows Task Scheduler setiap hari.
REM 1. Ambil harga   2. dbt build   3. Ekspor data dashboard   4. Commit   5. Push
REM Semua output dicatat ke logs\pipeline.log
REM ============================================================

REM Pindah ke folder project (satu tingkat di atas folder scripts)
cd /d "%~dp0.."

if not exist logs mkdir logs

echo. >> logs\pipeline.log
echo ===== %date% %time% ===== >> logs\pipeline.log

REM Kalau kamu memakai virtual environment, aktifkan di sini:
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat

REM Langkah 1: jalankan pipeline
python -u src\run_pipeline.py >> logs\pipeline.log 2>&1

REM Langkah 2: perbarui tabel analisis dengan dbt (data\warehouse.duckdb)
pushd dbt_harga_pangan
dbt build --profiles-dir . >> ..\logs\pipeline.log 2>&1
popd

REM Langkah 3: ekspor tabel dbt ke data\marts\*.parquet untuk dashboard
python -u scripts\export_marts.py >> logs\pipeline.log 2>&1

REM Langkah 4 dan 5: commit dan push data baru (kalau ada)
git add data\raw\*.csv data\marts\*.parquet >> logs\pipeline.log 2>&1
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "data: harga pangan %date%" >> logs\pipeline.log 2>&1
    REM Ambil dulu perubahan dari GitHub (misalnya file yang diedit lewat web)
    git pull --rebase >> logs\pipeline.log 2>&1
    git push >> logs\pipeline.log 2>&1
) else (
    echo Tidak ada data baru untuk di-commit. >> logs\pipeline.log
)
