import time
import uuid

from queue import Empty, Queue
from simulator.customer_worker_pool import CustomerWorkerPool

class Worker:
    def __init__(self, customer_pool: CustomerWorkerPool, queue: Queue, work_completion_callback, shutdown_event=None):
        self.id = uuid.uuid4()
        self.customer_pool = customer_pool
        self.queue = queue
        self.last_used = time.time()
        self.active = True
        self._on_done = work_completion_callback
        self.shutdown_event = shutdown_event

        print(f"[{self}] created")

    def run(self):
        try:
            while not (self.shutdown_event and self.shutdown_event.is_set()) and self.active:
                try:
                    message = self.queue.get(timeout=1)
                    user_id = message["user_id"]
                    sequence = message["sequence"]
                    self._execute_sequence(user_id, sequence)
                    self._on_done(self)
                except Empty:
                    continue
        except Exception as e:
            print(f"[{self}] crashed: {e}")

    def _execute_sequence(self, user_id: int, sequence: list):
        for action in sequence:
            if not self.active:
                break

            action_name = action["name"]
            delay = action.get("delay", 0)

            self.customer_pool.dispatch_action(user_id, action_name)

            if delay > 0:
                time.sleep(delay)

            self.last_used = time.time()

    def __repr__(self):
        return f"<TestGeneratorWorker {self.id}>"