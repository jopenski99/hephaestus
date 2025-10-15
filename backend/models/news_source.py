from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class NewsSource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    outlet_name: str = Field(index=True)
    domain: str = Field(unique=True, index=True)
    last_crawled: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})   