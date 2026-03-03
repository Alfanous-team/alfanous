
"""
This module contains customized query parsers for Arabic and Quran.

TODO Buckwalter/Other codings Search  {bw!  kutubo }
TODO Upgrading Tuple Search to Embeded Query Search  {1! word="foo"}
TODO Smart-search : take the optimal choice with NLP!
TODO Synonyme-Antonyme Upgrade to related search {syn!  fire }
FIXME multifields
"""

import re

from whoosh import qparser

from whoosh.qparser import QueryParser
from whoosh.query import Term

from alfanous.data import arabic_to_english_fields

# Import query plugins for integration with Whoosh 2.7
from whoosh.qparser.plugins import SingleQuotePlugin


class StandardParser(QueryParser):  #
    def __init__(self, schema, mainfield, otherfields, termclass=Term):
        super(StandardParser, self).__init__(
            mainfield,
            schema=schema,
            group=qparser.OrGroup,
            termclass=termclass
        )


class ArabicParser(StandardParser):
    """a customized parser that respects Arabic properties"""

    def __init__(self,
                 schema,
                 mainfield,
                 otherfields=[],
                 termclass=Term,
                 ara2eng=arabic_to_english_fields):

        super(ArabicParser, self).__init__(schema=schema,
                                           mainfield=mainfield,
                                           otherfields=otherfields,
                                           termclass=termclass)
        self.ara2eng = ara2eng
        
        # Add Whoosh 2.7 query plugins for custom Arabic syntax
        # Import here to avoid circular dependency
        from alfanous.query_plugins import (
            SynonymsPlugin,
            AntonymsPlugin,
            DerivationPlugin,
            SpellErrorsPlugin,
            TashkilPlugin,
            TuplePlugin,
            ArabicWildcardPlugin,
            StemmingPlugin
        )
        
        # Remove SingleQuotePlugin to allow our TashkilPlugin to work
        self.remove_plugin_class(SingleQuotePlugin)
        
        # Add all Arabic query plugins (instantiate plugin classes)
        self.add_plugin(SynonymsPlugin())
        self.add_plugin(AntonymsPlugin())
        self.add_plugin(DerivationPlugin())
        self.add_plugin(SpellErrorsPlugin())
        self.add_plugin(TashkilPlugin())
        self.add_plugin(TuplePlugin())
        self.add_plugin(ArabicWildcardPlugin())
        self.add_plugin(StemmingPlugin())

    def _preprocess_query(self, querystr):
        """Translate Arabic field names, range keywords, and logical operators before Whoosh parsing."""
        # Split on quoted strings ('...' and "...") to protect their contents
        parts = re.split(r'("[^"]*"|\'[^\']*\')', querystr)

        result_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Inside quotes - preserve as-is
                result_parts.append(part)
                continue

            p = part

            # 1. Replace Arabic field names with English schema equivalents
            def replace_field(match):
                field = match.group(1)
                return self.ara2eng.get(field, field) + ':'
            p = re.sub(r'([\w\u0600-\u06FF]+):', replace_field, p)

            # 2. Replace Arabic range keyword 'الى'/'إلى' with 'TO' inside brackets
            def replace_range(m):
                inner = re.sub(r'(?<!\S)(الى|إلى)(?!\S)', 'TO', m.group(1))
                return '[' + inner + ']'
            p = re.sub(r'\[([^\]]+)\]', replace_range, p)

            # 3. Replace Arabic logical operators (only when surrounded by whitespace)
            _arabic_ops = {'وليس': 'ANDNOT', 'ليس': 'NOT', 'و': 'AND',
                           'أو': 'OR', 'او': 'OR'}
            _arabic_ops_re = re.compile(
                r'(?<=[^\S\n])(' + '|'.join(re.escape(k) for k in _arabic_ops) + r')(?=[^\S\n])'
            )
            p = _arabic_ops_re.sub(lambda m: _arabic_ops[m.group(1)], p)
            p = re.sub(r'^(' + '|'.join(re.escape(k) for k in ('ليس', 'وليس')) + r')(?=\s)',
                       lambda m: _arabic_ops[m.group(1)], p)

            # 4. Replace symbol binary operators surrounded by spaces
            _sym_ops = {'+': 'AND', '|': 'OR', '-': 'ANDNOT'}
            _sym_ops_re = re.compile(
                r'(?<=\s)(' + '|'.join(re.escape(k) for k in _sym_ops) + r')(?=\s)'
            )
            p = _sym_ops_re.sub(lambda m: _sym_ops[m.group(1)], p)

            result_parts.append(p)

        return ''.join(result_parts)

    def parse(self, querystr, normalize=True, debug=False):
        """Parse a query string, first preprocessing Arabic field names and range syntax."""
        return super(ArabicParser, self).parse(
            self._preprocess_query(querystr), normalize=normalize, debug=debug
        )


class QuranicParser(ArabicParser):
    """a customized query parser for Quran"""

    def __init__(self,
                 schema,
                 mainfield="aya",
                 otherfields=[],
                 termclass=Term,
                 ara2eng=arabic_to_english_fields):
        super(QuranicParser, self).__init__(schema=schema,
                                            mainfield=mainfield,
                                            otherfields=otherfields,
                                            termclass=termclass)

