from typing import Optional, Union

from pydantic import BaseModel


class TokenBase(BaseModel):
    token: Union[str, None]


class TokenCreate(TokenBase):
    pass


class Token(TokenBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True