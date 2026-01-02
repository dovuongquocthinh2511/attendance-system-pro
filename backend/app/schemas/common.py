from typing import Optional
from pydantic import BaseModel

class ActionResponse(BaseModel):
    """
    Generic response for actions (Create, Update, Delete, etc.)
    """
    msg: str
    id: Optional[int] = None
    state: Optional[str] = None
