from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, declarative_base
from sqlalchemy import select, insert, update, text
from clickhouse_sqlalchemy import types

class LocalDB:
    def __init__(self):
        pass


BASE = declarative_base()

class BaseModel(BASE):
    __tablename__ = "gitmaster"
    __table_args__ = {"schema" : "gitforgex"}

    FILEPATH : Mapped[str] = mapped_column(types.String)
    FILESIZE : Mapped[str] = mapped_column(types.String)
    FILELASTSIZE : Mapped[str] = mapped_column(types.String, server_default=-1)
    FILEHASH : Mapped[str] = mapped_column(types.String)
    FILELASTMODIFIEDHASH : Mapped[str] = mapped_column(types.String, server_default=None)
    FILEMODIFIED : Mapped[str] = mapped_column(types.String, server_default=False)
    FILETRACKSTATUS : Mapped[str] = mapped_column(types.String, server_default=False)
    FILELASTTRACKSTATUS : Mapped[str] = mapped_column(types.String, server_default=False)
    FILESTAGESTATUS : Mapped[str] = mapped_column(types.String, server_default=False)
    FILELASTSTAGESTATUS : Mapped[str] = mapped_column(types.String, server_default=False)
    FILECOMMITSTATUS : Mapped[str] = mapped_column(types.String, server_default=False)
    FILELASTCOMMITSTATUS : Mapped[str] = mapped_column(types.String, server_default=False)
    FILECOMMITMESSAGE : Mapped[str] = mapped_column(types.String, server_default=None)
    FILELASTCOMMITMESSAGE : Mapped[str] = mapped_column(types.String, server_default=None)
    FILECOMMITHASH : Mapped[str] = mapped_column(types.String, server_default=None)
    FILELASTCOMMITHASH : Mapped[str] = mapped_column(types.String, server_default=None)
    FILECOMMITDATETIME : Mapped[str] = mapped_column(types.String, server_default=None)
    FILELASTCOMMITDATETIME : Mapped[str] = mapped_column(types.String, server_default=None)


class PrepareQuery:
    def __init__(self):
        self.select_query = None
        self.insert_query = None
        self.update_query = None

    def prepare_insert(self, payload):
        query = insert(BaseModel).values(**payload)
        self.insert_query = query

    def prepare_update(self, payload):
        pass

