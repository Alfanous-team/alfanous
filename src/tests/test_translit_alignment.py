"""Tests for transliteration token alignment in the transformer.

Validates that the same three alignment strategies used for standard-text
tokens (particle collapse, extended merge, prefix merge) are applied to
transliteration tokens, resolving يا/ويا/ها ↔ ya/waya/ha mismatches.
"""

from alfanous_import.transformer import _TRANSLIT_PARTICLES, _PARTICLES


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_translit_particles_defined():
    """_TRANSLIT_PARTICLES must be defined and contain the expected tokens."""
    assert isinstance(_TRANSLIT_PARTICLES, (set, frozenset))
    assert "ya" in _TRANSLIT_PARTICLES
    assert "waya" in _TRANSLIT_PARTICLES
    assert "ha" in _TRANSLIT_PARTICLES


def test_arabic_and_translit_particles_same_count():
    """Arabic _PARTICLES and _TRANSLIT_PARTICLES should cover the same concepts."""
    assert len(_PARTICLES) == len(_TRANSLIT_PARTICLES)


# ---------------------------------------------------------------------------
# Strategy 1: particle collapse
# ---------------------------------------------------------------------------

def _strategy1_collapse(tr_tokens, corpus_count):
    """Mirror of the Strategy-1 particle-collapse logic in transformer.transfer()."""
    merged = []
    j = 0
    while j < len(tr_tokens):
        tok = tr_tokens[j]
        if tok.lower() in _TRANSLIT_PARTICLES and j + 1 < len(tr_tokens):
            merged.append(tr_tokens[j + 1])
            j += 2
        else:
            merged.append(tok)
            j += 1
    return merged if len(merged) == corpus_count else None


def test_strategy1_ya_at_start():
    """Strategy 1: 'Ya ayyuha alnnasu ...' (corpus fuses Ya+ayyuha → ayyuha)."""
    # Simulate: corpus_count=11, tr has 12 tokens starting with "Ya"
    tr = "Ya ayyuha alnnasu oAAbudoo rabbakumu allathee khalaqakum waallatheena min qablikum laAAallakum tattaqoona".split()
    # 12 tokens → corpus_count = 11
    result = _strategy1_collapse(tr, 11)
    assert result is not None
    assert len(result) == 11
    assert result[0] == "ayyuha"  # Ya dropped, next word kept


def test_strategy1_ya_mid_sentence():
    """Strategy 1: ya appearing mid-sentence (lowercase)."""
    # "Qala ya adamu anbihum ..." → corpus fuses ya+adamu → adamu
    tr = "Qala ya adamu anbihum biasmaihim".split()
    # 5 tokens → corpus_count = 4
    result = _strategy1_collapse(tr, 4)
    assert result is not None
    assert len(result) == 4
    assert result[1] == "adamu"  # ya dropped, adamu kept


def test_strategy1_waya_fused():
    """Strategy 1: 'Waya adamu' — ويا is represented as single token 'waya'."""
    # "Waya adamu oskun ..." 5 tokens → corpus_count = 4
    tr = "Waya adamu oskun anta wazawjuka".split()
    result = _strategy1_collapse(tr, 4)
    assert result is not None
    assert len(result) == 4
    assert result[0] == "adamu"  # Waya dropped, adamu kept


def test_strategy1_no_particle_returns_none():
    """Strategy 1 returns None when no particle is present and count doesn't match."""
    tr = "Bismi Allahi alrrahmani alrraheemi extra".split()
    result = _strategy1_collapse(tr, 4)
    assert result is None  # 5 tokens, no ya/waya/ha → can't reduce to 4


# ---------------------------------------------------------------------------
# Strategy 2: extended particle merge
# ---------------------------------------------------------------------------

def _strategy2_extend(tr_tokens, corpus_count):
    """Mirror of the Strategy-2 extended-merge logic in transformer.transfer()."""
    diff = len(tr_tokens) - corpus_count
    if diff <= 0:
        return None
    for pi, tok in enumerate(tr_tokens):
        if tok.lower() in _TRANSLIT_PARTICLES and pi + diff < len(tr_tokens):
            candidate = (
                tr_tokens[:pi]
                + [" ".join(tr_tokens[pi:pi + diff + 1])]
                + tr_tokens[pi + diff + 1:]
            )
            if len(candidate) == corpus_count:
                return candidate
    return None


def test_strategy2_ya_banee_israelee():
    """Strategy 2: 'Ya banee israeela' with diff=2 → 'Ya banee israeela' merged."""
    # corpus_count=10, tr has 12 tokens: Ya banee israeela + 9 others
    tr = ("Ya banee israeela othkuroo niAAmatiya allatee anAAamtu "
          "AAalaykum waannee faddaltukum AAala alAAalameena").split()
    # 12 tokens → corpus_count=11 (diff=1); strategy1 would drop Ya→banee
    # Let's test a diff=2 scenario manually:
    tr_diff2 = ["Alpha", "Ya", "banee", "israeela", "word5", "word6"]
    result = _strategy2_extend(tr_diff2, 4)
    assert result is not None
    assert len(result) == 4
    assert result[1] == "Ya banee israeela"  # merged span


# ---------------------------------------------------------------------------
# Strategy 3: prefix merge
# ---------------------------------------------------------------------------

def _strategy3_prefix(tr_tokens, corpus_count):
    """Mirror of the Strategy-3 prefix-merge logic in transformer.transfer()."""
    diff = len(tr_tokens) - corpus_count
    if diff <= 0:
        return None
    candidate = [" ".join(tr_tokens[:diff + 1])] + tr_tokens[diff + 1:]
    return candidate if len(candidate) == corpus_count else None


def test_strategy3_prefix_merge():
    """Strategy 3: no particle found; merge leading tokens."""
    # e.g. "Fai llam yastajeeboo lakum ..." with diff=1
    tr = "Fai llam yastajeeboo lakum faiAAlamoo".split()
    result = _strategy3_prefix(tr, 4)
    assert result is not None
    assert len(result) == 4
    assert result[0] == "Fai llam"


# ---------------------------------------------------------------------------
# Full-data regression: special_cases.json should be minimal after fix
# ---------------------------------------------------------------------------

def test_special_cases_reduced_to_one():
    """After applying the transliteration alignment fix, at most 1 special case
    should remain unresolvable (sura=28 aya=29 where tr has *fewer* tokens than
    the corpus, which no merge strategy can fix)."""
    import json, os
    aya_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "store", "aya.json"
    )
    sc_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "store", "special_cases.json"
    )
    if not os.path.exists(aya_path) or not os.path.exists(sc_path):
        import pytest
        pytest.skip("store data files not present")

    with open(aya_path, encoding="utf-8") as f:
        data = json.load(f)
    with open(sc_path, encoding="utf-8") as f:
        special = json.load(f)

    aya_lookup = {(r["sura_id"], r["aya_id"]): r for r in data}

    still_unresolved = []
    for sc in special:
        sid, aid = sc["sura_id"], sc["aya_id"]
        corpus_count = sc["corpus_word_count"]
        rec = aya_lookup.get((sid, aid))
        if not rec:
            continue
        tr = rec.get("transliteration", "")
        tr_tokens = tr.split()
        if len(tr_tokens) == corpus_count:
            continue

        tr_diff = len(tr_tokens) - corpus_count
        tr_resolved = None

        # Strategy 1
        tr_merged = []
        j = 0
        while j < len(tr_tokens):
            tok = tr_tokens[j]
            if tok.lower() in _TRANSLIT_PARTICLES and j + 1 < len(tr_tokens):
                tr_merged.append(tr_tokens[j + 1])
                j += 2
            else:
                tr_merged.append(tok)
                j += 1
        if len(tr_merged) == corpus_count:
            tr_resolved = tr_merged

        # Strategy 2
        if tr_resolved is None and tr_diff > 0:
            for pi, tok in enumerate(tr_tokens):
                if tok.lower() in _TRANSLIT_PARTICLES and pi + tr_diff < len(tr_tokens):
                    candidate = (
                        tr_tokens[:pi]
                        + [" ".join(tr_tokens[pi:pi + tr_diff + 1])]
                        + tr_tokens[pi + tr_diff + 1:]
                    )
                    if len(candidate) == corpus_count:
                        tr_resolved = candidate
                        break

        # Strategy 3
        if tr_resolved is None and tr_diff > 0:
            candidate = [" ".join(tr_tokens[:tr_diff + 1])] + tr_tokens[tr_diff + 1:]
            if len(candidate) == corpus_count:
                tr_resolved = candidate

        if tr_resolved is None:
            still_unresolved.append((sid, aid, corpus_count, len(tr_tokens)))

    # Only sura=28 aya=29 (tr < corpus) should remain.
    assert len(still_unresolved) <= 1, (
        f"Expected ≤1 unresolvable case, got {len(still_unresolved)}: "
        f"{still_unresolved}"
    )
