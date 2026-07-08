import re
from typing import Dict, Iterable, List, Set, Tuple

from text_preprocessing import preprocess_text


POSITIVE_EMOJIS = set("😀😃😄😁😆😊😍🥰😘😋🤩🥳👍👌🙏❤♥🔥✨💯")
NEGATIVE_EMOJIS = set("😞😔😟😕🙁☹️😣😖😫😩😭😢😡😠🤬😤🤮👎💔")

POSITIVE_BASE_WORDS = [
    "alhamdulillah",
    "aman",
    "asik",
    "bagus",
    "baik",
    "bangga",
    "bantu",
    "berhasil",
    "berkesan",
    "berkualitas",
    "bersahabat",
    "bersih",
    "betah",
    "cepat",
    "cerdas",
    "cocok",
    "efektif",
    "efisien",
    "enak",
    "favorit",
    "fix",
    "fyp",
    "fresh",
    "gampang",
    "gercep",
    "hebat",
    "hemat",
    "higienis",
    "informatif",
    "inovatif",
    "instan",
    "jadi",
    "jelas",
    "juara",
    "kencang",
    "keren",
    "komplit",
    "konsisten",
    "kreatif",
    "kuat",
    "lengkap",
    "lancar",
    "layak",
    "lega",
    "lembut",
    "lumayan",
    "mantap",
    "mantep",
    "memuaskan",
    "menarik",
    "membantu",
    "minta",
    "minat",
    "mudah",
    "murah",
    "nyaman",
    "oke",
    "ok",
    "optimal",
    "pas",
    "penasaran",
    "pengen",
    "praktis",
    "premium",
    "profesional",
    "puas",
    "ramah",
    "rapi",
    "recommended",
    "rekomendasi",
    "responsif",
    "sabar",
    "senang",
    "sesuai",
    "setuju",
    "sip",
    "simpel",
    "solutif",
    "stabil",
    "suka",
    "terbaik",
    "terjangkau",
    "terpercaya",
    "top",
    "unggul",
    "worth",
    "wow",
]

NEGATIVE_BASE_WORDS = [
    "aneh",
    "bad",
    "berantakan",
    "berat",
    "boros",
    "bocor",
    "buruk",
    "cacat",
    "capek",
    "cemen",
    "cuma",
    "cuman",
    "crash",
    "curang",
    "delay",
    "dibatalkan",
    "eror",
    "error",
    "gagal",
    "gangguan",
    "hancur",
    "hilang",
    "iri",
    "jenuh",
    "jelek",
    "kapok",
    "kasar",
    "kecewa",
    "kecil",
    "komplain",
    "kosong",
    "klemuan",
    "kelamaan",
    "kurang",
    "lemot",
    "lambat",
    "lama",
    "macet",
    "mahal",
    "mengecewakan",
    "menipu",
    "ngadat",
    "ngambek",
    "ngelag",
    "payah",
    "parah",
    "palsu",
    "panas",
    "ribet",
    "rugi",
    "rumit",
    "rusak",
    "salah",
    "sampah",
    "sempit",
    "sulit",
    "sayang",
    "takut",
    "telat",
    "tipu",
    "zonk",
]

POSITIVE_CONTEXTS = [
    "admin",
    "aplikasi",
    "barang",
    "dashboard",
    "data",
    "desain",
    "fitur",
    "grafik",
    "harga",
    "hasil",
    "informasi",
    "kualitas",
    "layanan",
    "menu",
    "produk",
    "proses",
    "respon",
    "server",
    "sistem",
    "tampilan",
    "tim",
    "ui",
    "upload",
]

NEGATIVE_CONTEXTS = [
    "admin",
    "aplikasi",
    "barang",
    "dashboard",
    "data",
    "fitur",
    "grafik",
    "harga",
    "hasil",
    "informasi",
    "koneksi",
    "kualitas",
    "layanan",
    "menu",
    "pelayanan",
    "pengiriman",
    "produk",
    "proses",
    "respon",
    "server",
    "sistem",
    "tampilan",
    "ui",
    "upload",
]

POSITIVE_EXPLICIT_PHRASES = [
    "alhamdulillah enak",
    "bagus banget",
    "bagus sekali",
    "baik banget",
    "cepat sampai",
    "harga bersahabat",
    "harga murah",
    "jadi mau",
    "jadi pengen",
    "kualitas bagus",
    "mau ini",
    "mau dong",
    "mau juga",
    "mau min",
    "menu menarik",
    "menu kaya gitu",
    "menu kayak gitu",
    "minta menu",
    "minta dong",
    "boleh juga",
    "pengen coba",
    "pengen ini",
    "pelayanan baik",
    "pelayanan cepat",
    "pelayanan ramah",
    "pengiriman cepat",
    "puas banget",
    "puas sekali",
    "seru banget",
    "sekali kali",
    "spill dong",
    "spill min",
    "sangat bagus",
    "sangat membantu",
    "sangat puas",
    "sangat rekomendasi",
    "sesuai harapan",
    "setuju banget",
    "tertarik banget",
    "tidak mengecewakan",
    "top banget",
    "worth it",
    "worth it banget",
]

NEGATIVE_EXPLICIT_PHRASES = [
    "agak kecewa",
    "belum ada",
    "belum jelas",
    "belum keluar",
    "belum sesuai",
    "barang rusak",
    "bikin kecewa",
    "bikin ribet",
    "buruk sekali",
    "error terus",
    "gagal terus",
    "harga mahal",
    "jadi takut",
    "jangan sampai",
    "jatah kecil",
    "kok belum",
    "kok gitu",
    "kok lama",
    "kok kecil",
    "kualitas buruk",
    "ga ada",
    "ga berani",
    "ga jelas",
    "ga sesuai",
    "ga suka",
    "gak ada",
    "gak berani",
    "gak jelas",
    "gak sesuai",
    "gak suka",
    "kurang bagus",
    "kurang baik",
    "kurang cepat",
    "kurang jelas",
    "kurang nyaman",
    "kurang puas",
    "lama banget",
    "lambat sekali",
    "lama amat",
    "pelayanan buruk",
    "pelayanan jelek",
    "pelayanan lambat",
    "pengiriman lama",
    "ngak ada",
    "ngak berani",
    "ngak jelas",
    "ngak sesuai",
    "ngak suka",
    "nggak ada",
    "nggak berani",
    "nggak jelas",
    "nggak sesuai",
    "nggak suka",
    "porsi kecil",
    "sangat kecewa",
    "sangat lambat",
    "sangat mahal",
    "sangat mengecewakan",
    "sangat parah",
    "susah digunakan",
    "takut gagal",
    "tidak bagus",
    "tidak berfungsi",
    "tidak jelas",
    "tidak membantu",
    "tidak nyaman",
    "tidak puas",
    "tidak ramah",
    "tidak rekomendasi",
    "tidak sesuai",
    "tidak suka",
    "tidak worth",
]

NEGATION_WORDS = {
    "belum",
    "bukan",
    "ga",
    "gak",
    "ngak",
    "nggak",
    "tidak",
    "tak",
}

NEGATION_EXCEPTIONS = {
    "tidak mengecewakan",
    "ga mengecewakan",
    "gak mengecewakan",
    "nggak mengecewakan",
    "ngak mengecewakan",
}

CONTRAST_WORDS = {
    "cuma",
    "cuman",
    "namun",
    "padahal",
    "tapi",
}

SARCASM_CUES = {
    "haha",
    "hahaha",
    "hehe",
    "hehehe",
    "lah",
    "masa",
    "wkwk",
    "wkwkwk",
    "yaelah",
}

SOFT_NEGATIVE_PATTERNS = [
    r"\bga\s+berani\b",
    r"\bgak\s+berani\b",
    r"\bngak\s+berani\b",
    r"\bnggak\s+berani\b",
    r"\bbelum\s+(ada|bisa|jelas|keluar|sesuai)\b",
    r"\bkok\s+(belum|lama|gitu|begitu)\b",
    r"\b(ko|kok)\s+(kecil|dikit|sedikit)\b",
    r"\bkenapa\s+(belum|lama|gitu|begitu)\b",
    r"\bmasa\s+(belum|gitu|begitu)\b",
    r"\b(cuma|cuman)\s+\w+\s+(kecil|dikit|sedikit|doang)\b",
    r"\b(porsi|jatah|bagian)\s+(kecil|dikit|sedikit)\b",
    r"\bkelamaan\b",
    r"\bklemuan\b",
]

SOFT_POSITIVE_PATTERNS = [
    r"\bmau\s+(ini|dong|juga|min)\b",
    r"\b(mau|pengen|ingin|pingin|request|minta)\s+(ini|coba|dong|juga|min|menu)\b",
    r"\bspill\s+(dong|min)\b",
    r"\bjadi\s+mau\b",
    r"\bjadi\s+pengen\b",
    r"\bsekali\s+kali\b",
    r"\b(kaya|kayak)\s+gitu\b",
    r"\bpenasaran\s+(dong|nih|banget)?\b",
]

POSITIVE_PREFIXES = [
    "agak",
    "cukup",
    "lumayan",
    "makin",
    "paling",
    "sangat",
    "semakin",
    "terasa",
]

NEGATIVE_PREFIXES = [
    "agak",
    "cukup",
    "makin",
    "paling",
    "sangat",
    "semakin",
    "terasa",
    "terlalu",
]

POSITIVE_SUFFIXES = [
    "banget",
    "sekali",
    "sih",
    "kok",
    "parah",
    "abis",
    "luar biasa",
    "buat saya",
]

NEGATIVE_SUFFIXES = [
    "banget",
    "sekali",
    "sih",
    "kok",
    "parah",
    "abis",
    "terus",
    "buat saya",
]

POSITIVE_VERB_PREFIXES = [
    "bikin",
    "terasa",
    "kelihatan",
    "jadi",
    "membuat",
]

NEGATIVE_VERB_PREFIXES = [
    "bikin",
    "terasa",
    "kelihatan",
    "jadi",
    "membuat",
]


def _normalize_keyword(keyword: str) -> str:
    return re.sub(r"\s+", " ", keyword.strip().lower())


def _dedupe_keywords(keywords: Iterable[str]) -> List[str]:
    normalized = {_normalize_keyword(keyword) for keyword in keywords if keyword.strip()}
    return sorted(normalized, key=lambda item: (-len(item.split()), item))


def _build_keyword_variants(
    base_words: List[str],
    contexts: List[str],
    explicit_phrases: List[str],
    prefixes: List[str],
    suffixes: List[str],
    verb_prefixes: List[str],
) -> List[str]:
    variants: Set[str] = set(explicit_phrases)
    variants.update(base_words)

    for word in base_words:
        for prefix in prefixes:
            variants.add(f"{prefix} {word}")
        for suffix in suffixes:
            variants.add(f"{word} {suffix}")
        for verb_prefix in verb_prefixes:
            variants.add(f"{verb_prefix} {word}")

    for context in contexts:
        for word in base_words:
            variants.add(f"{context} {word}")
            variants.add(f"{word} {context}")
            variants.add(f"{context} terasa {word}")
            variants.add(f"{context} sangat {word}")
            variants.add(f"{context} makin {word}")
            variants.add(f"{context} cukup {word}")

    return _dedupe_keywords(variants)


POSITIVE_KEYWORDS = _build_keyword_variants(
    POSITIVE_BASE_WORDS,
    POSITIVE_CONTEXTS,
    POSITIVE_EXPLICIT_PHRASES,
    POSITIVE_PREFIXES,
    POSITIVE_SUFFIXES,
    POSITIVE_VERB_PREFIXES,
)

NEGATIVE_KEYWORDS = _build_keyword_variants(
    NEGATIVE_BASE_WORDS,
    NEGATIVE_CONTEXTS,
    NEGATIVE_EXPLICIT_PHRASES,
    NEGATIVE_PREFIXES,
    NEGATIVE_SUFFIXES,
    NEGATIVE_VERB_PREFIXES,
)

_OVERLAPPING_KEYWORDS = set(POSITIVE_KEYWORDS) & set(NEGATIVE_KEYWORDS)
POSITIVE_KEYWORDS = [keyword for keyword in POSITIVE_KEYWORDS if keyword not in _OVERLAPPING_KEYWORDS]
NEGATIVE_KEYWORDS = [keyword for keyword in NEGATIVE_KEYWORDS if keyword not in _OVERLAPPING_KEYWORDS]


def _build_keyword_pattern(keywords: List[str]) -> re.Pattern:
    alternatives = "|".join(re.escape(keyword) for keyword in keywords)
    return re.compile(r"\b(?:" + alternatives + r")\b")


POSITIVE_PATTERN = _build_keyword_pattern(POSITIVE_KEYWORDS)
NEGATIVE_PATTERN = _build_keyword_pattern(NEGATIVE_KEYWORDS)
SOFT_NEGATIVE_PATTERN = re.compile("|".join(SOFT_NEGATIVE_PATTERNS))
SOFT_POSITIVE_PATTERN = re.compile("|".join(SOFT_POSITIVE_PATTERNS))


def _count_keyword_matches(text: str, pattern: re.Pattern) -> int:
    return len(pattern.findall(text))


def _count_social_context(text: str) -> Tuple[int, int]:
    positive_extra = len(SOFT_POSITIVE_PATTERN.findall(text))
    negative_extra = len(SOFT_NEGATIVE_PATTERN.findall(text))
    tokens = text.split()

    for index, token in enumerate(tokens):
        if token not in NEGATION_WORDS:
            continue
        window = " ".join(tokens[index : index + 4])
        if any(exception in window for exception in NEGATION_EXCEPTIONS):
            continue
        if POSITIVE_PATTERN.search(window):
            negative_extra += 2
            positive_extra -= 1

    for index, token in enumerate(tokens):
        if token not in CONTRAST_WORDS:
            continue
        after_contrast = " ".join(tokens[index + 1 :])
        if not after_contrast:
            continue
        if NEGATIVE_PATTERN.search(after_contrast) or SOFT_NEGATIVE_PATTERN.search(after_contrast):
            negative_extra += 2
        if POSITIVE_PATTERN.search(after_contrast) or SOFT_POSITIVE_PATTERN.search(after_contrast):
            positive_extra += 1

    if SARCASM_CUES.intersection(tokens) and POSITIVE_PATTERN.search(text):
        if NEGATIVE_PATTERN.search(text) or SOFT_NEGATIVE_PATTERN.search(text):
            negative_extra += 2
            positive_extra -= 1

    return max(positive_extra, 0), max(negative_extra, 0)


def _count_emoji_context(raw_text: object) -> Tuple[int, int]:
    raw = "" if raw_text is None else str(raw_text)
    positive = sum(1 for char in raw if char in POSITIVE_EMOJIS)
    negative = sum(1 for char in raw if char in NEGATIVE_EMOJIS)
    return min(positive, 3), min(negative, 3)


def analyze_comment(comment: object) -> Dict[str, object]:
    processed_comment = preprocess_text(comment)
    positive_score = _count_keyword_matches(processed_comment, POSITIVE_PATTERN)
    negative_score = _count_keyword_matches(processed_comment, NEGATIVE_PATTERN)
    positive_extra, negative_extra = _count_social_context(processed_comment)
    positive_emoji, negative_emoji = _count_emoji_context(comment)
    positive_score += positive_extra
    negative_score += negative_extra
    positive_score += positive_emoji
    negative_score += negative_emoji

    if positive_score > negative_score:
        sentiment = "Positif"
    elif negative_score > positive_score:
        sentiment = "Negatif"
    else:
        sentiment = "Netral"

    return {
        "processed_comment": processed_comment,
        "positive_score": positive_score,
        "negative_score": negative_score,
        "sentiment": sentiment,
    }


def analyze_dataframe(df):
    result_df = df.copy()
    analysis = result_df["comment"].apply(analyze_comment)
    result_df["processed_comment"] = analysis.apply(lambda item: item["processed_comment"])
    result_df["positive_score"] = analysis.apply(lambda item: item["positive_score"])
    result_df["negative_score"] = analysis.apply(lambda item: item["negative_score"])
    result_df["sentiment"] = analysis.apply(lambda item: item["sentiment"])
    return result_df
