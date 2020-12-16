import csv
from datetime import datetime
from io import StringIO

from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse, StreamingResponse
from starlette.requests import Request
from starlette.status import HTTP_303_SEE_OTHER
from starlette.templating import Jinja2Templates

import db
from models import History, Room

import yaml

yaml_dict = yaml.load(open("key.yaml").read())

app = FastAPI(
    title=yaml_dict["title"], description=yaml_dict["description"], version=yaml_dict["version"]
)

templates = Jinja2Templates(directory="templates")
jinja_env = templates.env


@app.get("/")
async def index(request: Request):

    room = db.session.query(Room).all()
    history = db.session.query(History).all()

    return templates.TemplateResponse(
        "index.html", {"request": request, "room": room, "history": history,"title":yaml_dict["title"]}
    )


@app.get("/revise")
async def revise(request: Request):

    room = db.session.query(Room).all()
    history = db.session.query(History).all()

    return templates.TemplateResponse(
        "revise.html", {"request": request, "room": room, "history": history,"title":yaml_dict["title"]}
    )


@app.post("/revise/add")
async def add(
    request: Request,
    historydatetime: str = Form(...),
    studentid: int = Form(...),
    studentname: str = Form(...),
    status: int = Form(...),
):

    record_history = History(
        time=datetime.strptime(historydatetime, "%Y/%m/%d %H:%M"),
        student_id=studentid,
        student_name=studentname,
        status_bool=[False, True][status],
    )

    db.session.add(record_history)
    db.session.commit()
    db.session.close()

    return RedirectResponse("/revise", status_code=HTTP_303_SEE_OTHER)


@app.post("/revise/enter")
async def enter(
    request: Request,
    enterdatetime: str = Form(...),
    studentid: int = Form(...),
    studentname: str = Form(...),
):

    data = await request.form()

    time = datetime.strptime(enterdatetime, "%Y/%m/%d %H:%M")

    record_room = Room(time=time, student_id=studentid, student_name=studentname,)

    db.session.add(record_room)
    db.session.commit()

    if "withHistory" in data:
        status_bool = True

        record_history = History(
            time=time,
            student_id=studentid,
            student_name=studentname,
            status_bool=status_bool,
        )

        db.session.add(record_history)
        db.session.commit()

    db.session.close()

    return RedirectResponse("/revise", status_code=HTTP_303_SEE_OTHER)


@app.api_route("/revise/delete/{id}", methods=["POST", "DELETE"])
async def delete(id: int):

    db.session.delete(db.session.query(History).filter_by(id=id).first())
    db.session.commit()
    db.session.close()

    return RedirectResponse("/revise", status_code=HTTP_303_SEE_OTHER)


@app.api_route("/revise/left/{student_id}", methods=["POST", "DELETE"])
async def left(student_id: int):

    db.session.delete(db.session.query(Room).filter_by(student_id=student_id).first())
    db.session.commit()
    db.session.close()

    return RedirectResponse("/revise", status_code=HTTP_303_SEE_OTHER)


@app.get("/download")
async def download():

    history = db.session.query(History).all()

    f = StringIO()
    writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL, lineterminator="\n")

    writer.writerow(["id", "time", "student_id", "student_name", "status"])
    for u in history:
        writer.writerow(
            [u.id, u.time, u.student_id, u.student_name, ["退室", "入室"][u.status_bool]]
        )

    response = StreamingResponse(iter([f.getvalue()]), media_type="text/csv")
    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=history{}.csv".format(
        datetime.now().strftime("%Y%m%d%H%M")
    )

    return response
