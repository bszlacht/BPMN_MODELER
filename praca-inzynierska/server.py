from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from typing import Any
import pandas as pd
import os
from pathlib import Path
import shutil
from pydantic import BaseSettings
from main_process import discover_process_main
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from starlette.status import HTTP_504_GATEWAY_TIMEOUT


class Settings(BaseSettings):
    case_column: str = None
    activity_column: str = None
    start_column: str = None
    start_node: str = 'Register'
    end_node: str = 'End'
    out_file_path: str = f'{os.path.abspath(os.getcwd())}\cache\log'
    out_bpmn_path: str = f'{os.path.abspath(os.getcwd())}\cache\graph'
    eps: float = 0.2
    filter_threshold = 20
    is_csv: bool = False
    is_xes: bool = False
    log_name: str = None
    bpmn_name: str = 'manually-generated-complex-output.xml'
    REQUEST_TIMEOUT = 10
    max_e: int = 1


settings = Settings()
app = FastAPI()

origins = ["http://localhost:8080", "http://localhost:8000", "http://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins  # ,
    # allow_credentials=True,
    # allow_methods=["*"],
    # allow_headers=["*"],
)


@app.middleware('http')
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=settings.REQUEST_TIMEOUT)
    except asyncio.TimeoutError:
        return JSONResponse({'detail': f'Request exceeded the time limit for processing'},
                            status_code=HTTP_504_GATEWAY_TIMEOUT)


@app.get("/get-max-w")
async def get_max_w(
        request: Request
) -> Any:
    return settings.max_e


@app.post("/resetColumns")
async def reset_columns(
        request: Request,
) -> Any:
    settings.case_column = None
    settings.activity_column = None
    settings.start_column = None
    return 200


@app.post("/uploadfile/")
async def upload_file(
        request: Request,
        file: UploadFile = File(...),
) -> Any:
    print(file.content_type)
    print(file)
    if file is None:
        raise HTTPException(status_code=422, detail="Parameters not given")
    if file.content_type != "text/csv" and file.content_type != "application/octet-stream":
        raise HTTPException(400, detail="Invalid document type")

    save_upload_file(file, Path(f'{settings.out_file_path}\{file.filename}'))
    settings.log_name = file.filename

    if file.content_type == "text/csv":
        settings.is_csv = True
        df = pd.read_csv(Path(f'{settings.out_file_path}\{file.filename}'))
        list_of_column_names = list(df.columns)
        return list_of_column_names

    else:
        settings.is_xes = True
        return {
            "file": file.filename
        }


@app.post("/set-column-names/")
async def set_column_names(
        case_column: str = Form(...),
        activity_column: str = Form(...),
        start_column: str = Form(...),
        # start_node: str = Form(...),
        # end_node: str = Form(...),
) -> Any:
    settings.case_column = case_column
    settings.activity_column = activity_column
    settings.start_column = start_column
    # settings.start_node = start_node
    # settings.end_node = end_node
    print(case_column)
    print(activity_column)
    print(start_column)
    print(type(start_column))
    return {
        "case_column": settings.case_column,
        "activity_column": settings.activity_column,
        "start_column": settings.start_column,
    }


@app.post("/set-eps-filter")
async def set_eps_filter(
        eps: float = Form(...),
        filter_threshold: int = Form(...),
) -> Any:
    print("eps = " + str(eps))
    print("filter = " + str(filter_threshold))
    settings.eps = eps
    settings.filter_threshold = filter_threshold

    return {
        "eps": settings.eps,
        "filter_threshold": settings.filter_threshold
    }


@app.get("/get-bpmn")
def get_bpmn():
    if settings.is_csv:
        settings.max_e = discover_process_main(log_path=f'{settings.out_file_path}\{settings.log_name}',
                              out_path=settings.out_bpmn_path,
                              case_column=settings.case_column,
                              activity_column=settings.activity_column,
                              start_column=settings.start_column,
                              eps=settings.eps,
                              filter_threshold=settings.filter_threshold)
    elif settings.is_xes:
        print(settings.log_name)
        settings.max_e = discover_process_main(log_path=f'{settings.out_file_path}\{settings.log_name}',
                              out_path=settings.out_bpmn_path,
                              case_column=None,
                              activity_column=None,
                              start_column=None,
                              eps=settings.eps,
                              filter_threshold=settings.filter_threshold)

    with open(f'{settings.out_bpmn_path}\{settings.bpmn_name}') as f:
        lines = f.readlines()
    res = ""
    for count, line in enumerate(lines):
        res += line
    # print(res)

    return res

    # return f'{settings.out_bpmn_path}\{settings.bpmn_name}'


def save_upload_file(file: UploadFile, destination: Path) -> None:
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        pass
