from pydantic import BaseModel
from typing import Optional

# Common properties for both Create and Read
class MarketBase(BaseModel):
    name: str
    address: Optional[str] = None

# Properties to receive on Market creation
class MarketCreate(MarketBase):
    pass # For now, we only need name and address

# Properties to return to the client (Response)
class Market(MarketBase):
    id: int

    class Config:
        # This allows Pydantic to read data from SQLAlchemy models
        from_attributes = True