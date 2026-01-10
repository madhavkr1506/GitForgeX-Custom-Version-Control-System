import os, json
import pandas as pd
from pathlib import Path
from Metadata.filesMeta import Master
from cryptography.hazmat.primitives import hashes

from Logging import *

class Action:
    def __init__(self):
        self.log = PrintLog()
        self.log = self.log.log

        self.master = Master()
    def add(self, track_dir_path):
        Action.AddActions(self.log, self.master, track_dir_path)

    class AddActions:
        def __init__(self, log : PrintLog,  master : Master, path : Path):
            self.master = master

            self.log = log
            self.entries = []

            self.list_all_entry(path=path)
            for filepath in self.entries:
                filesize = self.get_entry_size(filepath=filepath)
                f_data = self.get_entry_data(file=filepath)

                filehash = self.get_entry_digest(f_data=f_data)
                filehashhex = self.get_entry_hex(filehash=filehash)

                duplicate_entry = self.handle_duplicate_in_master(filepath=filepath, filesize=filesize, filehashhex=filehashhex)
                if duplicate_entry:
                    self.log.info(json.dumps({
                        "response" : f"no change in found in file\nfilepath: {str(filepath)}\tduplicate entry: {duplicate_entry}",
                        "u_status" : "failed"
                    }, indent=4))
                    continue
                entry_node = self.node_creation(filepath=filepath, filesize=filesize, filehash=filehashhex)
                self.make_entry_in_master(meta_node=entry_node)

        def list_all_entry(self, path : Path) -> list:
            try:
                for entry in path.iterdir():
                    if entry.is_dir() and "cache" in str(entry):
                        continue
                    if entry.is_dir():
                        self.list_all_entry(path=entry)
                    if entry.is_file():
                        self.entries.append(entry)

                if self.entries is [] and len(self.entries) == 0:
                    self.log.info({
                        "response" : f"files not found at {path}",
                        "u_status" : "failed"
                    })
                    return []
                return self.entries
            except Exception as e:
                self.log.error(json.dumps(
                    {
                        "response": f"failed list all files: {str(e)}",
                        "u_status": "failed"
                    }
                ))
        
        def get_entry_size(self, filepath):
            if len(self.entries) == 0:
                return
            f_size = os.path.getsize(filename=filepath)
            return f_size

        def get_entry_data(self, file):
            f_data = None
            if not file:
                return f_data
            
            with open(file=file, mode="r") as f:
                f_data = f.read()

            if f_data:
                f_data = f_data.encode("utf-8")
            return f_data
        
        def get_entry_digest(self, f_data):
            filehash = None
            if not f_data:
                return filehash
            
            hash = hashes.Hash(algorithm=hashes.SHA256())
            hash.update(f_data)
            filehash = hash.finalize()
            return filehash
        
        def get_entry_hex(self, filehash : bytes) -> str:
            if len(filehash) == 0:
                return ""
            
            return filehash.hex()
        
        def node_creation(self, filepath, filesize, filehash) -> Master.MetaNode:
            try:
                if not all(
                    [filepath, filesize, filehash]
                ):
                    self.log.error(f"meta node creation failed")
                
                meta_node = self.master.MetaNode(filepath=str(filepath), filesize=filesize, filehash=filehash)
                print("metanode", meta_node)
                return meta_node

            except Exception as e:
                self.log.error(json.dumps(
                    {
                        "response": f"failed at node creation: {str(e)}",
                        "u_status": "failed"
                    }
                ))
            
        def handle_duplicate_in_master(self, filepath, filesize, filehashhex):
            duplicate_found = False
            self.read_csv = pd.read_csv(self.master.filepath)
            row_count = self.read_csv.loc[(self.read_csv["FILE.PATH"] == str(filepath)) & (self.read_csv["FILE.SIZE"] == filesize) & (self.read_csv["FILE.HASH"] == filehashhex), "FILE.PATH"].count()
            if row_count > 0:
                duplicate_found = True
            return duplicate_found

        def make_entry_in_master(self, meta_node : Master.MetaNode):
            if meta_node is None:
                self.log.waring("meta node is not prepared yet!")
                return

            columns = [key.upper() for key, value in meta_node.__dict__.items()]
            new_row = {
                key.upper() : value for key, value in meta_node.__dict__.items()
            }
            row = [new_row]
            df = pd.DataFrame(row)
            df.to_csv(self.master.filepath, mode="a", header=False, index=False)