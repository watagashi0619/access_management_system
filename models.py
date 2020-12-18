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
    student_id = Column("student_id", String(256))
    student_name = Column("student_name", String(256))
    status_bool = Column("status_bool", BOOLEAN)

    def __init__(
        self,
        student_id: str,
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
            + self.student_id
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
    student_id = Column("student_id", String(256), primary_key=True)
    student_name = Column("student_name", String(256))
    time = Column(
        "time", DateTime, default=datetime.now(), server_default=current_timestamp()
    )

    def __init__(
        self, student_id: str, student_name: str, time: datetime = datetime.now()
    ):
        self.time = time.replace(microsecond=0)
        self.student_id = student_id
        self.student_name = student_name

    def __str__(self):
        return (
            " student_id -> "
            + self.student_id
            + ", time -> "
            + self.time.strftime("%Y/%m/%d %H:%M:%S")
        )


class Visited(Base):
    """
    来たことがある人
    student_id : 学籍番号
    student_name : 名前
    """

    __tablename__ = "visited"
    student_id = Column("student_id", String(256), primary_key=True)
    student_name = Column("student_name", String(256))

    def __init__(
        self, student_id: str, student_name: str,
    ):
        self.student_id = student_id
        self.student_name = student_name

    def __str__(self):
        return (
            " student_id -> "
            + self.student_id
            + ", student_name -> "
            + self.student_name
        )


class Sounds(Base):
    """
    在室者管理
    soundfile : ファイル名
    available : 利用可能設定
    for_me_enter : 入場曲設定
    for_me_exit : 退場曲設定
    exclude : 除外設定
    """

    __tablename__ = "sounds"
    soundfile = Column("soundfile", String(256), primary_key=True)
    available = Column("available", BOOLEAN)
    for_me_enter = Column("for_me_enter", String(256))
    for_me_exit = Column("for_me_exit", String(256))
    exclude = Column("exclude", String(256))

    def __init__(
        self,
        soundfile: str,
        available: bool,
        for_me_enter: str,
        for_me_exit: str,
        exclude: str,
    ):
        self.soundfile = soundfile
        self.available = available
        self.for_me_enter = for_me_enter
        self.for_me_exit = for_me_exit
        self.exclude = exclude

    def __str__(self):
        return (
            " soundfile -> "
            + str(self.soundfile)
            + ", available -> "
            + str(self.available)
            + ", for_me_enter -> "
            + self.for_me_enter
            + ", for_me_exit  -> "
            + self.for_me_exit
            + ", exclude -> "
            + self.exclude
        )
