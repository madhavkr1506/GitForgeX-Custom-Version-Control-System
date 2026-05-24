from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True, slots=True)
class FileNode:
    path:str
    absolute_path:str
    content_hash:str
    path_hash:str
    size:int
    created_at:datetime
    modified_at:datetime
    last_seen:datetime
    inode:Optional[int]=None
    permissions:Optional[str]=None
    extension:str=""
    encoding:str="utf-8"
    is_binary:bool=False
    is_symlink:bool=False
    exists:bool=True

@dataclass(frozen=True, slots=True)
class TreeNode:
    path:str
    tree_hash:str
    files:tuple[str, ...]=()
    directories:tuple[str, ...]=()

@dataclass(slots=True)
class Snapshot:
    snapshot_hash:str=""
    created_at:datetime=field(
        default_factory=lambda:datetime.now(timezone.utc)
    )
    files:dict[str, FileNode]=field(default_factory=dict)
    trees:dict[str, TreeNode]=field(default_factory=dict)
    @property
    def total_files(self):
        return len(self.files)
    
    @property
    def total_size(self):
        return sum(node.size for node in self.files.values())

@dataclass(slots=True)
class StageArea:
    staged_files:dict[str, FileNode]=field(default_factory=dict)
    staged_at:datetime=field(
        default_factory=lambda:datetime.now(timezone.utc)
    )

@dataclass(slots=True)
class DiffResult:
    added:set[str]=field(default_factory=set)
    modified:set[str]=field(default_factory=set)
    deleted:set[str]=field(default_factory=set)
    unchanged:set[str]=field(default_factory=set)
    renamed:dict[str, str]=field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class Commit:
    commit_hash:str
    parent_hash:Optional[str]
    snapshot_hash:str
    author:str
    message:str
    created_at:datetime=field(
        default_factory=lambda:datetime.now(timezone.utc)
    )
    branch:str="main"
    tags:tuple[str, ...]=()

@dataclass(slots=True)
class Branch:
    name:str
    head_commit:Optional[str]=None
    created_at:datetime=field(
        default_factory=lambda:datetime.now(timezone.utc)
    )

@dataclass(slots=True)
class ObjectDatabase:
    blob_objects:dict[str, bytes]=field(
        default_factory=dict
    )
    tree_objects:dict[str, bytes]=field(
        default_factory=dict
    )
    commit_objects:dict[str, Commit]=field(
        default_factory=dict
    )

@dataclass(slots=True)
class RepositoryConfig:
    repository_format_version:str="1"
    default_branch:str="main"
    ignore_patterns:set[str]=field(
        default_factory=set
    )
    autocrlf:bool=False

@dataclass(slots=True)
class RepositoryState:
    repository_root:str
    repository_id:str
    created_at:datetime=field(
        default_factory=lambda:datetime.now(timezone.utc)
    )
    current_snapshot:Snapshot=field(
        default_factory=Snapshot
    )
    previous_snapshot:Snapshot=field(
        default_factory=Snapshot
    )
    stage_area:StageArea=field(default_factory=StageArea)
    commits:dict[str, Commit]=field(default_factory=dict)
    branches:dict[str, Branch]=field(default_factory=dict)
    current_branch:str="main"
    head_commit:Optional[str]=None
    object_database:ObjectDatabase=field(
        default_factory=ObjectDatabase
    )
    initialized:bool=False
    detached_head:bool=False
    dirty:bool=False

