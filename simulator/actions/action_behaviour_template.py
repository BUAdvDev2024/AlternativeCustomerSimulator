# pylint: disable=duplicate-code

import requests
from simulator.customer import Customer

class Behaviour:
    def __init__(self):
        self.order_id = 0

    # pyright: reportStaticMethod=true
    def get_endpoint(self, customer: Customer, config: dict):
        return config.get("base_url")

    # pyright: reportStaticMethod=true
    def get_method(self, customer: Customer, config: dict):
        """
        Returns HTTP method
        :param customer: Customer object
        :param config: Action configuration
        :return: dict
        """
        return "POST"

    def get_header(self, customer: Customer, config: dict):
        """
        Returns HTTP header dictionary
        :param customer: Customer object
        :param config: Action configuration
        :return: dict
        """
        return {
            "Content-Type": "application/json"
        }

    def get_body(self, customer: Customer, config: dict):
        """
        Returns HTTP header dictionary
        :param customer: Customer object
        :param config: Action configuration
        :return: dict or None
        """
        product_id = "default_id"
        quantity = 1
        self.order_id += 1

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
        :param customer: Customer object
        :param response: HTTP Response object
        :param config: Action configuration
        """

        print(f"[{customer}] received response : status code='{response.status_code}', body='{response.json()}',\nrequest.body='{response.request.body}'")