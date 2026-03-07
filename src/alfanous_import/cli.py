

import os
from alfanous_import.transformer import Transformer
from alfanous_import.updater import update_translations_list

from optparse import OptionParser, OptionGroup

usage = "usage: %prog [options]  SOURCE_PATH DESTINATION_PATH "
parser = OptionParser(usage=usage, version="Alfanous 0.4 - Importer")

commands = OptionGroup(parser, "Options", "Choose what to do:  ")

commands.add_option("-x", "--index", dest="index", type="choice", choices=["main", "word"],
                    help="create  indexes", metavar="TYPE")

commands.add_option("--translations", dest="translations_path",
                    help="path to translation zips store used to embed translations "
                         "as nested child documents into the main index (used with -x main)",
                    metavar="TRANSLATIONS_PATH", default=None)

commands.add_option("--corpus", dest="corpus_path",
                    help="path to quranic corpus morphology XML used to embed word "
                         "occurrences as nested child documents into the main index "
                         "(used with -x main)",
                    metavar="CORPUS_PATH", default=None)

commands.add_option("-d", "--download", dest="download", type="choice",
                    choices=["tanzil_simple_clean", "tanzil_uthmani"],
                    help="download Quranic resources", metavar="FIELD")

commands.add_option("-u", "--update", dest="update", type="choice", choices=["translations"],
                    help="update store information files", metavar="FIELD")

# ── Indexing performance options ─────────────────────────────────────────────
perf = OptionGroup(parser, "Performance options",
                   "Control index build speed and output size.")

perf.add_option("--procs", dest="procs", type="int", default=1,
                help="number of writer processes (default: 1).  "
                     "Values > 1 enable multi-process indexing for faster builds.",
                metavar="N")

perf.add_option("--multisegment", dest="multisegment", action="store_true", default=False,
                help="when --procs > 1, keep sub-process segments separate instead of "
                     "merging them (faster commit, more segments).  "
                     "Recommended for test/CI builds.")

perf.add_option("--batch-size", dest="batch_size", type="int", default=0,
                help="commit every N top-level records and reopen the writer "
                     "(0 = single commit at the end, default).  "
                     "Reduces peak memory for very large builds.",
                metavar="N")

perf.add_option("--optimize", dest="optimize", action="store_true", default=False,
                help="merge all segments into one on the final commit.  "
                     "Produces the smallest index and fastest search reads.  "
                     "Recommended for production builds.")

perf.add_option("--no-merge", dest="no_merge", action="store_true", default=False,
                help="skip segment merging on the final commit "
                     "(equivalent to merge=False).  "
                     "Fastest commit; useful for test/CI builds.")

parser.add_option_group(commands)
parser.add_option_group(perf)

parser.set_defaults(help=True)

(options, args) = parser.parse_args()


if options.index:
    if len(args) == 2:
        SOURCE = args[0]
        DESTINATION = args[1]
    else:
        parser.error("Choose SOURCE_PATH and DISTINATION_PATH")

    # --optimize implies a full merge; --no-merge skips merging
    _merge    = not options.no_merge
    _optimize = options.optimize

    if options.index == "main":
        T = Transformer(index_path=DESTINATION, resource_path=SOURCE)
        ayaSchema = T.build_schema(tablename='aya')
        T.build_docindex(ayaSchema,
                         translations_store_path=options.translations_path,
                         corpus_path=options.corpus_path,
                         merge=_merge,
                         optimize=_optimize,
                         procs=options.procs,
                         multisegment=options.multisegment,
                         batch_size=options.batch_size)

    elif options.index == "word":
        T = Transformer(index_path=DESTINATION, resource_path=SOURCE)
        wordqcSchema = T.build_schema(tablename='wordqc')
        T.build_docindex(wordqcSchema, tablename='wordqc',
                         merge=_merge,
                         optimize=_optimize,
                         procs=options.procs,
                         multisegment=options.multisegment,
                         batch_size=options.batch_size)


if options.update:
    if len(args) != 2:
        parser.error("Choose SOURCE_PATH and DISTINATION_PATH")

    SOURCE = args[0]
    DESTINATION = args[1]

    if options.update == "translations":
        update_translations_list(
            translations_list_file=DESTINATION,
            translations_store_path=SOURCE if os.path.isdir(SOURCE) else None,
        )
