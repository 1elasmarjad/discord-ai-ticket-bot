from sqlmodel import Field, SQLModel, create_engine

from settings import settings


class Guild(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category_channel_id: int | None


sqlite_file_name = "dev.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=settings.dev_mode)

SQLModel.metadata.create_all(engine)
