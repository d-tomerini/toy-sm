from fastapi import FastAPI
from database import engine
from core.config import settings
from routers import auth, market, players, team
import models


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)


models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(market.router)
app.include_router(players.router)
app.include_router(team.router)
