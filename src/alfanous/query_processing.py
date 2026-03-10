
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
from whoosh.qparser.plugins import SingleQuotePlugin, EveryPlugin

# ---------------------------------------------------------------------------
# Pre-compiled regexes and operator tables used by ArabicParser._preprocess_query.
# Defined at module level so they are compiled once per process, not once per
# parse() call.
# ---------------------------------------------------------------------------

# Split a query string on quoted sub-strings to protect their contents.
_QUOTE_SPLIT_RE = re.compile(r'("[^"]*"|\'[^\']*\')')

# Match a field-name token followed immediately by ':'.
_FIELD_RE = re.compile(r'([\w\u0600-\u06FF]+):')

# Match a full bracket range expression.
_RANGE_OUTER_RE = re.compile(r'\[([^\]]+)\]')

# Match the Arabic range word "الى"/"إلى" when not adjacent to non-whitespace.
_RANGE_INNER_RE = re.compile(r'(?<!\S)(الى|إلى)(?!\S)')

# Arabic logical operator table.  Insertion order is significant: longer
# tokens (وليس) must appear before their prefixes (و / ليس) so the alternation
# in _ARABIC_OPS_RE always matches the longest token first.
_ARABIC_OPS = {
    'وليس': 'ANDNOT',
    'ليس':  'NOT',
    'و':    'AND',
    'أو':   'OR',
    'او':   'OR',
}

# Matches an Arabic logical operator surrounded by horizontal whitespace.
_ARABIC_OPS_RE = re.compile(
    r'(?<=[^\S\n])(' + '|'.join(re.escape(k) for k in _ARABIC_OPS) + r')(?=[^\S\n])'
)

# Matches a leading NOT operator at the very start of a (sub-)expression.
_START_NOT_RE = re.compile(
    r'^(' + '|'.join(re.escape(k) for k in ('ليس', 'وليس')) + r')(?=\s)'
)

# Symbol binary operator table.
_SYM_OPS = {'+': 'AND', '|': 'OR', '-': 'ANDNOT'}

# Matches a symbol binary operator surrounded by spaces.
_SYM_OPS_RE = re.compile(
    r'(?<=\s)(' + '|'.join(re.escape(k) for k in _SYM_OPS) + r')(?=\s)'
)


class StandardParser(QueryParser):  #
    def __init__(self, schema, mainfield, otherfields, termclass=Term):
        super().__init__(
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

        super().__init__(schema=schema,
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
            ArabicWildcardPlugin
        )
        
        # Remove SingleQuotePlugin to allow our TashkilPlugin to work
        self.remove_plugin_class(SingleQuotePlugin)
        # Remove EveryPlugin so *:* does not translate to a match-all query
        self.remove_plugin_class(EveryPlugin)
        
        # Add all Arabic query plugins (instantiate plugin classes)
        self.add_plugin(SynonymsPlugin())
        self.add_plugin(AntonymsPlugin())
        self.add_plugin(DerivationPlugin())
        self.add_plugin(SpellErrorsPlugin())
        self.add_plugin(TashkilPlugin())
        self.add_plugin(TuplePlugin())
        self.add_plugin(ArabicWildcardPlugin())

    def _preprocess_query(self, querystr):
        """Translate Arabic field names, range keywords, and logical operators before Whoosh parsing."""
        # Split on quoted strings ('...' and "...") to protect their contents
        parts = _QUOTE_SPLIT_RE.split(querystr)

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
            p = _FIELD_RE.sub(replace_field, p)

            # 2. Replace Arabic range keyword 'الى'/'إلى' with 'TO' inside brackets
            def replace_range(m):
                inner = _RANGE_INNER_RE.sub('TO', m.group(1))
                return '[' + inner + ']'
            p = _RANGE_OUTER_RE.sub(replace_range, p)

            # 3. Replace Arabic logical operators (only when surrounded by whitespace)
            p = _ARABIC_OPS_RE.sub(lambda m: _ARABIC_OPS[m.group(1)], p)
            p = _START_NOT_RE.sub(lambda m: _ARABIC_OPS[m.group(1)], p)

            # 4. Replace symbol binary operators surrounded by spaces
            p = _SYM_OPS_RE.sub(lambda m: _SYM_OPS[m.group(1)], p)

            result_parts.append(p)

        return ''.join(result_parts)

    def parse(self, querystr, normalize=True, debug=False):
        """Parse a query string, first preprocessing Arabic field names and range syntax."""
        return super().parse(
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
        super().__init__(schema=schema,
                         mainfield=mainfield,
                         otherfields=otherfields,
                         termclass=termclass)

