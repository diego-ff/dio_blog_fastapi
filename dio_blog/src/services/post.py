from databases.interfaces import Record
from database import database
from models.post import posts
from exceptions import NotFoundPostError
from schemas.post import PostIn, PostUpdateIn

class PostService:
    async def read_all(
        self,
        published: bool | str | None = None,
        limit: int = 10,
        skip: int = 0
    ) -> list[Record]:
        """
        Retorna todos os posts, com suporte a filtro 'published'.
        Se published não for informado, retorna todos.
        """
        query = posts.select()

        # ✅ Converte 'on', 'true', '1' para True e 'off', 'false', '0' para False
        if isinstance(published, str):
            if published.lower() in ["true", "1", "on", "yes"]:
                published = True
            elif published.lower() in ["false", "0", "off", "no"]:
                published = False
            else:
                published = None

        # ✅ Aplica o filtro apenas se for True/False
        if published is not None:
            query = query.where(posts.c.published == published)

        query = query.limit(limit).offset(skip)
        return await database.fetch_all(query)

    async def create(self, post: PostIn) -> int:
        command = posts.insert().values(
            title=post.title,
            content=post.content,
            published_at=post.published_at,
            published=post.published,
        )
        return await database.execute(command)

    async def read(self, id: int) -> Record:
        return await self.__get_by_id(id)

    async def update(self, id: int, post: PostUpdateIn) -> Record:
        total = await self.count(id)
        if not total:
            raise NotFoundPostError

        data = post.model_dump(exclude_unset=True)
        command = posts.update().where(posts.c.id == id).values(**data)
        await database.execute(command)

        return await self.__get_by_id(id)

    async def delete(self, id: int) -> None:
        command = posts.delete().where(posts.c.id == id)
        await database.execute(command)

    async def count(self, id: int) -> int:
        query = "SELECT COUNT(id) AS total FROM posts WHERE id = :id"
        result = await database.fetch_one(query, {"id": id})
        return result.total

    async def __get_by_id(self, id: int) -> Record:
        query = posts.select().where(posts.c.id == id)
        post = await database.fetch_one(query)
        if not post:
            raise NotFoundPostError
        return post
