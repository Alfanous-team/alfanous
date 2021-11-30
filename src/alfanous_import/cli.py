

from alfanous_import.importer import ZekrModelsImporter, QuranicCorpusImporter
from alfanous_import.transformer import Transformer
from alfanous_import.updater import update_translations_list

from optparse import OptionParser, OptionGroup

usage = "usage: %prog [options]  SOURCE_PATH DESTINATION_PATH "
parser = OptionParser(usage=usage, version="Alfanous 0.4 - Importer")

commands = OptionGroup(parser, "Options", "Choose what to do:  ")

commands.add_option("-x", "--index", dest="index", type="choice", choices=["main", "extend", "word"],
                    help="create  indexes", metavar="TYPE")

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
        T.build_docindex(ayaSchema)

    elif options.index == "extend":
        E = ZekrModelsImporter(pathindex=DESTINATION, pathstore=SOURCE)
        E.load_translationModels()

    elif options.index == "word":
        T = Transformer(index_path=DESTINATION, resource_path=SOURCE)
        wordqcSchema = T.build_schema(tablename='wordqc')
        T.build_docindex(wordqcSchema, tablename='wordqc')


if options.update:
    if len(args) != 2:
        parser.error("Choose SOURCE_PATH and DISTINATION_PATH")

    SOURCE = args[0]
    DESTINATION = args[1]

    if options.update == "translations":
        update_translations_list(TSE_index=SOURCE, translations_list_file=DESTINATION)
    elif options.update == "wordqc":
        QCI = QuranicCorpusImporter(SOURCE, DESTINATION)
