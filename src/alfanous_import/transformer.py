#!/usr/bin/env python

import logging
import os.path
import re
import operator
import sqlite3 as lite

## attention : these libraries will be pickled in the indexes
from whoosh.fields import Schema, STORED, ID, KEYWORD, TEXT, NUMERIC
from whoosh.formats import Positions, Frequency
from whoosh.filedb.filestore import FileStorage
from whoosh import index

from alfanous.engines import QuranicSearchEngine
from alfanous.indexing import QseDocIndex
from alfanous.text_processing import QStandardAnalyzer, QDiacAnalyzer, QArabicSymbolsFilter, QUthmaniDiacAnalyzer, \
    QUthmaniAnalyzer, APermissibleAnalyzer
from alfanous.Support.PyArabic.araby import strip_tashkeel
from alfanous.searching import QReader
from functools import reduce

logging.basicConfig(level=logging.INFO)


class FrequencyZ(Frequency):
    def clean(self):
        pass


def unicode_decode(word):
    import codecs
    return word

class Transformer:
    def __init__(self, ixpath, dypypath, dbpath="main.db"):
        if dbpath:
            self.__mainDb = self.__connect(dbpath)
            self.cur = self.__mainDb.cursor()
        if not (os.path.exists(ixpath)):
            os.makedirs(ixpath)
        self.__storage = FileStorage(ixpath)
        self.__ixpath = ixpath
        self.__dypypath = dypypath

    def __str__(self):
        return "< Alfanous.Transformer >"

    def print_to_json(self, d, filename):
        with  open(f"{self.__dypypath}{filename}.json", "w") as f:
            import json
            json.dump(d, f, indent=4, sort_keys=True, ensure_ascii=False)

        return "OK"

    def __connect(self, dbpath):
        return lite.connect(dbpath)

    def change_DB(self, dbpath):
        return self.__connect(dbpath)

    def __3states(self, str):
        if str == "yes":
            return "True"
        elif str == "no":
            return "False"
        else:
            return None

    def build_schema(self, tablename):
        """build schema from field table"""

        print("require list of arabic_to_english_fields ...")
        cur = self.__mainDb.cursor()
        cur.execute(
            "select search_name,type,analyser,is_stored,boost,phrase,is_scorable,is_unique,format from field where table_name='" + tablename + "' and is_indexed='yes'")
        res = cur.fetchall()

        print("processing list found  and building raw schema ...")
        Schema_raw = "Schema("
        for line in res:
            print(line)
            search_name = str(line[0])
            if search_name not in ["", "None"]:
                # 1
                Schema_raw += search_name + "="
                # 2
                type = str(line[1]).upper()
                if type == "NONE":
                    type = "STORED"
                Schema_raw += type + "("
                Comma = False
                # 3
                analyser = str(line[2])
                if not (analyser == "None" or analyser == ""):
                    Schema_raw += "analyzer=" + analyser
                    Comma = True
                # 4
                is_stored = self.__3states(str(line[3]))
                if is_stored in ["True", "False"]:
                    if Comma: Schema_raw += ","
                    Schema_raw += "stored=" + is_stored
                    Comma = True
                # 5
                boost = str(line[4])
                if not (boost == "None" or boost == ""):
                    if Comma: Schema_raw += ","
                    Schema_raw += "field_boost=" + boost
                    Comma = True
                # 6
                """phrase=self.__3states(str(line[5]))
                if phrase in ["True","False"]:
                    if Comma==True:Schema_raw+=","
                    Schema_raw+="phrase="+phrase
                    Comma=True"""
                """#7
                is_scorable=self.__3states(str(line[6]))
                if is_scorable in ["True","False"]:
                    if Comma==True:Schema_raw+=","
                    Schema_raw+="scorable="+is_scorable
                    Comma=True"""
                # 8
                is_unique = self.__3states(str(line[7]))
                if is_unique in ["True", "False"]:
                    if Comma: Schema_raw += ","
                    Schema_raw += "unique=" + is_stored
                    Comma = True

                # 9
                format = str(line[8])
                if not (format == "None" or format == ""):
                    if Comma: Schema_raw += ","
                    Schema_raw += "vector=" + format
                    Comma = True

                # last
                Schema_raw += "),"
        else:
            pass  # ignored
        Schema_raw = Schema_raw[:-1] + ")"
        print(Schema_raw)

        ldict = {}
        exec("res_schema=" + Schema_raw, globals(), ldict)
        return ldict.get('res_schema')

    def transfer(self, ix, tablename="aya"):
        """transfer from database to index"""
        self.__unlock_docindex(ix)
        # print "search arabic_to_english_fields real names ..."

        schema = ix.schema
        cur = self.__mainDb.cursor()
        seq = []
        for field in list(schema._fields.keys()):
            seq.append(field)
        query = "select name,search_name from field where search_name IN ('" + "','".join(seq) + "')"
        cur.execute(query)

        # build dict{search_name:name}  and re-order it
        names_dict = {}
        for line in cur.fetchall():
            names_dict[line[1]] = line[0]

        seq = []
        for field in list(schema._fields.keys()):
            seq.append(names_dict[field])

        # print "loading DATA..."
        query = "select " + ",".join(['"' + x + '"' for x in seq]) + " from " + tablename
        # print query
        cur.execute(query)
        Data = cur.fetchall()

        logging.info(f"writing documents in index (total: {len(Data)}) ....")
        writer = ix.writer()

        cpt = 0
        fields = list(schema._fields.keys())
        for line in Data:

            writer.add_document(
                **{
                    fields[i]: line[i] for i in range(len(fields)) if line[i]
                }
            )

            cpt += 1
            if not cpt % 1559:
                logging.info(f" - milestone:  {cpt} ( {cpt * 100 / len(Data)}% )")
        logging.info("done.")
        writer.commit()
        self.__lock_docindex(ix)

    def build_docindex(self, schema, tablename="aya"):
        """build document index from aya table"""
        assert schema, "schema is empty"
        ix = self.__storage.create_index(schema)
        self.transfer(ix, tablename)
        return "OK"

    def update_docindex(self, schema, tablename="aya"):
        """update the data in document index
            index schema must have at least an id

            """
        ix = self.__storage.open_index()
        self.__transfer(ix, tablename)
        return "OK"

    def __lock_docindex(self, ix):
        """ lock index """
        # try:
        #    ix.lock()
        # except LockError as LE:
        #    print LE

    def __unlock_docindex(self, ix):
        ix = self.__storage.open_index()
        # return ix.unlock()

    dheader = """
    """

    def transfer_stopwords(self):

        self.cur.execute("select word from stopwords")
        stop_words = [item[0] for item in self.cur.fetchall()]

        return self.print_to_json(stop_words, 'stop_words')

    def transfer_std2uth_words(self):

        self.cur.execute("select word_,uthmani   from word")
        standard2uthmani = {item[0]: item[1] for item in self.cur.fetchall() if item[0] != item[1] and item[1]}

        return self.print_to_json(standard2uthmani, 'standard_to_uthmani')

    def transfer_synonymes(self):

        self.cur.execute("select word,synonymes from synonymes")
        word_regex = re.compile("[^ ,،]+")
        syn_dict = {}
        for item in self.cur.fetchall():
            syn_dict[strip_tashkeel(item[0])] = [strip_tashkeel(w) for w in word_regex.findall(item[1])]

        return self.print_to_json(syn_dict, 'synonyms')

    def transfer_ara2eng_names(self):
        """ load the arabic names of arabic_to_english_fields and save the as a dictionary"""

        self.cur.execute("select name_arabic,search_name from field where table_name='aya'")
        ar_to_en_dict = {item[0]: item[1] for item in self.cur.fetchall()}

        return self.print_to_json(ar_to_en_dict, 'arabic_names')

    def transfer_word_props(self):

        props = ["word", "word_", "root", "type"]
        word_props = {prop: [] for prop in props}

        self.cur.execute(f'select {",".join(props)} from word')

        for item in self.cur.fetchall():
            if reduce(operator.and_, list(map(bool, item)), True):
                for i, prop in zip(range(len(props)), props):
                    word_props[prop].append(item[i])

        return self.print_to_json(word_props, 'word_props')

    def transfer_derivations(self):
        levels = ["word_", "lemma", "root"]
        derivations = {level: [] for level in levels}

        self.cur.execute(f'select {",".join(levels)} from word')

        for item in self.cur.fetchall():
            for i, level in zip(range(len(levels)), levels):
                derivations[level].append(item[i])

        return self.print_to_json(derivations, 'derivations')

    def transfer_vocalizations(self):
        QSE = QuranicSearchEngine(self.__ixpath)

        if not QSE.OK:
            return

        mfw = QSE.most_frequent_words(9999999, "aya_")
        vocalization_dict = { strip_tashkeel(word): unicode_decode(word) for _,word in mfw}

        return self.print_to_json(vocalization_dict, "vocalizations")


if __name__ == "__main__":
    T = Transformer(ixpath="../../indexes/main/", dypypath="../alfanous/resources/",
                    dbpath="../../resources/databases/main.db")

    T.transfer_vocalizations()

