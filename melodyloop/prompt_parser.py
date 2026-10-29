"""
Local rule-based prompt parser and optional TF-IDF caption matcher for MelodyLoop 2.0.
Translates user natural language music descriptions into structured condition attributes
(mood, tempo, pitch register, dynamics) without external APIs or large language models.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
import numpy as np

from melodyloop.conditional_data import (
    MOOD_VOCAB,
    TEMPO_VOCAB,
    REGISTER_VOCAB,
    DYNAMICS_VOCAB,
    MOOD_TO_IDX,
    TEMPO_TO_IDX,
    REGISTER_TO_IDX,
    DYNAMICS_TO_IDX,
)

# Synonyms and keywords for rule-based parsing
MOOD_KEYWORDS = {
    "calm": [
        "calm", "peaceful", "relaxing", "relax", "gentle", "meditative", "serene",
        "tranquil", "soothing", "quiet", "ambient", "restful", "chill",
    ],
    "happy": [
        "happy", "cheerful", "joyful", "uplifting", "positive", "bright", "sunny",
        "upbeat", "lively", "playful", "glad", "delightful",
    ],
    "sad": [
        "sad", "melancholy", "melancholic", "sorrow", "mournful", "grief", "gloomy",
        "heartbroken", "depressing", "somber", "crying", "tearful",
    ],
    "energetic": [
        "energetic", "energy", "intense", "motivational", "action", "driving",
        "powerful", "vigorous", "dynamic", "punchy", "fast-paced",
    ],
    "dramatic": [
        "dramatic", "drama", "epic", "dark", "tense", "suspenseful", "heavy",
        "cinematic", "scary", "mysterious", "ominous",
    ],
    "romantic": [
        "romantic", "love", "reflective", "dream", "dreamy", "intimate",
        "sentimental", "passion", "tender", "sweet",
    ],
}

TEMPO_KEYWORDS = {
    "slow": [
        "slow", "sluggish", "adagio", "lento", "grave", "andante", "unhurried",
        "slow-paced", "leisurely", "low tempo", "slow tempo",
    ],
    "moderate": [
        "moderate", "moderato", "medium tempo", "medium speed", "mid tempo",
        "normal speed", "steady", "balanced pace", "andantino",
    ],
    "fast": [
        "fast", "rapid", "quick", "allegro", "presto", "vivace", "swift",
        "very fast", "high speed", "brisk", "speedy", "high tempo",
    ],
}

REGISTER_KEYWORDS = {
    "low": [
        "low", "bass", "deep", "low register", "low pitch", "low notes",
        "lower octave", "bottom", "heavy notes", "dark register",
    ],
    "middle": [
        "middle", "mid", "central", "medium pitch", "middle register",
        "mid-range", "normal register", "central octave",
    ],
    "high": [
        "high", "treble", "soprano", "high register", "high pitch", "high notes",
        "upper octave", "top", "sparkling", "bright register", "shrill",
    ],
}

DYNAMICS_KEYWORDS = {
    "soft": [
        "soft", "quiet", "pianissimo", "gentle", "delicate",
        "soft dynamics", "low volume", "whisper", "tender", "pp",
    ],
    "medium": [
        "medium", "moderate dynamics", "normal volume", "mezzo-forte",
        "mezzo", "balanced dynamics", "standard volume",
    ],
    "strong": [
        "strong", "loud", "forte", "fortissimo", "punchy", "powerful dynamics",
        "heavy dynamics", "hard", "aggressive", "high volume", "intense dynamics",
    ],
}

INSTRUMENT_KEYWORDS = {
    "piano": ["piano", "grand piano", "upright piano", "keys", "keyboard"],
    "guitar": ["guitar", "acoustic guitar", "electric guitar"],
    "strings": ["violin", "cello", "viola", "strings", "orchestra"],
    "drums": ["drums", "percussion", "beat"],
}


@dataclass
class ParsedPrompt:
    mood: str = "any"
    tempo: str = "any"
    pitch_register: str = "any"
    dynamics: str = "any"
    instrument: str = "piano"
    explicit_conditions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recognized_tokens: Dict[str, str] = field(default_factory=dict)
    raw_prompt: str = ""

    def to_condition_indices(self) -> Tuple[int, int, int, int]:
        """Convert string condition values to model tensor indices."""
        m_idx = MOOD_TO_IDX.get(self.mood, 0)
        t_idx = TEMPO_TO_IDX.get(self.tempo, 0)
        r_idx = REGISTER_TO_IDX.get(self.pitch_register, 0)
        d_idx = DYNAMICS_TO_IDX.get(self.dynamics, 0)
        return m_idx, t_idx, r_idx, d_idx

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mood": self.mood,
            "tempo": self.tempo,
            "pitch_register": self.pitch_register,
            "dynamics": self.dynamics,
            "instrument": self.instrument,
            "explicit_conditions": self.explicit_conditions,
            "warnings": self.warnings,
            "recognized_tokens": self.recognized_tokens,
        }


def parse_text_prompt(prompt: str) -> ParsedPrompt:
    """
    Parse a free-text music description into structured musical conditions.
    Applies case-insensitive matching, synonym resolution, and conflict checking.
    """
    cleaned = prompt.strip().lower()
    result = ParsedPrompt(raw_prompt=prompt)

    if not cleaned:
        result.warnings.append("Empty prompt provided. Using default / unconstrained conditions.")
        return result

    # 1. Match Mood
    found_moods: Set[str] = set()
    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            # Word boundary check
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, cleaned):
                found_moods.add(mood)
                result.recognized_tokens[kw] = f"mood:{mood}"
                break

    if len(found_moods) == 1:
        result.mood = list(found_moods)[0]
        result.explicit_conditions.append(f"mood={result.mood}")
    elif len(found_moods) > 1:
        # Prioritize first mentioned
        chosen = sorted(list(found_moods))[0]
        result.mood = chosen
        result.explicit_conditions.append(f"mood={chosen}")
        result.warnings.append(
            f"Multiple conflicting moods detected ({', '.join(found_moods)}). Selected '{chosen}'."
        )

    # 2. Match Tempo / Speed
    found_tempos: Set[str] = set()
    for tempo, keywords in TEMPO_KEYWORDS.items():
        for kw in keywords:
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, cleaned):
                found_tempos.add(tempo)
                result.recognized_tokens[kw] = f"tempo:{tempo}"
                break

    if len(found_tempos) == 1:
        result.tempo = list(found_tempos)[0]
        result.explicit_conditions.append(f"tempo={result.tempo}")
    elif len(found_tempos) > 1:
        chosen = sorted(list(found_tempos))[0]
        result.tempo = chosen
        result.explicit_conditions.append(f"tempo={chosen}")
        result.warnings.append(
            f"Multiple conflicting speeds detected ({', '.join(found_tempos)}). Selected '{chosen}'."
        )

    # 3. Match Pitch Register
    found_registers: Set[str] = set()
    for reg, keywords in REGISTER_KEYWORDS.items():
        for kw in keywords:
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, cleaned):
                found_registers.add(reg)
                result.recognized_tokens[kw] = f"register:{reg}"
                break

    if len(found_registers) == 1:
        result.pitch_register = list(found_registers)[0]
        result.explicit_conditions.append(f"pitch_register={result.pitch_register}")
    elif len(found_registers) > 1:
        chosen = sorted(list(found_registers))[0]
        result.pitch_register = chosen
        result.explicit_conditions.append(f"pitch_register={chosen}")
        result.warnings.append(
            f"Multiple pitch registers detected ({', '.join(found_registers)}). Selected '{chosen}'."
        )

    # 4. Match Dynamics
    found_dynamics: Set[str] = set()
    for dyn, keywords in DYNAMICS_KEYWORDS.items():
        for kw in keywords:
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, cleaned):
                found_dynamics.add(dyn)
                result.recognized_tokens[kw] = f"dynamics:{dyn}"
                break

    if len(found_dynamics) == 1:
        result.dynamics = list(found_dynamics)[0]
        result.explicit_conditions.append(f"dynamics={result.dynamics}")
    elif len(found_dynamics) > 1:
        chosen = sorted(list(found_dynamics))[0]
        result.dynamics = chosen
        result.explicit_conditions.append(f"dynamics={chosen}")
        result.warnings.append(
            f"Multiple dynamics detected ({', '.join(found_dynamics)}). Selected '{chosen}'."
        )

    # 5. Check Instruments
    for inst, keywords in INSTRUMENT_KEYWORDS.items():
        for kw in keywords:
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, cleaned):
                if inst != "piano":
                    result.warnings.append(
                        f"Non-piano instrument '{inst}' requested. MelodyLoop 2.0 generates piano-family music."
                    )
                break

    if not result.explicit_conditions:
        result.warnings.append(
            "No specific conditions recognized in prompt. Generating under default unconstrained parameters."
        )

    return result


class LocalCaptionMatcher:
    """
    Lightweight TF-IDF retriever for matching user prompts to representative
    MidiCaps training captions. Trained strictly on training-split captions.
    """

    def __init__(self, max_features: int = 1000):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.sample_captions: List[str] = []
        self.sample_meta: List[Dict[str, Any]] = []
        self.max_features = max_features

    def fit_from_json(self, json_path: str, max_samples: int = 2000):
        from sklearn.feature_extraction.text import TfidfVectorizer

        captions = []
        meta = []
        import json

        with open(json_path, "r", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                # Strictly exclude test set
                if r.get("test_set", False):
                    continue
                cap = r.get("caption", "")
                if cap and len(captions) < max_samples:
                    captions.append(cap)
                    meta.append({
                        "mood": r.get("mood", []),
                        "genre": r.get("genre", []),
                        "tempo": r.get("tempo"),
                        "tempo_word": r.get("tempo_word"),
                    })
                if len(captions) >= max_samples:
                    break

        self.sample_captions = captions
        self.sample_meta = meta

        self.vectorizer = TfidfVectorizer(max_features=self.max_features, stop_words="english")
        self.tfidf_matrix = self.vectorizer.fit_transform(captions)

    def match(self, prompt: str, top_k: int = 1) -> List[Dict[str, Any]]:
        if self.vectorizer is None or self.tfidf_matrix is None:
            return []

        prompt_vec = self.vectorizer.transform([prompt])
        from sklearn.metrics.pairwise import cosine_similarity
        sims = cosine_similarity(prompt_vec, self.tfidf_matrix).flatten()

        top_indices = np.argsort(sims)[::-1][:top_k]
        results = []
        for idx in top_indices:
            results.append({
                "caption": self.sample_captions[idx],
                "similarity": float(sims[idx]),
                "meta": self.sample_meta[idx],
            })
        return results
