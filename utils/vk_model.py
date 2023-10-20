from typing import Optional, List, Dict

from pydantic import BaseModel


class VKResponse(BaseModel):

    response: Optional[List[Dict]] = None


class PersonID(BaseModel):

    id: Optional[int]

