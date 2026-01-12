import os
import json
from pathlib import Path
from Metadata import *
from cryptography.hazmat.primitives import hashes

from Logging import *
class AddActions:
    def __init__(self, path : Path = None):
        log = PrintLog()
        self.log = log.log

        self.entries = []

        self.worktreepath = "./.gitforgex/"

        self.list_allfiles(path=path)
        for filepath in self.entries:
            filesize = self.fetch_filesize(filepath=filepath)
            filedata = self.fetch_filedata(filepath=filepath)
            filehash = self.fetch_filehash(contents=filedata)

            duplicate_found = self.handle_duplicate_in_worktree(filepath=filepath, filesize=filesize, filehash=filehash)
            if duplicate_found:
                self.log.info(json.dumps({
                    "response" : f"no change in found in file and filepath: {str(filepath)} and duplicate found: {duplicate_found}",
                    "u_status" : "failed"
                }, indent=4))
                continue
            else:
                self.log.info(json.dumps({
                    "response" : f"change found in file and filepath: {str(filepath)} and duplicate found: {duplicate_found}",
                    "u_status" : "success"
                }, indent=4))

            filenode = self.node_creation(filepath=filepath, filesize=filesize, filehash=filehash)
            self.build_binary_object(filenode=filenode)

    def list_allfiles(self, path : Path) -> list:
        try:
            for entry in path.iterdir():
                if entry.is_dir() and "cache" in str(entry):
                    continue
                if entry.is_dir():
                    self.list_allfiles(path=entry)
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
    
    def fetch_filesize(self, filepath):
        f_size = os.path.getsize(filename=filepath)
        return f_size

    def fetch_filedata(self, filepath):
        filedata = None
        if not filepath:
            return filedata
        
        with open(file=filepath, mode="r") as f:
            filedata = f.read()

        if filedata:
            filedata = filedata.encode("utf-8")
        return filedata
    
    def fetch_filehash(self, contents):
        hash256hex = None
        if not contents:
            return hash256hex
        
        if isinstance(contents, str):
            contents = contents.encode("UTF-8")
        
        hashsha256 = hashes.Hash(algorithm=hashes.SHA256())
        hashsha256.update(contents)
        hashdigest = hashsha256.finalize()
        hash256hex = hashdigest.hex()
        return hash256hex
    
    def node_creation(self, filepath, filesize, filehash) -> MetaNode:
        try:
            if not all(
                [filepath, filesize, filehash]
            ):
                self.log.error(
                    json.dumps(
                        {
                            "response": f"node is not created. missing required fields filepath={filepath} filesize={filesize} filehash={filehash}",
                            "u_status": "failed"
                        }, indent=4
                    )
                )
            
            filenode = MetaNode(path=str(filepath), size=filesize, hash_=filehash)
            return filenode

        except Exception as e:
            self.log.error(json.dumps(
                {
                    "response": f"node is not created: {str(e)}",
                    "u_status": "failed"
                }
            ))
        
    def handle_duplicate_in_worktree(self, filepath = None, filesize = -1, filehash = None):
        duplicate_found = False
        filepathhash = self.fetch_filehash(contents=str(filepath))
        filepath = Path(f"{self.worktreepath}/{filepathhash}/{filehash}")
        if os.path.exists(filepath):
            duplicate_found = True
        return duplicate_found

    def build_binary_object(self, filenode : MetaNode = None):
        try:
            os.makedirs(name=self.worktreepath, exist_ok=True)
            filepath = filenode.path
            filepathhash = self.fetch_filehash(contents=str(filepath))
            filehash = filenode.current.get("hash")
            path = os.path.join(self.worktreepath, filepathhash, f"{filehash}.json")

            payload = None
            with open(file=path, mode="w") as binfile:
                payload = filenode.__dict__
                # payload = json.dumps(payload)
                json.dump(payload, binfile, indent=4)
            binfile.close()
            payload = None
        except Exception as e:
            self.log.error(
                json.dumps(
                    {
                        "response": f"binary file is not created inside worktree: {str(e)}",
                        "u_status": "failed"
                    }, indent=4
                )
            )