from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Time, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from .database import Base


class Lap(Base):
    __tablename__ = 'Laps'
    lap_id = Column(Integer, primary_key=True)
    driver = Column(String(50), ForeignKey('Drivers.driver_id'), primary_key=True)
    team = Column(String(50))
    sector1 = Column(Float)
    sector2 = Column(Float)
    sector3 = Column(Float)
    lap_time = Column(Time)
    valid = Column(Boolean)
    hub = Column(String(15))
    grandprix = Column(String(50), ForeignKey('GPs.gp_id'), primary_key=True)

    drivers = relationship("Driver", back_populates="laps")
    gps = relationship("GP", back_populates="laps")

class GP(Base):
    __tablename__ = 'GPs'
    gp_id = Column(String(50), primary_key=True)
    name = Column(String(100), unique=True)
    season = Column(Integer)
    track = Column(String(75))
    condition = Column(String(16))
    game = Column(String(50))
    active = Column(Boolean, default=True)
    held_at = Column(String(75))

    laps = relationship("Lap", back_populates="gps")

class Driver(Base):
    __tablename__ = 'Drivers'
    driver_id = Column(String(50), primary_key=True)
    name = Column(String(50), unique=True)
    display_name = Column(String(50))
    team = Column(String(50), default=None)
    discord_id = Column(String(50), default=None)

    laps = relationship("Lap", back_populates="drivers")

class Team(Base):
    __tablename__ = 'Teams'
    team_id = Column(String(50), primary_key=True)
    name = Column(String(75), nullable=False, unique=True)
    driver_1 = Column(String(50))
    driver_2 = Column(String(50), default=None)
    seed = Column(Float, default=None)
    created_at = Column(DateTime, nullable=False)
    created_by = Column(String(50), nullable=False)
    owner = Column(String(50), nullable=False)