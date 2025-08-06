import random
import threading
import time

from generator.worker import Worker
from queue import Queue
from simulator.customer_worker_pool import CustomerWorkerPool

class ActionGenerator:
    def __init__(self, user_ids: list[int], customer_worker_pool: CustomerWorkerPool, config: dict):
        self.user_ids = user_ids
        self.customer_worker_pool = customer_worker_pool

        self.free_workers = set()
        self.busy_workers = set()
        self.all_workers = set()

        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()

        self._load_test_script(config)

    def _load_test_script(self, config: dict):
        self.min_workers = config.get("min_workers", 3)
        self.max_workers = config.get("max_workers", 10)
        self.keep_alive = config.get("keep_alive", 5)
        self.generate_rate = config.get("generate_rate", 1)
        self.sequences = config.get("sequences", [])

    def _start_worker(self):
        queue  = Queue()
        worker = Worker(self.customer_worker_pool, queue, self._on_worker_done, self.shutdown_event)
        thread = threading.Thread(target=worker.run, daemon=True)
        thread.start()

        self.free_workers.add(worker)
        self.all_workers.add(worker)

    def _assign_work(self, user_id: int, sequence: dict):
        if not self.free_workers:
            return False

        worker = self.free_workers.pop()
        self.busy_workers.add(worker)
        worker.queue.put({
            "user_id": user_id,
            "sequence": sequence
        })
        worker.last_used = time.time()

        return True

    def _on_worker_done(self, worker: Worker):
        with self.lock:
            self.busy_workers.discard(worker)
            self.free_workers.add(worker)
            worker.last_used = time.time()

    def _terminate_idle_workers(self):
        now = time.time()
        with self.lock:
            expired = [w for w in self.free_workers if now - w.last_used > self.keep_alive]
            for w in expired:
                print(f"[{self}] Shutting down idle worker: {w}")
                self.free_workers.remove(w)
                self.all_workers.remove(w)
                w.active = False

    def run(self):
        # Spawn minimum number of workers first
        print(f"[{self}] Starting with {self.min_workers} workers...")
        for _ in range(self.min_workers):
            self._start_worker()

        # Work out the rate of sequences to generate every second
        sequence_rate = 1 / self.generate_rate

        while not (self.shutdown_event and self.shutdown_event.is_set()):
            start_time = time.time()

            # Clean up any idle workers
            self._terminate_idle_workers()

            # Choose random user_id & sequence
            user_id = random.choice(self.user_ids)
            sequence = random.choice(self.sequences)["actions"]

            # Either assign work to a free worker, spin up a new worker, or do nothing
            # and try again next loop
            with self.lock:
                if self.free_workers:
                    self._assign_work(user_id, sequence)
                elif len(self.all_workers) < self.max_workers:
                    self._start_worker()
                    self._assign_work(user_id, sequence)

            # Make use of elapsed time to stay within the sequence rate
            elapsed_time = time.time() - start_time
            sleep_time = max(0.0, sequence_rate - elapsed_time)
            time.sleep(sleep_time)

    def shutdown(self):
        self.shutdown_event.set()
        print(f"[{self}] Shutting down WorkGenerator...")

    def __repr__(self):
        return f"<ActionGenerator>"