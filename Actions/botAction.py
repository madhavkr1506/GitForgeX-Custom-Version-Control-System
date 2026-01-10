import os, json
import time
from typing import List
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import mapped_column, Mapped, declarative_base
from clickhouse_sqlalchemy import types

from sqlalchemy import Select

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


class MasterNode:
    def __init__(self, git_commit_msg : str = None, git_files_hash : List[str] = [], git_commithash : str = None):
        self.git_commit_msg = git_commit_msg
        self.git_files_hash = git_files_hash
        self.git_commithash = git_commithash

class DBConnection:
    def __init__(self):
        self.db_engine = None
        self.db_session = None
        self.prepare_database_variables()

    def prepare_database_variables(self):
        self.database_user = "robot"
        self.database_name = "gitforgex"
        self.db_hostport = "9000"
        self.db_hostipaddr = "10.0.0.21"
        self.db_password = "robot123"

    def create_dbengine(self):
        try:
            connection_url = f"clickhouse+native://{self.database_user}:{self.db_password}@{self.db_hostipaddr}:{self.db_hostport}/{self.database_name}"
            print(
                json.dumps(
                    {
                        "response": f"connection url: {connection_url}"
                    }
                ), flush=True
            )

            self.db_engine = create_engine(
                url=connection_url,
                echo=False
            )
            return {
                "response": f"database engine created",
                "b_status": f"success" 
            }

        except Exception as e:
            print(json.dumps({
                "response": f"database engine is not created: {str(e)}",
                "b_status": f"failed" 
            }, indent=4), flush=True)
        
    def create_dbsession(self):
        try:
            if self.db_engine is None:
                response = self.create_dbengine()
                print(
                    json.dumps(
                        {
                            "response": f"response: {response}"
                        }
                    ), flush=True
                )
            if self.db_engine is not None:
                print(json.dumps({
                    "response": "database engine is already created",
                    "b_status": "success"
                }), flush=True)
            session = sessionmaker(
                bind=self.db_engine,
                expire_on_commit=False,
                autoflush=True
            )
            self.db_session = session()
            return {
                "response": f"database session is created",
                "b_status": "success"
            }
        except Exception as e:
            print(json.dumps({
                "response": f"database session is not created: {str(e)}",
                "b_status": "failed"
            }, indent=4), flush=True)

    def test_session_reliablity(self):
        try:
            if self.db_session is None:
                response = self.create_dbsession()
                print(
                    json.dumps(
                        {
                            "response": f"response: {response}"
                        }
                    ), flush=True
                )

            if self.db_session is not None:
                print(json.dumps({
                    "response": "database session is already initialized",
                    "b_status": "success"
                }, indent=4), flush=True)
            
            test_query = text("select version();")
            time.sleep(10)
            response = self.db_session.execute(test_query)
            row_record = response.fetchone()
            print(
                    json.dumps(
                        {
                            "response": f"response: {row_record}"
                        }
                    ), flush=True
                )
            self.db_session.commit()
            if row_record is not None:
                return{
                    "response": "session test completed",
                    "b_status": "success"
                }
            return {
                "response": "session test not completed",
                "b_status": "failed"
            }
        except Exception as e:
            if self.db_session is not None:
                self.db_session.rollback()
                self.db_session.close()
            if self.db_engine is not None:
                self.db_engine.dispose()
            print(
                json.dumps(
                    {
                        "response": f"test session reliablity is not completed: {str(e)}",
                        "b_status": "failed"
                    }, indent=4
                ), flush=True
            )
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
            ModelClass
        ).where(ModelClass.git_commithash == commithash)
        self.select_query = query


class BotHandler:
    def __init__(self):
        self.master_node = None
        self.prepare_query = PrepareQuery()
        self.dbconnection = DBConnection()
        response = self.dbconnection.create_dbsession()
        print(
            json.dumps(
                {
                    "response": f"database session response: {response}"
                }, indent=4
            ), flush=True
        )
        self.session = None
        if response.get("b_status") == "success":
            self.session = self.dbconnection.db_session
            print(
            json.dumps(
                {
                    "response": f"database session response: {str(self.session)}"
                }, indent=4
            ), flush=True
        )

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
                return {
                    "response": "master node is not prepared. missing metadata",
                    "b_status": "failed"
                }
            return {
                    "response": "master node is prepared",
                    "b_status": "success"
                }

            
        except Exception as e:
            print(json.dumps({
                "response": f"master node is not prepared: {str(e)}",
                "b_status": "failed"
            }, indent=4), flush=True)

    def insert_indb(self, commithash, fileshash, commitmsg):
        try:
            if self.master_node is None:
                response = self.prepare_masternode(commithash, fileshash, commitmsg)
                print(
                    json.dumps(
                        {
                            "response": f"prepare master node response: {response}"
                        }, indent=4
                    ), flush=True
                )
                if response.get("b_status") == "failed":
                    print(
                        json.dumps(
                            {
                                "response": f"prepare master node response: {response}"
                            }, indent=4
                        ), flush=True
                    )
                    return

            payload = {
                "git_commithash": self.master_node.git_commithash,
                "git_commit_msg": self.master_node.git_commit_msg,
                "git_files_hash": [self.master_node.git_files_hash],
            }
            self.prepare_query.prepare_insert()
            query = self.prepare_query.insert_query
            print(
                json.dumps(
                    {
                        "insert query": str(query),
                        "db session": str(self.session) 
                    }, indent=4
                ), flush=True
            )
            if self.session is not None:
                response = self.session.execute(query, payload)
                self.session.commit()
                print(
                    json.dumps(
                        {
                            "response received": str(response)
                        }, indent=4
                    ), flush=True
                )
                if response is not None:
                    print(json.dumps({
                        "response": "insert operation completed",
                        "b_status": "success"
                    }, indent=4), flush=True)
                
        except Exception as e:
            if self.session is not None:
                self.session.rollback()
                self.session.close()
            print(json.dumps({
                "response": f"insert operation is not completed: {str(e)}",
                "b_status": "failed"
            }, indent=4))

    def select_fromdb(self):
        try:
            pass
        except Exception as e:
            print(json.dumps(
                {
                    "response": f"select operation not completed: {str(e)}",
                    "b_status": "failed"
                }, indent=4
            ))
        
class Handshake:
    def __init__(self, signature : str = None, vamessage : str = None):
        self.signature = signature
        self.signature = bytes.fromhex(self.signature)
        self.vamessage = vamessage
        self.vamessage = bytes.fromhex(self.vamessage)

        self.public_key_store = "/src/app/.git/Keystores/publickey.pem"
        self.public_key = None
        self.adjust_signatures_verification_params()

    def adjust_signatures_verification_params(self):
        self.pupadding = padding.PSS(mgf=padding.MGF1(algorithm=hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
        self.pualgorithm = hashes.SHA256()

    def load_keys(self):
        try:
            if not os.path.exists(self.public_key_store):
                return {
                    "response": f"public key is not found on server",
                    "b_status": "failed"
                }
            
            pem = None
            key = None

            with open(file=self.public_key_store, mode="rb") as pukey:
                pem = pukey.read()
            
            pukey.close()

            key = serialization.load_pem_public_key(
                data=pem
            )

            self.public_key = key

            key = None

            return{
                "response": f"public key: {self.public_key}\t public key type: {type(self.public_key)}",
                "b_status": "success"
            }

            
        except Exception as e:
            print(json.dumps(
                {
                    "response": f"failed to check public key store point: {str(e)}",
                    "b_status": "failed"
                }, indent=4
            ), flush=True)
    
    def validate_signature(self):
        try:
            if self.signature is None:
                print({
                    "response": f"signature not found",
                    "b_status": "failed"
                }, flush=True)
            if self.public_key is None:
                response = self.load_keys()
                if response.get("b_status") == "success":
                    print(
                        json.dumps(
                            {
                                "response": response
                            }, indent=4
                        ), flush=True
                    )
                else:
                    return{
                        "response": f"public key is not found",
                        "b_status": "failed"
                    }

            self.public_key.verify(
                signature=self.signature,
                data=self.vamessage,
                padding=self.pupadding,
                algorithm=self.pualgorithm
            )
            return {
                "response": f"congratulation ::) you have been allowed to make push",
                "b_status": "success"
            }

        except Exception as e:
            print(json.dumps(
                {
                    "response": f"signature validation failed: {str(e)}",
                    "b_status": "failed"
                }, indent=4
            ), flush=True)
