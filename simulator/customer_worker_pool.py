import threading
from queue import Queue
from simulator.customer import Customer
from simulator.customer_worker import CustomerWorker
from simulator.action_registry import ActionRegistry
from simulator.metrics import MetricsTracker
from util import yaml_loader

class CustomerWorkerPool:
    def __init__(self, config: dict, metrics: MetricsTracker, action_registry: ActionRegistry):
        self.config    = config
        self.metrics   = metrics
        self.registry  = action_registry

        self.shutdown_event = threading.Event()

                            # key     -> value
        self.customers = {} # user_id -> Customer
        self.queues    = {} # user_id -> Queue
        self.threads   = {} # user_id -> Thread

        print(f"[CustomerWorkerPool] created ")

        self._load_customers()


    def _load_customers(self):
        print(f"[CustomerWorkerPool] loading customers...")

        customers_file = self.config.get("customers_file")
        if not customers_file:
            raise ValueError("Missing 'customers_file' in config.")

        customers = yaml_loader.load_yaml(customers_file).get("customers")
        if not customers:
            raise ValueError("Missing 'customers' in customers_file.")

        for customer in customers:
            user_id = customer.get("user_id")
            email = customer.get("email")
            password = customer.get("password")

            self.customers[user_id] = Customer(email, password, user_id)
            self.queues[user_id] = Queue()

    def run(self):
        print(f"[CustomerWorkerPool] creating customer workers...")
        for i, (user_id, customer) in enumerate(self.customers.items()):
            queue = self.queues[user_id]
            worker = CustomerWorker(
                customer=customer,
                queue=queue,
                action_registry=self.registry,
                metrics=self.metrics,
                shutdown_event=self.shutdown_event
            )
            thread = threading.Thread(target=worker.run, daemon=True)
            self.threads[user_id] = thread
            thread.start()

    def dispatch_action(self, user_id: int, action_name: str):
        """
        Enqueue a single action to the appropriate CustomerWorker.
        """
        if user_id not in self.queues:
            raise ValueError(f"No worker for customer with user ID {user_id}")

        self.queues[user_id].put({
            "action_name": action_name
        })

    def shutdown(self):
        """
        Stops all worker threads, and waits for them to shut down.
        """
        print("[CustomerWorkerPool] Stopping all workers...")
        self.shutdown_event.set()
        for thread in self.threads.values():
            thread.join(timeout=3)
        print("[CustomerWorkerPool] All workers have been stopped.")