from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.sql_app.database import get_db
from app.sql_app import data_fetch, crud, schemas
import json

router = APIRouter(
    tags=["Insert"],
    prefix= "/insert"
)

ranges= {
    (20, 26): data_fetch.read_old_laps,
    (21, 28): data_fetch.read_mid_laps,
    (2, 9): data_fetch.read_new_laps
}

@router.post("/")
async def insert_laps_from_google(request: Request, db: Session = Depends(get_db)):
    req = json.loads(await request.body())
    cols = (req["range"]["columnStart"], req["range"]["columnEnd"])
    rows = (req["range"]["rowStart"], req["range"]["rowEnd"])
    gp_name = req["sheetName"]

    
    if cols in ranges.keys():
        gp = crud.get_gp_by_name(db, gp_name)
        if gp == None:
            gp = crud.create_gp(db, schemas.GPBase(**{"name": gp_name, "track": "N/A", "condition": "dry", "game": "F1 22"}))
        laps = ranges[cols](gp_name, rows)
        crud.insert_laps(db, gp.gp_id, laps)
        return 200
    elif rows == (1,1) and cols == (15,15):
        gp = crud.get_gp_by_name(db, gp_name)
        if gp == None:
            gp = crud.create_gp(db, schemas.GPBase(**{"name": gp_name, "track": "N/A", "condition": "dry", "game": "F1 22"}))
        if "value" in req.keys():
            crud.set_track(db, gp_name, req["value"])
        return 200
    elif rows == (1,1) and cols == (14,14):
        gp = crud.get_gp_by_name(db, gp_name)
        if gp == None:
            gp = crud.create_gp(db, schemas.GPBase(**{"name": gp_name, "track": "N/A", "condition": "dry", "game": "F1 22"}))
        if "value" in req.keys():
            crud.set_date(db, gp_name, req["value"])
        return 200
    elif rows == (1,1) and cols == (13,13): # CHECK COL
        gp = crud.get_gp_by_name(db, gp_name)
        if gp == None:
            gp = crud.create_gp(db, schemas.GPBase(**{"name": gp_name, "track": "N/A", "condition": "dry", "game": "F1 22"}))
        if "value" in req.keys():
            crud.set_condition(db, gp_name, req["value"])
        return 200
    elif rows == (1,1) and cols == (12,12): # CHECK COL
        gp = crud.get_gp_by_name(db, gp_name)
        if gp == None:
            gp = crud.create_gp(db, schemas.GPBase(**{"name": gp_name, "track": "N/A", "condition": "dry", "game": "F1 22"}))
        if "value" in req.keys():
            crud.set_game(db, gp_name, req["value"])
        return 200
    return Response(status_code=404)
