import fastapi
import uvicorn
from .routers import scoreboard, users, teams, insert, gp, admin
from fastapi import Request, Response
from .secret import API_KEY
from .sql_app import models
from .sql_app.database import engine


models.Base.metadata.create_all(bind=engine)

app = fastapi.FastAPI()

app.include_router(scoreboard.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(insert.router)
app.include_router(gp.router)
app.include_router(admin.router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    key = request.headers.get("X-Api-Key")
    if key != API_KEY:
        return Response(status_code=401, content="Incorrect Credentials")
    response = await call_next(request)
    return response