import os
from datetime import datetime

import db
from models import *


def table_management(student_id, student_name, time):

    # 入室経験があれば1
    visited = (
        db.session.query(Visited.student_id).filter_by(student_id=student_id).scalar()
        is not None
    )

    if not visited:
        record_visited = Visited(student_id=student_id, student_name=student_name)
        db.session.add(record_visited)
        db.session.commit()

    # 在室していれば1
    exists = (
        db.session.query(Room.student_id).filter_by(student_id=student_id).scalar()
        is not None
    )

    if not exists:
        record_room = Room(
            time=time.replace(microsecond=0),
            student_id=student_id,
            student_name=student_name,
        )
        db.session.add(record_room)
        db.session.commit()
    else:
        db.session.query(Room.student_id).filter_by(student_id=student_id).delete()

    record_history = History(
        time=time.replace(microsecond=0),
        student_id=student_id,
        student_name=student_name,
        status_bool=(not exists),
    )

    db.session.add(record_history)
    db.session.commit()
    db.session.close()

    return exists


def main():
    # テーブルがない場合にこれ単体で実行することでテーブルを作成
    path = SQLITE3_NAME
    Base.metadata.create_all(db.engine)


if __name__ == "__main__":
    main()
    table_management("3210987624", "test2", datetime.now())
