import re
import math
import unicodedata
from typing import Dict, Any, List, Set

# Vietnamese prefix particles often omitted or added by learners
VIETNAMESE_PREFIX_PARTICLES = {
    "sự", "tính", "việc", "cuộc", "cái", "con", "người", "nhà",
    "nơi", "chỗ", "đồ", "vật", "được", "bị", "làm", "khiến", "tình trạng"
}

# Common synonym mappings for vocabulary learning
SYNONYM_GROUPS: List[Set[str]] = [
    {"kiên trì", "bền chí", "kiên nhẫn", "bền bỉ", "nhẫn nại", "chịu khó", "kiên cường"},
    {"phổ biến", "thông thường", "khắp nơi", "rộng rãi", "đại trà", "quen thuộc", "ở khắp mọi nơi", "có mặt khắp nơi"},
    {"quan trọng", "thiết yếu", "cốt yếu", "chủ chốt", "then chốt", "trọng yếu"},
    {"thành công", "đạt được", "thắng lợi", "thành tựu", "thành đạt"},
    {"thất bại", "hỏng", "bại", "đổ vỡ", "thua cuộc"},
    {"thông minh", "sáng dạ", "nhanh trí", "lanh lợi", "khôn ngoan", "tài giỏi"},
    {"khó khăn", "gian nan", "vất vả", "trở ngại", "thử thách", "gian nan vất vả"},
    {"nhanh", "mau", "chóng", "lẹ", "tốc độ", "nhanh chóng", "mau chóng"},
    {"chậm", "từ từ", "chậm chạp", "chậm trễ", "trì trệ"},
    {"to lớn", "khổng lồ", "vĩ đại", "rộng lớn", "bao la", "to bự"},
    {"nhỏ bé", "bé nhỏ", "tí hon", "ít ỏi", "nhỏ nhắn"},
    {"đẹp", "xinh", "xinh xắn", "xinh đẹp", "dễ nhìn", "ưa nhìn", "tuyệt đẹp"},
    {"xấu", "tệ", "xấu xí", "dở", "kém", "tồi tệ"},
    {"bắt đầu", "khởi đầu", "mở đầu", "tiến hành", "bắt tay vào"},
    {"kết thúc", "hoàn thành", "chấm dứt", "xong", "kết liễu", "ngừng"},
    {"tìm kiếm", "tìm", "lùng", "tra cứu", "săn tìm"},
    {"giúp đỡ", "hỗ trợ", "cứu trợ", "giúp", "tiếp sức"},
    {"bảo vệ", "gìn giữ", "phòng hộ", "che chở", "bảo tồn"},
    {"phát triển", "mở rộng", "tiến bộ", "nâng cao", "tăng trưởng", "phát đạt"},
    {"cải thiện", "nâng cao", "tiến bộ", "sửa đổi", "hoàn thiện", "trau dồi"},
    {"người đi bộ", "khách bộ hành", "người đi đường"},
    {"nguy hiểm", "nguy hại", "rủi ro", "hiểm họa", "khôn lường"},
    {"an toàn", "bảo đảm", "yên tâm", "chắc chắn", "vững chắc"},
    {"thân thiện", "hòa đồng", "gần gũi", "niềm nở", "cởi mở"},
    {"chính xác", "chuẩn xác", "đúng đắn", "đúng", "chuẩn"},
    {"mạnh mẽ", "kiên cường", "vững vàng", "mạnh", "khỏe mạnh"}
]

def normalize_vietnamese_text(text: str) -> str:
    """Normalize text: lowercase, NFKC, remove punctuation."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text.strip().lower())
    # Replace punctuation with spaces
    text = re.sub(r"[.,/#!$%^&*;:{}=\-_`~()?\"'\[\]\\<>+]", " ", text)
    # Collapse multiple whitespaces
    return " ".join(text.split())

def strip_vietnamese_particles(text: str) -> str:
    """Strip leading grammatical particles like 'sự', 'tính', 'việc'."""
    tokens = text.split()
    while tokens and tokens[0] in VIETNAMESE_PREFIX_PARTICLES:
        tokens = tokens[1:]
    return " ".join(tokens)

def split_definition_senses(definition: str) -> List[str]:
    """Split definition into individual senses/meanings."""
    if not definition:
        return []
    # Split by semicolon, comma, slash, pipe, newline
    raw_parts = re.split(r"[;,/|\n()]", definition)
    senses = []
    for part in raw_parts:
        cleaned = normalize_vietnamese_text(part)
        if cleaned and len(cleaned) > 1:
            senses.append(cleaned)
    if not senses:
        senses = [normalize_vietnamese_text(definition)]
    return senses

def get_char_and_word_vector(text: str, n_char: int = 3) -> Dict[str, float]:
    """
    Build frequency vector combining:
    - Character n-grams (subwords) for typo and morphology tolerance
    - Word unigrams and bigrams for lexical/phrase semantics
    """
    vec: Dict[str, float] = {}
    tokens = text.split()
    
    # Word unigrams (weight: 1.5)
    for w in tokens:
        key = f"w:{w}"
        vec[key] = vec.get(key, 0.0) + 1.5

    # Word bigrams (weight: 2.0)
    for i in range(len(tokens) - 1):
        bg = f"{tokens[i]}_{tokens[i+1]}"
        key = f"bg:{bg}"
        vec[key] = vec.get(key, 0.0) + 2.0

    # Character n-grams (weight: 1.0)
    compact_text = text.replace(" ", "")
    if len(compact_text) >= n_char:
        for i in range(len(compact_text) - n_char + 1):
            ngram = compact_text[i:i+n_char]
            key = f"c:{ngram}"
            vec[key] = vec.get(key, 0.0) + 1.0

    return vec

def vector_cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """Compute cosine similarity between two feature vectors."""
    if not vec1 or not vec2:
        return 0.0

    dot_product = 0.0
    for k, v1 in vec1.items():
        if k in vec2:
            dot_product += v1 * vec2[k]

    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0

    return min(1.0, max(0.0, dot_product / (norm1 * norm2)))

def token_jaccard_similarity(text1: str, text2: str) -> float:
    """Compute Jaccard token overlap between two texts."""
    tokens1 = set(text1.split())
    tokens2 = set(text2.split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    return intersection / union if union > 0 else 0.0

def are_synonyms(text1: str, text2: str) -> bool:
    """Check if text1 and text2 match any synonym dictionary group."""
    core1 = strip_vietnamese_particles(text1)
    core2 = strip_vietnamese_particles(text2)
    for group in SYNONYM_GROUPS:
        in1 = any(core1 == s or core1 in s or s in core1 for s in group)
        in2 = any(core2 == s or core2 in s or s in core2 for s in group)
        if in1 and in2:
            return True
    return False

def calculate_vietnamese_semantic_similarity(
    user_text: str, target_definition: str, threshold: float = 0.52
) -> Dict[str, Any]:
    """
    Evaluates Vietnamese meaning similarity between user input and target definition.
    Combines:
    1. Direct & Substring matching across multi-sense definitions
    2. Core particle stripping (e.g. 'sự kiên trì' -> 'kiên trì')
    3. Synonym dictionary matching
    4. Subword character & word n-gram Vector Embedding Cosine Similarity
    5. Token Jaccard overlap
    """
    user_norm = normalize_vietnamese_text(user_text)
    if not user_norm:
        return {
            "is_similar": False,
            "similarity_score": 0.0,
            "percentage": 0,
            "matched_sense": "",
            "feedback": "Chưa nhập nghĩa tiếng Việt"
        }

    user_core = strip_vietnamese_particles(user_norm)
    senses = split_definition_senses(target_definition)

    best_score = 0.0
    best_sense = ""

    user_vec = get_char_and_word_vector(user_norm)

    for sense in senses:
        sense_norm = normalize_vietnamese_text(sense)
        sense_core = strip_vietnamese_particles(sense_norm)

        # 1. Exact match or Core match
        if user_norm == sense_norm or user_core == sense_core:
            score = 1.0
        # 2. Substring containment
        elif user_core and (user_core in sense_core or sense_core in user_core):
            score = max(0.90, len(user_core) / max(len(sense_core), 1))
        # 3. Synonym matching
        elif are_synonyms(user_norm, sense_norm):
            score = 0.92
        else:
            # 4. Vector Embedding Cosine + Token Jaccard
            sense_vec = get_char_and_word_vector(sense_norm)
            cos_sim = vector_cosine_similarity(user_vec, sense_vec)
            jac_sim = token_jaccard_similarity(user_norm, sense_norm)
            score = (cos_sim * 0.65) + (jac_sim * 0.35)

        if score > best_score:
            best_score = score
            best_sense = sense

    is_similar = best_score >= threshold
    pct = int(round(best_score * 100))

    if best_score >= 0.90:
        feedback = "Chính xác hoàn toàn! (Tương đồng 90-100%)"
    elif best_score >= threshold:
        feedback = f"Chấp nhận: Tương đồng ngữ nghĩa cao ({pct}%)"
    else:
        feedback = f"Chưa sát nghĩa (Độ tương đồng: {pct}%)"

    return {
        "is_similar": is_similar,
        "similarity_score": round(best_score, 3),
        "percentage": pct,
        "matched_sense": best_sense,
        "feedback": feedback
    }
