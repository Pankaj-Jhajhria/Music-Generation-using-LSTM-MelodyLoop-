"""
Unit tests for MelodyLoop prompt parser and synonym extraction.
"""

from melodyloop.prompt_parser import parse_text_prompt, ParsedPrompt


def test_standard_user_prompts():
    # Prompt 1: Calm, slow, soft
    p1 = parse_text_prompt("Generate a calm, slow piano melody with soft dynamics.")
    assert p1.mood == "calm"
    assert p1.tempo == "slow"
    assert p1.dynamics == "soft"
    assert p1.pitch_register == "any"
    assert p1.instrument == "piano"
    assert len(p1.warnings) == 0

    # Prompt 2: Energetic, fast, strong
    p2 = parse_text_prompt("Create energetic piano music with fast rhythms and strong dynamics.")
    assert p2.mood == "energetic"
    assert p2.tempo == "fast"
    assert p2.dynamics == "strong"
    assert p2.pitch_register == "any"

    # Prompt 3: Melancholic, low register
    p3 = parse_text_prompt("Generate a melancholic melody in a low register.")
    assert p3.mood == "sad"
    assert p3.pitch_register == "low"
    assert p3.tempo == "any"

    # Prompt 4: Dramatic, high register, strong
    p4 = parse_text_prompt("Generate dramatic music with a high register and strong dynamics.")
    assert p4.mood == "dramatic"
    assert p4.pitch_register == "high"
    assert p4.dynamics == "strong"


def test_conflict_resolution_and_warnings():
    # Both slow and fast mentioned
    p = parse_text_prompt("A piece that starts slow then gets fast")
    assert p.tempo in ("slow", "fast")
    assert any("conflicting speeds" in w.lower() for w in p.warnings)

    # Non-piano instrument warning
    p_guitar = parse_text_prompt("Play a calm tune on electric guitar")
    assert p_guitar.mood == "calm"
    assert any("non-piano instrument" in w.lower() for w in p_guitar.warnings)

    # Empty prompt
    p_empty = parse_text_prompt("")
    assert p_empty.mood == "any"
    assert p_empty.tempo == "any"
    assert any("empty prompt" in w.lower() for w in p_empty.warnings)


def test_condition_indices_mapping():
    p = parse_text_prompt("Calm, slow, low register, soft dynamics")
    m_idx, t_idx, r_idx, d_idx = p.to_condition_indices()
    assert m_idx > 0
    assert t_idx > 0
    assert r_idx > 0
    assert d_idx > 0

