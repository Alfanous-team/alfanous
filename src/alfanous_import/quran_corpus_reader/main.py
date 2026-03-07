"""
Quranic Corpus morphology XML reader.

HowTo
=====
Parse a morphology line::

    >>> API.MorphologyParser.parse("fa+ POS:INTG LEM:maA l:P+")
    {'prefixes': [...], 'base': [...], 'suffixes': []}

"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Dict, Generator, List

from pyparsing import (
    CharsNotIn,
    Group,
    Keyword,
    Literal,
    OneOrMore,
    Optional,
    SkipTo,
    Word,
    ZeroOrMore,
    alphas,
)

from .constants import (
    BUCKWALTER2UNICODE,
    DERIV,
    DERIVclass,
    NOM,
    NOMclass,
    PGN,
    PGNclass,
    POS,
    POSclass,
    PREFIX,
    PREFIXclass,
    PRON,
    VERB,
    VERBclass,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reverse_class(dictionary: Dict) -> Dict:
    """Invert a class-mapping dict (values may be plain values or lists)."""
    result: Dict = {}
    for key, value in dictionary.items():
        if not isinstance(value, list):
            value = [value]
        for v in value:
            result.setdefault(v, []).append(key)
    return result


def _buck2uni(string: str) -> str:
    """Decode a Buckwalter-transliterated string to Unicode Arabic."""
    return "".join(BUCKWALTER2UNICODE[ch] for ch in string)


# ---------------------------------------------------------------------------
# Pre-computed inverted class dicts (built once at import time)
# ---------------------------------------------------------------------------

_INV_PREFIX: Dict = _reverse_class(PREFIXclass)
_INV_POS: Dict    = _reverse_class(POSclass)
_INV_PGN: Dict    = _reverse_class(PGNclass)
_INV_DERIV: Dict  = _reverse_class(DERIVclass)
_INV_VERB: Dict   = _reverse_class(VERBclass)
_INV_NOM: Dict    = _reverse_class(NOMclass)


# ---------------------------------------------------------------------------
# Pyparsing grammar — built once at module level, not per parse() call
# ---------------------------------------------------------------------------

def _make_keywords(tags: List[str]):
    result = Keyword(tags[0])
    for item in tags[1:]:
        result = result | Keyword(item)
    return result


def _make_literals(tags: List[str]):
    result = Literal(tags[0])
    for item in tags[1:]:
        result = result | Literal(item)
    return result


_begin  = Keyword("$").suppress()
_center = Keyword("\u00a3").suppress()   # £
_last   = Keyword("\u00b5").suppress()   # µ
_end    = Keyword("#").suppress()
_skip   = SkipTo(_end).suppress()

_prefix   = Word(alphas + "+:")
_prefixes = Group(ZeroOrMore(~_center + _prefix))

_genderK = _make_keywords(["M", "F"])
_numberK = _make_keywords(["S", "D", "P"])
_genderL = _make_literals(["M", "F"])
_numberL = _make_literals(["S", "D", "P"])
_personL = _make_literals(["1", "2", "3"])

_person_ = _personL + Optional(_genderL) + Optional(_numberL)
_gender_ = _genderL + _numberL
_gen     = _person_ | _gender_ | _numberK | _genderK

_pos   = "POS:" + Word(alphas)
_lem   = "LEM:" + CharsNotIn(" ")
_root  = "ROOT:" + CharsNotIn(" ")
_sp    = "SP:" + CharsNotIn(" ")
_mood  = "MOOD:" + CharsNotIn(" ")

_aspect = _make_keywords(["PERF", "IMPF", "IMPV"])
_voice  = _make_keywords(["ACT", "PASS"])
_form   = _make_keywords([
    "(I)", "(II)", "(III)", "(IV)", "(V)", "(VI)",
    "(VII)", "(VIII)", "(IX)", "(X)", "(XI)", "(XII)",
])
_verb   = _aspect | _voice | _form
_voc    = Keyword("+voc").suppress()
_deriv  = _make_keywords(["ACT", "PCPL", "PASS", "VN"])
_state  = _make_keywords(["DEF", "INDEF"])
_case   = _make_keywords(["NOM", "ACC", "GEN"])
_nom    = _case | _state

_tag      = _lem | _root | _sp | _mood | _gen | _verb | _deriv | _nom | _voc | _skip
_part     = Group(_center + _pos + ZeroOrMore(~_center + ~_last + ~_end + _tag))
_base     = Group(OneOrMore(~_end + ~_last + _part))
_pron     = "PRON:" + Group(_gen)
_suffixes = Group(ZeroOrMore(~_end + _last + _pron))

_GRAMMAR  = _begin + _prefixes + _base + _suffixes + _end


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

class API:
    """Quranic Corpus morphology XML API."""

    def __init__(self, source: str = "../../store/quranic-corpus-morpology.xml") -> None:
        self.corpus = ET.parse(source)

    class MorphologyParser:
        """Parse morphology tag strings from the Quranic Corpus XML."""

        @staticmethod
        def parse_step1(morph: str):
            """Tokenise a raw morphology string using the module-level grammar."""
            string = (
                "$ "
                + str(morph)
                .replace("POS:", "\u00a3 POS:")
                .replace("PRON:", "\u00b5 PRON:")
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                + " #"
            )
            return _GRAMMAR.parseString(string)

        @staticmethod
        def parse_step2(parsedlist) -> Dict[str, Any]:
            """Convert the pyparsing result into a plain Python dict."""
            result: Dict[str, Any] = {}

            # --- prefixes ---------------------------------------------------
            result["prefixes"] = [
                {
                    "token":       PREFIX[tok][1],
                    "arabictoken": PREFIX[tok][0],
                    "type":        _INV_PREFIX[tok][0],
                }
                for tok in parsedlist[0]
            ]

            # --- base -------------------------------------------------------
            result["base"] = []
            for part in parsedlist[1]:
                part_dict: Dict[str, Any] = {}
                idx = 0
                while idx < len(part):
                    tag = part[idx]
                    if tag.endswith(":"):
                        next_tag = part[idx + 1]
                        if tag == "POS:":
                            part_dict["type"]       = _INV_POS[next_tag][0]
                            part_dict["pos"]        = POS[next_tag][1]
                            part_dict["arabicpos"]  = POS[next_tag][0]
                        elif tag == "ROOT:":
                            part_dict["root"]       = next_tag
                            part_dict["arabicroot"] = _buck2uni(next_tag)
                        elif tag == "LEM:":
                            part_dict["lemma"]       = next_tag
                            part_dict["arabiclemma"] = _buck2uni(next_tag)
                        elif tag == "SP:":
                            part_dict["special"]       = next_tag
                            part_dict["arabicspecial"] = _buck2uni(next_tag)
                        elif tag == "MOOD:":
                            part_dict["mood"]       = VERB[next_tag][1]
                            part_dict["arabicmood"] = VERB[next_tag][0]
                        idx += 2   # consume both the key and the value
                        continue
                    if tag in PGN:
                        part_dict[_INV_PGN[tag][0]] = PGN[tag]
                    elif tag in ("ACT", "PASS"):
                        next_tag = part[idx + 1] if idx + 1 < len(part) else None
                        if next_tag == "PCPL":
                            deriv_key = tag + " PCPL"
                            part_dict[_INV_DERIV[deriv_key][0]] = DERIV[deriv_key][1]
                            idx += 2   # consume "ACT"/"PASS" + "PCPL"
                            continue
                        part_dict[_INV_VERB[tag][0]] = VERB[tag][1]
                    elif tag in VERB:
                        part_dict[_INV_VERB[tag][0]] = VERB[tag][1]
                    elif tag in NOM:
                        nom_field    = _INV_NOM[tag][0]
                        arabic_field = "arabicstate" if nom_field == "state" else "arabiccase"
                        part_dict[nom_field]    = NOM[tag][1]
                        part_dict[arabic_field] = NOM[tag][0]
                    elif tag == "VN":
                        part_dict[_INV_DERIV[tag][0]] = DERIV[tag][1]
                    idx += 1
                result["base"].append(part_dict)

            # --- suffixes ---------------------------------------------------
            result["suffixes"] = []
            suffixes = parsedlist[2]
            idx = 0
            while idx < len(suffixes):
                if suffixes[idx] == "PRON:":
                    pron_dict: Dict[str, Any] = {}
                    p_set = set(PRON["*"])
                    for pgn_tag in suffixes[idx + 1]:
                        if pgn_tag in PGN:
                            pron_dict[_INV_PGN[pgn_tag][0]] = PGN[pgn_tag]
                            p_set &= PRON[pgn_tag]
                    pron_dict["arabictoken"] = p_set.pop() if p_set else ""
                    result["suffixes"].append(pron_dict)
                idx += 1

            return result

        @staticmethod
        def parse(string: str) -> Dict[str, Any]:
            """Parse a morphology string and return a structured dict."""
            return API.MorphologyParser.parse_step2(
                API.MorphologyParser.parse_step1(string)
            )

    def all_words_generator(self) -> Generator[Dict[str, Any], None, None]:
        """Yield one dict per word token across the full corpus."""
        for chapter in self.corpus.findall(".//chapter"):
            sura_id = int(chapter.attrib["number"])
            for verse in chapter.findall("verse"):
                aya_id = int(verse.attrib["number"])
                for word in verse.findall("word"):
                    yield {
                        "sura_id":    sura_id,
                        "aya_id":     aya_id,
                        "word_id":    int(word.attrib["number"]),
                        "word":       word.attrib["token"],
                        "morphology": API.MorphologyParser.parse(
                            word.attrib["morphology"]
                        ),
                    }


if __name__ == "__main__":
    print(API.MorphologyParser.parse("fa+ POS:INTG LEM:maA ROOT:qawol l:P+"))
