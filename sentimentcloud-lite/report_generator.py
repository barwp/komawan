from datetime import datetime
from io import BytesIO

from fpdf import FPDF


def build_insight(topic: str, summary: dict[str, int]) -> str:
    total = max(summary.get("total", 0), 1)
    positive = summary.get("Positif", 0)
    negative = summary.get("Negatif", 0)
    neutral = summary.get("Netral", 0)

    dominant = max(
        ("positif", positive),
        ("negatif", negative),
        ("netral", neutral),
        key=lambda item: item[1],
    )[0]

    if dominant == "positif":
        note = (
            "Sentimen publik cenderung positif. Pertahankan aspek yang disukai "
            "pengguna dan pantau komentar negatif sebagai bahan perbaikan."
        )
    elif dominant == "negatif":
        note = (
            "Sentimen publik cenderung negatif. Perlu perhatian khusus pada "
            "keluhan yang sering muncul agar kualitas layanan atau produk membaik."
        )
    else:
        note = (
            "Sentimen publik cenderung netral. Komentar belum menunjukkan arah "
            "opini yang kuat, sehingga pemantauan lanjutan masih diperlukan."
        )

    positive_pct = positive / total * 100
    negative_pct = negative / total * 100
    neutral_pct = neutral / total * 100
    return (
        f"Berdasarkan hasil analisis, sentimen publik terhadap topik \"{topic}\" "
        f"cenderung {dominant}. Komposisi sentimen: positif {positive_pct:.1f}%, "
        f"negatif {negative_pct:.1f}%, dan netral {neutral_pct:.1f}%. {note}"
    )


def generate_summary_pdf(topic: str, analysis_date: str, summary: dict[str, int]) -> bytes:
    total = max(summary.get("total", 0), 1)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 9, "Ringkasan Analisis Sentimen")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "SentimentCloud Lite", ln=True)
    pdf.ln(5)

    rows = [
        ("Nama Topik", topic),
        ("Tanggal Analisis", analysis_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Total Komentar", str(summary.get("total", 0))),
        (
            "Positif",
            f"{summary.get('Positif', 0)} ({summary.get('Positif', 0) / total * 100:.1f}%)",
        ),
        (
            "Negatif",
            f"{summary.get('Negatif', 0)} ({summary.get('Negatif', 0) / total * 100:.1f}%)",
        ),
        (
            "Netral",
            f"{summary.get('Netral', 0)} ({summary.get('Netral', 0) / total * 100:.1f}%)",
        ),
    ]

    for label, value in rows:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(45, 8, label, border=0)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, f": {value}", ln=True)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Insight Otomatis", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, build_insight(topic, summary))

    output = pdf.output(dest="S")
    if isinstance(output, bytearray):
        return bytes(output)
    if isinstance(output, str):
        return output.encode("latin-1")
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
