"""
Update aya.json and word.json from the Quran-Researcher database dump.

Source: https://github.com/assem-ch/Quran-Researcher
SQL URL: https://raw.githubusercontent.com/assem-ch/Quran-Researcher/refs/heads/main/quran-researcher.sql

The script parses the MySQL dump and:
- Updates the ``uthmani`` field in aya.json from the ``ayahs`` table.
- Updates the ``root`` field in word.json using the ``words`` and ``roots`` tables.
- Updates the ``root`` column in word_props.json from the updated word.json.
- Updates the ``root`` column in derivations.json from the updated word.json.
"""

import json
import re
import urllib.request


SQL_URL = (
    "https://raw.githubusercontent.com/assem-ch/Quran-Researcher"
    "/refs/heads/main/quran-researcher.sql"
)

# Matches the aya-number + sura-name suffix appended to text_othmani values.
_OTHMANI_SUFFIX_RE = re.compile(r"\s*\(\d+\)\s+\S.*$")


def fetch_sql(url=SQL_URL):
    """Download the SQL dump and return it as a string."""
    if not url.startswith("https://"):
        raise ValueError(f"Only HTTPS URLs are allowed, got: {url!r}")
    with urllib.request.urlopen(url) as resp:  # noqa: S310
        return resp.read().decode("utf-8")


def _unescape_sql_string(s):
    """Unescape a MySQL string literal (handle \' and \\)."""
    return s.replace("\\'", "'").replace("\\\\", "\\")


def _iter_insert_rows(sql, table):
    """
    Yield each row's value-tuple string from INSERT statements for *table*.

    The MySQL dump uses multi-row INSERT statements like::

        INSERT INTO `table` (`col1`, ...) VALUES
        (val1, val2, ...),
        (val1, val2, ...);

    Each yielded item is the raw parenthesised string, e.g.
    ``"(1, 2, 'text')"`` *including* the outer parentheses.
    """
    pattern = re.compile(
        r"INSERT INTO `" + re.escape(table) + r"`[^V]+VALUES\s+(.*?);",
        re.DOTALL,
    )
    for match in pattern.finditer(sql):
        values_block = match.group(1)
        # Split on ),\n( boundaries
        for row in re.split(r"\),\s*\n\(", values_block):
            row = row.strip().lstrip("(").rstrip(")")
            yield row


def _split_mysql_row(row):
    """
    Split a MySQL row string into a list of Python values.

    Handles NULL, integers, and single-quoted strings (with escaped quotes).
    """
    values = []
    i = 0
    while i < len(row):
        if row[i] == " " or row[i] == "\n":
            i += 1
            continue
        if row[i:i+4] == "NULL":
            values.append(None)
            i += 4
            # skip trailing comma
            while i < len(row) and row[i] in (", "):
                i += 1
        elif row[i] == "'":
            # Find the closing quote, respecting escaped quotes
            j = i + 1
            buf = []
            while j < len(row):
                if row[j] == "\\" and j + 1 < len(row):
                    buf.append(row[j:j+2])
                    j += 2
                elif row[j] == "'":
                    j += 1
                    break
                else:
                    buf.append(row[j])
                    j += 1
            values.append(_unescape_sql_string("".join(buf)))
            # skip trailing comma/space
            while j < len(row) and row[j] in (", "):
                j += 1
            i = j
        else:
            # Numeric value
            j = i
            while j < len(row) and row[j] not in (",", " ", "\n"):
                j += 1
            token = row[i:j].strip()
            try:
                values.append(int(token))
            except ValueError:
                try:
                    values.append(float(token))
                except ValueError:
                    values.append(token)
            # skip trailing comma/space
            while j < len(row) and row[j] in (", "):
                j += 1
            i = j
    return values


def parse_ayahs(sql):
    """Return a dict mapping aya gid -> {uthmani}."""
    columns = ["id", "sura_id", "ayah_num", "text_othmani", "text_clean", "tafseer"]
    result = {}
    for row_str in _iter_insert_rows(sql, "ayahs"):
        vals = _split_mysql_row(row_str)
        if len(vals) != len(columns):
            continue
        row = dict(zip(columns, vals))
        gid = row["id"]
        # Strip the " (n) SuraName" suffix from text_othmani
        othmani = _OTHMANI_SUFFIX_RE.sub("", row["text_othmani"] or "").strip()
        result[gid] = {
            "uthmani": othmani,
        }
    return result


def parse_roots(sql):
    """Return a dict mapping root_id -> root_text."""
    columns = ["id", "root_text"]
    result = {}
    for row_str in _iter_insert_rows(sql, "roots"):
        vals = _split_mysql_row(row_str)
        if len(vals) != len(columns):
            continue
        result[vals[0]] = vals[1]
    return result


def parse_words(sql, roots):
    """
    Return a dict mapping word_text -> root_text.

    When the same word_text appears with multiple roots, the first
    encountered root is kept (mirrors the order in the SQL dump).
    """
    columns = [
        "id", "ayah_id", "root_id", "word_text", "word_clean",
        "position", "global_position", "real_position",
    ]
    result = {}
    for row_str in _iter_insert_rows(sql, "words"):
        vals = _split_mysql_row(row_str)
        if len(vals) != len(columns):
            continue
        row = dict(zip(columns, vals))
        word_text = row["word_text"] or ""
        if word_text and word_text not in result:
            root_id = row["root_id"]
            result[word_text] = roots.get(root_id, "") if root_id is not None else ""
    return result


def update_aya_json(aya_json_path, ayahs_data):
    """Update aya.json in-place with the uthmani field."""
    with open(aya_json_path, encoding="utf-8") as fh:
        ayas = json.load(fh)

    updated = 0
    for aya in ayas:
        gid = aya.get("gid")
        if gid in ayahs_data:
            data = ayahs_data[gid]
            aya["uthmani"] = data["uthmani"]
            updated += 1

    with open(aya_json_path, "w", encoding="utf-8") as fh:
        json.dump(ayas, fh, ensure_ascii=False, indent=4)

    print(f"aya.json: updated {updated}/{len(ayas)} entries.")


def update_word_json(word_json_path, word_root_map):
    """Update word.json in-place with root data from Quran-Researcher."""
    with open(word_json_path, encoding="utf-8") as fh:
        words = json.load(fh)

    updated = 0
    for word_entry in words:
        word_text = word_entry.get("word", "")
        if word_text in word_root_map:
            root = word_root_map[word_text].replace(" ", "")
            if root:
                word_entry["root"] = root
                updated += 1

    with open(word_json_path, "w", encoding="utf-8") as fh:
        json.dump(words, fh, ensure_ascii=False, indent=4)

    print(f"word.json: updated {updated}/{len(words)} entries with root data.")


def update_word_props_json(word_props_json_path, word_json_path):
    """
    Update word_props.json in-place using root data from the (already updated) word.json.

    Existing entries whose root value differs from word.json are updated.
    Words that now have a root in word.json but are not yet in word_props.json
    are appended as new entries.
    """
    with open(word_props_json_path, encoding="utf-8") as fh:
        props = json.load(fh)
    with open(word_json_path, encoding="utf-8") as fh:
        words = json.load(fh)

    # Build index: vocalized word -> position in props arrays
    word_pos = {w: i for i, w in enumerate(props["word"])}

    updated = 0
    added = 0
    for word_entry in words:
        word_text = word_entry.get("word", "")
        root = word_entry.get("root") or ""
        if not root:
            continue
        if word_text in word_pos:
            i = word_pos[word_text]
            if props["root"][i] != root:
                props["root"][i] = root
                updated += 1
        else:
            props["root"].append(root)
            props["type"].append(word_entry.get("type") or "")
            props["word"].append(word_text)
            props["word_"].append(word_entry.get("word_") or "")
            added += 1

    with open(word_props_json_path, "w", encoding="utf-8") as fh:
        json.dump(props, fh, ensure_ascii=False, indent=4)

    print(f"word_props.json: updated {updated}, added {added} entries.")


def update_derivations_json(derivations_json_path, word_json_path):
    """
    Update derivations.json in-place using root data from the (already updated) word.json.

    derivations.json and word.json share the same row order (aligned by index), so root
    values are transferred positionally.  Only non-empty roots from word.json are written.
    """
    with open(derivations_json_path, encoding="utf-8") as fh:
        deriv = json.load(fh)
    with open(word_json_path, encoding="utf-8") as fh:
        words = json.load(fh)

    updated = 0
    for i, word_entry in enumerate(words):
        root = word_entry.get("root") or ""
        if root and root != deriv["root"][i]:
            deriv["root"][i] = root
            updated += 1

    with open(derivations_json_path, "w", encoding="utf-8") as fh:
        json.dump(deriv, fh, ensure_ascii=False, indent=4)

    print(f"derivations.json: updated {updated} root entries.")


def run(sql_source=None, aya_json=None, word_json=None, word_props_json=None, derivations_json=None):
    """
    Main entry point.

    Parameters
    ----------
    sql_source:
        Path to a local SQL file, or ``None`` to download from :data:`SQL_URL`.
    aya_json:
        Path to aya.json.  Defaults to the standard resource path relative
        to this file.
    word_json:
        Path to word.json.  Defaults to the standard resource path relative
        to this file.
    word_props_json:
        Path to word_props.json.  Defaults to the standard resource path
        relative to this file.
    derivations_json:
        Path to derivations.json.  Defaults to the standard resource path
        relative to this file.
    """
    import os

    base = os.path.join(os.path.dirname(__file__), "..", "..", "store")
    if aya_json is None:
        aya_json = os.path.join(base, "aya.json")
    if word_json is None:
        word_json = os.path.join(base, "word.json")
    if word_props_json is None:
        word_props_json = os.path.join(os.path.dirname(__file__), "..", "alfanous", "resources", "word_props.json")
    if derivations_json is None:
        derivations_json = os.path.join(os.path.dirname(__file__), "..", "alfanous", "resources", "derivations.json")

    if sql_source is None:
        print(f"Downloading SQL from {SQL_URL} …")
        sql = fetch_sql()
    else:
        print(f"Reading SQL from {sql_source} …")
        with open(sql_source, encoding="utf-8") as fh:
            sql = fh.read()

    print("Parsing ayahs table …")
    ayahs_data = parse_ayahs(sql)
    print(f"  found {len(ayahs_data)} ayahs.")

    print("Parsing roots table …")
    roots = parse_roots(sql)
    print(f"  found {len(roots)} roots.")

    print("Parsing words table …")
    word_root_map = parse_words(sql, roots)
    print(f"  found {len(word_root_map)} unique word forms.")

    print(f"Updating {aya_json} …")
    update_aya_json(aya_json, ayahs_data)

    print(f"Updating {word_json} …")
    update_word_json(word_json, word_root_map)

    print(f"Updating {word_props_json} …")
    update_word_props_json(word_props_json, word_json)

    print(f"Updating {derivations_json} …")
    update_derivations_json(derivations_json, word_json)

    print("Done.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Update aya.json, word.json, word_props.json and derivations.json from Quran-Researcher SQL dump."
    )
    parser.add_argument(
        "--sql",
        metavar="FILE",
        help="Path to a local SQL dump file (default: download from GitHub).",
    )
    parser.add_argument(
        "--aya-json",
        metavar="FILE",
        help="Path to aya.json (default: src/alfanous/resources/aya.json).",
    )
    parser.add_argument(
        "--word-json",
        metavar="FILE",
        help="Path to word.json (default: src/alfanous/resources/word.json).",
    )
    parser.add_argument(
        "--word-props-json",
        metavar="FILE",
        help="Path to word_props.json (default: src/alfanous/resources/word_props.json).",
    )
    parser.add_argument(
        "--derivations-json",
        metavar="FILE",
        help="Path to derivations.json (default: src/alfanous/resources/derivations.json).",
    )
    args = parser.parse_args()
    run(
        sql_source=args.sql,
        aya_json=args.aya_json,
        word_json=args.word_json,
        word_props_json=args.word_props_json,
        derivations_json=args.derivations_json,
    )
