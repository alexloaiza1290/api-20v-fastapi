from pydantic import BaseModel, Field

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=20)
    content: str = Field(..., min_length=1, max_length=255)