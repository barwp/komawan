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
- Riwayat analisis sederhana menggunakan SQLite lokal atau PostgreSQL cloud.
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

File `data/sentimentcloud.db` akan dibuat otomatis saat aplikasi berjalan lokal tanpa `DATABASE_URL`.
Saat `DATABASE_URL` tersedia, aplikasi otomatis memakai PostgreSQL cloud.

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

- Streamlit Community Cloud
- Google Cloud Run
- Railway
- Render

Untuk deploy berbasis container, gunakan `Dockerfile` yang sudah tersedia.

## Deploy ke Streamlit Community Cloud

Untuk Streamlit Community Cloud, gunakan file utama di root repository:

```text
streamlit_app.py
```

Langkah ringkas:

1. Push project ke GitHub.
2. Buka Streamlit Community Cloud.
3. Pilih repository.
4. Isi main file path dengan `streamlit_app.py`.
5. Tambahkan secrets jika menggunakan database cloud.

## Database Cloud

Aplikasi mendukung PostgreSQL cloud melalui environment variable atau Streamlit Secrets:

```toml
DATABASE_URL = "postgresql://username:password@host:port/database"
```

Untuk Streamlit Community Cloud, simpan nilai tersebut di **App settings > Secrets**. Nama key yang direkomendasikan tetap `DATABASE_URL`.
Setelah secrets disimpan, reboot aplikasi. Di sidebar aplikasi akan muncul status:

```text
Database: PostgreSQL Cloud
Host: db.<project-ref>.supabase.co
```

Jika status masih `SQLite Lokal`, berarti `DATABASE_URL` belum terbaca oleh Streamlit.

Jika `DATABASE_URL` tidak ada, aplikasi otomatis memakai SQLite lokal di `data/sentimentcloud.db`.

Alur penyimpanan database:

- `analysis_history`: menyimpan ringkasan analisis, seperti topik, tanggal, total komentar, positif, negatif, dan netral.
- `uploaded_csv_files`: menyimpan file CSV asli yang diunggah pengguna dalam bentuk teks.
- `sentiment_results`: menyimpan hasil analisis per komentar, termasuk komentar asli, hasil preprocessing, skor positif, skor negatif, dan label sentimen.

Rekomendasi mudah untuk MVP:

- Supabase PostgreSQL
- Neon PostgreSQL
- Railway PostgreSQL

Untuk Supabase/Neon, copy connection string PostgreSQL dari dashboard lalu masukkan ke **Streamlit Cloud > App settings > Secrets**.
