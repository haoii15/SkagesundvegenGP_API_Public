from typing import Optional
from datetime import time, datetime
from pydantic import BaseModel

# Pydantic model for the Laps class
class LapBase(BaseModel):
    lap_id: int
    driver: str
    team: Optional[str] 
    sector1: float
    sector2: float
    sector3: float
    lap_time: time
    valid: int
    hub: str
    grandprix: str

class Lap(LapBase):
    
    class Config:
        orm_mode = True


# Pydantic model for the GP class
class GPBase(BaseModel):
    name: str
    track: str
    active: int = 1
    condition: str
    game: str

class GP(GPBase):
    gp_id: str
    season: int
    held_at: str

    laps : list[Lap] = []

    class Config:
        orm_mode = True


# Pydantic model for the Driver class
class DriverBase(BaseModel):
    name: str
    display_name: Optional[str]
    team: Optional[str] = None
    discord_id: Optional[str] = None

class Driver(DriverBase):

    driver_id: str
    laps : list[Lap] = []

    class Config:
        orm_mode = True

# Pydantic model for the Team class
class TeamBase(BaseModel):
    name: str
    driver_1: str
    driver_2: Optional[str] = None
    seed: Optional[float] = None
    created_by: str
    owner: str
class Team(TeamBase):
    team_id: str
    created_at: datetime
