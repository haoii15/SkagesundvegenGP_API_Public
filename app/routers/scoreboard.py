from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.sql_app import crud
from app.sql_app.database import get_db


router = APIRouter(
    tags=["Scoreboard"],
    prefix= "/scoreboard"
)


@router.get("/")
def get_total(db: Session = Depends(get_db)):
    return crud.get_total(db)

@router.get("/season/{season}")
def get_total(season:int, db: Session = Depends(get_db)):
    return crud.get_total(db, season=season)

@router.get("/gp/{gp_name}")
def get_scoreboard(gp_name: str, db: Session = Depends(get_db)):
    return crud.get_scoreboard(db, gp_name)

