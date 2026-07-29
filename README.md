# SentimentCloud Lite

SentimentCloud Lite adalah aplikasi Streamlit untuk analisis sentimen komentar media sosial dari file CSV.

## Deploy Streamlit Cloud

Gunakan file utama:

```text
streamlit_app.py
```

Dependency ada di:

```text
requirements.txt
```

## Database Cloud

Aplikasi otomatis memakai PostgreSQL cloud jika tersedia `DATABASE_URL`.

Tambahkan di **Streamlit Cloud > App settings > Secrets**:

```toml
DATABASE_URL = "postgresql://username:password@host:port/database"
```

Jika `DATABASE_URL` tidak diisi, aplikasi memakai SQLite lokal sebagai fallback.

Rekomendasi database mudah:

- Supabase PostgreSQL
- Neon PostgreSQL
- Railway PostgreSQL

## Struktur

Kode utama aplikasi ada di folder:

```text
sentimentcloud-lite/
```
