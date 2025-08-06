import requests
from queue import Empty, Queue

from simulator.action_registry import ActionRegistry
from simulator.customer import Customer
from simulator.metrics import MetricsTracker


class CustomerWorker:
    def __init__(self, customer: Customer, queue: Queue, action_registry: ActionRegistry, metrics: MetricsTracker, shutdown_event=None):
        self.customer = customer
        self.queue = queue
        self.registry = action_registry
        self.metrics = metrics
        self.shutdown_event = shutdown_event

        print(f"[{self}] started")

    def run(self):
        try:
            # Worker loop : read from queue
            while not (self.shutdown_event and self.shutdown_event.is_set()):
                try:
                    message = self.queue.get(timeout=1)
                    self._execute_action(message.get("action_name"))
                except Empty:
                    continue
        except Exception as e:
            print(f"[{self}] crashed: {e}")

    def _execute_action(self, action_name: str):
        try:
            action = self.registry.get(action_name)
            action_config = action.get("config")
            action_behaviour = action.get("behaviour")

            endpoint = action_behaviour.get_endpoint(self.customer, action_config)
            method = action_behaviour.get_method(self.customer, action_config)
            headers = action_behaviour.get_header(self.customer, action_config)
            body = action_behaviour.get_body(self.customer, action_config)

            print(f"[{self}] Sending request: {method} {endpoint} | Body: {body}")

            response = requests.request(
                method=method,
                url=endpoint,
                headers=headers,
                json=body,
                timeout=10
            )

            # Let action behaviour process response and update customer object
            action_behaviour.process_response(self.customer, response, action_config)

            # Update metrics
            if response.status_code == 200:
                self.metrics.log_success(action_name, self.customer.user_id)
            else:
                self.metrics.log_failure(action_name, self.customer.user_id)

        except Exception as e:
            print(f"[{self}] Error in action '{action_name}': {e}")
            self.metrics.log_failure(action_name, self.customer.user_id)

    def __repr__(self):
        return f"<CustomerWorker {self.customer.user_id}>"