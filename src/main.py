from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.controllers import auth, post
from src.exceptions import NotFoundPostError




tags_metadata = [
    {
        "name": "auth",
        "description": "Operações para autenticação",
    },
    {
        "name": "post",
        "description": "Operações para manter posts",
        "externalDocs": {
            "description": "Documentação externa para Posts API",
            "url": "https://post-api.com/",
        },
    },
]

servers = [
    {"url": "http://localhost:8000", "description": "Local environment"},
    {
        "url": "https://dio-blog-fastapi.onrender.com",
        "description": "Production environment",
    },
]

app = FastAPI(
    title="Dio blog API",
    version="1.2.0",
    summary="API para blog pessoal.",
    description="""
DIO Blog API ajuda você a criar seu blog pessoal 🚀

## Posts

Você será capaz de:

* Criar posts
* Listar posts
* Recuperar post por ID
* Atualizar posts
* Excluir posts
""",
    openapi_tags=tags_metadata,
    servers=servers,
    redoc_url=None,
)

# =========================
# CORS (CONFIGURAÇÃO FINAL)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTERS
# =========================
app.include_router(post.router, tags=["post"])
app.include_router(auth.router, tags=["auth"])

# =========================
# EXCEPTION HANDLERS
# =========================
@app.exception_handler(NotFoundPostError)
async def not_found_post_exception_handler(request: Request, exc: NotFoundPostError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Post not found!"},
    )
