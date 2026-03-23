import logging

from alfanous import api

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

a = api.search(u">>ملك")
logger.debug(a)
#api.do({"action":"search","query":u"الله"})
#api.do({"action":"search","query":u"Allh"}) # Buckwalter transliteration