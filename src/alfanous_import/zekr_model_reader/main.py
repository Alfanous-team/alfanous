import os.path
import re
from zipfile import ZipFile



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

        for i in range(6236):
            doc = {"gid": i + 1, "id": props["id"],
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
