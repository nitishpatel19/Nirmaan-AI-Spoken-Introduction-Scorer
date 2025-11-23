
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import re
from collections import Counter

WORD_RE = re.compile(r"[A-Za-z']+")

def tokenize(text: str) -> List[str]:
    return WORD_RE.findall(text.lower())

SALUTATION_PATTERNS = {
    "excellent": {"phrases": [
        "i am excited to", "i'm excited to",
        "it is my pleasure", "it's my pleasure",
        "i am very happy to", "i'm very happy to",
        "i am glad to", "i'm glad to",
    ], "score": 5},
    "good": {"phrases": [
        "good morning", "good afternoon", "good evening",
        "good day", "greetings",
    ], "score": 4},
    "normal": {"phrases": ["hi ", "hello ", "hey "], "score": 2},
    "none": {"phrases": [], "score": 0},
}

MUST_HAVE_SLOTS = {
    "name": ["my name is", "i am ", "i'm "],
    "age": ["years old", "year old"],
    "class_or_grade": ["class ", "grade ", "standard ", "i study in", "i am studying in"],
    "school": ["school", "college", "university"],
    "hobbies_or_interests_or_goals": [
        "my hobby", "my hobbies", "i like to", "i love to",
        "my interest", "my interests",
        "i want to become", "i want to be", "my dream is",
        "my goal is", "my aim is",
    ],
}
MUST_HAVE_SLOT_SCORE = 4

GOOD_TO_HAVE_SLOTS = {
    "family_background": ["my family", "we are a family", "my father", "my mother", "my parents"],
    "origin_location": ["i am from", "i'm from", "i belong to", "i come from"],
    "thanks_or_closing": ["thank you", "thanks for listening", "that's all about me"],
    "school_highlights": ["i study at", "i am studying at", "my school name is"],
    "extra_curricular": ["sports", "music", "dance", "competition", "club"],
}
GOOD_TO_HAVE_SLOT_SCORE = 2

FLOW_MAX_SCORE = 5
FLOW_STAGES = [
    ("salutation", ["good morning", "good afternoon", "good evening", "hi ", "hello ", "hey "]),
    ("name", ["my name is", "i am ", "i'm "]),
    ("basic_details", ["years old", "year old", "class ", "grade ", "standard ", "i study in"]),
    ("family_or_origin", ["my family", "my father", "my mother", "i am from", "i'm from"]),
    ("hobbies_or_goals", ["my hobby", "my hobbies", "my goal", "my aim", "i want to be", "i want to become"]),
]

SPEECH_RATE_BUCKETS = [
    (161, float("inf"), 2),
    (141, 160, 6),
    (111, 140, 10),
    (81, 110, 6),
    (0, 80, 2),
]
SPEECH_RATE_MAX = 10

TTR_BUCKETS = [
    (0.9, 1.0, 10),
    (0.7, 0.89, 8),
    (0.5, 0.69, 6),
    (0.3, 0.49, 4),
    (0.0, 0.29, 2),
]
TTR_MAX = 10

FILLER_WORDS = [
    "um", "uh", "er", "ah", "like", "you know", "kind of", "sort of",
    "basically", "actually", "literally", "so yeah",
]
FILLER_BUCKETS = [
    (0, 3, 15),
    (4, 6, 12),
    (7, 9, 9),
    (10, 12, 6),
    (13, float("inf"), 3),
]
CLARITY_MAX = 15

ENGAGEMENT_BUCKETS = [
    (0.9, 1.0, 15),
    (0.7, 0.89, 12),
    (0.5, 0.69, 9),
    (0.3, 0.49, 6),
    (0.0, 0.29, 3),
]
ENGAGEMENT_MAX = 15

POSITIVE_WORDS = {
    "excited", "happy", "glad", "honoured", "honored",
    "proud", "eager", "interested", "grateful", "thankful",
    "delighted", "thrilled", "joyful", "enthusiastic",
}
NEGATIVE_WORDS = {
    "sad", "upset", "angry", "bored", "unhappy",
    "nervous", "anxious", "scared", "afraid",
}

@dataclass
class CriterionScore:
    name: str
    max_score: float
    score: float
    details: Dict[str, Any]

    def to_dict(self):
        d = asdict(self)
        d["score_normalized_0_1"] = round(self.score / self.max_score, 3) if self.max_score else None
        return d

def score_salutation(text: str) -> CriterionScore:
    t = text.lower() + " "
    tier = "none"
    phrase = None
    score = 0
    for name, cfg in SALUTATION_PATTERNS.items():
        for p in cfg["phrases"]:
            if p in t:
                tier = name
                phrase = p
                score = cfg["score"]
                break
        if phrase:
            break
    return CriterionScore("Salutation quality", SALUTATION_PATTERNS["excellent"]["score"], score,
                          {"tier": tier, "matched_phrase": phrase})

def _slot_present(t: str, patterns: List[str]) -> bool:
    return any(p in t for p in patterns)

def score_keywords(text: str):
    t = text.lower()
    must_hits, must_score = {}, 0
    for slot, pats in MUST_HAVE_SLOTS.items():
        present = _slot_present(t, pats)
        must_hits[slot] = present
        if present:
            must_score += MUST_HAVE_SLOT_SCORE

    good_hits, good_score = {}, 0
    for slot, pats in GOOD_TO_HAVE_SLOTS.items():
        present = _slot_present(t, pats)
        good_hits[slot] = present
        if present:
            good_score += GOOD_TO_HAVE_SLOT_SCORE

    return [
        CriterionScore("Core details (must-have keywords)",
                       MUST_HAVE_SLOT_SCORE*len(MUST_HAVE_SLOTS),
                       must_score, {"slots": must_hits}),
        CriterionScore("Additional flavour (good-to-have details)",
                       GOOD_TO_HAVE_SLOT_SCORE*len(GOOD_TO_HAVE_SLOTS),
                       good_score, {"slots": good_hits}),
    ]

def score_flow(text: str) -> CriterionScore:
    t = text.lower()
    positions = {}
    for name, patterns in FLOW_STAGES:
        pos_list = []
        for p in patterns:
            i = t.find(p)
            if i != -1:
                pos_list.append(i)
        positions[name] = min(pos_list) if pos_list else None
    idxs = [p for p in positions.values() if p is not None]
    ordered = idxs == sorted(idxs) and len(idxs) >= 2
    score = FLOW_MAX_SCORE if ordered else 0
    return CriterionScore("Flow / structure", FLOW_MAX_SCORE, score,
                          {"stage_positions": positions, "is_ordered": ordered})

def score_speech_rate(tokens: List[str], duration_seconds: Optional[float]) -> CriterionScore:
    if not duration_seconds or duration_seconds <= 0:
        return CriterionScore(
            "Speech rate (WPM) – requires audio duration",
            SPEECH_RATE_MAX,
            0.0,
            {"wpm": None, "bucket": None, "note": "duration_seconds not provided", "not_applicable": True},
        )
    wpm = len(tokens) / (duration_seconds / 60.0)
    label, score = None, 0.0
    for low, high, s in SPEECH_RATE_BUCKETS:
        if low <= wpm <= high:
            label, score = f"{low}–{high}", float(s)
            break
    return CriterionScore("Speech rate (WPM)", SPEECH_RATE_MAX, score,
                          {"wpm": round(wpm, 2), "bucket": label})

def score_ttr(tokens: List[str]) -> CriterionScore:
    if not tokens:
        return CriterionScore("Vocabulary richness (TTR)", TTR_MAX, 0.0, {"ttr": 0.0})
    unique = set(tokens)
    ttr = len(unique) / len(tokens)
    label, score = None, 0.0
    for low, high, s in TTR_BUCKETS:
        if low <= ttr <= high:
            label, score = f"{low}–{high}", float(s)
            break
    return CriterionScore("Vocabulary richness (Type–Token Ratio)", TTR_MAX, score,
                          {"ttr": round(ttr, 3), "bucket": label})

def score_clarity(tokens: List[str]) -> CriterionScore:
    if not tokens:
        return CriterionScore("Clarity (filler word rate)", CLARITY_MAX, 0.0,
                              {"filler_count": 0, "rate_per_100": 0.0})
    token_str = " ".join(tokens)
    filler_count = 0
    for phrase in [fw for fw in FILLER_WORDS if " " in fw]:
        filler_count += token_str.count(phrase)
    single = {fw for fw in FILLER_WORDS if " " not in fw}
    cnt = Counter(tokens)
    filler_count += sum(cnt[w] for w in single)
    rate = filler_count * 100.0 / max(len(tokens), 1)
    label, score = None, 0.0
    for low, high, s in FILLER_BUCKETS:
        if low <= rate <= high:
            label, score = f"{low}–{high}", float(s)
            break
    return CriterionScore("Clarity (filler words)", CLARITY_MAX, score,
                          {"filler_count": filler_count,
                           "rate_per_100_words": round(rate, 2),
                           "bucket": label})

def score_engagement(tokens: List[str]) -> CriterionScore:
    if not tokens:
        return CriterionScore("Engagement / positivity", ENGAGEMENT_MAX, 0.0, {"positivity": 0.0})
    s = set(tokens)
    pos = sum(1 for w in s if w in POSITIVE_WORDS)
    neg = sum(1 for w in s if w in NEGATIVE_WORDS)
    total = pos + neg
    positivity = 0.5 if total == 0 else pos / total
    label, score = None, 0.0
    for low, high, s in ENGAGEMENT_BUCKETS:
        if low <= positivity <= high:
            label, score = f"{low}–{high}", float(s)
            break
    return CriterionScore("Engagement / positivity", ENGAGEMENT_MAX, score,
                          {"positivity_index_0_1": round(positivity, 3),
                           "bucket": label,
                           "positive_hits": pos,
                           "negative_hits": neg})

def evaluate_transcript(transcript: str, duration_seconds: Optional[float] = None):
    text = transcript.strip()
    tokens = tokenize(text)
    criteria = []
    criteria.append(score_salutation(text))
    criteria.extend(score_keywords(text))
    criteria.append(score_flow(text))
    criteria.append(score_speech_rate(tokens, duration_seconds))
    criteria.append(score_ttr(tokens))
    criteria.append(score_clarity(tokens))
    criteria.append(score_engagement(tokens))

    raw_total = sum(c.score for c in criteria)
    raw_max = sum(c.max_score for c in criteria if not c.details.get("not_applicable", False))
    overall = 0.0 if raw_max == 0 else raw_total / raw_max * 100.0

    meta = {
        "word_count": len(tokens),
        "duration_seconds": duration_seconds,
        "raw_total": raw_total,
        "raw_max": raw_max,
    }

    return {
        "overall_score": round(overall, 2),
        "max_score": 100.0,
        "criteria": [c.to_dict() for c in criteria],
        "meta": meta,
    }

if __name__ == "__main__":
    s = ("Good morning, my name is Aparna. I am 13 years old and I study in class 8. "
         "I am from Hyderabad and I live with my family. My hobbies are reading and playing badminton. "
         "My goal is to become a scientist. Thank you for listening.")
    print(evaluate_transcript(s, duration_seconds=60))
