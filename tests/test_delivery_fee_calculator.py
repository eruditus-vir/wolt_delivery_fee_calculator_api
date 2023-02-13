import datetime

import pytz
from pydantic import ValidationError

from wolt_backend_calculator.delivery_fee_calculator import *  # will also import constants needed
import pytest
from wolt_backend_calculator.constants import CENT_MULTIPLICATION_CONSTANT

HELSINKI_TZ = pytz.timezone("Europe/Helsinki")
# yes it is absolutely needed to do it like this other yes it plays around with daylight saving time
# and give out non +02:00 format for timezone in ISO format
# once it's localised, the converted back to utc version will be 13 and 15 hour respectively
HELSINKI_NON_RUSH_DT = HELSINKI_TZ.localize(datetime(year=2022, month=1, day=7, hour=15, minute=0))
HELSINKI_RUSH_DT = HELSINKI_TZ.localize(datetime(year=2022, month=1, day=7, hour=17, minute=0))


def test_delivery_fee_calculator_calculate_surcharge_based_on_number_of_items():
    # not really sure if this method is good for testing or not but it seems to make sense
    # however, the bad thing it actually tie the test with the logic, which in a way makes sense
    # test safe number of items
    for i in range(1, MAX_SAFE_NUMBER_OF_ITEMS):
        assert DeliveryFeeCalculator.calculate_surcharge_based_on_number_of_items(i) == 0
    # test non-bulk charges
    for i in range(MAX_SAFE_NUMBER_OF_ITEMS + 1, BULK_CUTOFF_NUMBER_OF_ITEMS):
        number_of_items_to_charge = i - MAX_SAFE_NUMBER_OF_ITEMS
        assert DeliveryFeeCalculator.calculate_surcharge_based_on_number_of_items(
            i) == number_of_items_to_charge * SURCHARGE_PER_EXTRA_ITEM
    # test bulk charges
    assert DeliveryFeeCalculator.calculate_surcharge_based_on_number_of_items(BULK_CUTOFF_NUMBER_OF_ITEMS) == (
            BULK_CUTOFF_NUMBER_OF_ITEMS - MAX_SAFE_NUMBER_OF_ITEMS) * SURCHARGE_PER_EXTRA_ITEM + BULK_FEE
    assert DeliveryFeeCalculator.calculate_surcharge_based_on_number_of_items(BULK_CUTOFF_NUMBER_OF_ITEMS + 5) == (
            BULK_CUTOFF_NUMBER_OF_ITEMS - MAX_SAFE_NUMBER_OF_ITEMS + 5) * SURCHARGE_PER_EXTRA_ITEM + BULK_FEE


def test_delivery_fee_calculator_calculate_surcharge_based_on_number_of_items_bad():
    # test less than 0
    with pytest.raises(InvalidNumberOfItems):
        DeliveryFeeCalculator.calculate_surcharge_based_on_number_of_items(-1)
    # test 0
    with pytest.raises(InvalidNumberOfItems):
        DeliveryFeeCalculator.calculate_surcharge_based_on_number_of_items(0)
    # test float
    with pytest.raises(InvalidNumberOfItems):
        DeliveryFeeCalculator.calculate_surcharge_based_on_number_of_items(0.5)
    # test string
    with pytest.raises(InvalidNumberOfItems):
        DeliveryFeeCalculator.calculate_surcharge_based_on_number_of_items("1")
    # # test REALLY large number which should exceed integer limit
    # # this is not really applicable with python
    # with pytest.raises(InvalidNumberOfItems):
    #     DeliveryFeeCalculator.calculate_surcharge_based_on_number_of_items(12309540545453)


def test_delivery_fee_calculator_calculate_fee_based_on_distance():
    # I could make it the same as number of items but I find the effort to write such item to be more mentally
    # taxing than what writing tests should be
    assert DeliveryFeeCalculator.calculate_fee_based_on_distance(0) == INITIAL_COST_BASED_DISTANCE
    assert DeliveryFeeCalculator.calculate_fee_based_on_distance(100) == INITIAL_COST_BASED_DISTANCE
    assert DeliveryFeeCalculator.calculate_fee_based_on_distance(500) == INITIAL_COST_BASED_DISTANCE
    assert DeliveryFeeCalculator.calculate_fee_based_on_distance(999) == INITIAL_COST_BASED_DISTANCE
    assert DeliveryFeeCalculator.calculate_fee_based_on_distance(
        1000) == INITIAL_COST_BASED_DISTANCE
    assert DeliveryFeeCalculator.calculate_fee_based_on_distance(
        1001) == INITIAL_COST_BASED_DISTANCE + ADD_COST_BASED_DISTANCE
    assert DeliveryFeeCalculator.calculate_fee_based_on_distance(
        1499) == INITIAL_COST_BASED_DISTANCE + ADD_COST_BASED_DISTANCE
    assert DeliveryFeeCalculator.calculate_fee_based_on_distance(
        1500) == INITIAL_COST_BASED_DISTANCE + ADD_COST_BASED_DISTANCE
    assert DeliveryFeeCalculator.calculate_fee_based_on_distance(
        1501) == INITIAL_COST_BASED_DISTANCE + ADD_COST_BASED_DISTANCE * 2


def test_delivery_fee_calculator_calculate_fee_based_on_distance_bad():
    # test less than 0
    with pytest.raises(InvalidDeliveryDistance):
        DeliveryFeeCalculator.calculate_fee_based_on_distance(-1)
    # i feel like maybe i could handle this case better but not sure how.
    with pytest.raises(InvalidDeliveryDistance):
        DeliveryFeeCalculator.calculate_fee_based_on_distance(-13849354895945855)
    # test float
    with pytest.raises(InvalidDeliveryDistance):
        DeliveryFeeCalculator.calculate_fee_based_on_distance(0.5)
    # test string
    with pytest.raises(InvalidDeliveryDistance):
        DeliveryFeeCalculator.calculate_fee_based_on_distance("1")
    # in java this is probably useful but for python, it's unbounded
    # which raised the question, should there be upper limit
    # with pytest.raises(InvalidDeliveryDistance):
    #     DeliveryFeeCalculator.calculate_fee_based_on_distance(12309540545453)


def test_delivery_fee_calculator_calculate_surcharge_based_on_cart_value():
    #
    val = 0 * CENT_MULTIPLICATION_CONSTANT
    assert DeliveryFeeCalculator.calculate_surcharge_based_on_cart_value(val) == 10 * CENT_MULTIPLICATION_CONSTANT
    val = 15 * CENT_MULTIPLICATION_CONSTANT
    assert DeliveryFeeCalculator.calculate_surcharge_based_on_cart_value(val) == 0
    val = 1 * CENT_MULTIPLICATION_CONSTANT
    assert DeliveryFeeCalculator.calculate_surcharge_based_on_cart_value(val) == 9 * CENT_MULTIPLICATION_CONSTANT
    # this should not be a case.
    val = int(0.01 * CENT_MULTIPLICATION_CONSTANT)
    assert DeliveryFeeCalculator.calculate_surcharge_based_on_cart_value(val) == int(
        9.99 * CENT_MULTIPLICATION_CONSTANT)
    val = 10 * CENT_MULTIPLICATION_CONSTANT
    assert DeliveryFeeCalculator.calculate_surcharge_based_on_cart_value(val) == 0


def test_delivery_fee_calculator_calculate_surcharge_based_on_cart_value_bad():
    # test less than 0
    with pytest.raises(InvalidCartValue):
        DeliveryFeeCalculator.calculate_surcharge_based_on_cart_value(-1)
    # test float
    with pytest.raises(InvalidCartValue):
        DeliveryFeeCalculator.calculate_surcharge_based_on_cart_value(0.5)
    # test string
    with pytest.raises(InvalidCartValue):
        DeliveryFeeCalculator.calculate_surcharge_based_on_cart_value("1")


def test_delivery_fee_calculator_calculate_fee_multiplication_value_based_on_time():
    time = datetime(year=2022, month=1, day=1, hour=3, minute=0)
    assert DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time(time) == 1.0

    time = HELSINKI_NON_RUSH_DT
    assert DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time(time) == 1.0

    time = datetime(year=2022, month=1, day=7, hour=15, minute=0)
    assert DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time(time) == RUSH_HOUR_CONSTANT

    time = HELSINKI_RUSH_DT
    assert DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time(time) == RUSH_HOUR_CONSTANT

    time = datetime(year=2022, month=1, day=7, hour=18, minute=59, second=59, )
    assert DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time(time) == RUSH_HOUR_CONSTANT

    time = HELSINKI_TZ.localize(datetime(year=2022, month=1, day=7, hour=20, minute=59, second=59))
    assert DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time(time) == RUSH_HOUR_CONSTANT

    time = HELSINKI_TZ.localize(datetime(year=2022, month=1, day=7, hour=21, minute=0, second=0))
    assert DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time(time) == 1.0


def test_delivery_fee_calculator_calculate_fee_multiplication_value_based_on_time_bad():
    with pytest.raises(InvalidTime):
        DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time("2021-10-12T13:00:00Z")

    with pytest.raises(InvalidTime):
        DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time(-1)

    with pytest.raises(InvalidTime):
        DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time(3094590509590509590.23)


def test_delivery_fee_calculator_calculate_delivery_fee():
    # why no bad version of this function? pydantic BaseModel actually evaluate in its initialization
    # hence all typing for evaluated input is correct
    order = DeliveryOrder(cart_value=150045, delivery_distance=10504505, number_of_items=1322,
                          time=datetime(year=2022, month=1, day=7, hour=19, minute=0))
    assert DeliveryFeeCalculator.calculate_delivery_fee(order).delivery_fee == 0

    order = DeliveryOrder(cart_value=1, delivery_distance=10504505, number_of_items=1322,
                          time=HELSINKI_NON_RUSH_DT)
    assert DeliveryFeeCalculator.calculate_delivery_fee(order).delivery_fee == MAXIMUM_DELIVERY_FEE

    order = DeliveryOrder(cart_value=790, delivery_distance=2235, number_of_items=4,
                          time=HELSINKI_RUSH_DT)
    assert DeliveryFeeCalculator.calculate_delivery_fee(order).delivery_fee == 852

    order = DeliveryOrder(cart_value=790, delivery_distance=2235, number_of_items=6,
                          time=HELSINKI_RUSH_DT)
    assert DeliveryFeeCalculator.calculate_delivery_fee(order).delivery_fee == 972

    order = DeliveryOrder(cart_value=1000, delivery_distance=0, number_of_items=14,
                          time=datetime(year=2022, month=1, day=7, hour=15, minute=0))
    assert DeliveryFeeCalculator.calculate_delivery_fee(order).delivery_fee == 984

    order = DeliveryOrder(cart_value=1000, delivery_distance=0, number_of_items=14,
                          time=HELSINKI_NON_RUSH_DT)
    assert DeliveryFeeCalculator.calculate_delivery_fee(order).delivery_fee == 820


def test_delivery_fee_calculator_calculate_delivery_fee_bad():
    # can only test exact type only, pydantic BaseModel handle type validation for order
    with pytest.raises(InvalidCartValue):
        order = DeliveryOrder(cart_value=-1, delivery_distance=10504505, number_of_items=1322,
                              time=datetime(year=2022, month=1, day=7, hour=15, minute=0,
                                            tzinfo=pytz.timezone('Europe/Helsinki')))
        DeliveryFeeCalculator.calculate_delivery_fee(order)

    with pytest.raises(InvalidCartValue):
        order = DeliveryOrder(cart_value=-129323, delivery_distance=10504505, number_of_items=1322,
                              time=datetime(year=2022, month=1, day=7, hour=15, minute=0,
                                            tzinfo=pytz.timezone('Europe/Helsinki')))
        DeliveryFeeCalculator.calculate_delivery_fee(order)

    with pytest.raises(InvalidDeliveryDistance):
        order = DeliveryOrder(cart_value=0, delivery_distance=-23, number_of_items=1322,
                              time=datetime(year=2022, month=1, day=7, hour=15, minute=0,
                                            tzinfo=pytz.timezone('Europe/Helsinki')))
        DeliveryFeeCalculator.calculate_delivery_fee(order)

    with pytest.raises(InvalidNumberOfItems):
        order = DeliveryOrder(cart_value=0, delivery_distance=0, number_of_items=0,
                              time=datetime(year=2022, month=1, day=7, hour=15, minute=0,
                                            tzinfo=pytz.timezone('Europe/Helsinki')))
        DeliveryFeeCalculator.calculate_delivery_fee(order)
