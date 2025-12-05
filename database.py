import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Field, SQLModel, func, select
from datetime import datetime
from settings import settings


class Guild(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category_channel_id: int | None

    created_at: datetime = Field(default_factory=datetime.now)


class TicketChannel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    guild_id: int = Field(foreign_key="guild.id")
    ticket_number: int
    user_id: int

    created_at: datetime = Field(default_factory=datetime.now)
    closed_at: datetime | None = None

    @classmethod
    async def get_largest_ticket_number(cls, session: AsyncSession, guild_id: int):
        result = await session.exec(
            select(func.max(TicketChannel.ticket_number)).where(
                TicketChannel.guild_id == guild_id
            )
        )

        return result.one() or 0


sqlite_file_name = "dev.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

engine = create_async_engine(sqlite_url, echo=settings.dev_mode)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_db_and_tables())
