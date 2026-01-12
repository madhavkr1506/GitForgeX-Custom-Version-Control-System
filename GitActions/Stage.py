
import json
from pathlib import *
from Logging import *

class Staging:
    def __init__(self):
        self.log = PrintLog()
        self.log = self.log.log

        self.worktreepath = Path("./.gitforgex/")
        self.untracked_count = 0
    def run(self):
        steps = [self.staged_changes]
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

        self.log.info(f"staging state is updated: {filepath}")


    def staged_changes(self, filepath = None) -> bool:
        for filepath in self.worktreepath.glob("**/*"):
            if filepath.is_dir():
                continue
            contents = self.reading_entry_state(filepath=filepath)     
                   
            current_tracked = contents.get("current").get("tracked")
            last_tracked = contents.get("last").get("tracked")
            last_committed = contents.get("last").get("committed")

            if not (current_tracked and last_tracked and last_committed):
                self.untracked_count += 1
                contents["current"]["staged"] = True
                contents["current"]["modified"] = True
                contents["current"]["tracked"] = True
                self.updating_entry_state(filepath=filepath, payload=contents)
                self.log.info(
                    "changes are in staging mode\nchanges are in tracking mode"
                )
        if self.untracked_count > 0:
            self.log.info(f"untracked count: {self.untracked_count}")


