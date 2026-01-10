import os
import pandas as pd

class Master:
    def __init__(self):
        self.filename = "gitforgex.csv"
        self.filepath = f"./Metadata/{self.filename}"
        self._initialize_csv()

    def _initialize_csv(self):
        try:
            if not os.path.exists(self.filepath):
                master_df = pd.DataFrame(
                    {
                        "FILE.PATH" : pd.Series(dtype="string"),
                        "FILE.SIZE" : pd.Series(dtype="int64"),
                        "FILE.HASH" : pd.Series(dtype="string"),
                        "FILE.MODIFIED" : pd.Series(dtype="bool"),
                        "FILE.TRACK.STATUS" : pd.Series(dtype="bool"),
                        "FILE.STAGE.STATUS" : pd.Series(dtype="bool"),
                        "FILE.COMMIT.STATUS" : pd.Series(dtype="bool"),
                        "FILE.COMMIT.MESSAGE" : pd.Series(dtype="string"),
                        "FILE.COMMIT.HASH" : pd.Series(dtype="string"),
                        "FILE.COMMIT.DATETIME" : pd.Series(dtype="string"),
                        "FILE.LAST.SIZE" : pd.Series(dtype="int64"),
                        "FILE.LAST.MODIFIED.HASH" : pd.Series(dtype="string"),
                        "FILE.LAST.TRACK.STATUS" : pd.Series(dtype="bool"),
                        "FILE.LAST.STAGE.STATUS" : pd.Series(dtype="bool"),
                        "FILE.LAST.COMMIT.STATUS" : pd.Series(dtype="bool"),
                        "FILE.LAST.COMMIT.MESSAGE" : pd.Series(dtype="string"),
                        "FILE.LAST.COMMIT.HASH" : pd.Series(dtype="string"),
                        "FILE.LAST.COMMIT.DATETIME" : pd.Series(dtype="string"),
                    }
                )
                master_df.to_csv(self.filepath, mode="w", header=True, index=False)
        except Exception as e:
            raise Exception(str(e))
        
    class MetaNode:
        def __init__(self, filepath, filesize, filehash, filemodified = False, filetrackstatus = False, filestagestatus = False, filecommitstatus = False, filecommitmessage = None, filecommithash = None, filecommitdatetime = None, filelastsize = -1, filelastmodifiedhash = None, filelasttrackstatus = False, filelaststagestatus = False, filelastcommitstatus = False, filelastcommitmessage = None, filelastcommithash = None, filelastcommitdatetime = None):
            self.filepath = filepath 
            self.filesize = filesize
            self.filehash = filehash
            self.filemodified = filemodified
            self.filetrackstatus = filetrackstatus
            self.filestagestatus = filestagestatus
            self.filecommitstatus = filecommitstatus
            self.filecommitmessage = filecommitmessage
            self.filecommithash = filecommithash
            self.filecommitdatetime = filecommitdatetime
            self.filelastsize = filelastsize
            self.filelastmodifiedhash = filelastmodifiedhash
            self.filelasttrackstatus = filelasttrackstatus
            self.filelaststagestatus = filelaststagestatus
            self.filelastcommitstatus = filelastcommitstatus
            self.filelastcommitmessage = filelastcommitmessage
            self.filelastcommithash = filelastcommithash
            self.filelastcommitdatetime = filelastcommitdatetime