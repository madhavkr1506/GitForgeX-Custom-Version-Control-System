import sys
import subprocess
from Logging import *
from Metadata import *

class GitReset:
    def __init__(self):
        log = PrintLog()
        self.log = log.log

        self.working_node = NodeReferenceState()
        self.working_module = self.working_node.working_module

        self.contents = None

        self.commits_repo = {}

        self.show_commits = False
        self.user_preference_filehash = None
        self.user_preference_commit_hash = None
        self.user_selected_preference = False

    def run(self):
        steps = [self.list_allcommits, self.choose_commit_to_reset, self.get_changes_to_local]
        for step in steps:
            step()

    def list_allcommits(self):
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

            if len(self.commits_repo) > 0:
                self.log.info(f"commits list: {self.commits_repo}")
                self.show_commits = True
            else:
                self.log.info(f"no commits found: {self.commits_repo}")
                self.show_commits = False

        except Exception as e:
            self.show_commits = False
            self.log.error(f"all commits are not not listed: {str(e)}")

    def choose_commit_to_reset(self):
        try:
            if not self.show_commits:
                return
            self.log.info(
                json.dumps(self.commits_repo, indent=4)
            )
            self.log.info(f"choose filehash and commit hash you want to reset: ")
            user_preference_filehash, user_preference_commit_hash = sys.stdin.readline().split(" ")
            self.user_preference_filehash = user_preference_filehash
            self.user_preference_commit_hash = user_preference_commit_hash
            if self.user_preference_filehash is not None and self.user_preference_commit_hash is not None:
                self.log.info(f"user preference is stored: filehash={self.user_preference_filehash} and commit hash={self.user_preference_commit_hash}")
                self.user_selected_preference = True

        except Exception as e:
            self.log.error(f"failed function choose commit to reset: {str(e)}")

    def get_changes_to_local(self, output_filepath = None):
        try:
            cmd = None
            def prepare_cmd():
                cmd_ = [
                    "curl", 
                    "-X", "GET",
                    f"http://localhost:8000/get",
                    "-F", f"filehash={self.user_preference_filehash}",
                    "-F", f"commit_hash={self.user_preference_commit_hash}",
                    "-o", f"{output_filepath}"
                ]
                return cmd_
            
            if self.user_selected_preference:
                response = None

                cmd = prepare_cmd()
                self.log.info(f"command prepare: {cmd}")

                response = subprocess.run(args=cmd, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if response.returncode == 0:
                    self.log.info(f"process has completed its execution: {response.args}")
                    self.log.info(f"standard output: {response.stdout}")
                else:
                    self.log.warning(f"process has failed to complete its execution: {response.returncode}")
                    self.log.warning(f"standard error: {response.stderr}")

        except Exception as e:
            self.log.error(f"failed function get changes to local: {str(e)}")


