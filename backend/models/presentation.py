from pydantic import BaseModel
import json

class PresentationCreate(BaseModel):
    topic: str
    purpose: str
    audience: str
   