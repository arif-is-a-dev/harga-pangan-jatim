@echo off
REM ============================================================
REM jalankan_harian.bat
REM Dipanggil oleh Windows Task Scheduler setiap hari.
REM 1. Ambil harga hari ini   2. Commit CSV   3. Push ke GitHub
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

REM Langkah 2 dan 3: commit dan push CSV baru (kalau ada)
git add data\raw\*.csv >> logs\pipeline.log 2>&1
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "data: harga pangan %date%" >> logs\pipeline.log 2>&1
    git push >> logs\pipeline.log 2>&1
) else (
    echo Tidak ada CSV baru untuk di-commit. >> logs\pipeline.log
)
