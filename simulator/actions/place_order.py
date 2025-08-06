# pylint: disable=duplicate-code
import random

import requests
import json
from simulator.customer import Customer

PLACE_ORDER_API = "post"

class Behaviour:
    def __init__(self):
        self.order_id = 0

    def get_endpoint(self, customer, config):
        return f"{config.get("base_url")}{PLACE_ORDER_API}"

    def get_method(self, customer: Customer, config: dict):
        """
        Returns HTTP method
        :param self:
        :param customer: Customer object
        :param config: Action configuration
        :return: dict
        """
        return "POST"

    def get_header(self, customer: Customer, config: dict):
        """
        Returns HTTP header dictionary
        :param self:
        :param customer: Customer object
        :param config: Action configuration
        :return: dict
        """
        auth_key = config.get("auth_key", "")
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_key}"
        }

    def get_body(self, customer: Customer, config: dict):
        """
        Returns HTTP header dictionary
        :param self:
        :param customer: Customer object
        :param config: Action configuration
        :return: dict or None
        """

        product_id = "default_id"
        quantity = 1
        self.order_id = random.randint(0, 3000000)

        return {
            "email": customer.email,
            "password": customer.password,
            "user_id": customer.user_id,
            "order_id": self.order_id,
            "product_id": product_id,
            "quantity": quantity
        }

    def process_response(self, customer: Customer, response: requests.Response, config: dict):
        """
        Handles HTTP response and updates customer if needed
        :param self:
        :param customer: Customer object
        :param response: HTTP Response object
        :param config: Action configuration
        """
        print(f"[{customer}] received response : status code='{response.status_code}', body='{response.json()}'")

        status_code = response.status_code
        if status_code == 200:
            body_str = response.request.body.decode("utf-8")
            body_data = json.loads(body_str)

            customer.placed_orders.append(body_data.get("order_id"))
            print(f"[{customer}] placed order success, open orders : {customer.placed_orders}")
