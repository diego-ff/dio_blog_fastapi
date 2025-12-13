from fastapi import FastAPI
from contextlib import asynccontextmanager
from dio_blog.src.database import database, metadata, engine
from dio_blog.src.controllers import auth, post



@asynccontextmanager
async def lifespan(app: FastAPI):
    from dio_blog.src.models.post import posts  # noqa
    await database.connect()
    metadata.create_all(engine)
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(post.router)
app.include_router(auth.router)
