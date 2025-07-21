from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    user_id: str
    username: str
    email: Optional[str] = None
    organization: Optional[str] = None
    permissions: List[str] = [] 