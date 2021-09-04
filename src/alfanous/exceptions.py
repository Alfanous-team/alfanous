


class Ta7rif(Exception):
    def __init__(self, type="new", value="undefined", original=None, aya_gid=None, msg=""):
        self.type = type
        self.aya_gid = aya_gid
        self.value = value
        self.original = original
        self.msg = msg

    def __str__(self):
        return "\nTa7rif in Holy Quran :\n\tType:" + str(self.type) \
               + "\n\tvalue:" + str(self.value) \
               + "\n\toriginalvalue:" + str(self.original) \
               + "\n\taya_gid:" + str(self.aya_gid) \
               + "\n\n" + str(self.msg)
