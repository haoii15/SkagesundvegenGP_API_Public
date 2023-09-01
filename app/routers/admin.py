from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.sql_app import crud
from app.sql_app.database import get_db

router = APIRouter(
    tags=["Admin"],
    prefix= "/admin"
)


@router.put("/query")
def query(query: str = Body(...), db: Session = Depends(get_db)):
    r = crud.query(db, query)
    if r:
        return {"code": 200, "error": 0, "detail": "Query utført"}
    else:
        return {"code": 400, "error": 1, "detail": "Någe fucka seg"}


