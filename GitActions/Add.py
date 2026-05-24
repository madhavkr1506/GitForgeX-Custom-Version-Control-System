import os
import json
from pathlib import Path
from Metadata import *
from dataclasses import asdict
from cryptography.hazmat.primitives import hashes

from Logging import *
class AddActions:
    def __init__(self, path : Path = None):
        log = PrintLog()
        self.log = log.log
        self.entries = []

        self.node = NodeReferenceState()

        self.list_allfiles(path=path)
        for filepath in self.entries:
            filesize = self.fetch_filesize(filepath=filepath)
            filedata = self.fetch_filedata(filepath=filepath)
            filehash = self.fetch_filehash(contents=filedata)

            duplicate_found = self.handle_duplicate_in_worktree(filepath=filepath, filesize=filesize, filehash=filehash)
            if duplicate_found:
                self.log.info(f"no change in found in file and filepath: {str(filepath)} and duplicate found: {duplicate_found}")
                continue
            else:
                self.log.info(f"change found in file and filepath: {str(filepath)} and duplicate found: {duplicate_found}")

            self.node_creation(filepath=str(filepath), filesize=filesize, filehash=filehash)
            self.build_binary_object()

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
                self.log.warning(f"entries are empty. no files found at path={path}")
                return []
            return self.entries
        except Exception as e:
            self.log.error(f"list all files failed: {str(e)}")
    
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
            if not all([filepath, filesize, filehash]):
                self.log.error(f"node is not created. missing required fields filepath={filepath} filesize={filesize} filehash={filehash}")
                return
            # filenode = MetaNode(path=str(filepath), size=filesize, hash_=filehash)
            # return filenode
            self.node.curr.path = filepath
            self.node.curr.size = filesize
            self.node.curr.hash = filehash

        except Exception as e:
            self.log.error(f"node creation failed: {str(e)}")
        
    def handle_duplicate_in_worktree(self, filepath = None, filesize = -1, filehash = None):
        try:
            duplicate_found = False
            filepathhash = self.fetch_filehash(contents=str(filepath))
            filepath = Path(f"{self.node.working_module}/{filepathhash}/{filehash}.json")
            if os.path.exists(path=filepath):
                duplicate_found = True
            return duplicate_found
        except Exception as e:
            self.log.error(f"handle duplicate in worktree failed: {str(e)}")

    def build_binary_object(self, filenode : MetaNode = None):
        try:
            # filepath = filenode.path
            filepath = self.node.curr.path
            filepathhash = self.fetch_filehash(contents=str(filepath))
            dirpath = os.path.join(self.node.working_module, filepathhash)
            os.makedirs(name=dirpath, exist_ok=True)
            # filehash = filenode.current.get("hash")
            filehash = self.node.curr.hash
            filepath = os.path.join(self.node.working_module, filepathhash, f"{filehash}.json")
            payload = asdict(self.node.curr)
            with open(file=filepath, mode="w") as jsonfile:
                json.dump(payload, jsonfile, indent=4, default=str)
            jsonfile.close()
        except Exception as e:
            self.log.error(f"binary object is not created: {str(e)}")