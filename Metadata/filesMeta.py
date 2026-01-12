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
