import csv
import os
import shutil
import subprocess
from datetime import datetime
from io import StringIO

import yaml
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.status import HTTP_303_SEE_OTHER
from starlette.templating import Jinja2Templates

import db
from models import *

yaml_dict = yaml.load(open("key.yaml").read())

app = FastAPI(
    title=yaml_dict["title"],
    description=yaml_dict["description"],
    version=yaml_dict["version"],
)

app.mount("/enter_sounds", StaticFiles(directory="enter_sounds"), name="enter_sounds")
app.mount("/exit_sounds", StaticFiles(directory="exit_sounds"), name="exit_sounds")

templates = Jinja2Templates(directory="templates")
jinja_env = templates.env

ALLOWED_EXTENSIONS = set(["wav", "mp3"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/")
async def index(request: Request):

    room = db.session.query(Room).all()
    history = db.session.query(History).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "room": room,
            "history": history,
            "title": yaml_dict["title"],
        },
    )


@app.get("/soundsetting")
async def revise(request: Request):
    enter_sounds = db.session.query(EnterSounds).all()
    exit_sounds = db.session.query(ExitSounds).all()
    visited = db.session.query(Visited).all()

    return templates.TemplateResponse(
        "sound.html",
        {
            "request": request,
            "title": yaml_dict["title"],
            "enter_sounds": enter_sounds,
            "exit_sounds": exit_sounds,
            "visited": visited,
        },
    )


@app.post("/soundsetting/upload/{enter_or_exit}")
async def sound_upload_enter(enter_or_exit: int, file: UploadFile = File(...)):
    if file and allowed_file(file.filename):
        filename = file.filename
        fileobj = file.file
        if enter_or_exit == 1:
            upload_dir = open(os.path.join("./enter_sounds", filename), "wb+")
        else:
            upload_dir = open(os.path.join("./exit_sounds", filename), "wb+")
        shutil.copyfileobj(fileobj, upload_dir)
        upload_dir.close()

        if enter_or_exit == 1:
            record_sound = EnterSounds(
                soundfile=filename,
                available=True,
                for_me="",
                exclude="",
            )
        else:
            record_sound = ExitSounds(
                soundfile=filename,
                available=True,
                for_me="",
                exclude="",
            )

        db.session.add(record_sound)
        db.session.commit()
        db.session.close()

        return RedirectResponse("/soundsetting", status_code=HTTP_303_SEE_OTHER)
    if file and not allowed_file(file.filename):
        return {"warning": "Illegal extension"}


@app.api_route(
    "/soundsetting/delete/{enter_or_exit}/{soundfile}", methods=["POST", "DELETE"]
)
async def delete(enter_or_exit: int, soundfile: str):

    if enter_or_exit == 1:
        db.session.delete(
            db.session.query(EnterSounds).filter_by(soundfile=soundfile).first()
        )
        subprocess.run(["rm", "enter_sounds/" + soundfile])
    else:
        db.session.delete(
            db.session.query(ExitSounds).filter_by(soundfile=soundfile).first()
        )
        subprocess.run(["rm", "exit_sounds/" + soundfile])

    db.session.commit()
    db.session.close()

    return RedirectResponse("/soundsetting", status_code=HTTP_303_SEE_OTHER)


@app.get("/revise")
async def revise(request: Request):

    room = db.session.query(Room).all()
    history = db.session.query(History).all()

    return templates.TemplateResponse(
        "revise.html",
        {
            "request": request,
            "room": room,
            "history": history,
            "title": yaml_dict["title"],
        },
    )


@app.post("/revise/add")
async def add(
    request: Request,
    historydatetime: str = Form(...),
    studentid: str = Form(...),
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
    studentid: str = Form(...),
    studentname: str = Form(...),
):

    data = await request.form()

    time = datetime.strptime(enterdatetime, "%Y/%m/%d %H:%M")

    record_room = Room(
        time=time,
        student_id=studentid,
        student_name=studentname,
    )

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
async def left(student_id: str):

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
