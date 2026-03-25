"""Tests for word sub-schema configuration and facet field catalogue.

These tests validate schema changes that do NOT require a built index:
- word_standard and lemma are KEYWORD type in fields.json
- root, lemma, type, pos, gender, case, state, derivation are facet_allowed
- chapter, topic, subtopic are ID type in fields.json (exact-match filtering)
- _WORD_ALL_INDEXED_FIELDS includes word_standard and lemma
- _WORD_FACET_FIELDS contains the expected set of morphological facet fields
- _TRANS_FACET_FIELDS contains sura_id, aya_id, trans_id, trans_lang
- _AYA_FACET_FIELDS contains the expected aya-level facet fields
"""

import json
import os
import pytest

from alfanous import paths as _paths

_STORE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(_paths.__file__), "..", "..", "store")
) + os.sep
_FIELDS_JSON = _STORE_PATH + "fields.json"


@pytest.fixture(scope="module")
def fields_by_name():
    with open(_FIELDS_JSON) as f:
        fields = json.load(f)
    return {fld["name"]: fld for fld in fields if fld.get("search_name")}


# ---------------------------------------------------------------------------
# Existing field-type tests
# ---------------------------------------------------------------------------

def test_word_standard_is_keyword(fields_by_name):
    """word_standard must be declared as KEYWORD in fields.json."""
    assert fields_by_name["word_standard"]["type"] == "KEYWORD", (
        "word_standard should be KEYWORD so it is searchable via MultifieldParser"
    )


def test_lemma_is_keyword(fields_by_name):
    """lemma must be declared as KEYWORD in fields.json."""
    assert fields_by_name["lemma"]["type"] == "KEYWORD", (
        "lemma should be KEYWORD in fields.json"
    )


# ---------------------------------------------------------------------------
# chapter / topic / subtopic must be ID so exact-match filtering works
# ---------------------------------------------------------------------------

def test_chapter_is_id(fields_by_name):
    """chapter must be declared as ID in fields.json for exact-match filtering."""
    assert fields_by_name["chapter"]["type"] == "ID", (
        "chapter should be ID so filter=chapter:value works correctly"
    )


def test_topic_is_id(fields_by_name):
    """topic must be declared as ID in fields.json for exact-match filtering."""
    assert fields_by_name["topic"]["type"] == "ID", (
        "topic should be ID so filter=topic:value works correctly"
    )


def test_subtopic_is_id(fields_by_name):
    """subtopic must be declared as ID in fields.json for exact-match filtering."""
    assert fields_by_name["subtopic"]["type"] == "ID", (
        "subtopic should be ID so filter=subtopic:value works correctly"
    )


# ---------------------------------------------------------------------------
# facet_allowed flags
# ---------------------------------------------------------------------------

def test_root_facet_allowed(fields_by_name):
    """root must have facet_allowed=true in fields.json."""
    assert fields_by_name["root"].get("facet_allowed") is True, (
        "root should have facet_allowed=true in fields.json"
    )


def test_lemma_facet_allowed(fields_by_name):
    """lemma must have facet_allowed=true in fields.json."""
    assert fields_by_name["lemma"].get("facet_allowed") is True, (
        "lemma should have facet_allowed=true in fields.json"
    )


def test_type_facet_allowed(fields_by_name):
    """type must have facet_allowed=true in fields.json."""
    assert fields_by_name["type"].get("facet_allowed") is True, (
        "type should have facet_allowed=true in fields.json"
    )


@pytest.mark.parametrize("field_name", ["pos", "gender", "case", "state", "derivation"])
def test_word_morphological_fields_facet_allowed(fields_by_name, field_name):
    """Word morphological fields shown in the facet UI must have facet_allowed=true."""
    assert fields_by_name[field_name].get("facet_allowed") is True, (
        f"{field_name} should have facet_allowed=true in fields.json"
    )


@pytest.mark.parametrize("field_name", ["chapter", "topic", "subtopic"])
def test_aya_theme_fields_facet_allowed(fields_by_name, field_name):
    """Aya-level theme fields must have facet_allowed=true in fields.json."""
    assert fields_by_name[field_name].get("facet_allowed") is True, (
        f"{field_name} should have facet_allowed=true in fields.json"
    )


# ---------------------------------------------------------------------------
# _WORD_ALL_INDEXED_FIELDS membership
# ---------------------------------------------------------------------------

def test_word_standard_in_word_all_indexed_fields():
    """word_standard must be in _WORD_ALL_INDEXED_FIELDS."""
    from alfanous.outputs import _WORD_ALL_INDEXED_FIELDS
    assert "word_standard" in _WORD_ALL_INDEXED_FIELDS, (
        "word_standard must be in _WORD_ALL_INDEXED_FIELDS so the word "
        "MultifieldParser includes it as a default search field"
    )


def test_lemma_in_word_all_indexed_fields():
    """lemma must be in _WORD_ALL_INDEXED_FIELDS (not just a facet field)."""
    from alfanous.outputs import _WORD_ALL_INDEXED_FIELDS
    assert "lemma" in _WORD_ALL_INDEXED_FIELDS, (
        "lemma must be in _WORD_ALL_INDEXED_FIELDS so it is searchable via "
        "the word MultifieldParser"
    )


# ---------------------------------------------------------------------------
# _WORD_FACET_FIELDS — the expanded set shown in the word-facet UI
# ---------------------------------------------------------------------------

_EXPECTED_WORD_FACET_FIELDS = frozenset({
    "root", "type", "pos", "lemma", "case", "state", "derivation", "gender",
    "number", "person", "form", "voice", "aspect", "mood",
})


def test_word_facet_fields_set():
    """_WORD_FACET_FIELDS must contain the expected morphological facet fields."""
    from alfanous.outputs import _WORD_FACET_FIELDS
    assert _WORD_FACET_FIELDS == _EXPECTED_WORD_FACET_FIELDS, (
        f"_WORD_FACET_FIELDS should be {_EXPECTED_WORD_FACET_FIELDS!r}; "
        f"got {_WORD_FACET_FIELDS!r}"
    )


@pytest.mark.parametrize("field_name", sorted(_EXPECTED_WORD_FACET_FIELDS))
def test_word_facet_field_membership(field_name):
    """Each expected word facet field must be present in _WORD_FACET_FIELDS."""
    from alfanous.outputs import _WORD_FACET_FIELDS
    assert field_name in _WORD_FACET_FIELDS


# ---------------------------------------------------------------------------
# _TRANS_FACET_FIELDS — translation child-doc facet fields
# ---------------------------------------------------------------------------

def test_trans_facet_fields_contains_sura_id():
    """_TRANS_FACET_FIELDS must contain sura_id."""
    from alfanous.outputs import _TRANS_FACET_FIELDS
    assert "sura_id" in _TRANS_FACET_FIELDS


def test_trans_facet_fields_contains_aya_id():
    """_TRANS_FACET_FIELDS must contain aya_id."""
    from alfanous.outputs import _TRANS_FACET_FIELDS
    assert "aya_id" in _TRANS_FACET_FIELDS


def test_trans_facet_fields_contains_trans_id():
    """_TRANS_FACET_FIELDS must contain trans_id."""
    from alfanous.outputs import _TRANS_FACET_FIELDS
    assert "trans_id" in _TRANS_FACET_FIELDS


def test_trans_facet_fields_contains_trans_lang():
    """_TRANS_FACET_FIELDS must contain trans_lang."""
    from alfanous.outputs import _TRANS_FACET_FIELDS
    assert "trans_lang" in _TRANS_FACET_FIELDS


# ---------------------------------------------------------------------------
# _AYA_FACET_FIELDS — aya-level facet field catalogue
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("field_name", [
    "sura_id", "juz", "chapter", "topic", "subtopic", "sura_type",
])
def test_aya_facet_fields_membership(field_name):
    """Key aya-level fields must be present in _AYA_FACET_FIELDS."""
    from alfanous.outputs import _AYA_FACET_FIELDS
    assert field_name in _AYA_FACET_FIELDS


# ---------------------------------------------------------------------------
# show?query=facets catalogue in self._all
# ---------------------------------------------------------------------------

def test_show_facets_structure():
    """show?query=facets must return a dict keyed by unit with field lists."""
    from alfanous.outputs import Raw, _WORD_FACET_FIELDS, _TRANS_FACET_FIELDS, _AYA_FACET_FIELDS

    r = Raw.__new__(Raw)
    r._facets = {
        "aya": sorted(_AYA_FACET_FIELDS),
        "word": sorted(_WORD_FACET_FIELDS),
        "translation": sorted(_TRANS_FACET_FIELDS),
    }
    assert set(r._facets.keys()) == {"aya", "word", "translation"}
    assert "sura_id" in r._facets["aya"]
    assert "root" in r._facets["word"]
    assert "sura_id" in r._facets["translation"]
    assert "aya_id" in r._facets["translation"]


# ---------------------------------------------------------------------------
# Transformer schema-builder tests
# ---------------------------------------------------------------------------

def test_schema_builder_lemma_keyword():
    """Transformer.build_schema must produce a KEYWORD field for lemma."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import KEYWORD
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["lemma"], KEYWORD), (
        "Transformer.build_schema must produce KEYWORD for lemma"
    )


def test_schema_builder_word_standard_keyword():
    """Transformer.build_schema must produce a KEYWORD field for word_standard."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import KEYWORD
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["word_standard"], KEYWORD), (
        "Transformer.build_schema must produce KEYWORD for word_standard"
    )


def test_schema_builder_chapter_id():
    """Transformer.build_schema must produce an ID field for chapter."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import ID
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["chapter"], ID), (
        "Transformer.build_schema must produce ID for chapter so that "
        "filter=chapter:value works"
    )


def test_schema_builder_topic_id():
    """Transformer.build_schema must produce an ID field for topic."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import ID
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["topic"], ID), (
        "Transformer.build_schema must produce ID for topic so that "
        "filter=topic:value works"
    )


def test_schema_builder_subtopic_id():
    """Transformer.build_schema must produce an ID field for subtopic."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import ID
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["subtopic"], ID), (
        "Transformer.build_schema must produce ID for subtopic so that "
        "filter=subtopic:value works"
    )


# ---------------------------------------------------------------------------
# constants.py — PGN values (person/gender/number use English descriptions)
# ---------------------------------------------------------------------------

def test_pgn_person_english():
    """PGN person codes must map to English descriptions."""
    from alfanous_import.quran_corpus_reader.constants import PGN
    assert PGN["1"] == "first person"
    assert PGN["2"] == "second person"
    assert PGN["3"] == "third person"


def test_pgn_gender_english():
    """PGN gender codes must map to English descriptions."""
    from alfanous_import.quran_corpus_reader.constants import PGN
    assert PGN["M"] == "masculine"
    assert PGN["F"] == "feminine"


def test_pgn_number_english():
    """PGN number codes must map to English descriptions."""
    from alfanous_import.quran_corpus_reader.constants import PGN
    assert PGN["S"] == "singular"
    assert PGN["D"] == "dual"
    assert PGN["P"] == "plural"


# ---------------------------------------------------------------------------
# constants.py — VERB form patterns use Arabic morphological patterns
# ---------------------------------------------------------------------------

def test_verb_form_arabic_patterns():
    """Verb forms (I)-(XII) must have non-empty Arabic morphological patterns."""
    from alfanous_import.quran_corpus_reader.constants import VERB
    expected = {
        "(I)":    "فَعَلَ",
        "(II)":   "فَعَّلَ",
        "(III)":  "فَاعَلَ",
        "(IV)":   "أَفْعَلَ",
        "(V)":    "تَفَعَّلَ",
        "(VI)":   "تَفَاعَلَ",
        "(VII)":  "إِنْفَعَلَ",
        "(VIII)": "إِفْتَعَلَ",
        "(IX)":   "إِفْعَلَّ",
        "(X)":    "إِسْتَفْعَلَ",
        "(XI)":   "إِفْعَالَّ",
        "(XII)":  "إِفْعَوْعَلَ",
    }
    for code, arabic in expected.items():
        assert VERB[code][0] == arabic, f"VERB['{code}'][0] should be '{arabic}'"


# ---------------------------------------------------------------------------
# transformer.py — _parse_stem_features stores Arabic for voice/aspect/derivation/form
# ---------------------------------------------------------------------------

def _make_stem_features_parser():
    """Return the _parse_stem_features inner function from _load_corpus_words_txt."""
    import sys
    sys.path.insert(0, _STORE_PATH + "/../src")
    # _parse_stem_features is a closure; extract it by running a minimal corpus stub
    import types, io
    from alfanous_import import transformer as _t
    import inspect, textwrap

    src = inspect.getsource(_t._load_corpus_words_txt)
    # Isolate the inner function definition
    lines = src.splitlines()
    start = next(i for i, l in enumerate(lines) if "def _parse_stem_features" in l)
    end   = next(i for i, l in enumerate(lines) if i > start and l.strip().startswith("qasf"))
    fn_src = textwrap.dedent("\n".join(lines[start:end]))
    ns = {}
    from alfanous_import.quran_corpus_reader.constants import (
        BUCKWALTER2UNICODE, POS, PGN, PGNclass, VERB, NOM, DERIV, PREFIX,
    )
    from alfanous_import.quran_corpus_reader.main import _INV_POS
    # _b2u is a helper defined in the same outer function scope; replicate it
    def _b2u(s):
        return "".join(BUCKWALTER2UNICODE.get(ch, ch) for ch in s)
    exec(fn_src, {
        "BUCKWALTER2UNICODE": BUCKWALTER2UNICODE, "POS": POS, "PGN": PGN,
        "PGNclass": PGNclass, "VERB": VERB, "NOM": NOM, "DERIV": DERIV,
        "PREFIX": PREFIX, "_INV_POS": _INV_POS, "_b2u": _b2u,
    }, ns)
    return ns["_parse_stem_features"]


@pytest.fixture(scope="module")
def parse_stem():
    return _make_stem_features_parser()


def test_parse_stem_voice_arabic(parse_stem):
    """voice field from STEM features must be Arabic (مبني للمجهول for PASS)."""
    feats = parse_stem("STEM|POS:V|PASS|PERF")
    assert feats.get("voice") == "مبني للمجهول"


def test_parse_stem_aspect_arabic(parse_stem):
    """aspect field from STEM features must be Arabic."""
    assert parse_stem("STEM|POS:V|PERF")["aspect"] == "فعل ماض"
    assert parse_stem("STEM|POS:V|IMPF")["aspect"] == "فعل مضارع"
    assert parse_stem("STEM|POS:V|IMPV")["aspect"] == "فعل أمر"


def test_parse_stem_derivation_arabic(parse_stem):
    """derivation field must be Arabic (اسم فاعل / اسم مفعول / مصدر)."""
    assert parse_stem("STEM|POS:N|ACT|PCPL")["derivation"] == "اسم فاعل"
    assert parse_stem("STEM|POS:N|PASS|PCPL")["derivation"] == "اسم مفعول"
    assert parse_stem("STEM|POS:N|VN")["derivation"] == "مصدر"


def test_parse_stem_form_arabic(parse_stem):
    """form field must be the Arabic morphological pattern."""
    assert parse_stem("STEM|POS:V|(II)")["form"] == "فَعَّلَ"
    assert parse_stem("STEM|POS:V|(X)")["form"] == "إِسْتَفْعَلَ"


# ---------------------------------------------------------------------------
# fields.json — Arabic names for person / gender / number
# ---------------------------------------------------------------------------

def test_person_name_arabic(fields_by_name):
    """person field must have name_arabic = الاسناد."""
    assert fields_by_name["person"]["name_arabic"] == "الاسناد"


def test_gender_name_arabic(fields_by_name):
    """gender field must have name_arabic = الجنس."""
    assert fields_by_name["gender"]["name_arabic"] == "الجنس"


def test_number_name_arabic(fields_by_name):
    """number field must have name_arabic = العدد."""
    assert fields_by_name["number"]["name_arabic"] == "العدد"


# ---------------------------------------------------------------------------
# transformer.py — inference rules (TXT reader path)
# Tests use _load_corpus_words_txt with a synthetic in-memory corpus file.
# ---------------------------------------------------------------------------

def _make_words_loader():
    """Return a callable that runs _load_corpus_words_txt on an in-memory file."""
    import tempfile, os
    from alfanous_import import transformer as _t

    def load(lines):
        """Write *lines* to a temp file and return the result dict."""
        content = "\n".join(lines) + "\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                        delete=False, encoding="utf-8") as fh:
            fh.write(content)
            name = fh.name
        try:
            return _t._load_corpus_words_txt(name)
        finally:
            os.unlink(name)

    return load


@pytest.fixture(scope="module")
def load_words():
    return _make_words_loader()


def test_infer_voice_active_for_verb(load_words):
    """Verbs with no ACT/PASS tag must get voice inferred as مبني للمعلوم."""
    # Perfect verb, no voice tag
    result = load_words([
        "(1:1:1:1)\tktb\tV\tSTEM|POS:V|LEM:ktb|ROOT:ktb|PERF|3|M|S",
    ])
    words = result[(1, 1)]
    assert len(words) == 1
    assert words[0]["voice"] == "مبني للمعلوم"


def test_infer_voice_passive_not_overridden(load_words):
    """Verbs with an explicit PASS tag must keep مبني للمجهول."""
    result = load_words([
        "(1:1:1:1)\tktb\tV\tSTEM|POS:V|LEM:ktb|ROOT:ktb|PERF|PASS|3|M|S",
    ])
    words = result[(1, 1)]
    assert words[0]["voice"] == "مبني للمجهول"


def test_infer_mood_indicative_for_impf(load_words):
    """Imperfect verbs with no MOOD: tag must get mood inferred as مرفوع."""
    result = load_words([
        "(1:1:1:1)\tyktb\tV\tSTEM|POS:V|LEM:ktb|ROOT:ktb|IMPF|3|M|S",
    ])
    words = result[(1, 1)]
    assert words[0]["mood"] == "مرفوع"


def test_infer_mood_not_applied_to_perf(load_words):
    """Perfect verbs must NOT have mood inferred (mood only applies to IMPF)."""
    result = load_words([
        "(1:1:1:1)\tktb\tV\tSTEM|POS:V|LEM:ktb|ROOT:ktb|PERF|3|M|S",
    ])
    words = result[(1, 1)]
    assert words[0]["mood"] is None


def test_infer_mood_explicit_subj_kept(load_words):
    """Imperfect verbs with explicit MOOD:SUBJ must keep منصوب."""
    result = load_words([
        "(1:1:1:1)\tyktb\tV\tSTEM|POS:V|LEM:ktb|ROOT:ktb|IMPF|MOOD:SUBJ|3|M|S",
    ])
    words = result[(1, 1)]
    assert words[0]["mood"] == "منصوب"


def test_infer_state_definite_for_noun(load_words):
    """Nouns with no DEF/INDEF tag must get state inferred as معرفة."""
    result = load_words([
        "(1:1:1:1)\tAlktAb\tN\tSTEM|POS:N|LEM:ktAb|ROOT:ktb|M|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["state"] == "معرفة"


def test_infer_state_definite_for_nominal(load_words):
    """Adjectives (Nominals) with no state tag must get state inferred as معرفة."""
    result = load_words([
        "(1:1:1:1)\tkbyr\tADJ\tSTEM|POS:ADJ|LEM:kbyr|ROOT:kbr|M|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["state"] == "معرفة"


def test_infer_state_indefinite_not_overridden(load_words):
    """Nouns with explicit INDEF tag must keep نكرة."""
    result = load_words([
        "(1:1:1:1)\tktAb\tN\tSTEM|POS:N|LEM:ktAb|ROOT:ktb|M|NOM|INDEF",
    ])
    words = result[(1, 1)]
    assert words[0]["state"] == "نكرة"


def test_infer_number_singular_for_noun(load_words):
    """Nouns with no S/D/P number tag must get number inferred as singular."""
    result = load_words([
        "(1:1:1:1)\tAlktAb\tN\tSTEM|POS:N|LEM:ktAb|ROOT:ktb|M|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["number"] == "singular"


def test_infer_number_singular_for_nominal(load_words):
    """Adjectives (Nominals) with no number tag must get number inferred as singular."""
    result = load_words([
        "(1:1:1:1)\tkbyr\tADJ\tSTEM|POS:ADJ|LEM:kbyr|ROOT:kbr|M|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["number"] == "singular"


def test_infer_number_plural_not_overridden(load_words):
    """Nouns with explicit P tag must keep plural."""
    result = load_words([
        "(1:1:1:1)\tktb\tN\tSTEM|POS:N|LEM:ktAb|ROOT:ktb|M|P|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["number"] == "plural"


def test_infer_number_dual_not_overridden(load_words):
    """Nouns with explicit D tag must keep dual."""
    result = load_words([
        "(1:1:1:1)\tktAbAn\tN\tSTEM|POS:N|LEM:ktAb|ROOT:ktb|M|D|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["number"] == "dual"


def test_no_number_inference_for_verb(load_words):
    """Verbs must NOT have number inferred (number is explicit in PGN for verbs)."""
    result = load_words([
        "(1:1:1:1)\tktb\tV\tSTEM|POS:V|LEM:ktb|ROOT:ktb|PERF|3|M",
    ])
    words = result[(1, 1)]
    # No number PGN (M is gender, not number) → should NOT get singular inferred
    # because type is "Verbs", not "Nouns"/"Nominals"
    assert words[0]["number"] is None


# ---------------------------------------------------------------------------
# constants.py — missing POS particle tags (CIRC, COM, INT, RSLT)
# ---------------------------------------------------------------------------

def test_pos_circ():
    """CIRC must map to حرف حال / Circumstantial particle."""
    from alfanous_import.quran_corpus_reader.constants import POS
    assert POS["CIRC"] == ("حرف حال", "Circumstantial particle")


def test_pos_com():
    """COM must map to واو المعية / Comitative particle."""
    from alfanous_import.quran_corpus_reader.constants import POS
    assert POS["COM"] == ("واو المعية", "Comitative particle")


def test_pos_int():
    """INT must map to حرف تفسير / Particle of interpretation."""
    from alfanous_import.quran_corpus_reader.constants import POS
    assert POS["INT"] == ("حرف تفسير", "Particle of interpretation")


def test_pos_rslt():
    """RSLT must map to حرف واقع في جواب الشرط / Result particle."""
    from alfanous_import.quran_corpus_reader.constants import POS
    assert POS["RSLT"] == ("حرف واقع في جواب الشرط", "Result particle")


def test_pos_circ_com_int_rslt_in_posclass():
    """CIRC, COM, INT, RSLT must all appear in POSclass Particles."""
    from alfanous_import.quran_corpus_reader.constants import POSclass
    particles = POSclass["Particles"]
    for tag in ("CIRC", "COM", "INT", "RSLT"):
        assert tag in particles, f"'{tag}' missing from POSclass['Particles']"


def test_inv_pos_circ_com_int_rslt():
    """_INV_POS must resolve CIRC, COM, INT, RSLT to the 'Particles' category."""
    from alfanous_import.quran_corpus_reader.main import _INV_POS
    for tag in ("CIRC", "COM", "INT", "RSLT"):
        assert _INV_POS.get(tag) == ["Particles"], (
            f"_INV_POS['{tag}'] should be ['Particles']"
        )


# ---------------------------------------------------------------------------
# constants.py — PREFIX dict: missing waw and fa prefix tags
# ---------------------------------------------------------------------------

def test_prefix_new_waw_entries():
    """w:CONJ+, w:REM+, w:CIRC+, w:SUP+, w:COM+ must be in PREFIX with (و, wa)."""
    from alfanous_import.quran_corpus_reader.constants import PREFIX
    for tag in ("w:CONJ+", "w:REM+", "w:CIRC+", "w:SUP+", "w:COM+"):
        assert tag in PREFIX, f"'{tag}' missing from PREFIX"
        assert PREFIX[tag] == ("و", "wa"), f"PREFIX['{tag}'] should be ('و', 'wa')"


def test_prefix_new_fa_entries():
    """f:RSLT+ and f:SUP+ must be in PREFIX with (ف, fa)."""
    from alfanous_import.quran_corpus_reader.constants import PREFIX
    for tag in ("f:RSLT+", "f:SUP+"):
        assert tag in PREFIX, f"'{tag}' missing from PREFIX"
        assert PREFIX[tag] == ("ف", "fa"), f"PREFIX['{tag}'] should be ('ف', 'fa')"


# ---------------------------------------------------------------------------
# constants.py — PREFIXclass: correct category assignments
# ---------------------------------------------------------------------------

def test_prefixclass_w_p_is_preposition():
    """w:P+ must be in PREFIXclass 'preposition', not 'resumption'."""
    from alfanous_import.quran_corpus_reader.constants import PREFIXclass
    assert "w:P+" in PREFIXclass["preposition"]
    assert "w:P+" not in PREFIXclass.get("resumption", [])


def test_prefixclass_resumption_uses_rem_tags():
    """PREFIXclass 'resumption' must contain f:REM+ and w:REM+."""
    from alfanous_import.quran_corpus_reader.constants import PREFIXclass
    resumption = PREFIXclass["resumption"]
    assert "f:REM+" in resumption
    assert "w:REM+" in resumption


def test_prefixclass_conjunction_includes_wconj():
    """PREFIXclass 'conjunction' must include w:CONJ+."""
    from alfanous_import.quran_corpus_reader.constants import PREFIXclass
    assert "w:CONJ+" in PREFIXclass["conjunction"]


def test_prefixclass_new_categories():
    """New PREFIXclass categories must contain the right tags."""
    from alfanous_import.quran_corpus_reader.constants import PREFIXclass
    assert "w:CIRC+" in PREFIXclass["circumstantial"]
    assert "w:COM+"  in PREFIXclass["comitative"]
    assert "f:RSLT+" in PREFIXclass["result"]
    assert "f:SUP+"  in PREFIXclass["supplemental"]
    assert "w:SUP+"  in PREFIXclass["supplemental"]


def test_all_prefix_tags_have_category():
    """Every key in PREFIX must appear in _INV_PREFIX (PREFIXclass is complete)."""
    from alfanous_import.quran_corpus_reader.constants import PREFIX
    from alfanous_import.quran_corpus_reader.main import _INV_PREFIX
    missing = [t for t in PREFIX if t not in _INV_PREFIX]
    assert not missing, f"Prefix tags missing from PREFIXclass: {missing}"


# ---------------------------------------------------------------------------
# transformer.py — verb forms VII–XII use إِ (hamza-below alif + kasra)
# ---------------------------------------------------------------------------

def test_parse_stem_form_vii(parse_stem):
    """(VII) form tag must produce Arabic pattern إِنْفَعَلَ (hamza-below alif)."""
    feats = parse_stem("STEM|POS:V|(VII)|PERF|3|M|S")
    assert feats.get("form") == "إِنْفَعَلَ"


def test_parse_stem_form_viii(parse_stem):
    """(VIII) form tag must produce Arabic pattern إِفْتَعَلَ (hamza-below alif)."""
    feats = parse_stem("STEM|POS:V|(VIII)|PERF|3|M|S")
    assert feats.get("form") == "إِفْتَعَلَ"


def test_parse_stem_form_ix(parse_stem):
    """(IX) form tag must produce Arabic pattern إِفْعَلَّ (hamza-below alif)."""
    feats = parse_stem("STEM|POS:V|(IX)|PERF|3|M|S")
    assert feats.get("form") == "إِفْعَلَّ"


def test_parse_stem_form_x(parse_stem):
    """(X) form tag must produce Arabic pattern إِسْتَفْعَلَ (hamza-below alif)."""
    feats = parse_stem("STEM|POS:V|(X)|PERF|3|M|S")
    assert feats.get("form") == "إِسْتَفْعَلَ"


def test_parse_stem_form_xi(parse_stem):
    """(XI) form tag must produce Arabic pattern إِفْعَالَّ (hamza-below alif)."""
    feats = parse_stem("STEM|POS:V|(XI)|PERF|3|M|S")
    assert feats.get("form") == "إِفْعَالَّ"


def test_parse_stem_form_xii(parse_stem):
    """(XII) form tag must produce Arabic pattern إِفْعَوْعَلَ (hamza-below alif)."""
    feats = parse_stem("STEM|POS:V|(XII)|PERF|3|M|S")
    assert feats.get("form") == "إِفْعَوْعَلَ"


def test_verbclass_has_no_q_forms():
    """VERBclass['form'] must NOT contain any (Q*) tags — they don't exist in corpus."""
    from alfanous_import.quran_corpus_reader.constants import VERBclass
    for form in VERBclass["form"]:
        assert not form.startswith("(Q"), f"Spurious quadriliteral tag '{form}' in VERBclass"


def test_verb_has_no_q_entries():
    """VERB dict must NOT contain (Q1)–(Q4) — those tags are absent from the corpus."""
    from alfanous_import.quran_corpus_reader.constants import VERB
    for q in ("(Q1)", "(Q2)", "(Q3)", "(Q4)"):
        assert q not in VERB, f"Spurious key '{q}' found in VERB dict"


# ---------------------------------------------------------------------------
# transformer.py — CIRC/COM/INT/RSLT POS tags parsed correctly
# ---------------------------------------------------------------------------

def test_parse_stem_circ_pos(parse_stem):
    """POS:CIRC must set arabicpos to حرف حال and type to Particles."""
    feats = parse_stem("STEM|POS:CIRC")
    assert feats.get("arabicpos") == "حرف حال"
    assert feats.get("type") == "Particles"


def test_parse_stem_com_pos(parse_stem):
    """POS:COM must set arabicpos to واو المعية and type to Particles."""
    feats = parse_stem("STEM|POS:COM")
    assert feats.get("arabicpos") == "واو المعية"
    assert feats.get("type") == "Particles"


def test_parse_stem_int_pos(parse_stem):
    """POS:INT must set arabicpos to حرف تفسير and type to Particles."""
    feats = parse_stem("STEM|POS:INT")
    assert feats.get("arabicpos") == "حرف تفسير"
    assert feats.get("type") == "Particles"


def test_parse_stem_rslt_pos(parse_stem):
    """POS:RSLT must set arabicpos to حرف واقع في جواب الشرط and type to Particles."""
    feats = parse_stem("STEM|POS:RSLT")
    assert feats.get("arabicpos") == "حرف واقع في جواب الشرط"
    assert feats.get("type") == "Particles"

