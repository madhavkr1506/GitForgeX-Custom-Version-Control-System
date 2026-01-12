import sys
from pathlib import *
from Metadata import *
from Logging import *
from cryptography.hazmat.primitives import hashes
from Metadata import *

class Commit:
    def __init__(self):
        log = PrintLog()
        self.log = log.log

        self.working_node = NodeReferenceState()
        self.working_module = self.working_node.working_module

        self.contents = {}

        self.commit_required = False
        self.hashinputs = []
        self.commit_hash = None
        self.commit_msgs = None

    def run(self):
        steps = [self.check_commit_required, self.get_commit_hash, self.get_commit_message, self.changing_entry_state]
        for step in steps:
            step()

    def check_commit_required(self):
        for filepath in self.working_module.glob("**/*"):
            if filepath.is_dir() or "cache" in str(filepath):
                continue

            self.working_node.reading_node_state(filepath=filepath)     
            self.contents = self.working_node.contents

            current_stage = self.contents.get("current").get("staged")
            current_track = self.contents.get("current").get("tracked")
            current_commit = self.contents.get("current").get("committed") 
            if (current_stage and current_track and not current_commit):
                self.commit_required = True
                print(f"commit required. path = {filepath}")
                filehash = self.contents.get("current").get("hash")
                self.hashinputs.append(filehash)
            else:
                self.log.info(f"commit not required. path = {filepath}")
                # self.commit_required = False
                
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
            print(f"input commit message: ", end="\t", flush=True)
            input = sys.stdin.readline()
            self.commit_msgs = input.strip()

    def changing_entry_state(self):
        try:
            if self.commit_msgs is not None and self.commit_hash is not None:
                for filepath in self.working_module.glob("**/*"):
                    if filepath.is_dir() or "cache" in str(filepath):
                        continue
                    self.working_node.reading_node_state(filepath=filepath)
                    self.contents = self.working_node.contents
                    current_tracked = self.contents.get("current").get("tracked")
                    current_staged = self.contents.get("current").get("staged")
                    if (current_staged and current_tracked):
                        self.contents["current"]["message"] = self.commit_msgs
                        self.contents["current"]["commit_hash"] = self.commit_hash
                        self.working_node.updating_node_state(filepath=filepath, payload=self.contents)
                        self.log.info(f"commit has created and commit message are added to node")
        except Exception as e:
            self.log.error(f"change in node is not updated: {str(e)}")