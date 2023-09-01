from sqlalchemy import func
from sqlalchemy.sql import text
from hashlib import blake2b
from uuid import uuid4
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, date
from app.config import POINTS, ALLOWED_LAPS, ALLOWED_OVERFLOW
from app.services.formatter import format_laptime

def generate_id():
    h = blake2b(digest_size=5)
    h.update(uuid4().bytes)
    return h.hexdigest()

def query(db: Session, q: str):
    try:
        db.execute(text(q+";"))
        db.commit()
        return 1
    except Exception as e:
        print(e)
        return 0

def create_driver(db: Session, driver: schemas.DriverBase):
    id = generate_id()
    db_driver = models.Driver(**driver.dict(), driver_id=id)
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

def create_gp(db: Session, gp: schemas.GPBase):
    id = generate_id()
    dt = date(datetime.now().year, datetime.now().month, datetime.now().day).isocalendar()
    held = f"week {dt.week} {dt.year}"
    db_gp = models.GP(**gp.dict(), gp_id=id, season=int(dt.year), held_at=held )
    db.add(db_gp)
    db.commit()
    db.refresh(db_gp)
    return db_gp

def create_team(db: Session, team: schemas.TeamBase):
    id = generate_id()
    now = datetime.now()
    db_team = models.Team(**team.dict(), team_id=id, created_at=now)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def create_lap(db: Session, lap: schemas.LapBase):
    db_lap = models.Lap(**lap.dict())
    db.add(db_lap)
    db.commit()
    db.refresh(db_lap)
    return db_lap

def truncate_teams(db: Session):
    db.query(models.Team).delete()
    db.commit()

def truncate(db: Session):
    db.query(models.Lap).delete()
    db.query(models.GP).delete()
    db.query(models.Driver).delete()
    db.query(models.Team).delete()
    db.commit()

def get_driver_by_id(db: Session, driver_id: str):
    return db.query(models.Driver).filter(models.Driver.driver_id == driver_id).first()

def get_driver_by_name(db: Session, driver_name: str):
    return db.query(models.Driver).filter(models.Driver.name == driver_name).first()

def get_driver_by_discord(db: Session, discord_id:str):
    return db.query(models.Driver).filter(models.Driver.discord_id == discord_id).first()

def get_drivers(db: Session):
    return db.query(models.Driver).filter(models.Driver.driver_id != None).all()

def get_driver_gps(db: Session, driver_id):
    return db.query(models.Lap).filter(models.Lap.driver == driver_id).all()

def get_driver_laps(db: Session, driver_id: str, gp_id: str):
    return db.query(models.Lap).filter(models.Lap.driver == driver_id).filter(models.Lap.grandprix == gp_id).all()

def update_driver_name(db: Session, driver_name: str, new_name: str):
    return db.query(models.Driver).filter(models.Driver.name == driver_name).update({models.Driver.name: new_name, models.Driver.display_name: new_name}) and db.commit()

def delete_driver_by_name(db: Session, driver_name: str):
    return db.query(models.Driver).filter(models.Driver.name == driver_name).delete() and db.commit()

def set_discord_id(db: Session, name:str, discord_id: str):
    return db.query(models.Driver).filter(models.Driver.name == name).update({models.Driver.discord_id: discord_id}) and db.commit()

def set_team(db: Session, driver_id:str, team_id: str):
    return db.query(models.Driver).filter(models.Driver.driver_id == driver_id).update({models.Driver.team: team_id}) and db.commit()
    
def set_driver1(db: Session, team_id:str, driver_id: str):
    return db.query(models.Team).filter(models.Team.team_id == team_id).update({models.Team.driver_1: driver_id}) and db.commit()

def set_driver2(db: Session, team_id:str, driver_id: str):
    return db.query(models.Team).filter(models.Team.team_id == team_id).update({models.Team.driver_2: driver_id}) and db.commit()

def set_owner(db: Session, team_id: str, driver_id: str):
    return db.query(models.Team).filter(models.Team.team_id == team_id).update({models.Team.owner: driver_id}) and db.commit()

def seed(db: Session, team_id:str):
    seed_ = seed_team(db, team_id)
    db.query(models.Team).filter(models.Team.team_id == team_id).update({models.Team.seed: seed_})
    db.commit()
    return seed_

def unseed(db: Session, team_id:str):
    return db.query(models.Team).filter(models.Team.team_id == team_id).update({models.Team.seed: None}) and db.commit()

def get_gp(db: Session, gp_id: str):
    return db.query(models.GP).filter(models.GP.gp_id == gp_id).first()

def get_gp_by_name(db: Session, gp_name: str):
    return db.query(models.GP).filter(models.GP.name == gp_name).first()

def set_track(db: Session, gp_name: str, track: str):
    return db.query(models.GP).filter(models.GP.name == gp_name).update({models.GP.track: track}) and db.commit()

def set_date(db: Session, gp_name: str, input: str):
    year, month, day = input.split(",")
    dt = date(int(year), int(month), int(day)).isocalendar()
    held = f"week {dt.week} {dt.year}"
    return db.query(models.GP).filter(models.GP.name == gp_name).update({models.GP.held_at: held, models.GP.season: int(dt.year)}) and db.commit()

def set_condition(db: Session, gp_name: str, input: str):
    return db.query(models.GP).filter(models.GP.name == gp_name).update({models.GP.condition: input}) and db.commit()

def set_game(db: Session, gp_name: str, input: str):
    return db.query(models.GP).filter(models.GP.name == gp_name).update({models.GP.game: input}) and db.commit()


def flip_active(db: Session, gp_id: str, input):
    return db.query(models.GP).filter(models.GP.gp_id == gp_id).update({models.GP.active: input}) and db.commit()

def get_seasons(db: Session):
    r = db.query(models.GP.season).filter(models.GP.gp_id != None).distinct().all()
    l =[]
    for season in r:
        l.append(season[0])
    return l


def get_gps(db: Session, season = None):
    if season:
        return db.query(models.GP).filter(models.GP.season == season).all()
    else:
        return db.query(models.GP).filter(models.GP.gp_id != None).all()
    
def get_active_gps(db: Session, season = None):
    if season:
        return db.query(models.GP).filter(models.GP.active, models.GP.season == season).all()
    else:
        return db.query(models.GP).filter(models.GP.active).all()
    
def get_gp_result(db: Session, gp_name: str):
    laps = []
    gp = db.query(models.GP).filter(models.GP.name == gp_name).first()
    drivers = db.query(models.Lap).filter(models.Lap.grandprix == gp.gp_id).all()

    overflow = get_overflow(db, gp.gp_id)
    unique_drivers = {lap.driver for lap in drivers}
    stig = get_driver_by_name(db, "The Stig")
    if stig.driver_id in unique_drivers:
        unique_drivers.remove(stig.driver_id)

    for driver in unique_drivers:
        lap = db.query(models.Driver.name, models.Lap.sector1, models.Lap.sector2, models.Lap.sector3, models.Lap.lap_time, models.Lap.team) \
                    .join(models.Driver, models.Lap.driver == models.Driver.driver_id) \
                    .filter(
                        models.Lap.driver == driver,
                        models.Lap.grandprix == gp.gp_id,
                        models.Lap.lap_id <= overflow,
                        models.Lap.valid == 1
                    ) \
                    .order_by(models.Lap.lap_time) \
                    .limit(1) \
                    .all()
        if len(lap) == 0:
            continue
        else:
            lap = list(lap[0])
        if lap[5]:
            lap[5] = get_team(db, lap[5]).name
        lap[4] = format_laptime(lap[4])
        laps.append(lap)

    laps.sort(key=lambda x:x[4])

    return laps

def get_overflow(db: Session, gp_id: str):

    max_laps = db.query(models.Driver.name, func.max(models.Lap.lap_id).label("total_laps")) \
                .join(models.Lap, models.Lap.driver == models.Driver.driver_id) \
                .filter(models.Lap.grandprix == gp_id) \
                .group_by(models.Driver.driver_id) \
                .order_by(func.max(models.Lap.lap_id).desc()) \
                .all()
    if len(max_laps) < 2:
        return ALLOWED_LAPS + ALLOWED_OVERFLOW
    else:
        return max_laps[1][1] + ALLOWED_OVERFLOW
    
def get_laps_team(db: Session, team_id: str):
    return db.query(models.Lap).filter(models.Lap.team == team_id).all()

def get_team(db: Session, team_id: str):
    return db.query(models.Team).filter(models.Team.team_id == team_id).first()

def get_team_by_name(db: Session, team_name: str):
    return db.query(models.Team).filter(models.Team.name == team_name).first()

def get_teams(db: Session):
    return db.query(models.Team).filter(models.Team.team_id != None).all()

def delete_team(db: Session, team_id: str):
    return db.query(models.Team).filter(models.Team.team_id == team_id).delete() and db.commit()


def seed_team(db: Session, team_id: str):
    team = get_team(db, team_id)
    if team.driver_1 == None or team.driver_2 == None:
        return {"code": 400, "error": 10000, "detail": "Something fucked up really bad"}
    
    driver1, driver2 = get_driver_by_id(db, team.driver_1), get_driver_by_id(db, team.driver_2)
    if driver1 == None or driver2 == None:
        return {"code": 400, "error": 10000, "detail": "Something fucked up really bad"}

    ranking = get_total(db, season=2022)
    rank_d1 = None
    rank_d2 = None
    for idx, driver in enumerate(ranking):
        if driver[0] == driver1.name:
            rank_d1 = idx+1
        if driver[0] == driver2.name:
            rank_d2 = idx+1

    d1 = rank_d1 if rank_d1 else len(ranking)+1
    d2 = rank_d2 if rank_d2 else len(ranking)+1

    return d1 + d2

def get_total(db: Session, season:int = None):
    if season:
        gps = get_active_gps(db, season=season)
    else:
        gps = get_active_gps(db)

    tot = {}

    for gp in gps:
        for driver in get_scoreboard(db,gp.name):
            if driver[0] in tot.keys():
                tot[driver[0]][1] += driver[6]
            else:
                tot[driver[0]] = [driver[5], driver[6]]

    ret = []
    for key in tot.keys():
        ret.append([key, tot[key][0], tot[key][1]])

    return sorted(ret, key=lambda x: x[2], reverse=True)

def get_scoreboard(db: Session, gp_name: str):
    if get_gp_by_name(db, gp_name):
        result = get_gp_result(db, gp_name)
        for idx, driver in enumerate(result):
            driver.append(POINTS[idx])
        return result
    else:
        return f"{gp_name} e isje någe Grand Prix"

def insert_laps(db: Session, gp_id: str, laps: list):
    formatted_laps = []
    for lap in laps:
        driver = get_driver_by_name(db, lap[1])
        if driver == None:
            driver = create_driver(db, schemas.DriverBase(**{"name": lap[1], "display_name": lap[1]}))
        formatted_laps.append(schemas.LapBase(**{"lap_id": lap[0],
                                                 "driver": driver.driver_id,
                                                 "team": driver.team,
                                                 "sector1": lap[2],
                                                 "sector2": lap[3],
                                                 "sector3": lap[4],
                                                 "lap_time": "00:"+lap[5],
                                                 "valid": int(lap[6]),
                                                 "hub": lap[7],
                                                 "grandprix": gp_id
                                                 }))

    for lap in formatted_laps:
        create_lap(db, lap)