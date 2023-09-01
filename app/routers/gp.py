from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.sql_app import crud
from app.sql_app.database import get_db
from app.services.formatter import format_laptime


router = APIRouter(
    tags=["GP"],
    prefix= "/gp"
)

@router.get("/")
def get_grandprixes(db: Session = Depends(get_db)):
    gps = crud.get_gps(db)
    if len(gps) == 0:
        return {"code": 400, "error": 1, "detail": "Ingen Grand Prix å melde tebake om"}
    r = []
    for gp in gps:
        r.append([gp.name, gp.season, gp.track, gp.condition, gp.game, gp.held_at])
    return {"code": 200, "error": 0, "detail": r}

@router.get("/{season}")
def get_grandprixes_season(season: int, db: Session = Depends(get_db)):
    seasons = crud.get_seasons(db)
    if len(seasons) == 0:
        return {"code": 400, "error": 1, "detail": "Ingen sesongar å melde tebake om"}
    if season not in seasons:
        return {"code": 400, "error": 1, "detail": f"{season} e isje ein sesong"}
    gps = crud.get_gps(db, season)
    r = []
    for gp in gps:
        r.append([gp.name, gp.season, gp.track, gp.condition, gp.game, gp.held_at])
    return {"code": 200, "error": 0, "detail": r}

@router.get("/seasons/all")
def get_season_r(db: Session = Depends(get_db)):
    seasons = crud.get_seasons(db)
    if len(seasons) == 0:
        return {"code": 400, "error": 1, "detail": "Ingen sesongar å melda tebake om"}
    return {"code": 200, "error": 0, "detail": seasons}
    
@router.get("/laps/{driver_name}/{gp_name}")
def get_driver_laps(driver_name: str, gp_name: str, db: Session = Depends(get_db)):
    driver = crud.get_driver_by_name(db, driver_name)
    if driver == None:
        return {"code": 400, "error": 1, "detail": f"{driver_name} e ingen førar"}
    gp = crud.get_gp_by_name(db, gp_name)
    if gp == None:
        return {"code": 400, "error": 1, "detail": f"{gp_name} e isje någe Grand Prix"}
    laps = crud.get_driver_laps(db, driver.driver_id, gp.gp_id)
    if laps == None:
        return {"code": 400, "error": 1, "detail": "Ingen rundar å melda tebake om"}
    r = []
    for lap in laps:
        r.append([crud.get_driver_by_id(db, lap.driver).name, lap.sector1, lap.sector2, lap.sector3, format_laptime(lap.lap_time), lap.valid, lap.hub])
    return {"code": 200, "error": 0, "detail": r}


@router.put("/{gp_name}")
def flip_active(gp_name: str, db: Session = Depends(get_db)):
    gp = crud.get_gp_by_name(db, gp_name)
    if gp == None:
        return {"code": 400, "error": 1, "detail": f"{gp_name} e isje någe grand prix."}
    new = False if gp.active else True
    crud.flip_active(db, gp.gp_id, new)
    return {"code": 200, "error": 0, "detail": f"{gp_name} sin active e nå {new}"}

