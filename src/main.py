from fastapi import FastAPI, status, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse

from src.database import database, metadata, engine
from src.controllers import auth, post
from src.exceptions import NotFoundPostError
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.models.post import posts  # noqa
    await database.connect()
    metadata.create_all(engine)
    yield
    await database.disconnect()

tags_metadata = [
    {
        "name": "auth",
        "description": "Operações para autenticação",
    },
    {
        "name": "post",
        "description": "Operações para manter posts.",
        "externalDocs": {
            "description": "Documentação externa para Posts.api",
            "url": "https://post-api.com/",
        },
    },
]

servers = [
    {"url": "https://localhost:8000", "description": "Staging environment"},
    {"url": "https://dio-blog-fastapi.onrender.com", "description": "Production environment"},
]

app = FastAPI(
    title= "Dio blog API",
    version="1.2.0",
    summary="API para blog pessoal.",
    description = """
DIO blog API ajuda você a criar seu blog pessoal. 🚀

## Posts

Você será capaz de fazer:

* **Criar posts** 
* **Recuperar posts** 
* **Recuperar posts por ID** 
* **Atualizar posts**
* **Excluir posts**  
* **Limitar quantidade de posts diários** (_not implemented_).
""",
    openapi_tags=tags_metadata,
    servers= servers,
    redoc_url=None,
    # openapi_url=None, # disable docs
    lifespan=lifespan,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)
app.include_router(post.router, tags=["post"])
app.include_router(auth.router, tags=["auth"])

@app.exception_handler(NotFoundPostError)
async def not_found_post_exception_handler(request: Request, exc: NotFoundPostError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        cotent={"detail": "Post not found!"},
    )
