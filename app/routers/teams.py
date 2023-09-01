from fastapi import APIRouter, Depends
from app.sql_app import crud
from app.sql_app.database import get_db
from sqlalchemy.orm import Session
from app.sql_app.schemas import TeamBase

router = APIRouter(
    tags= ["Teams"],
    prefix= "/teams"
)

@router.get("/")
def get_teams(db: Session = Depends(get_db)):
    teams = crud.get_teams(db)
    if teams:
        ret = []
        for team in teams:
            d1 = crud.get_driver_by_id(db, team.driver_1).name if crud.get_driver_by_id(db, team.driver_1) != None else ""
            d2 = crud.get_driver_by_id(db, team.driver_2).name if crud.get_driver_by_id(db, team.driver_2) != None else ""
            ret.append([team.name, d1, d2, team.seed, team.created_at, crud.get_driver_by_id(db, team.created_by).name, crud.get_driver_by_id(db, team.owner).name])
        return {"code": 200, "error": 0, "detail": ret}
    else:
        return {"code": 400, "error": 0, "detail": None}


@router.get("/{team_name}")
def get_team(team_name: str, db: Session = Depends(get_db)):
    team = crud.get_team_by_name(db, team_name)
    if team == None:
        return {"code": 400, "error": 1, "detail": f"{team_name} e isje någe lag."}
    return {"code": 200, "error": 0, "detail": team}

@router.get("/id/{team_id}")
def get_team_id(team_id: str, db: Session = Depends(get_db)):
    team = crud.get_team(db, team_id)
    if team == None:
        return {"code": 400, "error": 1, "detail": f"Ingen lag me den iden"}
    return {"code": 200, "error": 0, "detail": team}

@router.post("/{team_name}")
def create_team(team_name: str, discord_id: str, db: Session = Depends(get_db)):
    driver = crud.get_driver_by_discord(db, discord_id)
    if driver == None:
        return {"code": 400, "error": 1, "detail": "Du e isje linka te ein førerkonto"}
    if driver.team != None:
        return {"code": 400, "error": 1, "detail": f"Du har allerede kontrakt me {crud.get_team(db, driver.team).name}"}
    team = crud.create_team(db, TeamBase(name=team_name, driver_1=driver.driver_id, created_by=driver.driver_id, owner=driver.driver_id))
    if team == None:
        return {"code": 400, "error":1, "detail": "Lagnavne e allerede tatt av någen andre."}
    crud.set_team(db, driver.driver_id, team.team_id)

    return {"code": 200, "error":0, "detail": team}

@router.put("/leave/{discord_id}")
def leave_team(discord_id: str, db: Session = Depends(get_db)):
    driver = crud.get_driver_by_discord(db, discord_id)
    if driver == None:
        return {"code": 400, "error": 1, "detail": "Du e isje linka te ein førerkonto"}
    if driver.team == None:
        return {"code": 400, "error": 1, "detail": "Du har isje kontrakt med et lag"}
    team = crud.get_team(db, driver.team)
    crud.set_team(db, driver.driver_id, None)
    crud.unseed(db, team.team_id)
    
    if team.driver_1 == driver.driver_id:
        if team.driver_2 == None:
            crud.set_driver1(db, team.team_id, None)
            team_laps = crud.get_laps_team(db, team.team_id)
            if team_laps:
                return {"code": 200, "error": 0, "detail": f"Du har nå forlatt {team.name} som siste gjenverane. {crud.get_driver_by_id(db, team.owner).name} eige nå et lag uten førere"}
            else:
                crud.delete_team(db, team.team_id)
                return {"code": 200, "error": 0, "detail": f"Du har nå forlatt {team.name} som siste gjenverane og dermed sletta lage"}
        else:
            crud.set_driver1(db, team.team_id, team.driver_2)
            driver2name = crud.get_driver_by_id(db, team.driver_2).name
            crud.set_driver2(db, team.team_id, None)
            return {"code": 200, "error": 0, "detail": f"Du har nå forlatt {team.name} og gjort {driver2name} te driver 1. {crud.get_driver_by_id(db, team.owner).name} eige fortsatt lage.!"}
    elif team.driver_2 == driver.driver_id:
        crud.set_driver2(db, team.team_id, None)
        return {"code": 200, "error": 0, "detail": f"Du har nå forlatt {team.name}"}
    else:
        return {"code": 400, "error": 10000, "detail": "Something fucked up really bad"}
    
@router.put("/join/{team_name}")
def join_team(team_name: str, discord_id:str, db: Session = Depends(get_db)):
    driver = crud.get_driver_by_discord(db, discord_id)
    if driver == None:
        return {"code": 400, "error": 1, "detail": "Du e isje linka te ein førerkonto"}
    if driver.team != None:
        return {"code": 400, "error": 1, "detail": f"Du har allerede kontrakt med {crud.get_team(db, driver.team).name}"}
    team = crud.get_team_by_name(db, team_name)
    if team == None:
        return {"code": 400, "error": 1, "detail": f"{team_name} e isje et lag"}
    
    if team.driver_1 == None:
        crud.set_driver1(db, team.team_id, driver.driver_id)
        crud.set_team(db, driver.driver_id, team.team_id)
        return {"code": 200, "error": 0, "detail": f"Du har nå joina {team.name}, et forlatt lag. Finn deg ein lagkamerat"}
    elif team.driver_2 == None:
        crud.set_driver2(db, team.team_id, driver.driver_id)
        crud.set_team(db, driver.driver_id, team.team_id)
        seed = crud.seed(db, team.team_id)
        return {"code": 200, "error": 0, "detail": seed}
    else:
        return {"code": 400, "error": 1, "detail": f"{team_name} har allerede to førere på kontrakt og e derfor fult. Smisk me {crud.get_driver_by_id(db, team.owner).name}"}
    
@router.put("/owner")
def new_owner_team(team_name: str, owner_id: str, new_owner_name:str, db: Session = Depends(get_db)):
    owner = crud.get_driver_by_discord(db, owner_id)
    if owner == None:
        return {"code": 400, "error": 1, "detail": "Du e isje linka te ein førerkonto"}
    team = crud.get_team_by_name(db, team_name)
    if team == None:
        return {"code": 400, "error": 1, "detail": f"{team_name} e isje et lag"}
    if team.owner != owner.driver_id:
        return {"code": 400, "error": 1, "detail": f"Du eige isje {team_name} og kan obviously isje gje de fra deg"}
    new_owner = crud.get_driver_by_name(db, new_owner_name)
    if new_owner == None:
        return {"code": 400, "error": 1, "detail": f"{new_owner_name} e ingen førerkonto"}
    if new_owner.discord_id == None:
        return {"code": 400, "error": 1, "detail": f"{new_owner.name} e isje linka te ein discord konto"}
    
    crud.set_owner(db, team.team_id, new_owner.driver_id)
    return {"code": 200, "error": 0, "detail": f"{new_owner.name} e nå eigar av {team.name}"}

@router.put("/remove")
def remove_driver(driver_name: str, owner_id:str, db: Session = Depends(get_db)):
    owner = crud.get_driver_by_discord(db, owner_id)
    if owner == None:
        return {"code": 400, "error": 1, "detail": "Du e isje linka te ein førerkonto"}
    driver = crud.get_driver_by_name(db, driver_name)
    if driver == None:
        return {"code": 400, "error": 1, "detail": f"{driver_name} e isje ein fører"}
    if driver.team == None:
        return {"code": 400, "error": 1, "detail": f"{driver_name} har isje kontrakt me et lag"}
    
    team = crud.get_team(db, driver.team)
    if team.owner != owner_id:
        return {"code": 400, "error": 1, "detail": f"Du eige isje {team.name} og kan obviously isje fjerne {driver_name} fra lage"}

    crud.set_team(db, driver.driver_id, None)
    crud.unseed(db, team.team_id)
    if team.driver_1 == driver.driver_id:
        if team.driver_2:
            crud.set_driver1(db, team.team_id, team.driver_2)
            return {"code": 400, "error": 1, "detail": f"Du har fjerna {driver.name} fra {team.name} og gjort {crud.get_driver_by_id(db, team.driver_1).name} te 1. fører"}
        else:
            crud.set_driver1(db, team.team_id, None)
            return {"code": 400, "error": 1, "detail": f"Du har fjerna {driver.name} fra {team.name}. Lage e tomt nå"}
    elif team.driver_2 == driver.driver_id:
        crud.set_driver2(db, team.team_id, None)
        return {"code": 400, "error": 1, "detail": f"Du har fjerna 2. fører{driver.name} fra {team.name}"}
    else:
        return {"code": 400, "error": 1, "detail": f"någe humbug her nå"}


@router.put("/")
def truncate(db: Session = Depends(get_db)):
    crud.truncate_teams(db)