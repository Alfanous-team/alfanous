"""
Example: Indexing additional translations with alfanous.index_translations()
============================================================================

This script demonstrates how to extend the Alfanous search index with
additional Zekr-compatible `.trans.zip` translation files using the
`alfanous.index_translations()` API.

Requirements
------------
- alfanous3  (pip install alfanous3)
- alfanous_import  (available under src/alfanous_import/ in the repository)

Running
-------
From the repository root::

    PYTHONPATH=src python3 examples/index_translations_example.py

Or point it at any folder that contains ``.trans.zip`` files::

    PYTHONPATH=src python3 examples/index_translations_example.py /path/to/translations
"""

import sys
import os

# ---------------------------------------------------------------------------
# Resolve the translations source directory
# ---------------------------------------------------------------------------
# Default: use the translation zips that ship with the repository
DEFAULT_SOURCE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "store", "Translations")
)

source_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SOURCE

print(f"Source directory: {source_dir}")
if not os.path.isdir(source_dir):
    print(f"ERROR: '{source_dir}' is not a directory.")
    sys.exit(1)

zip_files = [f for f in os.listdir(source_dir) if f.endswith(".trans.zip")]
print(f"Found {len(zip_files)} .trans.zip file(s): {', '.join(sorted(zip_files)) or '(none)'}")

# ---------------------------------------------------------------------------
# Import alfanous
# ---------------------------------------------------------------------------
import alfanous.api as alfanous

# ---------------------------------------------------------------------------
# 1. List currently available translations (before indexing)
# ---------------------------------------------------------------------------
print("\n--- Available translations (before) ---")
translations_before = alfanous.get_info("translations")
trans_dict = translations_before.get("show", {}).get("translations", {})
print(f"  {len(trans_dict)} translation(s) available")
for tid, name in sorted(trans_dict.items()):
    print(f"  {tid}: {name}")

# ---------------------------------------------------------------------------
# 2. Index translations from the source directory
# ---------------------------------------------------------------------------
print(f"\n--- Indexing translations from '{source_dir}' ---")
try:
    count = alfanous.index_translations(source=source_dir)
    if count:
        print(f"  {count} translation(s) newly indexed.")
    else:
        print("  All translations already present in the index — nothing new to add.")
except ImportError as exc:
    print(f"  ImportError: {exc}")
    print(
        "  Install the alfanous_import package from the repository:\n"
        "    pip install -e src/alfanous_import/"
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# 3. List available translations again (after indexing)
# ---------------------------------------------------------------------------
print("\n--- Available translations (after) ---")
translations_after = alfanous.get_info("translations")
trans_dict_after = translations_after.get("show", {}).get("translations", {})
print(f"  {len(trans_dict_after)} translation(s) available")
for tid, name in sorted(trans_dict_after.items()):
    marker = " (NEW)" if tid not in trans_dict else ""
    print(f"  {tid}: {name}{marker}")

# ---------------------------------------------------------------------------
# 4. Search in a specific translation
# ---------------------------------------------------------------------------
if trans_dict_after:
    sample_id = next(iter(sorted(trans_dict_after)))
    print(f"\n--- Sample search in translation '{sample_id}' ---")
    result = alfanous.search(u"الرحمن", unit="translation",
                             flags={"translation": sample_id})
    ayas = result.get("search", {}).get("ayas", {})
    total = ayas.get("counter", 0)
    print(f"  Found {total} result(s) for 'الرحمن' in '{sample_id}'")
