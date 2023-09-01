from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.sql_app.database import get_db
from app.sql_app.crud import get_driver_by_name, get_driver_by_discord, create_driver, set_discord_id, delete_driver_by_name, get_driver_by_id, get_driver_gps, get_drivers, get_team, update_driver_name
from app.sql_app.schemas import DriverBase


router = APIRouter(
    tags= ["Users"],
    prefix= "/users"
)

@router.get("/")
def all_users(db: Session = Depends(get_db)):
    resp = get_drivers(db)
    if resp == None:
        return {"code": 400, "error": 1, "detail": "ingen brukere å hente"}
    else:
        l = []
        for user in resp:
            if user.team:
                user.team = get_team(db, user.team).name
            l.append(user)
        return {"code": 200, "error": 0, "detail": l}


@router.put("/link/{username}")
def link_user_discord(username: str, discord_id: str, db: Session = Depends(get_db)):
    resp = verify_request(username, discord_id, db)
    if resp["code"] != 200:
        return resp
    
    if resp["error"] == 100:
        driver = DriverBase(name=username, display_name=username)
        new_id = create_driver(db, driver)
        if new_id == None:
            return {"code": 400, "error": 1, "detail": "Dette brukarnavne e allerede i bruk!"}

    set_discord_id(db, username, discord_id)
    return {"code": 200, "error": 0, "detail": username}

@router.put("/unlink")
def unlink_user_discord(discord_id: str, db: Session = Depends(get_db)):
    driver = get_driver_by_discord(db, discord_id)
    if driver == None:
        return {"code": 400, "error": 1, "detail": "Du e isje linka te ein førerkonto"}
    if driver.team != None:
        return {"code": 400, "error": 1, "detail": "Du har kontrakt me et lag, du kan isje unlinka før du forlate lage"}

    set_discord_id(db, driver.name, None)

    if len(get_driver_gps(db, driver.driver_id)) == 0:
        delete_driver_by_name(db, driver.name)
        return {"code": 200, "error": 0, "detail": driver.name + " og føreren e sletta"}
    
    return {"code": 200, "error": 0, "detail": driver.name}

@router.get("/link/verify/{username}")
def verify_request(username: str, discord_id: str, db: Session = Depends(get_db)):
    driver = get_driver_by_name(db, username)
    if driver == None:
        return {"code": 200, "error": 100, "detail": "Linkforespørselen e lagt te godkjenning"}

    if driver.discord_id != None:
        return {"code": 400, "error": 2, "detail": f"Denne førerkontoen er allerede linka til en discordkonto: {driver.discord_id}"}
    disc_driver = get_driver_by_discord(db, discord_id)
    if disc_driver != None:
        return {"code": 400, "error": 1, "detail": f"Du har allerede linka te ein aen førerkonto: {disc_driver.name}"}

    return {"code": 200, "error": 0, "detail": "Linkforespørselen e lagt te godkjenning"}

@router.post("/delete/{driver_name}")
def delete_driver_name(driver_name: str, db: Session = Depends(get_db)):
    driver = get_driver_by_name(db, driver_name)
    if driver == None:
        return {"code": 400, "error": 200, "detail": f"{driver_name} e ingen fører"}
    else:
        delete_driver_by_name(db, driver_name)
        return {"code": 200, "error": 0, "detail": f"{driver_name} e fjerna"}

@router.get("/name/{driver_name}")
def get_driver_name(driver_name: str, db: Session = Depends(get_db)):
    driver = get_driver_by_name(db, driver_name)
    if driver == None:
        return {"code": 400, "error": 200, "detail": f"{driver_name} e ingen fører"}
    else:
        return {"code": 200, "error": 0, "detail": driver}

@router.get("/discord/{discord_id}")
def get_driver_discord(discord_id: str, db: Session = Depends(get_db)):
    driver = get_driver_by_discord(db, discord_id)
    if driver == None:
        return {"code": 400, "error": 200, "detail": f"Du e isje kobla te någen fører"}
    else:
        return {"code": 200, "error": 0, "detail": driver}

@router.get("/id/{driver_id}")
def get_driver_discord(driver_id: str, db: Session = Depends(get_db)):
    driver = get_driver_by_id(db, driver_id)
    if driver == None:
        return {"code": 400, "error": 200, "detail": f"Denne id e ingen fører"}
    else:
        return {"code": 200, "error": 0, "detail": driver}

@router.patch("/name/{driver_name}/{new_name}")
def rename_driver(driver_name: str, new_name: str, db: Session = Depends(get_db)):
    ret = update_driver_name(db, driver_name, new_name)
    if ret:
        return {"code": 200, "error": 0, "detail": f"{driver_name} e nå {new_name}"}
    else:
        return {"code": 400, "error": 0, "detail": "Någe fucka seg"}
