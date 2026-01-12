import sys
import json
from pathlib import Path
from Metadata import *
from Logging import *
from cryptography.hazmat.primitives import hashes
from Metadata import *

class Commit:
    def __init__(self):
        log = PrintLog()
        self.log = log.log

        self.worktreepath = Path("./.gitforgex/")

        self.commit_required = False
        self.hashinputs = []
        self.commit_hash = None
        self.commit_msgs = None

    def run(self):
        steps = [self.check_commit_required, self.get_commit_hash, self.get_commit_message, self.changing_entry_state]
        for step in steps:
            step()

    def reading_entry_state(self, filepath):
        try:
            contents = None,
            with open(file=filepath, mode="r") as jsonfile:
                contents = json.load(jsonfile)
            jsonfile.close()
            return contents

        except Exception as e:
            self.log.error(
                "binary reading failed"
            )

    def updating_entry_state(self, filepath, payload):     
        with open(file=filepath, mode="w") as jsonfile:
            json.dump(payload, jsonfile, indent=4)
        jsonfile.close()

        self.log.info(f"commit state is updated: {filepath}")

    def check_commit_required(self):
        for filepath in self.worktreepath.glob("**/*"):
            if filepath.is_dir() or "cache" in str(filepath):
                continue

            contents = self.reading_entry_state(filepath=filepath)     

            current_staged = contents.get("current").get("staged")
            current_tracked = contents.get("current").get("tracked")
            current_hash = contents.get("current").get("hash")
            if (current_tracked and current_staged):
                self.commit_required = True
                self.hashinputs.append(current_hash)
                

    def get_commit_hash(self):
        if self.commit_required:
            hashsha256 = hashes.Hash(algorithm=hashes.SHA256())
            hashinputs = "".join(self.hashinputs)
            hashinputs = hashinputs.encode("UTF-8")
            hashsha256.update(hashinputs)
            hashdigest = hashsha256.finalize()
            hash256hex = hashdigest.hex()
            self.commit_hash = hash256hex


    def get_commit_message(self):
        if self.commit_required:
            print(f"Input commit message: ", end="\t", flush=True)
            input = sys.stdin.readline()
            self.commit_msgs = input.strip()

    def changing_entry_state(self):
        if self.commit_msgs is not None and self.commit_hash is not None:
            for filepath in self.worktreepath.glob("**/*"):
                if filepath.is_dir() or "cache" in str(filepath):
                    continue
                contents = self.reading_entry_state(filepath=filepath)
                current_staged = contents.get("current").get("staged")
                current_tracked = contents.get("current").get("tracked")
                if (current_staged and current_tracked):
                    contents["current"]["commit_hash"] = self.commit_hash
                    contents["current"]["message"] = self.commit_msgs

                    self.updating_entry_state(filepath=filepath, payload=contents)
                    self.log.info(
                        "changes are in commit mode\nchanges are in tracking mode"
                    )