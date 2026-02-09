import os, json
import time
from typing import List
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import mapped_column, Mapped, declarative_base
from clickhouse_sqlalchemy import types

from sqlalchemy import Select

import logging

class MasterNode:
    def __init__(self, git_commit_msg : str = None, git_files_hash : List[str] = [], git_commithash : str = None):
        self.git_commit_msg = git_commit_msg
        self.git_files_hash = git_files_hash
        self.git_commithash = git_commithash

class DBConnection:
    def __init__(self):

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        self.log = logging.getLogger(__name__)

        self.db_engine = None
        self.db_session = None
        self.prepare_database_variables()

    def prepare_database_variables(self):
        self.database_user = str(os.getenv("USERNAME")).lower()
        self.database_name = str(os.getenv("DATABASE")).lower()
        self.db_hostport = str(os.getenv("PORT")).lower()
        self.db_hostipaddr = str(os.getenv("HOST")).lower()
        self.db_password = str(os.getenv("PASSWORD")).lower()

    def create_dbengine(self):
        try:
            connection_url = f"clickhouse+native://{self.database_user}:{self.db_password}@{self.db_hostipaddr}:{self.db_hostport}/{self.database_name}"
            self.log.info(f"connection url: {connection_url}")
            self.db_engine = create_engine(
                url=connection_url,
                echo=False
            )
            return 0
        except Exception as e:
            self.log.error(f"problem.create_dbengine: {str(e)}")
            return 1
        
    def create_dbsession(self):
        try:
            if self.db_engine is not None:
                self.log.info(f"database engine is already created: {self.db_engine}")
            if self.db_engine is None:
                code = self.create_dbengine()
                if code == 0:
                    self.log.info(f"database engine is created: {self.db_engine}")
            session = sessionmaker(
                bind=self.db_engine,
                expire_on_commit=False,
                autoflush=True
            )
            self.db_session = session()
            return 0
        except Exception as e:
            self.log.error(f"problem.create_dbsession: {str(e)}")
            return 1

    def test_session_reliablity(self):
        try:
            if self.db_session is not None:
                self.log.info(f"database session is already created: {self.db_session}")
            if self.db_session is None:
                code = self.create_dbsession()
                if code == 0:
                    self.log.info(f"database session is created: {self.db_session}")

            random_query = text("select version();")
            response = self.db_session.execute(random_query)
            row_record = response.fetchone()
            self.log.info(f"fetched row record: {row_record}")
            self.db_session.commit()
            if row_record is not None:
                return 0
            return 1
        except Exception as e:
            if self.db_session is not None:
                self.db_session.rollback()
                self.db_session.close()
            if self.db_engine is not None:
                self.db_engine.dispose()
            self.log.error(f"problem.test_session_reliablity: {str(e)}")
        finally:
            if self.db_session is not None:
                self.db_session.close()
            if self.db_engine is not None:
                self.db_engine.dispose()

BASE = declarative_base()
class ModelClass(BASE):
    __tablename__ = "gitmaster"
    __table_args__ = {"schema" : "gitforgex"}
    gitid : Mapped[str] = mapped_column(
            types.UUID, primary_key=True,
            server_default=text("generateUUIDv4()")
        )
    git_commithash : Mapped[str] = mapped_column(types.String)
    git_commit_msg : Mapped[str] = mapped_column(types.String)
    git_files_hash : Mapped[list[str]] = mapped_column(types.Array(types.String))
    gitdatetime_event : Mapped[datetime] = mapped_column(
            types.DateTime,
            server_default=text("now()")
        )

class PrepareQuery:
    def __init__(self):
        self.select_query = None
        self.insert_query = None

    def prepare_insert(self):
        query = text("""
            INSERT INTO gitforgex.gitmaster (git_commithash, git_commit_msg, git_files_hash) values (:git_commithash, :git_commit_msg, :git_files_hash)
        """)
        self.insert_query = query

    def prepare_select(self, commithash):
        query = Select(
            ModelClass.git_files_hash
        ).where(ModelClass.git_commithash == commithash)
        self.select_query = query


class BotHandler:
    def __init__(self):

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        self.log = logging.getLogger(__name__)

        self.master_node = None
        self.prepare_query = PrepareQuery()
        self.dbconnection = DBConnection()
        code = self.dbconnection.create_dbsession()
        self.log.info(f"creating database session object")
        self.session = None
        if code == 0:
            self.session = self.dbconnection.db_session
            self.log.info(f"database session is created: {self.session}")

    def prepare_masternode(self, commithash, fileshash, commitmsg):
        try:
            self.master_node = MasterNode(
                git_commit_msg=commitmsg,
                git_files_hash=fileshash,
                git_commithash=commithash
            )
            if not all([
                self.master_node.__dict__
            ]):
                return 1
            return 0

        except Exception as e:
            self.log.error(f"problem.prepare_masternode: {str(e)}")
            return 1

    def insert_indb(self, commithash, fileshash, commitmsg):
        try:
            if self.master_node is None:
                code = self.prepare_masternode(commithash, fileshash, commitmsg)
                if code == 1:
                    self.log.warning(f"master node not prepared: {self.master_node.__dict__}")
                    return
            self.log.info(f"master node is prepared: {self.master_node.__dict__}")
            payload = {
                "git_commithash": self.master_node.git_commithash,
                "git_commit_msg": self.master_node.git_commit_msg,
                "git_files_hash": [self.master_node.git_files_hash],
            }
            self.prepare_query.prepare_insert()
            query = self.prepare_query.insert_query
            self.log.info(f"insert query: {query}\tdatabase session: {self.session}")
            if self.session is not None:
                response = self.session.execute(query, payload)
                self.session.commit()
                self.log.info(f"response received after executing query: {response}")
                if response is None:
                    self.log.warning(f"insert operation not completed. response received: {response}")
        except Exception as e:
            if self.session:
                self.session.rollback()
                self.session.close()
            self.log.error(f"problem.insert_indb: {str(e)}")

    def select_fromdb(self, commithash):
        try:
            self.prepare_query.prepare_select(commithash=commithash)
            query = self.prepare_query.select_query
            self.log.info(f"select query: {query}\tdatabase session: {self.session}")
            if self.session:
                response = self.session.execute(query)
                self.log.info(f"response received after executing query: {response}")
                rows = response.fetchall()
                if rows:
                    for row in rows:
                        self.log.info(f"fetched row record: {row}")
                else:
                    self.log.warning(f"select query is not completed. rows are not found: {rows}")
                return rows
            else:
                self.log.warning(f"session is not created")
        except Exception as e:
            if self.session:
                self.session.close()
            self.log.error(f"problem.select_fromdb: {str(e)}")
            