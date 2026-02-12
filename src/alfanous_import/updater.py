#!/usr/bin/python

import json
import logging

from alfanous.constants import LANGS
from alfanous.engines import TraductionSearchEngine


def update_translations_list(TSE_index="../../indexes/extend",
                             translations_list_file="../../resources/configs/translations.js"):
    TSE = TraductionSearchEngine(TSE_index)
    translation_list = {}
    for id in TSE.list_values("id"):
        try:
            lang, author = id.split('.')
            translation_list[id] = LANGS[lang] + "-" + author.title()
        except Exception as e:
            logging.error(e)
    f = open(translations_list_file, "w")
    f.write(json.dumps(translation_list))

    return translation_list
