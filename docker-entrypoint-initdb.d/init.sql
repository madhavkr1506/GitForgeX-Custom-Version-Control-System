create database if not exists gitforgex;

use gitforgex;

create table if not exists  gitmaster(
    gitid UUID default generateUUIDv4(), git_commithash String, git_commit_msg String, git_files_hash Array(String), gitdatetime_event DateTime default now()
)engine = MergeTree() order by (gitid);