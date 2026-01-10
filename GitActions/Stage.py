

import pandas as pd
from Metadata.filesMeta import Master

class Staging:
    def __init__(self):
        self.master = Master()
        self.filepath = self.master.filepath

        self.untracked_count = 0
        self.read_csv = None
    
    def run(self):
        steps = [self.check_untracked, self.mark_staged]
        for step in steps:
            step()

    def check_untracked(self) -> bool:
        if self.filepath is None:
            return False
        
        self.read_csv = pd.read_csv(self.filepath)
        print(f"file info\n{self.read_csv.head(2)}")

        self.untracked_count = self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == False) & (self.read_csv["FILE.LAST.TRACK.STATUS"] == False) & (self.read_csv["FILE.LAST.COMMIT.STATUS"] == False), "FILE.TRACK.STATUS"].count()
        print(f"untracked count: {self.untracked_count}")

        if self.untracked_count != 0:
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == False) & (self.read_csv["FILE.LAST.TRACK.STATUS"] == False) & (self.read_csv["FILE.LAST.COMMIT.STATUS"] == False), "FILE.TRACK.STATUS"] = True
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.LAST.TRACK.STATUS"] == False) & (self.read_csv["FILE.LAST.COMMIT.STATUS"] == False), "FILE.MODIFIED"] = True
            self.read_csv.to_csv(self.filepath, index=False)
            print(f"Changes are in tracking mode")
            return
        print(f"Changes are not in tracking mode")
        return
    
    def mark_staged(self):
        try:
            if self.untracked_count == 0:
                print(f"No new changes found. Nothing to staged")

            self.read_csv.loc[(self.read_csv["FILE.STAGE.STATUS"] == False) & (self.read_csv["FILE.TRACK.STATUS"] == True), "FILE.STAGE.STATUS"] = True
            self.read_csv.to_csv(self.filepath, index=False)
            print(f"Changes are in staging mode")

        except Exception as e:
            raise Exception(str(e))