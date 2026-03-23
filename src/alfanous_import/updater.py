#!/usr/bin/python

import json
import logging

from alfanous.constants import LANGS
from alfanous import paths


def update_translations_list(
    translations_list_file=paths.TRANSLATIONS_LIST_FILE,
    translations_store_path=None,
):
    """Rebuild translations.json.

    When *translations_store_path* is supplied the list is built by reading
    the ``.trans.zip`` files directly (no index required, no temp-dir
    extraction).  Otherwise the function falls back to iterating
    ``trans_id`` field terms from the built QSE index.
    """
    translation_list = {}

    if translations_store_path:
        from alfanous_import.transformer import _iter_translation_zips
        for props, _lines in _iter_translation_zips(translations_store_path):
            trans_id = props.get("id", "")
            lang     = props.get("language", "")
            author   = props.get("name", "")
            if trans_id and lang and author:
                translation_list[trans_id] = (
                    LANGS.get(lang, lang) + "-" + author.title()
                )
    else:
        from alfanous.engines import QuranicSearchEngine
        QSE = QuranicSearchEngine(paths.QSE_INDEX)
        for translation_id in QSE.list_values("trans_id"):
            if not translation_id:
                continue
            try:
                lang, author = translation_id.split('.')
                translation_list[translation_id] = LANGS[lang] + "-" + author.title()
            except Exception as e:
                logging.error(e)

    with open(translations_list_file, "w", encoding="utf-8") as f:
        json.dump(translation_list, f, indent=2, ensure_ascii=False)

    return translation_list
