
from pathlib import *
from Logging import *
from Metadata import *

class Staging:
    def __init__(self):
        self.log = PrintLog()
        self.log = self.log.log

        self.working_node = NodeReferenceState()
        self.working_module = self.working_node.working_module

        self.contents = {}

        self.untracked_count = 0
    def run(self):
        steps = [self.staged_changes]
        for step in steps:
            step()

    def staged_changes(self, filepath = None) -> bool:
        for filepath in self.working_module.glob("**/*"):
            if filepath.is_dir():
                continue
            self.working_node.reading_node_state(filepath=filepath)
            self.contents = self.working_node.contents  

            current_tracked = self.contents.get("current").get("tracked")
            last_tracked = self.contents.get("last").get("tracked")
            last_committed = self.contents.get("last").get("committed")

            if (not current_tracked) and (not last_committed):
                if (self.contents["current"]["staged"] and self.contents["current"]["modified"] and self.contents["current"]["tracked"]):
                    self.log.info(f"changes are already in staging mode")
                    continue
                self.contents["current"]["staged"] = True
                self.contents["current"]["modified"] = True
                self.contents["current"]["tracked"] = True
                self.working_node.updating_node_state(filepath=filepath, payload=self.contents)
                self.untracked_count += 1
                self.log.info("1.   changes are in staging mode\n2.   current entry is modified\n3.   current entry is tracked")
            elif (not current_tracked) and (last_committed):
                self.log.info(f"no changes are in staging mode. filepath={filepath}")
        if self.untracked_count > 0:
            self.log.info(f"untracked count: {self.untracked_count}")