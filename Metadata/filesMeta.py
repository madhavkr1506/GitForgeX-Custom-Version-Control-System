class MetaNode:
    def __init__(self, path, size, hash_):
        self.path = path
        self.current = {
            "size": size,
            "hash": hash_,
            "modified": False,
            "tracked": False,
            "staged": False,
            "committed": False,
            "message": None,
            "commit_hash": None,
            "commit_time": None
        }

        self.last = {
            "size": -1,
            "hash": None,
            "tracked": False,
            "staged": False,
            "committed": False,
            "message": None,
            "commit_hash": None,
            "commit_time": None
        }


from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class MetaNodeStatus:
    path:str = field(default="")
    size:int = field(default=0)
    hash:str = field(default="")
    modified:bool = field(default=False)
    tracked:bool = field(default=False)
    staged:bool = field(default=False)
    commited:bool = field(default=False)
    message:str = field(default="")
    commit_hash:str = field(default="")
    commit_time:str = field(default_factory=datetime.now)