import signal
import sys
import threading
import time

from generator.action_generator import ActionGenerator
from simulator.action_config_loader import load_actions_config
from simulator.action_registry import ActionRegistry
from simulator.customer_worker_pool import CustomerWorkerPool
from simulator.metrics import MetricsTracker
from util import yaml_loader

def main():
    print(f"[Main] loading config...")

    # Load all configs
    action_definition_path = "config/actions.yaml"
    action_definitions = load_actions_config(action_definition_path)

    worker_pool_config_path = "config/worker_pool.yaml"
    worker_pool_config = yaml_loader.load_yaml(worker_pool_config_path)

    action_generator_config_path = "config/test_script.yaml"
    action_generator_config = yaml_loader.load_yaml(action_generator_config_path)

    # Registry registers action name to action config and the behaviour module instance
    registry = ActionRegistry()
    registry.register_all(action_definitions)

    # Start a metric tracker to see HTTP success/fail metrics at the end
    metrics = MetricsTracker()

    # Start worker pool
    pool = CustomerWorkerPool(worker_pool_config, metrics, registry)
    pool.run()

    # Start action generator to send work to CustomerWorkerPool
    # Generator runs on a separate thread
    user_ids  = list(pool.customers.keys())
    generator = ActionGenerator(user_ids, pool, action_generator_config)
    generator_thread = threading.Thread(target=generator.run, daemon=True)
    generator_thread.start()

    # Handle shutdown gracefully
    def handle_exit(signum, frame):
        print("[Main] Shutdown signal received.")
        pool.shutdown()
        generator.shutdown()
        metrics.display_summary()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Keep main process alive while simulator is running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_exit(None, None)

if __name__ == "__main__":
    main()