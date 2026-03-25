"""Tests for word sub-schema configuration and facet field catalogue.

These tests validate schema changes that do NOT require a built index:
- standard is KEYWORD type; word_standard is TEXT type in fields.json
- root, lemma, type, pos, gender, case, state, derivation are facet_allowed
- chapter, topic, subtopic are ID type in fields.json (exact-match filtering)
- _WORD_ALL_INDEXED_FIELDS includes word_standard, standard, and lemma
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
    return {fld["search_name"]: fld for fld in fields if fld.get("search_name")}


# ---------------------------------------------------------------------------
# Existing field-type tests
# ---------------------------------------------------------------------------

def test_standard_is_keyword(fields_by_name):
    """standard must be declared as KEYWORD in fields.json (raw stored value)."""
    assert fields_by_name["standard"]["type"] == "KEYWORD", (
        "standard should be KEYWORD — raw stored Imla'i word for display"
    )


def test_word_standard_is_text(fields_by_name):
    """word_standard must be declared as TEXT in fields.json (normalized for search)."""
    assert fields_by_name["word_standard"]["type"] == "TEXT", (
        "word_standard should be TEXT with QStandardAnalyzer for normalized search"
    )


def test_uthmani_different_is_boolean(fields_by_name):
    """uthmani_different must be declared as BOOLEAN in fields.json."""
    assert fields_by_name["uthmani_different"]["type"] == "BOOLEAN", (
        "uthmani_different should be BOOLEAN"
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


def test_standard_in_word_all_indexed_fields():
    """standard must be in _WORD_ALL_INDEXED_FIELDS."""
    from alfanous.outputs import _WORD_ALL_INDEXED_FIELDS
    assert "standard" in _WORD_ALL_INDEXED_FIELDS, (
        "standard (raw KEYWORD) must be in _WORD_ALL_INDEXED_FIELDS"
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
    "number", "person", "form", "pattern", "voice", "aspect", "mood",
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


def test_schema_builder_standard_keyword():
    """Transformer.build_schema must produce a KEYWORD field for standard."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import KEYWORD
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["standard"], KEYWORD), (
        "Transformer.build_schema must produce KEYWORD for standard"
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

def test_pgn_person_arabic():
    """PGN person codes must map to (Arabic, English) tuples."""
    from alfanous_import.quran_corpus_reader.constants import PGN
    assert PGN["1"] == ("المتكلم", "first person")
    assert PGN["2"] == ("المخاطب", "second person")
    assert PGN["3"] == ("الغائب", "third person")


def test_pgn_gender_arabic():
    """PGN gender codes must map to (Arabic, English) tuples."""
    from alfanous_import.quran_corpus_reader.constants import PGN
    assert PGN["M"] == ("مذكر", "masculine")
    assert PGN["F"] == ("مؤنث", "feminine")


def test_pgn_number_arabic():
    """PGN number codes must map to (Arabic, English) tuples."""
    from alfanous_import.quran_corpus_reader.constants import PGN
    assert PGN["S"] == ("مفرد", "singular")
    assert PGN["D"] == ("مثنى", "dual")
    assert PGN["P"] == ("جمع", "plural")


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
        BUCKWALTER2UNICODE, POS, PGN, PGNclass, VERB, VERB_QUAD, NOM, DERIV, PREFIX,
        _INV_POS,
    )
    from alfanous.morphology import POSclass_arabic
    # _b2u is a helper defined in the same outer function scope; replicate it
    def _b2u(s):
        return "".join(BUCKWALTER2UNICODE.get(ch, ch) for ch in s)
    exec(fn_src, {
        "BUCKWALTER2UNICODE": BUCKWALTER2UNICODE, "POS": POS, "PGN": PGN,
        "PGNclass": PGNclass, "VERB": VERB, "VERB_QUAD": VERB_QUAD,
        "NOM": NOM, "DERIV": DERIV,
        "PREFIX": PREFIX, "_INV_POS": _INV_POS, "_b2u": _b2u,
        "POSclass_arabic": POSclass_arabic,
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
# transformer.py — combined PGN code parsing (e.g. 3MS, 1P, 2MP)
# ---------------------------------------------------------------------------

def test_parse_stem_pgn_3ms(parse_stem):
    """Combined PGN code '3MS' must set person, gender, and number in Arabic."""
    feats = parse_stem("STEM|POS:V|PERF|LEM:ktb|ROOT:ktb|3MS")
    assert feats.get("person") == "الغائب"
    assert feats.get("gender") == "مذكر"
    assert feats.get("number") == "مفرد"


def test_parse_stem_pgn_1p(parse_stem):
    """Combined PGN code '1P' must set person and number in Arabic (no gender)."""
    feats = parse_stem("STEM|POS:V|PERF|(IV)|LEM:>asoqayo|ROOT:sqy|1P")
    assert feats.get("person") == "المتكلم"
    assert feats.get("number") == "جمع"
    assert feats.get("gender") is None


def test_parse_stem_pgn_2mp(parse_stem):
    """Combined PGN code '2MP' must set person, gender, and number in Arabic."""
    feats = parse_stem("STEM|POS:V|IMPF|LEM:ktb|ROOT:ktb|2MP")
    assert feats.get("person") == "المخاطب"
    assert feats.get("gender") == "مذكر"
    assert feats.get("number") == "جمع"


def test_parse_stem_pgn_3fs(parse_stem):
    """Combined PGN code '3FS' must set person, gender, and number in Arabic."""
    feats = parse_stem("STEM|POS:V|IMPF|LEM:sqy|ROOT:sqy|3FS")
    assert feats.get("person") == "الغائب"
    assert feats.get("gender") == "مؤنث"
    assert feats.get("number") == "مفرد"


def test_parse_stem_noun_pgn_ms(parse_stem):
    """Noun combined PGN 'M' followed by case must parse gender correctly."""
    feats = parse_stem("STEM|POS:N|LEM:{som|ROOT:smw|M|GEN")
    assert feats.get("gender") == "مذكر"


def test_parse_stem_noun_pgn_mp(parse_stem):
    """Noun combined PGN code 'MP' must set gender and number in Arabic."""
    feats = parse_stem("STEM|POS:N|LEM:>asobaAT|ROOT:sbT|MP|GEN")
    assert feats.get("gender") == "مذكر"
    assert feats.get("number") == "جمع"


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
    """Nouns with no S/D/P number tag must get number inferred as مفرد."""
    result = load_words([
        "(1:1:1:1)\tAlktAb\tN\tSTEM|POS:N|LEM:ktAb|ROOT:ktb|M|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["number"] == "مفرد"


def test_infer_number_singular_for_nominal(load_words):
    """Adjectives (Nominals) with no number tag must get number inferred as مفرد."""
    result = load_words([
        "(1:1:1:1)\tkbyr\tADJ\tSTEM|POS:ADJ|LEM:kbyr|ROOT:kbr|M|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["number"] == "مفرد"


def test_infer_number_plural_not_overridden(load_words):
    """Nouns with explicit P tag must keep جمع."""
    result = load_words([
        "(1:1:1:1)\tktb\tN\tSTEM|POS:N|LEM:ktAb|ROOT:ktb|M|P|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["number"] == "جمع"


def test_infer_number_dual_not_overridden(load_words):
    """Nouns with explicit D tag must keep مثنى."""
    result = load_words([
        "(1:1:1:1)\tktAbAn\tN\tSTEM|POS:N|LEM:ktAb|ROOT:ktb|M|D|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["number"] == "مثنى"


def test_no_number_inference_for_verb(load_words):
    """Verbs must NOT have number inferred (number is explicit in PGN for verbs)."""
    result = load_words([
        "(1:1:1:1)\tktb\tV\tSTEM|POS:V|LEM:ktb|ROOT:ktb|PERF|3|M",
    ])
    words = result[(1, 1)]
    # No number PGN (M is gender, not number) → should NOT get مفرد inferred
    # because type is "Verbs", not "Nouns"/"Nominals"
    assert words[0]["number"] is None


def test_infer_form_i_for_verb(load_words):
    """Verbs with no explicit form tag must get form inferred as فَعَلَ (Form I)."""
    result = load_words([
        "(1:1:1:1)\tktb\tV\tSTEM|POS:V|LEM:ktb|ROOT:ktb|PERF|3|M|S",
    ])
    words = result[(1, 1)]
    assert words[0]["form"] == "فَعَلَ"


def test_infer_form_explicit_not_overridden(load_words):
    """Verbs with an explicit form tag (e.g. IV) must NOT be overridden to Form I."""
    result = load_words([
        "(1:1:1:1)\tktb\tV\tSTEM|POS:V|LEM:ktb|ROOT:ktb|PERF|(IV)|3|M|S",
    ])
    words = result[(1, 1)]
    assert words[0]["form"] == "أَفْعَلَ"


def test_no_form_inference_for_noun(load_words):
    """Nouns must NOT have form inferred (only verbs have form)."""
    result = load_words([
        "(1:1:1:1)\tktb\tN\tSTEM|POS:N|LEM:ktAb|ROOT:ktb|M|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["form"] is None


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
    from alfanous_import.quran_corpus_reader.constants import _INV_POS
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
    from alfanous_import.quran_corpus_reader.constants import PREFIX, _INV_PREFIX
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
# constants.py — VERB_QUAD: quadriliteral form patterns (root length = 4)
# ---------------------------------------------------------------------------

def test_verb_quad_patterns():
    """VERB_QUAD must map (I)–(IV) to the correct quadriliteral Arabic patterns."""
    from alfanous_import.quran_corpus_reader.constants import VERB_QUAD
    expected = {
        "(I)":   ("فَعْلَلَ",     "First form (quadriliteral)"),
        "(II)":  ("تَفَعْلَلَ",   "Second form (quadriliteral)"),
        "(III)": ("إِفْعَنْلَلَ", "Third form (quadriliteral)"),
        "(IV)":  ("إِفْعَلَلَّ",  "Fourth form (quadriliteral)"),
    }
    for code, (arabic, english) in expected.items():
        assert VERB_QUAD[code][0] == arabic,  f"VERB_QUAD['{code}'][0] should be '{arabic}'"
        assert VERB_QUAD[code][1] == english, f"VERB_QUAD['{code}'][1] should be '{english}'"


def test_verb_quad_only_covers_i_to_iv():
    """VERB_QUAD must only cover (I)–(IV); higher forms are triliteral-only."""
    from alfanous_import.quran_corpus_reader.constants import VERB_QUAD
    assert set(VERB_QUAD.keys()) == {"(I)", "(II)", "(III)", "(IV)"}


# ---------------------------------------------------------------------------
# transformer.py — quadriliteral dispatch: root length selects VERB_QUAD
# ---------------------------------------------------------------------------

def test_parse_stem_quad_form_i(parse_stem):
    """4-letter root + (I) tag → quadriliteral pattern فَعْلَلَ."""
    # Use a synthetic 4-letter root 'zHzH' (زحزح), same family as corpus entry
    feats = parse_stem("STEM|POS:V|(I)|ROOT:zHzH|PERF|3|M|S")
    assert feats.get("form") == "فَعْلَلَ", (
        "4-letter root with (I) should produce quadriliteral pattern فَعْلَلَ"
    )


def test_parse_stem_quad_form_ii(parse_stem):
    """4-letter root + (II) tag → quadriliteral pattern تَفَعْلَلَ."""
    feats = parse_stem("STEM|POS:N|ACT|PCPL|(II)|ROOT:zHzH|M|GEN")
    assert feats.get("form") == "تَفَعْلَلَ"


def test_parse_stem_quad_form_iii(parse_stem):
    """4-letter root + (III) tag → quadriliteral pattern إِفْعَنْلَلَ."""
    feats = parse_stem("STEM|POS:V|(III)|ROOT:zHzH|PERF|3|M|S")
    assert feats.get("form") == "إِفْعَنْلَلَ"


def test_parse_stem_quad_form_iv(parse_stem):
    """4-letter root + (IV) tag → quadriliteral pattern إِفْعَلَلَّ."""
    feats = parse_stem("STEM|POS:V|(IV)|ROOT:zHzH|PERF|3|M|S")
    assert feats.get("form") == "إِفْعَلَلَّ"


def test_parse_stem_triliteral_form_i_unchanged(parse_stem):
    """3-letter root + (I) tag → triliteral pattern فَعَلَ (unchanged)."""
    feats = parse_stem("STEM|POS:V|(I)|ROOT:ktb|PERF|3|M|S")
    assert feats.get("form") == "فَعَلَ"


def test_parse_stem_triliteral_form_iv_unchanged(parse_stem):
    """3-letter root + (IV) tag → triliteral pattern أَفْعَلَ (unchanged)."""
    feats = parse_stem("STEM|POS:V|(IV)|ROOT:nEm|PERF|3|M|S")
    assert feats.get("form") == "أَفْعَلَ"


def test_parse_stem_quad_root_high_forms_unchanged(parse_stem):
    """4-letter root + (V)–(XII) tags → standard triliteral patterns (no VERB_QUAD)."""
    feats = parse_stem("STEM|POS:V|(X)|ROOT:zHzH|IMPF|3|M|S")
    assert feats.get("form") == "إِسْتَفْعَلَ"


# ---------------------------------------------------------------------------
# transformer.py — CIRC/COM/INT/RSLT POS tags parsed correctly
# ---------------------------------------------------------------------------

def test_parse_stem_circ_pos(parse_stem):
    """POS:CIRC must set arabicpos to حرف حال and type to أدوات (Arabic)."""
    feats = parse_stem("STEM|POS:CIRC")
    assert feats.get("arabicpos") == "حرف حال"
    assert feats.get("type") == "أدوات"


def test_parse_stem_com_pos(parse_stem):
    """POS:COM must set arabicpos to واو المعية and type to أدوات (Arabic)."""
    feats = parse_stem("STEM|POS:COM")
    assert feats.get("arabicpos") == "واو المعية"
    assert feats.get("type") == "أدوات"


def test_parse_stem_int_pos(parse_stem):
    """POS:INT must set arabicpos to حرف تفسير and type to أدوات (Arabic)."""
    feats = parse_stem("STEM|POS:INT")
    assert feats.get("arabicpos") == "حرف تفسير"
    assert feats.get("type") == "أدوات"


def test_parse_stem_rslt_pos(parse_stem):
    """POS:RSLT must set arabicpos to حرف واقع في جواب الشرط and type to أدوات (Arabic)."""
    feats = parse_stem("STEM|POS:RSLT")
    assert feats.get("arabicpos") == "حرف واقع في جواب الشرط"
    assert feats.get("type") == "أدوات"


# ---------------------------------------------------------------------------
# Normalized lemma — tashkeel must be stripped for searchability
# ---------------------------------------------------------------------------

def test_lemma_vocalized(load_words):
    """Lemma must be stored WITH tashkeel (vocalized) to preserve the wazan/pattern."""
    result = load_words([
        "(1:1:1:1)\tbi\tP\tPREFIX|bi+",
        "(1:1:1:2)\tsomi\tN\tSTEM|POS:N|LEM:{som|ROOT:smw|M|GEN",
    ])
    words = result[(1, 1)]
    # LEM:{som → _b2u → ٱسْم (with sukun)
    assert words[0]["lemma"] is not None
    # Must contain Arabic diacritical marks (the vocalized lemma preserves wazan)
    import unicodedata
    assert any(unicodedata.category(c) == 'Mn' for c in words[0]["lemma"])


# ---------------------------------------------------------------------------
# Segments — per-word segment breakdown for treebank display
# ---------------------------------------------------------------------------

def test_segments_prefix_stem(load_words):
    """Word with prefix + stem must produce 2 segments."""
    result = load_words([
        "(1:1:1:1)\tbi\tP\tPREFIX|bi+",
        "(1:1:1:2)\tsomi\tN\tSTEM|POS:N|LEM:{som|ROOT:smw|M|GEN",
    ])
    words = result[(1, 1)]
    segs = words[0]["segments"]
    assert len(segs) == 2
    assert segs[0]["type"] == "PREFIX"
    assert segs[0]["pos"] == "ب"      # PREFIX bi+ → Arabic "ب"
    assert segs[1]["type"] == "STEM"
    assert segs[1]["pos"] == "اسم"    # POS:N → Arabic "اسم"


def test_segments_prefix_stem_suffix(load_words):
    """Word with prefix + stem + suffix must produce 3 segments."""
    result = load_words([
        "(1:1:1:1)\tfa\tCONJ\tPREFIX|f:CONJ+",
        "(1:1:1:2)\t>asoqayo\tV\tSTEM|POS:V|PERF|(IV)|LEM:>asoqayo|ROOT:sqy|1P",
        "(1:1:1:3)\tna`\tPRON\tSUFFIX|PRON:1P",
    ])
    words = result[(1, 1)]
    segs = words[0]["segments"]
    assert len(segs) == 3
    assert segs[0]["type"] == "PREFIX"
    assert segs[1]["type"] == "STEM"
    assert segs[1]["pos"] == "فعل"    # POS:V → Arabic "فعل"
    assert segs[2]["type"] == "SUFFIX"
    assert segs[2]["pos"] == "ضمير"   # PRON suffix → Arabic "ضمير"


def test_segments_stem_only(load_words):
    """Word with only a stem must produce 1 segment."""
    result = load_words([
        "(1:1:1:1)\t{ll~ahi\tPN\tSTEM|POS:PN|LEM:{ll~ah|ROOT:Alh|GEN",
    ])
    words = result[(1, 1)]
    segs = words[0]["segments"]
    assert len(segs) == 1
    assert segs[0]["type"] == "STEM"
    assert segs[0]["pos"] == "اسم علم"  # POS:PN → Arabic "اسم علم"


def test_segments_multi_suffix(load_words):
    """Word with 2 pronoun suffixes must produce segments for each."""
    result = load_words([
        "(1:1:1:1)\t>asoqayo\tV\tSTEM|POS:V|PERF|(IV)|LEM:>asoqayo|ROOT:sqy|1P",
        "(1:1:1:2)\tna`\tPRON\tSUFFIX|PRON:1P",
        "(1:1:1:3)\tkumuw\tPRON\tSUFFIX|PRON:2MP",
    ])
    words = result[(1, 1)]
    segs = words[0]["segments"]
    assert len(segs) == 3
    assert segs[1]["type"] == "SUFFIX"
    assert segs[2]["type"] == "SUFFIX"


# ---------------------------------------------------------------------------
# MORPHOLOGY_MAPPINGS — Arabic→English mappings for show info
# ---------------------------------------------------------------------------

def test_morphology_mappings_has_all_fields():
    """MORPHOLOGY_MAPPINGS must contain entries for all morphological fields."""
    from alfanous.morphology import MORPHOLOGY_MAPPINGS
    expected = {"pos", "gender", "number", "person", "form", "voice",
                "aspect", "mood", "case", "state", "derivation", "prefix"}
    assert set(MORPHOLOGY_MAPPINGS.keys()) == expected


def test_morphology_mappings_gender_arabic_to_english():
    """Gender mapping must translate Arabic values to English."""
    from alfanous.morphology import MORPHOLOGY_MAPPINGS
    assert MORPHOLOGY_MAPPINGS["gender"]["مذكر"] == "masculine"
    assert MORPHOLOGY_MAPPINGS["gender"]["مؤنث"] == "feminine"


def test_morphology_mappings_number_arabic_to_english():
    """Number mapping must translate Arabic values to English."""
    from alfanous.morphology import MORPHOLOGY_MAPPINGS
    assert MORPHOLOGY_MAPPINGS["number"]["مفرد"] == "singular"
    assert MORPHOLOGY_MAPPINGS["number"]["مثنى"] == "dual"
    assert MORPHOLOGY_MAPPINGS["number"]["جمع"] == "plural"


def test_morphology_mappings_person_arabic_to_english():
    """Person mapping must translate Arabic values to English."""
    from alfanous.morphology import MORPHOLOGY_MAPPINGS
    assert MORPHOLOGY_MAPPINGS["person"]["المتكلم"] == "first person"
    assert MORPHOLOGY_MAPPINGS["person"]["المخاطب"] == "second person"
    assert MORPHOLOGY_MAPPINGS["person"]["الغائب"] == "third person"


def test_morphology_mappings_voice_arabic_to_english():
    """Voice mapping must translate Arabic values to English."""
    from alfanous.morphology import MORPHOLOGY_MAPPINGS
    assert MORPHOLOGY_MAPPINGS["voice"]["مبني للمعلوم"] == "Active voice"
    assert MORPHOLOGY_MAPPINGS["voice"]["مبني للمجهول"] == "Passive voice"


def test_morphology_mappings_pos_covers_all():
    """POS mapping must cover all POS tags."""
    from alfanous.morphology import MORPHOLOGY_MAPPINGS, POS
    for tag, (ar, en) in POS.items():
        assert ar in MORPHOLOGY_MAPPINGS["pos"], f"POS Arabic '{ar}' missing from mapping"
        assert MORPHOLOGY_MAPPINGS["pos"][ar] == en


# ---------------------------------------------------------------------------
# stem — the Arabic text of the STEM morpheme segment
# ---------------------------------------------------------------------------

def test_stem_equals_lemma_for_noun(load_words):
    """For nouns, stem must equal the vocalized lemma."""
    result = load_words([
        "(1:1:1:1)\tbi\tP\tPREFIX|bi+",
        "(1:1:1:2)\tsomi\tN\tSTEM|POS:N|LEM:{som|ROOT:smw|M|GEN",
    ])
    words = result[(1, 1)]
    assert words[0]["stem"] == words[0]["lemma"]
    assert words[0]["stem"] is not None


def test_stem_lemma_x_pattern_for_verb(load_words):
    """For verbs, stem must equal the lemma (dictionary base form only)."""
    result = load_words([
        "(1:1:1:1)\tkataba\tV\tSTEM|POS:V|PERF|LEM:kataba|ROOT:ktb|3MS",
    ])
    words = result[(1, 1)]
    lemma = words[0]["lemma"]
    assert words[0]["stem"] == lemma


def test_stem_lemma_x_pattern_form_iv(load_words):
    """For Form IV verbs, stem must equal the lemma (no pattern appended)."""
    result = load_words([
        "(1:1:1:1)\t>aslm\tV\tSTEM|POS:V|PERF|(IV)|LEM:>aslama|ROOT:slm|3MS",
    ])
    words = result[(1, 1)]
    assert words[0]["stem"] == words[0]["lemma"]


def test_stem_special(load_words):
    """For words with a special (SP:) tag, stem must equal the special value."""
    result = load_words([
        "(1:1:1:1)\t<in~a\tACC\tSTEM|POS:ACC|LEM:<in~|SP:<in~",
    ])
    words = result[(1, 1)]
    assert words[0]["stem"] == words[0]["special"]
    assert words[0]["stem"] is not None


# ---------------------------------------------------------------------------
# pattern — morphological wazan (وزن)
# ---------------------------------------------------------------------------

def test_pattern_verb_equals_form(load_words):
    """For verbs, pattern must equal the form field."""
    result = load_words([
        "(1:1:1:1)\tktb\tV\tSTEM|POS:V|PERF|LEM:ktb|ROOT:ktb|3MS",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == words[0]["form"]
    assert words[0]["pattern"] == "فَعَلَ"  # inferred Form I


def test_pattern_verb_form_iv(load_words):
    """Verb Form IV must have pattern أَفْعَلَ."""
    result = load_words([
        "(1:1:1:1)\t>aslm\tV\tSTEM|POS:V|PERF|(IV)|LEM:>aslm|ROOT:slm|3MS",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "أَفْعَلَ"


def test_pattern_act_pcpl_form_i(load_words):
    """Form I active participle must have pattern فَاعِل."""
    result = load_words([
        "(1:1:1:1)\tma`liki\tN\tSTEM|POS:N|ACT|PCPL|LEM:ma`lik|ROOT:mlk|M|GEN",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "فَاعِل"


def test_pattern_pass_pcpl_form_i(load_words):
    """Form I passive participle must have pattern مَفْعُول."""
    result = load_words([
        "(1:1:1:1)\tmgDwb\tN\tSTEM|POS:N|PASS|PCPL|LEM:mgDwb|ROOT:gDb|M|GEN",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "مَفْعُول"


def test_pattern_act_pcpl_form_iv(load_words):
    """Form IV active participle must have pattern مُفْعِل."""
    result = load_words([
        "(1:1:1:1)\tmslm\tN\tSTEM|POS:N|ACT|PCPL|(IV)|LEM:mslm|ROOT:slm|M|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "مُفْعِل"


def test_pattern_pass_pcpl_form_iv(load_words):
    """Form IV passive participle must have pattern مُفْعَل."""
    result = load_words([
        "(1:1:1:1)\tmrsl\tN\tSTEM|POS:N|PASS|PCPL|(IV)|LEM:mrsl|ROOT:rsl|MP|GEN",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "مُفْعَل"


def test_pattern_act_pcpl_form_x(load_words):
    """Form X active participle must have pattern مُسْتَفْعِل."""
    result = load_words([
        "(1:1:1:1)\tmsotaqiym\tADJ\tSTEM|POS:ADJ|ACT|PCPL|(X)|LEM:msotaqiym|ROOT:qwm|M|ACC",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "مُسْتَفْعِل"


def test_pattern_vn_form_ii(load_words):
    """Form II verbal noun must have pattern تَفْعِيل."""
    result = load_words([
        "(1:1:1:1)\ttSryf\tN\tSTEM|POS:N|VN|(II)|LEM:tSryf|ROOT:Srf|M|GEN",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "تَفْعِيل"


def test_pattern_vn_form_iv(load_words):
    """Form IV verbal noun must have pattern إِفْعَال."""
    result = load_words([
        "(1:1:1:1)\t<HsAn\tN\tSTEM|POS:N|VN|(IV)|LEM:<HsAn|ROOT:Hsn|M|ACC",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "إِفْعَال"


def test_pattern_vn_form_x(load_words):
    """Form X verbal noun must have pattern اِسْتِفْعَال."""
    result = load_words([
        "(1:1:1:1)\t{stbdAl\tN\tSTEM|POS:N|VN|(X)|LEM:{stbdAl|ROOT:bdl|M|ACC",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "اِسْتِفْعَال"


def test_pattern_vn_form_i_uses_lemma(load_words):
    """Form I verbal noun has irregular patterns → pattern stays None (no assumption)."""
    result = load_words([
        "(1:1:1:1)\tTgyAn\tN\tSTEM|POS:N|VN|LEM:TgyAn|ROOT:Tgy|M|GEN",
    ])
    words = result[(1, 1)]
    # Form I VN is not in NOMINAL_PATTERN; pattern stays None instead of
    # falling back to the lemma, so callers must handle None explicitly.
    assert words[0]["pattern"] is None


def test_pattern_plain_noun_none(load_words):
    """Plain nouns (no derivation) must have pattern = None."""
    result = load_words([
        "(1:1:1:1)\tktAb\tN\tSTEM|POS:N|LEM:kitAb|ROOT:ktb|M|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] is None


def test_pattern_act_pcpl_form_viii(load_words):
    """Form VIII active participle must have pattern مُفْتَعِل."""
    result = load_words([
        "(1:1:1:1)\tmhtdy\tN\tSTEM|POS:N|ACT|PCPL|(VIII)|LEM:mhtdy|ROOT:hdy|M|NOM",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "مُفْتَعِل"


def test_pattern_vn_form_iii(load_words):
    """Form III verbal noun must have pattern فِعَال."""
    result = load_words([
        "(1:1:1:1)\tHsAb\tN\tSTEM|POS:N|VN|(III)|LEM:HsAb|ROOT:Hsb|M|GEN",
    ])
    words = result[(1, 1)]
    assert words[0]["pattern"] == "فِعَال"


# ---------------------------------------------------------------------------
# NOMINAL_PATTERN — verified lookup table
# ---------------------------------------------------------------------------

def test_nominal_pattern_form_i_act():
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert NOMINAL_PATTERN[(VERB["(I)"][0], DERIV["ACT PCPL"][0])] == "فَاعِل"

def test_nominal_pattern_form_i_pass():
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert NOMINAL_PATTERN[(VERB["(I)"][0], DERIV["PASS PCPL"][0])] == "مَفْعُول"

def test_nominal_pattern_form_i_vn_absent():
    """Form I VN is irregular — must NOT be in NOMINAL_PATTERN."""
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert (VERB["(I)"][0], DERIV["VN"][0]) not in NOMINAL_PATTERN

def test_nominal_pattern_form_ii_act():
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert NOMINAL_PATTERN[(VERB["(II)"][0], DERIV["ACT PCPL"][0])] == "مُفَعِّل"

def test_nominal_pattern_form_ii_pass():
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert NOMINAL_PATTERN[(VERB["(II)"][0], DERIV["PASS PCPL"][0])] == "مُفَعَّل"

def test_nominal_pattern_form_ii_vn():
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert NOMINAL_PATTERN[(VERB["(II)"][0], DERIV["VN"][0])] == "تَفْعِيل"

def test_nominal_pattern_form_iii_vn():
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert NOMINAL_PATTERN[(VERB["(III)"][0], DERIV["VN"][0])] == "فِعَال"

def test_nominal_pattern_form_iv_vn():
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert NOMINAL_PATTERN[(VERB["(IV)"][0], DERIV["VN"][0])] == "إِفْعَال"

def test_nominal_pattern_form_x_act():
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert NOMINAL_PATTERN[(VERB["(X)"][0], DERIV["ACT PCPL"][0])] == "مُسْتَفْعِل"

def test_nominal_pattern_form_x_pass():
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert NOMINAL_PATTERN[(VERB["(X)"][0], DERIV["PASS PCPL"][0])] == "مُسْتَفْعَل"

def test_nominal_pattern_form_x_vn():
    from alfanous_import.quran_corpus_reader.constants import NOMINAL_PATTERN, VERB, DERIV
    assert NOMINAL_PATTERN[(VERB["(X)"][0], DERIV["VN"][0])] == "اِسْتِفْعَال"

