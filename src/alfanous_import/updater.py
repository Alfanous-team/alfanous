#!/usr/bin/python

import json
import logging

from alfanous.constants import LANGS
from alfanous.engines import QuranicSearchEngine
from alfanous import paths


def update_translations_list(translations_list_file=paths.TRANSLATIONS_LIST_FILE):
    """Rebuild translations.json from nested ``trans_id`` values in the QSE index."""
    translation_list = {}

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
