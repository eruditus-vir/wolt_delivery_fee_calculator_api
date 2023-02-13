from wolt_backend_calculator.constants import MINIMUM_DELIVERY_FEE, MAXIMUM_DELIVERY_FEE


class InvalidDeliveryFee(Exception):
    def __int__(self,
                fee):
        self.fee = fee
        msg = "{} is outside the valid fee range of ({}, {})".format(fee, MINIMUM_DELIVERY_FEE, MAXIMUM_DELIVERY_FEE)
        super(InvalidDeliveryFee, self).__int__(msg)


class DeliveryFee:
    def __init__(self, delivery_fee: int):
        if not isinstance(delivery_fee, int):
            raise InvalidDeliveryFee("Only Integer is expected for delivery fee")
        if not (MINIMUM_DELIVERY_FEE <= delivery_fee <= MAXIMUM_DELIVERY_FEE):
            raise InvalidDeliveryFee(delivery_fee)
        self.delivery_fee = delivery_fee

    def __str__(self):
        return "€{:.2f}".format(self.delivery_fee / 100.)

    def to_dict(self):
        return {
            "delivery_fee": self.delivery_fee
        }
