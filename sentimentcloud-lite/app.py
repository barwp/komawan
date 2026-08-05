from datetime import datetime
from html import escape
from io import StringIO
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from database import (
    delete_history,
    fetch_history,
    init_db,
    save_history,
    save_sentiment_results,
    save_uploaded_csv,
)
from report_generator import build_insight, generate_summary_pdf
from sentiment_analyzer import analyze_dataframe


SENTIMENT_COLORS = {
    "Positif": "#22c55e",
    "Negatif": "#ef4444",
    "Netral": "#f59e0b",
}


st.set_page_config(
    page_title="SentimentCloud Lite",
    page_icon="SC",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --app-bg: #f7f8fb;
            --panel: #ffffff;
            --ink: #0f172a;
            --muted: #64748b;
            --line: #e2e8f0;
            --blue: #2563eb;
            --blue-soft: #eff6ff;
            --green: #16a34a;
            --red: #dc2626;
            --amber: #d97706;
        }
        .stApp {
            background: var(--app-bg);
            color: var(--ink);
        }
        .block-container {
            max-width: 1280px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 1rem;
        }
        .main-title {
            color: var(--ink);
            font-size: 2.15rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.25rem;
        }
        .sub-title {
            color: var(--muted);
            font-size: 1rem;
            margin-bottom: 1.2rem;
            max-width: 780px;
        }
        h1, h2, h3, h4, h5, h6, p, label, span {
            letter-spacing: 0;
        }
        h2, h3 {
            color: var(--ink);
        }
        div[data-testid="stMarkdownContainer"] p {
            color: var(--muted);
        }
        section[data-testid="stSidebar"] {
            background: #0f172a;
        }
        section[data-testid="stSidebar"] * {
            color: #e5e7eb;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            border-radius: 8px;
            padding: 0.45rem 0.6rem;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(255, 255, 255, 0.08);
        }
        .app-shell {
            background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
            margin-bottom: 1.2rem;
            padding: 1.25rem 1.35rem;
        }
        .title-row {
            align-items: flex-start;
            display: flex;
            justify-content: space-between;
            gap: 1rem;
        }
        .status-pill {
            background: #ecfeff;
            border: 1px solid #bae6fd;
            border-radius: 999px;
            color: #0369a1;
            flex: 0 0 auto;
            font-size: 0.78rem;
            font-weight: 800;
            padding: 0.35rem 0.7rem;
        }
        .section-title {
            color: var(--ink);
            font-size: 1.15rem;
            font-weight: 800;
            margin: 0 0 0.15rem;
        }
        .section-copy {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.55;
            margin: 0 0 0.85rem;
        }
        .soft-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.045);
            padding: 1rem;
        }
        .metric-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            min-height: 108px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .metric-label {
            color: var(--muted);
            font-size: 0.86rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .metric-value-row {
            align-items: baseline;
            display: flex;
            gap: 0.65rem;
            margin-top: 0.3rem;
        }
        .metric-value {
            color: var(--ink);
            font-size: 2.25rem;
            font-weight: 800;
            line-height: 1;
        }
        .metric-delta {
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 800;
            padding: 0.22rem 0.5rem;
        }
        .metric-total {
            background: #dbeafe;
            color: #1d4ed8;
        }
        .metric-positive {
            background: #dcfce7;
            color: #166534;
        }
        .metric-negative {
            background: #fee2e2;
            color: #991b1b;
        }
        .metric-neutral {
            background: #fef3c7;
            color: #854d0e;
        }
        .insight-box {
            background: var(--blue-soft);
            border: 1px solid #bfdbfe;
            border-left: 5px solid var(--blue);
            border-radius: 8px;
            color: #1e3a8a;
            font-size: 0.96rem;
            line-height: 1.65;
            margin: 1.25rem 0 1.6rem;
            padding: 1rem 1.1rem;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }
        .stButton button, .stDownloadButton button {
            border-radius: 8px;
            font-weight: 800;
        }
        div[data-testid="stFileUploader"] {
            background: #ffffff;
            border: 1px dashed #93c5fd;
            border-radius: 8px;
            padding: 0.65rem;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            border-radius: 8px;
        }
        .empty-state {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1.35rem;
        }
        .empty-title {
            color: var(--ink);
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }
        .empty-copy {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.55;
        }
        .sentiment-badge {
            display: inline-block;
            border-radius: 999px;
            padding: 0.2rem 0.55rem;
            font-size: 0.82rem;
            font-weight: 700;
        }
        .badge-positif {
            color: #166534;
            background: #dcfce7;
        }
        .badge-negatif {
            color: #991b1b;
            background: #fee2e2;
        }
        .badge-netral {
            color: #854d0e;
            background: #fef3c7;
        }
        @media (max-width: 900px) {
            .title-row {
                display: block;
            }
            .status-pill {
                display: inline-block;
                margin-top: 0.8rem;
            }
            .main-title {
                font-size: 1.7rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_session_state() -> None:
    defaults = {
        "analysis_df": None,
        "topic": "",
        "analysis_date": "",
        "summary": None,
        "selected_page": "Upload & Analisis",
        "sentiment_filter": "Semua",
        "search_filter": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def read_uploaded_csv(uploaded_file) -> Optional[pd.DataFrame]:
    if uploaded_file is None:
        return None

    try:
        return pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        st.error("File CSV kosong. Unggah file yang memiliki minimal kolom `comment`.")
    except UnicodeDecodeError:
        st.error("File CSV tidak dapat dibaca. Pastikan file menggunakan encoding UTF-8.")
    except Exception as exc:
        st.error(f"Format CSV tidak valid: {exc}")
    return None


def validate_comments_df(df: pd.DataFrame) -> bool:
    if df.empty:
        st.error("File CSV tidak memiliki data komentar.")
        return False

    if "comment" not in df.columns:
        st.error("Kolom wajib `comment` tidak ditemukan. Pastikan CSV memiliki kolom komentar.")
        return False

    valid_comment_count = df["comment"].fillna("").astype(str).str.strip().ne("").sum()
    if valid_comment_count == 0:
        st.error("Kolom `comment` kosong. Tambahkan minimal satu komentar untuk dianalisis.")
        return False

    return True


def make_summary(df: pd.DataFrame) -> dict[str, int]:
    counts = df["sentiment"].value_counts().to_dict()
    return {
        "total": int(len(df)),
        "Positif": int(counts.get("Positif", 0)),
        "Negatif": int(counts.get("Negatif", 0)),
        "Netral": int(counts.get("Netral", 0)),
    }


def calculate_percentage(value: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{value / total * 100:.1f}%"


def reset_filters() -> None:
    st.session_state.sentiment_filter = "Semua"
    st.session_state.search_filter = ""


def render_header() -> None:
    st.markdown(
        """
        <div class="app-shell">
            <div class="title-row">
                <div>
                    <div class="main-title">SentimentCloud Lite</div>
                    <div class="sub-title">Aplikasi Analisis Sentimen Berbasis Cloud Menggunakan Data Komentar Media Sosial</div>
                </div>
                <div class="status-pill">MVP Cloud Ready</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str, copy: str = "") -> None:
    copy_markup = f'<div class="section-copy">{escape(copy)}</div>' if copy else ""
    st.markdown(
        f'<div class="section-title">{escape(title)}</div>{copy_markup}',
        unsafe_allow_html=True,
    )


def render_upload_page() -> None:
    render_header()
    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        with st.container(border=True):
            render_section(
                "Upload Data",
                "Masukkan topik, unggah CSV, lalu jalankan analisis dari kolom comment.",
            )
            topic = st.text_input(
                "Nama topik atau kata kunci analisis",
                value=st.session_state.get("topic", ""),
                placeholder="Contoh: Kopi 118, Produk Baru, Layanan Kampus",
            )
            uploaded_file = st.file_uploader("Unggah file CSV", type=["csv"])

            if uploaded_file is not None:
                df = read_uploaded_csv(uploaded_file)
                if df is not None:
                    st.caption(f"{len(df):,} baris terbaca dengan {len(df.columns)} kolom.")
                    if "comment" in df.columns:
                        st.success("Kolom `comment` ditemukan. Data siap dianalisis.")
                    else:
                        st.warning("Kolom `comment` belum ditemukan. Ubah nama kolom komentar sebelum analisis.")

                    if st.button("Mulai Analisis Sentimen", type="primary", width="stretch"):
                        topic_name = topic.strip() or "Tanpa Topik"
                        if validate_comments_df(df):
                            cleaned_df = df.copy()
                            cleaned_df["comment"] = cleaned_df["comment"].fillna("").astype(str)
                            with st.spinner("Menganalisis komentar..."):
                                result_df = analyze_dataframe(cleaned_df)
                            summary = make_summary(result_df)
                            analysis_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            analysis_id = save_history(
                                topic=topic_name,
                                analysis_date=analysis_date,
                                total_comments=summary["total"],
                                positive_count=summary["Positif"],
                                negative_count=summary["Negatif"],
                                neutral_count=summary["Netral"],
                            )
                            save_uploaded_csv(
                                analysis_id=analysis_id,
                                file_name=uploaded_file.name,
                                row_count=len(cleaned_df),
                                column_count=len(cleaned_df.columns),
                                csv_content=cleaned_df.to_csv(index=False),
                            )
                            result_rows = []
                            for row_number, row in enumerate(result_df.to_dict("records"), start=1):
                                result_rows.append(
                                    {
                                        "row_number": row_number,
                                        "username": row.get("username"),
                                        "comment": row.get("comment", ""),
                                        "processed_comment": row.get("processed_comment", ""),
                                        "positive_score": row.get("positive_score", 0),
                                        "negative_score": row.get("negative_score", 0),
                                        "sentiment": row.get("sentiment", ""),
                                        "created_at": row.get("created_at"),
                                    }
                                )
                            save_sentiment_results(analysis_id, result_rows)

                            st.session_state.analysis_df = result_df
                            st.session_state.topic = topic_name
                            st.session_state.analysis_date = analysis_date
                            st.session_state.summary = summary
                            st.session_state.sentiment_filter = "Semua"
                            st.session_state.search_filter = ""
                            st.success("Analisis selesai. Buka halaman Dashboard untuk melihat hasil lengkap.")

    with right:
        with st.container(border=True):
            render_section(
                "Preview CSV",
                "Gunakan preview untuk memastikan kolom dan isi komentar sudah sesuai.",
            )
            if uploaded_file is None:
                st.markdown(
                    """
                    <div class="empty-state">
                        <div class="empty-title">Belum ada file diunggah</div>
                        <div class="empty-copy">Format minimal CSV membutuhkan kolom comment. Kolom username dan created_at bersifat opsional.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif df is not None:
                st.dataframe(df.head(12), width="stretch", hide_index=True)


def render_metrics(summary: dict[str, int]) -> None:
    total = summary["total"]
    cards = [
        ("Total Komentar", summary["total"], "100%", "metric-total"),
        ("Positif", summary["Positif"], calculate_percentage(summary["Positif"], total), "metric-positive"),
        ("Negatif", summary["Negatif"], calculate_percentage(summary["Negatif"], total), "metric-negative"),
        ("Netral", summary["Netral"], calculate_percentage(summary["Netral"], total), "metric-neutral"),
    ]
    cols = st.columns(4)
    for col, (label, value, percentage, tone_class) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{escape(label)}</div>
                    <div class="metric-value-row">
                        <div class="metric-value">{value}</div>
                        <div class="metric-delta {tone_class}">{percentage}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    left, right, reset_col = st.columns([1, 2, 0.8])
    with left:
        sentiment_filter = st.selectbox(
            "Filter sentimen",
            ["Semua", "Positif", "Negatif", "Netral"],
            key="sentiment_filter",
        )
    with right:
        search_filter = st.text_input(
            "Cari kata pada komentar",
            placeholder="Masukkan kata kunci komentar",
            key="search_filter",
        )
    with reset_col:
        st.write("")
        st.write("")
        st.button("Reset Filter", width="stretch", on_click=reset_filters)

    filtered_df = df.copy()
    if sentiment_filter != "Semua":
        filtered_df = filtered_df[filtered_df["sentiment"] == sentiment_filter]
    if search_filter.strip():
        query = search_filter.strip().lower()
        filtered_df = filtered_df[
            filtered_df["comment"].fillna("").astype(str).str.lower().str.contains(query, na=False, regex=False)
        ]
    return filtered_df


def render_charts(df: pd.DataFrame) -> None:
    chart_df = (
        df["sentiment"]
        .value_counts()
        .rename_axis("sentiment")
        .reset_index(name="jumlah")
        .sort_values("sentiment")
    )

    left, right = st.columns(2)
    with left:
        pie_fig = px.pie(
            chart_df,
            names="sentiment",
            values="jumlah",
            title="Distribusi Sentimen",
            color="sentiment",
            color_discrete_map=SENTIMENT_COLORS,
            hole=0.35,
        )
        pie_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            legend_title_text="",
            margin=dict(l=10, r=10, t=55, b=10),
        )
        st.plotly_chart(pie_fig, use_container_width=True)
    with right:
        bar_fig = px.bar(
            chart_df,
            x="sentiment",
            y="jumlah",
            title="Jumlah Sentimen",
            color="sentiment",
            color_discrete_map=SENTIMENT_COLORS,
            text="jumlah",
        )
        bar_fig.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Jumlah",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            margin=dict(l=10, r=10, t=55, b=10),
        )
        bar_fig.update_yaxes(gridcolor="#e2e8f0")
        st.plotly_chart(bar_fig, use_container_width=True)


def style_sentiment_table(df: pd.DataFrame):
    def sentiment_color(value):
        if value == "Positif":
            return "background-color: #dcfce7; color: #166534; font-weight: 700"
        if value == "Negatif":
            return "background-color: #fee2e2; color: #991b1b; font-weight: 700"
        if value == "Netral":
            return "background-color: #fef3c7; color: #854d0e; font-weight: 700"
        return ""

    return df.style.map(sentiment_color, subset=["sentiment"])


def render_dashboard_page() -> None:
    render_header()
    df = st.session_state.analysis_df
    summary = st.session_state.summary

    if df is None or summary is None:
        st.info("Belum ada hasil analisis. Unggah CSV dan jalankan analisis dari halaman Upload & Analisis.")
        return

    render_section(f"Hasil Analisis: {st.session_state.topic}", f"Tanggal analisis: {st.session_state.analysis_date}")
    render_metrics(summary)
    st.markdown(
        f'<div class="insight-box">{escape(build_insight(st.session_state.topic, summary))}</div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        render_section("Visualisasi Sentimen")
        render_charts(df)

    with st.container(border=True):
        render_section("Eksplorasi Komentar", "Filter data berdasarkan sentimen atau cari kata tertentu pada komentar.")
        filtered_df = apply_filters(df)
        st.caption(f"Menampilkan {len(filtered_df):,} dari {len(df):,} komentar.")

        display_columns = [
            column
            for column in [
                "username",
                "comment",
                "created_at",
                "processed_comment",
                "positive_score",
                "negative_score",
                "sentiment",
            ]
            if column in filtered_df.columns
        ]
        display_df = filtered_df[display_columns]
        if "sentiment" in display_df.columns:
            st.dataframe(style_sentiment_table(display_df), width="stretch", hide_index=True)
        else:
            st.dataframe(display_df, width="stretch", hide_index=True)

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    pdf_bytes = generate_summary_pdf(st.session_state.topic, st.session_state.analysis_date, summary)

    with st.container(border=True):
        render_section("Unduh Hasil")
        download_left, download_right = st.columns(2)
        with download_left:
            st.download_button(
                "Download Hasil CSV",
                data=csv_buffer.getvalue().encode("utf-8"),
                file_name=f"hasil_sentimen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                width="stretch",
            )
        with download_right:
            st.download_button(
                "Download Ringkasan PDF",
                data=pdf_bytes,
                file_name=f"ringkasan_sentimen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                width="stretch",
            )


def render_history_page() -> None:
    render_header()
    st.subheader("Riwayat Analisis")
    history = fetch_history()

    if not history:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-title">Belum ada riwayat analisis</div>
                <div class="empty-copy">Riwayat akan muncul setelah pengguna menjalankan analisis dari halaman Upload & Analisis.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    history_df = pd.DataFrame(history)
    renamed_df = history_df.rename(
        columns={
            "topic": "Nama Topik",
            "analysis_date": "Tanggal Analisis",
            "total_comments": "Total Komentar",
            "positive_count": "Positif",
            "negative_count": "Negatif",
            "neutral_count": "Netral",
        }
    )
    st.dataframe(
        renamed_df[
            [
                "Nama Topik",
                "Tanggal Analisis",
                "Total Komentar",
                "Positif",
                "Negatif",
                "Netral",
            ]
        ],
        width="stretch",
        hide_index=True,
    )

    with st.container(border=True):
        render_section("Kelola Riwayat")
        options = {
            f"{row['topic']} - {row['analysis_date']}": row["id"]
            for row in history
        }
        selected_label = st.selectbox("Pilih riwayat", list(options.keys()))
        if st.button("Hapus Riwayat Terpilih", type="secondary"):
            delete_history(options[selected_label])
            st.success("Riwayat berhasil dihapus.")
            st.rerun()


def render_about_page() -> None:
    render_header()
    st.subheader("Tentang Aplikasi")
    st.write(
        """
        SentimentCloud Lite adalah MVP analisis sentimen komentar media sosial berbasis CSV.
        Aplikasi ini menggunakan preprocessing teks sederhana, lexicon Bahasa Indonesia,
        visualisasi Plotly, dan penyimpanan riwayat dengan SQLite.
        """
    )
    st.write("Aplikasi ini tidak menggunakan login, API media sosial, GPU, atau model machine learning besar.")
    st.markdown(
        """
        **Format CSV minimal**

        - Kolom wajib: `comment`
        - Kolom opsional: `username`, `created_at`
        """
    )


def main() -> None:
    init_db()
    apply_styles()
    ensure_session_state()

    page = st.sidebar.radio(
        "Menu",
        ["Upload & Analisis", "Dashboard", "Riwayat Analisis", "Tentang Aplikasi"],
        key="selected_page",
    )
    st.sidebar.divider()
    st.sidebar.markdown("**SentimentCloud Lite**")
    st.sidebar.caption("Analisis sentimen CSV berbasis cloud.")

    if page == "Upload & Analisis":
        render_upload_page()
    elif page == "Dashboard":
        render_dashboard_page()
    elif page == "Riwayat Analisis":
        render_history_page()
    else:
        render_about_page()


if __name__ == "__main__":
    main()
