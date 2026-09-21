from pydantic import BaseModel

class OutlineItem(BaseModel):
    id: int
    title: str

class OutlineUpdate(BaseModel):
    outline: list[OutlineItem]