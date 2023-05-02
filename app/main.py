from fastapi import FastAPI
from .routers import post, user, auth, likes
from .config import settings

print(settings.database_username)

# from . import models
# from .database import engine
# models.Base.metadata.create_all(bind=engine)

app= FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(likes.router)


@app.get("/")
def root():
    return {"CLOAK": "Welcome to the anonymous world!!"}