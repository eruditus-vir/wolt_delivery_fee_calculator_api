from wolt_backend_calculator.delivery_fee import DeliveryFee, InvalidDeliveryFee
import pytest


def test_delivery_fee_invalid_amount():
    with pytest.raises(InvalidDeliveryFee):
        DeliveryFee(-10)

    with pytest.raises(InvalidDeliveryFee):
        DeliveryFee(-1)

    with pytest.raises(InvalidDeliveryFee):
        DeliveryFee(-1500)

    with pytest.raises(InvalidDeliveryFee):
        DeliveryFee(1600)

    with pytest.raises(InvalidDeliveryFee):
        DeliveryFee(1239023094434)

    with pytest.raises(InvalidDeliveryFee):
        DeliveryFee(-1239023094434)

    with pytest.raises(InvalidDeliveryFee):
        DeliveryFee("2323")

    with pytest.raises(InvalidDeliveryFee):
        DeliveryFee("1")

    with pytest.raises(InvalidDeliveryFee):
        DeliveryFee(0.1)


def test_delivery_fee_valid_amount():
    assert DeliveryFee(100).delivery_fee == 100
    assert DeliveryFee(0).delivery_fee == 0
    assert DeliveryFee(1500).delivery_fee == 1500
    assert DeliveryFee(1499).delivery_fee == 1499


def test_delivery_fee_str():
    assert DeliveryFee(100).__str__() == "€1.00"
    assert DeliveryFee(1433).__str__() == "€14.33"


def test_delivery_fee_todict():
    assert DeliveryFee(100).to_dict()["delivery_fee"] == 100
