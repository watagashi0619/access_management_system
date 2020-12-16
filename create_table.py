import os
from datetime import datetime

import db
from models import *


def table_management(student_id, student_name, time):
    path = SQLITE3_NAME
    if not os.path.isfile(path):
        # テーブルを作成
        Base.metadata.create_all(db.engine)

    # 存在していれば1
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
