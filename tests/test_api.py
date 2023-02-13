from wolt_backend_calculator.api import app
from datetime import datetime
from fastapi.testclient import TestClient
import pytz

client = TestClient(app)

HELSINKI_TZ = pytz.timezone("Europe/Helsinki")
# yes it is absolutely needed to do it like this other yes it plays around with daylight saving time
# and give out non +02:00 format for timezone in ISO format
HELSINKI_NON_RUSH_DT = HELSINKI_TZ.localize(datetime(year=2022, month=1, day=7, hour=15, minute=0))
HELSINKI_RUSH_DT = HELSINKI_TZ.localize(datetime(year=2022, month=1, day=7, hour=17, minute=0))


def test_calculate_delivery_fee_api():
    response = client.post("/deliveries",
                           json={"cart_value": 790, "delivery_distance": 2235, "number_of_items": 4,
                                 "time": "2021-10-12T13:00:00Z"})
    assert response.status_code == 200
    assert response.json() == {
        "delivery_fee": 710
    }

    response = client.post("/deliveries",
                           json={"cart_value": 790, "delivery_distance": 2235, "number_of_items": 4,
                                 "time": "2021-10-12T13:00:00Z", "hello": "world"})
    assert response.status_code == 200
    assert response.json() == {
        "delivery_fee": 710
    }

    response = client.post("/deliveries",
                           json=dict(cart_value=1000, delivery_distance=0, number_of_items=14,
                                     time=HELSINKI_NON_RUSH_DT.isoformat()))
    assert response.status_code == 200
    assert response.json() == {
        "delivery_fee": 820
    }

    response = client.post("/deliveries",
                           json=dict(cart_value=1000, delivery_distance=0, number_of_items=14,
                                     time=HELSINKI_RUSH_DT.isoformat()))
    assert response.status_code == 200
    assert response.json() == {
        "delivery_fee": 984
    }


def test_calculate_delivery_fee_api_invalid_content():
    response = client.post("/deliveries",
                           json={"cart": 790, "delivery_distance": 2235, "number_of_items": 4,
                                 "time": "2021-10-12T13:00:00Z"})
    assert response.status_code == 422

    response = client.post("/deliveries",
                           json={"time": "2021-10-12T13:00:00Z"})
    assert response.status_code == 422

    response = client.post("/deliveries",
                           json={"cart_value": 790, "delivery_distance": 2235, "number_of_items": 4,
                                 "time": "2021-10-12"})
    assert response.status_code == 422

    req_body = dict(cart_value=0, delivery_distance=0, number_of_items=0,
                    time=HELSINKI_NON_RUSH_DT.isoformat())
    response = client.post("/deliveries", json=req_body)
    assert response.status_code == 422
    assert response.json()["detail"] == "Number of items is not a positive integer"

    req_body = dict(cart_value=0, delivery_distance="bad", number_of_items=1,
                    time=HELSINKI_NON_RUSH_DT.isoformat())
    response = client.post("/deliveries", json=req_body)
    assert response.status_code == 422

    response = client.post("/deliveries",
                           json=dict(cart_value=1000, delivery_distance=5, number_of_items=14.7,
                                     time=HELSINKI_NON_RUSH_DT.isoformat()))
    assert response.status_code == 422

    response = client.post("/deliveries",
                           json=dict(cart_value="10", delivery_distance=5.5, number_of_items=14,
                                     time=HELSINKI_NON_RUSH_DT.isoformat()))
    assert response.status_code == 422

    response = client.post("/deliveries",
                           json=dict(cart_value="10", delivery_distance=5, number_of_items=14,
                                     time=HELSINKI_NON_RUSH_DT.isoformat()))
    assert response.status_code == 422

    response = client.post("/deliveries",
                           json=dict(cart_value=10, delivery_distance=-1, number_of_items=14,
                                     time=HELSINKI_NON_RUSH_DT.isoformat()))
    assert response.status_code == 422

    response = client.post("/deliveries",
                           json=dict(cart_value=-1283284324, delivery_distance=2, number_of_items=14,
                                     time=HELSINKI_NON_RUSH_DT.isoformat()))
    assert response.status_code == 422
