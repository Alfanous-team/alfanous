"""Legacy resource loader — superseded by :mod:`alfanous.data`.

This module is retained for backward compatibility only.  All runtime
resource loading (derivations, word properties, vocalizations, etc.) has
been moved to :mod:`alfanous.data`, which uses the live word-children index
as the primary source and falls back to the JSON files only when the index
is not yet built.

Do **not** add new code here.  Import from ``alfanous.data`` instead.
"""

from alfanous.data import (  # noqa: F401  (re-export for any legacy consumers)
    arabic_to_english_fields,
    std2uth_words,
    vocalization_dict,
    syndict,
    antdict,
    derivedict,
    worddict,
)
