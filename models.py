from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.mysql import BOOLEAN, INTEGER
from sqlalchemy.sql import exists
from sqlalchemy.sql.functions import current_timestamp

from db import Base

SQLITE3_NAME = "./db.sqlite3"


class History(Base):
    """
    履歴
    time : 入退室の時間
    student_id : 学籍番号
    student_name : 名前
    status_bool : 入室中 1 / 退出中 0
    """

    __tablename__ = "history"
    id = Column("id", INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    time = Column(
        "time", DateTime, default=datetime.now(), server_default=current_timestamp()
    )
    student_id = Column("student_id", INTEGER(unsigned=True))
    student_name = Column("student_name", String(256))
    status_bool = Column("status_bool", BOOLEAN)

    def __init__(
        self,
        student_id: int,
        student_name: str,
        status_bool: bool,
        time: datetime = datetime.now(),
    ):
        self.time = time.replace(microsecond=0)
        self.student_id = student_id
        self.student_name = student_name
        self.status_bool = status_bool

    def __str__(self):
        return (
            str(self.id)
            + ", time -> "
            + self.time.strftime("%Y/%m/%d %H:%M:%S")
            + ": student_id -> "
            + str(self.student_id)
            + ", student_name -> "
            + self.student_name
            + ": status_bool -> "
            + ["退室", "入室"][self.status_bool]
        )


class Room(Base):
    """
    在室者管理
    student_id : 学籍番号
    student_name : 名前
    status_bool : 入室中 1 / 退出中 0
    """

    __tablename__ = "room"
    student_id = Column("student_id", INTEGER(unsigned=True), primary_key=True)
    student_name = Column("student_name", String(256))
    time = Column(
        "time", DateTime, default=datetime.now(), server_default=current_timestamp()
    )

    def __init__(
        self, student_id: int, student_name: str, time: datetime = datetime.now()
    ):
        self.time = time.replace(microsecond=0)
        self.student_id = student_id
        self.student_name = student_name

    def __str__(self):
        return (
            " student_id -> "
            + str(self.student_id)
            + ", time -> "
            + self.time.strftime("%Y/%m/%d %H:%M:%S")
        )
