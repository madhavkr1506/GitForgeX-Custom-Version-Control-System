import pandas as pd
import subprocess, json
from datetime import datetime
from Metadata.filesMeta import Master
from Handshake.key import KeyGeneration

from Logging import *

class Push:
    def __init__(self):
        self.log = PrintLog()
        self.log = self.log.log

        self.master = Master()
        self.filepath = self.master.filepath

        self.read_csv = None

        self.filepaths = None
        self.commit_hash = None
        self.commit_message = None

        self.get_cmd = None
        self.post_cmd = None

        self.push_event_status = False
        self.prepare_post_cmd_status = True
        self.push_event_aftermath_status = False

    def run(self):
        self.validate_identity_with_handshake()

        steps = [self.list_entry_to_push, self.push_event_util, self.push_event_aftermath, self.reset_status]
        for step in steps:
            step()

    def validate_identity_with_handshake(self):
        try:
            self.handshake = KeyGeneration()
            
            funcs = [self.handshake.run, self.handshake.do_handshake]
            for fun in funcs:
                fun()

        except Exception as e:
            self.log.error(
                json.dumps({
                    "response": f"failed to validate with handshake activity: {str(e)}",
                    "u_status": "failed"
                }, indent=4)
            )

    def list_entry_to_push(self):
        try:
            self.read_csv = pd.read_csv(self.filepath)

            self.commit_hash = self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == False) & (self.read_csv["FILE.MODIFIED"] == True), "FILE.COMMIT.HASH"].unique()
            self.commit_message = self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == False) & (self.read_csv["FILE.MODIFIED"] == True), "FILE.COMMIT.MESSAGE"].unique()
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
                "-F", f"commit_hash={self.commit_hash[0]}",
                "-F", f"filehash={filehash}",
                "-F", f"commitmsg={self.commit_message[0]}"
            ]
            print(f"post command prepared: {cmd}")
            self.post_cmd = cmd
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
                self.post_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
            )
            if response.returncode == 0:
                print(f"Standard output: {response.stdout}")
                return
            print(f"Standard error: {response.stderr}")
            self.push_event_status = False
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
            for idx, row in self.read_csv.iterrows():
                entry, filehashhex = (row.get("FILE.PATH"), row.get("FILE.HASH")) if row.get("FILE.TRACK.STATUS") == True and row.get("FILE.STAGE.STATUS") == True and row.get("FILE.COMMIT.STATUS") == False else (None, None)
                print(f"filepath: {entry}\nfilehash: {filehashhex}")

                if entry is None:
                    continue
                
                self.get_post_cmd(filepath=entry, filehash=filehashhex)
                self.get_push_event()
                self.push_event_status = True
        except Exception as e:
            self.log.error(
                json.dumps(
                    {
                        "response": f"failed to make push event: {str(e)}",
                        "u_status": "failed"
                    }, indent=4
                )
            )
        
    def push_event_aftermath(self):
        if not self.push_event_status:
            self.log.info(
                json.dumps(
                    {
                        "response": f"pust event status is not set to true",
                        "u_status": "failed"
                    }, indent=4
                )
            )
            return
        try:
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == False), "FILE.COMMIT.STATUS"] = True
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == True), "FILE.COMMIT.DATETIME"] = str(datetime.now())

            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == True), "FILE.LAST.TRACK.STATUS"] = True
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == True), "FILE.LAST.STAGE.STATUS"] = True
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == True), "FILE.LAST.COMMIT.STATUS"] = True

            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == True), "FILE.LAST.COMMIT.MESSAGE"] = self.commit_message[0]
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == True), "FILE.LAST.COMMIT.HASH"] = self.commit_hash[0]
            
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == True), "FILE.LAST.COMMIT.DATETIME"] = str(datetime.now())

            self.read_csv.to_csv(self.filepath, index=False)
            self.push_event_aftermath_status = True
        except Exception as e:
            self.push_event_aftermath_status = False

    def reset_status(self):
        if not self.push_event_aftermath_status:
            json.dumps(
                {
                    "response": f"push event aftermath status is not set to true",
                    "u_status": "failed"
                }, indent=4
            )
            return
        try:
        
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == True), "FILE.COMMIT.DATETIME"] = None
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == True), "FILE.COMMIT.STATUS"] = False
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == True) & (self.read_csv["FILE.COMMIT.STATUS"] == False), "FILE.STAGE.STATUS"] = False
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == True) & (self.read_csv["FILE.STAGE.STATUS"] == False) & (self.read_csv["FILE.COMMIT.STATUS"] == False), "FILE.TRACK.STATUS"] = False
            self.read_csv.loc[(self.read_csv["FILE.TRACK.STATUS"] == False) & (self.read_csv["FILE.STAGE.STATUS"] == False) & (self.read_csv["FILE.COMMIT.STATUS"] == False), "FILE.MODIFIED"] = False

            self.read_csv.to_csv(self.filepath, index=False)
            self.push_event_aftermath = False
        except Exception as e:
            self.push_event_aftermath_status = True