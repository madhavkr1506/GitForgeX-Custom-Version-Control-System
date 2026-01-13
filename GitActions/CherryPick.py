import sys
import subprocess

from Logging import *
from Metadata import *

class CherryPickCommit:
    def __init__(self):
        log = PrintLog()
        self.log = log.log

        self.working_node = NodeReferenceState()
        self.working_module = self.working_node.working_module

        self.cherry_pick_commit = None
        self.contents = {}
        self.commits_repo = {}

        self.user_commit_hash_preference = None
        self.user_selected_preference = False

        self.cherry_pick_call = []

    def run(self):
        steps = [self.store_cherry_pick_commit, self.get_cmd_for_cherrypick, self.execute_cmd_for_cherry_pick]
        for step in steps:
            step()

    def store_cherry_pick_commit(self):
        try:
            for filepath in self.working_module.glob("**/*"):
                if filepath.is_dir() or "cache" in str(filepath):
                    continue
                self.working_node.reading_node_state(filepath=filepath)
                self.contents = self.working_node.contents
                committed = self.contents.get("last", {}).get("committed")
                commit_hash = self.contents.get("last", {}).get("commit_hash")
                filehash = self.contents.get("last", {}).get("hash")
                if committed and commit_hash is not None and filehash is not None:
                    self.commits_repo[filehash] = commit_hash
            
            self.log.info(f"commits repository listed below: ")
            for filehash, commit_hash in self.commits_repo.items():
                print(f"filehash: {filehash} => commit hash: {commit_hash}")

            if len(self.commits_repo) == 0:
                self.log.warning(f"no commits found to restore")
                return
            print("input commit hash: ", end="\t", flush=True)
            self.user_commit_hash_preference = sys.stdin.readline().strip()
            if len(self.user_commit_hash_preference) > 0:
                self.user_selected_preference = True

        except Exception as e:
            self.user_selected_preference = True
            self.log.error(f"failed method store cherry pick commit: {str(e)}")

    def get_cmd_for_cherrypick(self, filehash=None, commit_hash=None, outputpath = None):
        try:
            cmd = [
                "curl",
                "-X",
                "GET",
                f"http://localhost:8000/get",
                "-F", f"filehash={filehash}",
                "-F", f"commit_hash={self.user_commit_hash_preference}",
                "-o", f"{outputpath}"
            ]
            self.log.info(f"command prepared: {cmd}")
            self.cherry_pick_call = cmd
        except Exception as e:
            self.log.error(f"failed method get command for cherry pick: {str(e)}")

    def execute_cmd_for_cherry_pick(self):
        try:
            if len(self.cherry_pick_call) == 0:
                self.log.warning(f"cherry pick call is not initialized: {self.cherry_pick_call}")
            response = subprocess.run(args=self.cherry_pick_call, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if response.returncode == 0:
                self.log.info(f"process has completed its execution")
                self.log.info(f"standard response: {response.stdout}")
            else:
                self.log.warning(f"standard error: {response.stderr}")

        except Exception as e:
            self.log.error(f"failed method execute command for cherry pick: {str(e)}")