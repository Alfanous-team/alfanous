#!/usr/bin/python

import json
import logging

from alfanous.constants import LANGS
from alfanous.engines import TraductionSearchEngine
from alfanous import paths


def update_translations_list(TSE_index=paths.TSE_INDEX,
                             translations_list_file=paths.TRANSLATIONS_LIST_FILE):
    TSE = TraductionSearchEngine(TSE_index)
    # Only include translations that are actually indexed
    translation_list = {}
    for translation_id in TSE.list_values("id"):
        try:
            lang, author = translation_id.split('.')
            translation_list[translation_id] = LANGS[lang] + "-" + author.title()
        except Exception as e:
            logging.error(e)
    with open(translations_list_file, "w", encoding="utf-8") as f:
        json.dump(translation_list, f, indent=2, ensure_ascii=False)

    return translation_list
