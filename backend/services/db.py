from sqlmodel import SQLModel, create_engine, Session
from backend.api.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

async def init_db():
    from backend.models.user import User  # avoid circular imports
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
