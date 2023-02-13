# Wolt's Assignment: Delivery Fee Calculator (Backend)

Note: the task API is at path "/deliveries" and required post method. "/docs" path can still be used for swagger to show the API information.

Currently, this app is running online at ec2-44-204-64-243.compute-1.amazonaws.com port 8000.

Please do not spam it because it's running on a poor free-tier ec2 machine that I'm also using for other projects.

#### Table of content

- [Task](#task)
- [Stack Selected](#stack-selected)
- [Tasks](#tasks)
- [Rules for calculation](#rules-for-calculation)
- [Questions to test writer](#questions-to-test-writer)
- [Implementation](#implementation)
- [Installation](#installation)
- [Running](#running)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with
markdown-toc</a></i></small>

## Task

Build an HTTP API which could be used for calculating the delivery fee.

## Tech Stack Selected

Python - FastAPI, pytest, poetry as package manager

For specific refer to pyproject.toml

## Tasks

0. set up poetry (DONE)
1. Write tests for DeliveryFee (DONE)
2. Write tests for DeliveryFeeCalculator (DONE)
3. Write logic for DeliveryFeeCalculator (DONE)
4. Write tests for FastAPI (DONE)
5. Integrate FastAPI logic (DONE)
6. Write Dockerfile for deployment testing

## Rules for calculation

Rules for calculating a delivery fee (copied from assignment github please skip)

- If the cart value is less than 10€, a small order surcharge is added to the delivery price. The surcharge is the
  difference between the cart value and 10€. For example if the cart value is 8.90€, the surcharge will be 1.10€.
- A delivery fee for the first 1000 meters (=1km) is 2€. If the delivery distance is longer than that, 1€ is added for
  every additional 500 meters that the courier needs to travel before reaching the destination. Even if the distance
  would be shorter than 500 meters, the minimum fee is always 1€.
    - Example 1: If the delivery distance is 1499 meters, the delivery fee is: 2€ base fee + 1€ for the additional 500 m
      => 3€
    - Example 2: If the delivery distance is 1500 meters, the delivery fee is: 2€ base fee + 1€ for the additional 500 m
      => 3€
    - Example 3: If the delivery distance is 1501 meters, the delivery fee is: 2€ base fee + 1€ for the first 500 m + 1€
      for the second 500 m => 4€
- If the number of items is five or more, an additional 50 cent surcharge is added for each item above and including the
  fifth item. An extra "bulk" fee applies for more than 12 items of 1,20€
    - Example 1: If the number of items is 4, no extra surcharge
    - Example 2: If the number of items is 5, 50 cents surcharge is added
    - Example 3: If the number of items is 10, 3€ surcharge (6 x 50 cents) is added
    - Example 4: If the number of items is 13, 5,70€ surcharge is added ((9 * 50 cents) + 1,20€)
- The delivery fee can never be more than 15€, including possible surcharges.
- The delivery is free (0€) when the cart value is equal or more than 100€.
- During the Friday rush (3 - 7 PM UTC), the delivery fee (the total fee including possible surcharges) will be
  multiplied by 1.2x. However, the fee still cannot be more than the max (15€).

## Questions to test writer

While writing tests, I came across a various questions and therefore leave this for the one writing
the company giving this assignment.

1. While it is easy to write minimum boundary for various items, maximum boundary is not clearly defined.
    1. For example, what is the maximum delivery distance? what is the maximum number of items?
    2. For implementation, the author allow the value to be as much as the python language allowed.
    3. If the error is due to this maxmimum boundary, the server should respond with 500 since it was not able to handle
       the incoming request.
    4. This is an intentional bug because the company did not clearly define the maximum boundary.
2. What would be the best way to represent certain data fields?
    1. Because fee is all in cent (aka euro * 100), the author took the liberty to define 100 as
       CENT_MULTIPLICATION_CONSTANT
    2. this raises potential issue in term of floating point error but for the sake of readibility the author keep this
       as is.
3. Is 15-19 inclusive or exclusive for rush hour in term of ending?
    1. In my current implementation, once 19:00:00 is hit, the rush hour is over and the fee will not be multiplied by
       1.2
4. Possible improvement
    1. In current iteration, I raise incorrect exception of delivery fee, distance, and other fields as custom error
       class. This could be changed to TypeError instead.
    2. Maybe more tests on API function.

## Implementation

All implementation code is in "wolt_backend_calculator" folder and all tests are in "tests" folder.

Here is a few explanations for each class implementation:

1. Request body are modelled as DeliveryOrder which inherit from pyndantic.Basemodel.
    1. It is necessary for its body field to be StrictInt because otherwise "1" or 1.1 might be shaved to 1.
    2. It makes it easier to test
    3. Time format should be ISO, timezone will be taken into account if given.
2. Output class is DeliveryFee
    1. it has to_dict function to be used as a response body
3. The most important class is DeliveryFeeCalculator which only has static methods
    1. The choice to make it basically a static class is I simply see no need to
    2. The api will only use 1 function: calculate_delivery_fee
    3. Other functions are there for easier testing and ease of readability.
    4. Why not just use functions? Because I find classes and abstractions to be beautiful. This can be seen by custom
       exceptions.
        1. Now the issue of using custom exceptions with inheritance has its own issue when it comes to testing with
           pytest.
        2. For example, with pytest.raises() forces exact exception matching which make testing with
           InvalidDeliveryOrderValue only possible indirectly in api level.

Following is some notes about datetime

1. Datetime and timezone is a tricky subject for testing rush hour
    1. "2022-1-7T17:00:00+02:00" is basically 15:00 utc
    2. In testing, this can be confusing because we would have to initialize 19:00 datetime then add the pytz timezone of desired location and then
       localize it. Only then will the time be put as "2022-1-7T19:00:00+02:00" and will be "2022-1-7T17:00:00+00:00" 

## Installation

1. Install poetry on your system (brew, curl, wget, etc) (preferably 1.3.4 version but newer should not be a problem)
2. run "poetry install --no-interaction --no-ansi -vvv"

Alternatively, you can build a docker image for running.
change tag name to appropriate name and it's ok to remove --no-cache
> docker build --no-cache -t wolt .

## Running

To run the backend application, run the following
> poetry run uvicorn wolt_backend_calculator.api:app

Alternatively run it using docker.
> docker run -p 8000:8000 wolt

