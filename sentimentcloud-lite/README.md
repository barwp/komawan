# SentimentCloud Lite

**SentimentCloud Lite** adalah MVP untuk menganalisis sentimen komentar media sosial dari file CSV yang diunggah pengguna.

Judul aplikasi:

> Aplikasi Analisis Sentimen Berbasis Cloud Menggunakan Data Komentar Media Sosial

Aplikasi ini tidak mengambil data langsung dari Instagram, TikTok, X/Twitter, atau platform media sosial lain. Data dianalisis dari file CSV.

## Fitur Utama

- Upload CSV komentar media sosial.
- Preview data sebelum analisis.
- Validasi kolom wajib `comment`.
- Preprocessing teks Bahasa Indonesia.
- Analisis sentimen sederhana berbasis keyword lexicon.
- Label sentimen: Positif, Negatif, Netral.
- Dashboard statistik, pie chart, bar chart, dan tabel hasil.
- Filter berdasarkan sentimen dan pencarian kata komentar.
- Download hasil analisis dalam CSV.
- Download ringkasan PDF.
- Riwayat analisis sederhana menggunakan SQLite.
- Tanpa login dan tanpa API media sosial.

## Struktur File

```text
sentimentcloud-lite/
├── app.py
├── sentiment_analyzer.py
├── text_preprocessing.py
├── database.py
├── report_generator.py
├── requirements.txt
├── Dockerfile
├── .gitignore
├── README.md
├── sample_data/
│   └── contoh_komentar.csv
└── data/
    ├── .gitkeep
    └── sentimentcloud.db
```

File `data/sentimentcloud.db` akan dibuat otomatis saat aplikasi berjalan.

## Instalasi Lokal

Pastikan Python 3.11 sudah tersedia.

```bash
cd sentimentcloud-lite
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan dengan Streamlit

```bash
streamlit run app.py
```

Aplikasi akan tersedia di:

```text
http://localhost:8501
```

## Menjalankan dengan Docker

```bash
docker build -t sentimentcloud-lite .
docker run -p 8501:8501 sentimentcloud-lite
```

Aplikasi akan tersedia di:

```text
http://localhost:8501
```

## Format CSV yang Didukung

Kolom wajib:

- `comment`

Kolom opsional:

- `username`
- `created_at`

Contoh:

```csv
username,comment,created_at
andi_01,"Produknya sangat bagus dan pengirimannya cepat",2026-06-24
budi_02,"Pelayanannya lambat dan sangat mengecewakan",2026-06-24
citra_03,"Produknya biasa saja",2026-06-24
```

Contoh data tersedia di:

```text
sample_data/contoh_komentar.csv
```

## Contoh Akun

Contoh akun tidak diperlukan karena aplikasi ini berjalan tanpa login dan tanpa autentikasi.

## Deploy Cloud

Aplikasi ini dapat dideploy ke layanan cloud yang mendukung Docker atau aplikasi Python, seperti:

- Google Cloud Run
- Railway
- Render

Untuk deploy berbasis container, gunakan `Dockerfile` yang sudah tersedia.
