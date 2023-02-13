from wolt_backend_calculator.delivery_order import DeliveryOrder
from wolt_backend_calculator.delivery_fee import DeliveryFee
from wolt_backend_calculator.constants import CART_VALUE_SURCHARGE, MAXIMUM_DELIVERY_FEE
from wolt_backend_calculator.constants import RUSH_HOUR_CONSTANT, INITIAL_DISTANCE, INITIAL_COST_BASED_DISTANCE
from wolt_backend_calculator.constants import ADD_COST_BASED_DISTANCE, DISTANCE_PER_ADD_COST, SURCHARGE_PER_EXTRA_ITEM
from wolt_backend_calculator.constants import BULK_CUTOFF_NUMBER_OF_ITEMS, BULK_FEE, MAX_SAFE_NUMBER_OF_ITEMS
from wolt_backend_calculator.constants import CART_VALUE_CUTOFF_FOR_FREE_DELIVERY_FEE
from datetime import datetime
import math
import logging
import pytz


# these are basic classes used to simply distinguish Client input exceptions vs Server input exceptions in api
# no implementation was done because the logic the author went for doesn't demand for it yet
class InvalidDeliveryOrderValue(Exception):
    pass


class InvalidDeliveryDistance(InvalidDeliveryOrderValue):
    pass


class InvalidNumberOfItems(InvalidDeliveryOrderValue):
    pass


class InvalidCartValue(InvalidDeliveryOrderValue):
    pass


class InvalidTime(InvalidDeliveryOrderValue):
    pass


class DeliveryFeeCalculator:
    """
    All calculation methods are static.
    All calculation methods except calculate_delivery_fee will not be subjected to MAXIMUM_DELIVERY_FEE restriction
    This is by design choice because api will only be using calculate delivery fee and not any other methods
    Potential naming issue: fee vs surcharge probably mean the same thing in this context.
    """

    @staticmethod
    def calculate_surcharge_based_on_number_of_items(number_of_items: int) -> int:
        if not isinstance(number_of_items, int) or number_of_items <= 0:  # this ordering is important
            raise InvalidNumberOfItems("Number of items is not a positive integer")
        elif number_of_items <= MAX_SAFE_NUMBER_OF_ITEMS:
            return 0
        # if 5, it's 5-4 = 1, hence need to use 4
        number_of_extra_items = number_of_items - MAX_SAFE_NUMBER_OF_ITEMS
        fee = SURCHARGE_PER_EXTRA_ITEM * number_of_extra_items
        if number_of_items >= BULK_CUTOFF_NUMBER_OF_ITEMS:
            fee += BULK_FEE
        return fee

    @staticmethod
    def calculate_fee_based_on_distance(delivery_distance: int) -> int:
        if not isinstance(delivery_distance, int) or delivery_distance < 0:
            # not really sure if distance 0 should work
            raise InvalidDeliveryDistance("Delivery Distance must be positive or zero integer!")
        fee = INITIAL_COST_BASED_DISTANCE
        if delivery_distance <= INITIAL_DISTANCE:
            return fee
        distance_over_initial = delivery_distance - INITIAL_DISTANCE
        # I'm quite worried about floating point error tbh but I'll write some tests to cover that
        number_of_add_cost = int(math.ceil(distance_over_initial / DISTANCE_PER_ADD_COST))
        fee += number_of_add_cost * ADD_COST_BASED_DISTANCE
        return fee

    @staticmethod
    def calculate_surcharge_based_on_cart_value(cart_value: int) -> int:
        if not isinstance(cart_value, int) or cart_value < 0:
            # maybe u are ordering things that are free so cart val can be 0.
            raise InvalidCartValue("Cart value is not a positive or zero integer")
        if cart_value < CART_VALUE_SURCHARGE:
            return CART_VALUE_SURCHARGE - cart_value

        return 0

    @staticmethod
    def calculate_fee_multiplication_value_based_on_time(time: datetime) -> float:
        """
        simply check time and return multiplication value for rush hour, the default is always 1.0
        :param time:
        :return:
        """
        if not isinstance(time, datetime):
            raise InvalidTime("time is not an instance of datetime object")
        # ensure time is in utc, assume that no time zone specified means utc
        if time.tzinfo is not None:
            time = time.astimezone(pytz.utc)
        else:
            # note: we could also raise error for this but it might be too strict
            logging.warning("Since time's timezone is not specified, calculation api assume time given is in UTC.")
        # when Monday is 0 and Sunday is 6, hence friday is 4
        # for hour, 3pm - 7pm = 15-19
        if time.weekday() == 4 and 15 <= time.hour < 19:  # exclude 19.00
            return RUSH_HOUR_CONSTANT
        return 1.0

    @staticmethod
    def calculate_delivery_fee(delivery_order: DeliveryOrder) -> DeliveryFee:
        """
        calculate delivery fee based on specification.
        :param delivery_order:
        :return:
        """
        """
        TODO: figure out if there's a better way to do this early return
        A way which if I find to be decent but not that much better is to basically put these functions in loop
        then run through them one by one, if one of them return an instance of DeliveryFee, you can return it
        right away, meaning anyone of calculate functions can break the loop and return right away
        However, the testing might be too complicated because the return of calculate becomes
        Union[float, DeliveryFee] which for a simple app, is kinda ugly
        
        Another way is to simply remove all type and value checking into DeliveryOrder itself as isValid function 
        this way we remove all type checking from calculator class.
        
        I still believe that the first method is better
        """
        fee = DeliveryFeeCalculator.calculate_surcharge_based_on_cart_value(delivery_order.cart_value)
        # we simply let calculate_surcharge_based_on_cart_value do the checking for us first
        # this logic still have no place in that function after a lot of deliberation.
        if delivery_order.cart_value >= CART_VALUE_CUTOFF_FOR_FREE_DELIVERY_FEE:
            return DeliveryFee(0)
        fee += DeliveryFeeCalculator.calculate_fee_based_on_distance(delivery_order.delivery_distance)
        fee += DeliveryFeeCalculator.calculate_surcharge_based_on_number_of_items(delivery_order.number_of_items)
        fee *= DeliveryFeeCalculator.calculate_fee_multiplication_value_based_on_time(delivery_order.time)
        # the author takes the liberty to ceil the delivery fee
        return DeliveryFee(min(MAXIMUM_DELIVERY_FEE, int(math.ceil(fee))))
