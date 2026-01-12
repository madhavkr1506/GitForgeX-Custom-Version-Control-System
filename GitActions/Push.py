import json
import subprocess
from Logging import *
from Handshake import *
from pathlib import Path
from datetime import datetime

class Push:
    def __init__(self):
        self.log = PrintLog()
        self.log = self.log.log

        self.contents = {}

        self.worktreepath = Path("./.gitforgex/")

        self.commit_hash = None
        self.commit_msgs = None

        self.post_command = None

        self.push_status = False

    def run(self):
        flag = self.validate_identity_with_handshake()
        flag = True
        if flag:
            steps = [self.find_commit_hash_and_commit_message, self.push_event_util, self.changing_entry_state]
            for step in steps:
                step()

    def validate_identity_with_handshake(self):
        try:
            self.handshake = KeyGeneration()
            
            funcs = [self.handshake.run, self.handshake.do_handshake]
            for fun in funcs:
                fun()
            
            return True

        except Exception as e:
            self.log.error(
                json.dumps({
                    "response": f"failed to validate with handshake activity: {str(e)}",
                    "u_status": "failed"
                }, indent=4)
            )
            return False
    def reading_entry_state(self, filepath):
        try:
            contents = None,
            with open(file=filepath, mode="r") as jsonfile:
                contents = json.load(jsonfile)
            jsonfile.close()
            self.contents = contents

        except Exception as e:
            self.log.error(
                "binary reading failed"
            )

    def updating_entry_state(self, filepath, payload):     
        with open(file=filepath, mode="w") as jsonfile:
            json.dump(payload, jsonfile, indent=4)
        jsonfile.close()

        self.log.info(f"push state is updated: {filepath}")

    def find_commit_hash_and_commit_message(self):
        try:
            commit_hash_list = []
            commit_msgs_list = []
            for filepath in self.worktreepath.glob("**/*"):
                if filepath.is_dir() or "cache" in str(filepath):
                    continue
                self.reading_entry_state(filepath=filepath)
                current_tracked = self.contents.get("current").get("tracked")
                current_staged = self.contents.get("current").get("staged")
                current_committed = self.contents.get("current").get("committed")
                current_modified = self.contents.get("current").get("modified")

                if (current_tracked and current_staged and not current_committed and current_modified):
                    current_commit_hash = self.contents.get("current").get("commit_hash")
                    current_commit_msgs = self.contents.get("current").get("message")
                    commit_hash_list.append(current_commit_hash)
                    commit_msgs_list.append(current_commit_msgs)

            if len(set(current_commit_hash)) == 1 and len(set(current_commit_msgs)) == 1:
                self.commit_hash = current_commit_hash[0]
                self.commit_msgs = current_commit_msgs[0]
             
        except Exception as e:
            self.log.error(
                json.dumps(
                    {
                        "response": f"failed to list files that required push: {str(e)}",
                        "u_status": "failed"
                    }, indent=4
                )
            )
        
    def get_post_cmd(self, filepath, filehash):
        try:            
            cmd = [
                "curl",
                "-X", "POST",
                "http://localhost:8000/post",
                "-F", f"upload=@{filepath}",
                "-F", f"commit_hash={self.commit_hash}",
                "-F", f"filehash={filehash}",
                "-F", f"commitmsg={self.commit_msgs}"
            ]
            self.post_command = cmd
            print(f"post command prepared: {self.post_command}")
        except Exception as e:
            self.log.error(
                json.dumps(
                    {
                        "response": f"failed to create post command: {str(e)}",
                        "u_status": "failed"
                    }, indent=4
                )
            )
        
    def get_push_event(self):
        try:
            response = subprocess.run(
                self.post_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
            )
            if response.returncode == 0:
                print(f"Standard output: {response.stdout}")
                return
            print(f"Standard error: {response.stderr}")
            self.push_status = False
            return
        except Exception as e:
            self.log.error(
                json.dumps(
                    {
                        "response": f"failed to push file data to server: {str(e)}",
                        "u_status": "failed"
                    }, indent=4
                )
            )
        
    def push_event_util(self):
        try:
            for filepath in self.worktreepath.glob("**/*"):
                if filepath.is_dir() or "cache" in str(filepath):
                    continue
                self.reading_entry_state(filepath=filepath)
                current_staged = self.contents.get("current").get("staged")
                current_committed = self.contents.get("current").get("committed")
                current_tracked = self.contents.get("current").get("tracked")

                if (current_staged and current_tracked and not current_committed):
                    filepath_ = self.contents.get("path")
                    filehash_ = self.contents.get("current").get("hash")
                    if filepath_ is None:
                        continue
                    self.get_post_cmd(filepath=filepath_, filehash=filehash_)
                    self.get_push_event()
                    self.push_status = True
        except Exception as e:
            self.log.error(
                json.dumps(
                    {
                        "response": f"failed to make push event: {str(e)}",
                        "u_status": "failed"
                    }, indent=4
                )
            )
        
    def changing_entry_state(self):
        if not self.push_status:
            self.log.info("push event is not set to true")
            return

        for filepath in self.worktreepath.glob("**/*"):
            if filepath.is_dir() or "cache" in str(filepath):
                continue
        
            self.reading_entry_state(filepath=filepath)
            current_staged = self.contents.get("current").get("staged")
            current_tracked = self.contents.get("current").get("tracked")
            if (current_tracked and current_staged):
                self.contents["current"]["committed"] = True
                self.contents["current"]["commit_time"] = str(datetime.now())
                self.contents["last"]["size"] = self.contents["current"]["size"]
                self.contents["last"]["tracked"] = self.contents["current"]["tracked"]
                self.contents["last"]["staged"] = self.contents["current"]["staged"]
                self.contents["last"]["committed"] = self.contents["current"]["committed"]
                self.contents["last"]["message"] = self.contents["current"]["message"]
                self.contents["last"]["commit_hash"] = self.contents["current"]["commit_hash"]
                self.contents["last"]["commit_time"] = self.contents["current"]["commit_time"]

                self.updating_entry_state(filepath=filepath, payload=self.contents)
                self.log.info("push state is updated")