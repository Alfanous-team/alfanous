

from alfanous_import.importer import ZekrModelsImporter, QuranicCorpusImporter
from alfanous_import.transformer import Transformer
from alfanous_import.updater import update_translations_list

from optparse import OptionParser, OptionGroup

usage = "usage: %prog [options]  SOURCE_PATH DESTINATION_PATH "
parser = OptionParser(usage=usage, version="Alfanous 0.4 - Importer")

commands = OptionGroup(parser, "Options", "Choose what to do:  ")

commands.add_option("-x", "--index", dest="index", type="choice", choices=["main", "extend", "word"],
                    help="create  indexes", metavar="TYPE")

commands.add_option("--translations", dest="translations_path",
                    help="path to translation zips store used to embed transliteration "
                         "and tafsir text into the main index (used with -x main)",
                    metavar="TRANSLATIONS_PATH", default=None)

commands.add_option("-t", "--index-translation", dest="index_translation",
                    help="index a single translation zip file into the extend index. "
                         "ZIP_FILE is the path to the .trans.zip file; "
                         "provide the index directory as the single positional argument.",
                    metavar="ZIP_FILE", default=None)

commands.add_option("-d", "--download", dest="download", type="choice",
                    choices=["tanzil_simple_clean", "tanzil_uthmani"],
                    help="download Quranic resources", metavar="FIELD")

commands.add_option("-u", "--update", dest="update", type="choice", choices=["translations", "wordqc"],
                    help="update store information files", metavar="FIELD")

parser.add_option_group(commands)

parser.set_defaults(help=True)

(options, args) = parser.parse_args()


if options.index:
    if len(args) == 2:
        SOURCE = args[0]
        DESTINATION = args[1]
    else:
        parser.error("Choose SOURCE_PATH and DISTINATION_PATH")

    if options.index == "main":
        T = Transformer(index_path=DESTINATION, resource_path=SOURCE)
        ayaSchema = T.build_schema(tablename='aya')
        T.build_docindex(ayaSchema, translations_store_path=options.translations_path)

    elif options.index == "extend":
        E = ZekrModelsImporter(pathindex=DESTINATION, pathstore=SOURCE)
        E.load_translationModels()

    elif options.index == "word":
        T = Transformer(index_path=DESTINATION, resource_path=SOURCE)
        wordqcSchema = T.build_schema(tablename='wordqc')
        T.build_docindex(wordqcSchema, tablename='wordqc')


if options.index_translation:
    if len(args) != 1:
        parser.error("Provide DESTINATION_PATH (index directory) as the single positional argument")
    ZIP_FILE = options.index_translation
    DESTINATION = args[0]
    E = ZekrModelsImporter(pathindex=DESTINATION, pathstore="")
    E.index_single_translation(ZIP_FILE)


if options.update:
    if len(args) != 2:
        parser.error("Choose SOURCE_PATH and DISTINATION_PATH")

    SOURCE = args[0]
    DESTINATION = args[1]

    if options.update == "translations":
        update_translations_list(TSE_index=SOURCE, translations_list_file=DESTINATION)
    elif options.update == "wordqc":
        QCI = QuranicCorpusImporter(SOURCE, DESTINATION)
