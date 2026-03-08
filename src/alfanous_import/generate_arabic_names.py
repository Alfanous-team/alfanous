"""
Generate src/alfanous/resources/__generated__/arabic_names.json from store/fields.json.

The output maps every *indexed* field's search_name to its Arabic display
name::

    { "aya": "آية", "gid": "رقم", "sura_arabic": "سورة", … }

"Indexed" means the Whoosh field type is not ``STORED`` (i.e. the field can
actually be searched or filtered by users).  When the same search_name
appears more than once in fields.json, the first occurrence is kept.

The file is consumed by ``alfanous.data`` which reverses it at load time to
produce the ``{arabic_name: search_name}`` mapping used by the Arabic query
parser.

Run via::

    make generate_arabic_names
    # or directly:
    python -m alfanous_import.generate_arabic_names
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
FIELDS_JSON = os.path.join(_REPO_ROOT, "store", "fields.json")
OUTPUT_JSON = os.path.join(
    os.path.dirname(__file__), "..", "alfanous", "resources", "__generated__", "arabic_names.json"
)


def generate(fields_path=FIELDS_JSON, output_path=OUTPUT_JSON):
    """Read *fields_path* and write the arabic-names mapping to *output_path*."""
    with open(fields_path, encoding="utf-8") as fh:
        fields = json.load(fh)

    mapping = {}
    for field in fields:
        arabic_name = (field.get("name_arabic") or "").strip()
        search_name = (field.get("search_name") or "").strip()
        field_type = (field.get("type") or "").upper()

        # Skip fields without an Arabic name, without a search name,
        # or that are stored-only (not indexed/searchable).
        if not arabic_name or not search_name or field_type == "STORED":
            continue

        # First occurrence wins when the same search_name appears multiple times.
        if search_name not in mapping:
            mapping[search_name] = arabic_name

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(mapping, fh, ensure_ascii=False, indent=2, sort_keys=True)

    logger.info("Written %d entries to %s", len(mapping), output_path)
    return mapping


if __name__ == "__main__":
    generate()
