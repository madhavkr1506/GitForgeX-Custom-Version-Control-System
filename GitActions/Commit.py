import sys
import pandas as pd
from cryptography.hazmat.primitives import hashes
from Metadata.filesMeta import Master

class Commit:
    def __init__(self):
        self.master = Master()
        self.filepath = self.master.filepath

        self.read_csv = None

        self.staged_count = 0
        self.commit_required = False
        self.commit_message = ""

        self.commit_hash_hex = ""

    def run(self):
        steps = [self.check_commit_required, self.get_commit_hash, self.get_commit_message, self.add_commit_message, self.add_commit_hash]
        for step in steps:
            step()

    def check_commit_required(self):
        self.read_csv = pd.read_csv(self.filepath)
        tracked_count = self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True), "FILE.TRACK.STATUS"].count()
        if tracked_count == 0:
            self.commit_required = False
            return
        self.commit_required = True
        return

    def get_commit_hash(self):
        if self.commit_required:
            hash_digest = hashes.Hash(algorithm=hashes.SHA256())
            f_data_hash_hex = self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True), "FILE.HASH"]
            combined_f_data_hash_hex = "".join(f_data_hash_hex)
            print(f"Combined input data hash hex: {combined_f_data_hash_hex}")
            hash_digest.update(combined_f_data_hash_hex.encode("UTF-8"))
            hash_bytes_fmt = hash_digest.finalize()
            print(f"Hash bytes format: {hash_bytes_fmt}")
            self.commit_hash_hex = hash_bytes_fmt.hex()
            print(f"Commit hash hex: {self.commit_hash_hex}")

    def get_commit_message(self):
        if self.commit_required:
            print(f"Input commit message: ", end="\t", flush=True)
            input = sys.stdin.readline()
            self.commit_message = input.strip()

    def add_commit_message(self):
        if self.commit_message == "":
            self.commit_message = self.commit_hash_hex

        self.read_csv.loc[self.read_csv["FILE.STAGE.STATUS"] == True, "FILE.COMMIT.MESSAGE"] = self.commit_message
        self.read_csv.to_csv(self.filepath, header=False, index=False)

    def add_commit_hash(self):
        try:
            if self.commit_hash_hex == "" or self.commit_hash_hex is None:
                return
            
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == False), "FILE.COMMIT.HASH"] = self.commit_hash_hex

            self.read_csv.to_csv(self.filepath, index=False)
        except Exception as e:
            raise Exception(str(e))