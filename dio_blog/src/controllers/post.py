from fastapi import FastAPI, status, HTTPException, APIRouter, Depends, Query
from dio_blog.src.schemas.post import PostIn, PostUpdateIn
from dio_blog.src.views.post import PostOut
from dio_blog.src.services.post import PostService
from dio_blog.src.exceptions import NotFoundPostError
from dio_blog.src.security import login_required

router = APIRouter(prefix="/posts", dependencies=[Depends(login_required)])

service = PostService()


@router.get("/", response_model=list[PostOut])
async def read_posts(
    published: str = Query(..., pattern="on|off"),
    limit: int = Query(..., gt=0),
    skip: int = 0,
):
    return await service.read_all(published=published, limit=limit, skip=skip)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostOut)
async def create_post(post: PostIn):
    new_id = await service.create(post)
    return await service.read(new_id)



@router.get("/{id}", response_model=PostOut)
async def read_post(id: int):
    try:
        return await service.read(id)
    except NotFoundPostError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/{id}", response_model=PostOut)
async def update_post(id: int, post: PostUpdateIn):
    try:
        return await service.update(id=id, post=post)
    except NotFoundPostError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    try:
        await service.delete(id)
    except NotFoundPostError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
