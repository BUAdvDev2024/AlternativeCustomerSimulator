from collections import defaultdict
import threading

class MetricsTracker:
    def __init__(self):
        self.success_counts = defaultdict(int)
        self.failure_counts = defaultdict(int)
        self.per_customer = defaultdict(lambda: {"success": 0, "fail": 0})
        self.lock = threading.Lock()

    def log_success(self, action_name: str, user_id: int):
        with self.lock:
            self.success_counts[action_name] += 1
            self.per_customer[user_id]["success"] += 1

    def log_failure(self, action_name: str, user_id: int):
        with self.lock:
            self.failure_counts[action_name] += 1
            self.per_customer[user_id]["fail"] += 1

    def display_summary(self):
        print("===== Metrics Summary =====")
        print("HTTP Successes:")
        for action, count in self.success_counts.items():
            print(f"  -  {action}: {count}")
        print("\nHTTP Failures:")
        for action, count in self.failure_counts.items():
            print(f"  -  {action}: {count}")

        print("\nPer Customer:")
        for user_id, stats in self.per_customer.items():
            print(f"  ID {user_id}: ✅ {stats['success']} | ❌ {stats['fail']}")
