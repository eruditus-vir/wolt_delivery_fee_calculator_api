from fastapi import FastAPI, HTTPException
from wolt_backend_calculator.delivery_order import DeliveryOrder
from wolt_backend_calculator.delivery_fee_calculator import DeliveryFeeCalculator, InvalidDeliveryOrderValue
import logging

app = FastAPI()


@app.post("/deliveries")
async def calculate_delivery_fee_api(delivery_order: DeliveryOrder):
    try:
        delivery_fee = DeliveryFeeCalculator.calculate_delivery_fee(delivery_order)
    except InvalidDeliveryOrderValue as e:
        # https://stackoverflow.com/questions/6123425/rest-response-code-for-invalid-data
        # 422 Unprocessable Entity - https://www.rfc-editor.org/rfc/rfc4918#section-11.2
        # not really sure if I should be logging on server for something that's client's fault
        raise HTTPException(status_code=422, detail=e.__str__())
    except Exception as e:  # unknown error mostly from server side implementation
        logging.error("Error occur while processing request with following input {}\nError Line: {}".format(
            delivery_order.json(),
            e
        ))
        raise HTTPException(status_code=500)  # 500 Internal Server Error
    return delivery_fee.to_dict()
