from pydantic import BaseModel


class RequestDeliveries(BaseModel):
    type: str
    data: str
