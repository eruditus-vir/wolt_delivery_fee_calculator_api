from pydantic import BaseModel, StrictInt
from datetime import datetime


class DeliveryOrder(BaseModel):
    cart_value: StrictInt
    delivery_distance: StrictInt
    number_of_items: StrictInt
    time: datetime  # format should be according to ISO 8601:  https://fastapi.tiangolo.com/tutorial/extra-data-types/
