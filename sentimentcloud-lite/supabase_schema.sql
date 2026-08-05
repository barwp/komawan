-- SentimentCloud Lite - Supabase database flow
-- Jalankan di Supabase SQL Editor jika perlu membuat ulang schema.

create table if not exists public.analysis_history (
  id bigserial primary key,
  topic text not null,
  analysis_date text not null,
  total_comments integer not null check (total_comments >= 0),
  positive_count integer not null check (positive_count >= 0),
  negative_count integer not null check (negative_count >= 0),
  neutral_count integer not null check (neutral_count >= 0),
  created_at timestamptz not null default now()
);

alter table public.analysis_history enable row level security;

create index if not exists idx_analysis_history_created_at
  on public.analysis_history (created_at desc);

create index if not exists idx_analysis_history_topic
  on public.analysis_history (topic);

comment on table public.analysis_history is
  'Riwayat ringkas hasil analisis SentimentCloud Lite dari aplikasi Streamlit cloud.';

comment on column public.analysis_history.topic is
  'Nama topik analisis yang dimasukkan pengguna.';

comment on column public.analysis_history.analysis_date is
  'Tanggal analisis dari aplikasi, disimpan sebagai teks agar kompatibel dengan kode Streamlit saat ini.';

comment on column public.analysis_history.total_comments is
  'Total komentar pada file CSV yang dianalisis.';

comment on column public.analysis_history.positive_count is
  'Jumlah komentar berlabel Positif.';

comment on column public.analysis_history.negative_count is
  'Jumlah komentar berlabel Negatif.';

comment on column public.analysis_history.neutral_count is
  'Jumlah komentar berlabel Netral.';

create table if not exists public.uploaded_csv_files (
  id bigserial primary key,
  analysis_id bigint not null references public.analysis_history(id) on delete cascade,
  file_name text not null,
  row_count integer not null check (row_count >= 0),
  column_count integer not null check (column_count >= 0),
  csv_content text not null,
  uploaded_at timestamptz not null default now()
);

alter table public.uploaded_csv_files enable row level security;

create index if not exists idx_uploaded_csv_files_analysis_id
  on public.uploaded_csv_files (analysis_id);

comment on table public.uploaded_csv_files is
  'File CSV asli yang diunggah pengguna dan diproses oleh SentimentCloud Lite.';

comment on column public.uploaded_csv_files.csv_content is
  'Isi CSV asli dalam format teks. Untuk produksi, file besar lebih baik dipindahkan ke Cloud Storage.';

create table if not exists public.sentiment_results (
  id bigserial primary key,
  analysis_id bigint not null references public.analysis_history(id) on delete cascade,
  row_number integer not null check (row_number > 0),
  username text,
  comment text not null,
  processed_comment text not null,
  positive_score integer not null check (positive_score >= 0),
  negative_score integer not null check (negative_score >= 0),
  sentiment text not null check (sentiment in ('Positif', 'Negatif', 'Netral')),
  created_at text,
  analyzed_at timestamptz not null default now()
);

alter table public.sentiment_results enable row level security;

create index if not exists idx_sentiment_results_analysis_id
  on public.sentiment_results (analysis_id);

create index if not exists idx_sentiment_results_sentiment
  on public.sentiment_results (sentiment);

comment on table public.sentiment_results is
  'Hasil analisis sentimen per komentar dari file CSV yang diunggah.';

comment on column public.sentiment_results.comment is
  'Komentar asli dari CSV.';

comment on column public.sentiment_results.processed_comment is
  'Komentar setelah preprocessing teks.';
