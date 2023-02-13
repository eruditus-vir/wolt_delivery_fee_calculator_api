from pydantic import ValidationError

from wolt_backend_calculator.delivery_order import DeliveryOrder
import pytest
from datetime import datetime


def test_delivery_order():
    # these tests are just trying to determine the limit of pydantic BaseModel type checking
    # as we can see, float will still get through
    # hence it is justified that the calculator has all those checks.
    order = DeliveryOrder(cart_value=2133, delivery_distance=10504505, number_of_items=2,
                          time="2021-10-12T13:00:00Z")
    assert order.time.year == 2021


def test_delivery_order_bad():
    # why ValidationError? pydantic BaseModel actually evaluate in its initialization
    # hence all typing passed to calculator will be correct.
    with pytest.raises(ValidationError):
        DeliveryOrder(cart_value="badva", delivery_distance=10504505, number_of_items=1322,
                      time=datetime(year=2022, month=1, day=7, hour=15, minute=0))

    with pytest.raises(ValidationError):
        DeliveryOrder(cart_value="badva", delivery_distance=10504505, number_of_items=1322,
                      time=datetime(year=2022, month=1, day=7, hour=15, minute=0))

    with pytest.raises(ValidationError):
        DeliveryOrder(cart_value=2133, delivery_distance=10504505, number_of_items=1322,
                      time="2012-01-23")
