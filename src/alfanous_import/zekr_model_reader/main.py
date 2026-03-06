import json
import logging
import os.path
import re
from functools import lru_cache
from zipfile import ZipFile


@lru_cache(maxsize=1)
def _load_gid_verse_map():
    """Return a dict mapping gid (int) → (sura_id, aya_id) from alfanous aya.json."""
    try:
        from alfanous import paths as _alfanous_paths
        aya_json = os.path.join(_alfanous_paths.ROOT_RESOURCE, "aya.json")
    except ImportError:
        # Fallback: resolve relative to this file's location
        aya_json = os.path.normpath(os.path.join(
            os.path.dirname(__file__),
            "..", "..", "alfanous", "resources", "aya.json",
        ))
    with open(aya_json, encoding="utf-8") as f:
        data = json.load(f)
    return {int(entry["gid"]): (int(entry["sura_id"]), int(entry["aya_id"])) for entry in data}


class TranslationModel:

    def __init__(self, path="./example.zip_file"):
        """
            @param path:the path of model directory or zip_file file
            @attention: add the last slash for directories
            """
        print(path)
        assert os.path.exists(path), "path does not exist!!"

        if os.path.isfile(path):
            self.path = self.open_zip(path)
        else:
            assert False, "type of path is not defined : %s" % path

    def open_zip(self, zip_file, temp="/tmp/alfanous/"):
        """ """
        ZF = ZipFile(zip_file)
        if not os.path.exists(temp):
            os.mkdir(temp)
        ZF.extractall(temp)
        return temp

    def translation_properties(self):
        """ get the properties of the translation """
        tpfile = open(self.path + "translation.properties", "r")
        # linerx = re.compile( "[^=\r\n#]+=[^=\r\n#]+" )
        wordrx = re.compile("[^=\r\n#]+")
        D = {}
        for line in tpfile.readlines():
            res = wordrx.findall(line)
            if len(res) == 2: D[res[0]] = res[1]

        return D

    def translation_lines(self, props):
        """ return the lines list of translation """
        tfile = open(self.path + props["file"], "r")
        linerx = re.compile("[^" + props["lineDelimiter"] + "]+")
        return linerx.findall(tfile.read())

    def document_list(self):
        props = self.translation_properties()
        lines = self.translation_lines(props)
        assert len(lines) == 6236, "the number of lines is not 6236"

        gid_map = _load_gid_verse_map()
        for i in range(6236):
            gid = i + 1
            verse = gid_map.get(gid)
            if verse is None:
                logging.warning("gid=%d not found in verse map; sura_id and aya_id will be None", gid)
                sura_id, aya_id = None, None
            else:
                sura_id, aya_id = verse
            doc = {"gid": gid, "id": props["id"],
                   "sura_id": sura_id,
                   "aya_id": aya_id,
                   "text": lines[i],
                   "type": "translation",
                   "lang": props["language"],
                   "country": props["country"],
                   "author": props["name"],
                   "copyright": props["copyright"],
                   "binary": None}  # the same of the schema
            yield doc


if __name__ == "__main__":
    TM = TranslationModel("./example.zip_file")
    props = TM.translation_properties()
