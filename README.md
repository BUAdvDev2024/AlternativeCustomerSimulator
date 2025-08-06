# AlternativeCustomerSimulator

A customer action simulator responsible for simulating user actions via HTTP requests to various microservice APIs.

> Open a pull request, create an issue, or contact the lead developer directly to make changes to this repository.

---

## 🧠 How It Works

### 📌 Customer Action

A **customer action** represents an interaction that a customer performs through HTTP to a microservice API.

Examples:
- A customer login HTTP request
- A table booking HTTP request
- An order placement HTTP request

Actions are defined in `config/actions.yaml`. Example:

```yaml
actions:
  - name: "PlaceOrder"
    behaviour: "simulator/actions/place_order.py"
    auth_key: "INSERT_AUTH_KEY"
    base_url: "https://httpbin.org/"
```

Each action requires:
- `name`: Name of the action (e.g., `"PlaceOrder"`)
- `behaviour`: Path to the Python module that implements the behavior

Optional fields such as `auth_key`, `base_url`, etc., can be added as needed and will be made available inside the behaviour module.

The behavior module must implement the following functions:

```python
def get_endpoint(customer: Customer, action_config: dict) -> str: ...
def get_method(customer: Customer, action_config: dict) -> str: ...
def get_header(customer: Customer, action_config: dict) -> dict: ...
def get_body(customer: Customer, action_config: dict) -> dict | None: ...
def process_response(customer: Customer, response: requests.Response, action_config: dict): ...
```

These allow full control over request construction and response handling.

---

### 🛠 Create Custom Customer Actions

To simulate new customer interactions with your microservice:

1. Define the action in `config/actions.yaml`
2. Copy the template from `simulator/actions/action_behaviour_template.py`
3. Rename and implement your custom behavior
4. Ensure the behavior file path is set in the action config

---

## 👤 Define Customers

The simulator requires at least one customer defined in the config file (default: `config/customers.yaml`).

You can change the customer config file path via `customers_file` in `config/worker_pool.yaml`.

### Example: `customers.yaml`

```yaml
customers:
  - user_id: 1
    email: user1@example.com
    password: pass1234
  - user_id: 2
    email: user2@example.com
    password: pass345
  - user_id: 3
    email: user3@example.com
    password: pass678
```

---

## 📈 Customize Simulator Load Generation

The simulator generates HTTP requests using the `ActionGenerator`, which is configured by `config/test_script.yaml`.

### 🔄 Action Sequences

Each sequence is a list of customer actions executed in order. Each action includes:
- `name`: Must match one from `config/actions.yaml`
- `delay`: Time in seconds to wait before the next action in the sequence

Example:

```yaml
min_workers: 3
max_workers: 20
keep_alive_seconds: 5
generate_rate: 10

sequences:
  - name: PlaceThenCancel
    actions:
      - name: PlaceOrder
        delay: 0
      - name: CancelOrder
        delay: 1

  - name: PlaceOnly
    actions:
      - name: PlaceOrder
        delay: 0
```

- `keep_alive_seconds`: Idle time after which a worker is terminated
- `generate_rate`: Target number of sequences per second (actual may vary under load)

---

## 🚀 How To Use

To run the simulator against your microservices:

Pre-requisite:
- Clone Repo:
```bash
git clone https://github.com/BUAdvDev2024/AlternativeCustomerSimulator.git
cd AlternativeCustomerSimulator
```

1. Define customer actions in `config/actions.yaml`
2. Implement the behavior logic using `action_template_behaviour.py`
3. Add customer accounts to `config/customers.yaml`
4. Adjust the test load config in `config/test_script.yaml`
5. Add your desired action sequences
6. Start the simulator:

If using Python:
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Start application:
```bash
python main.py
```

If using Docker:
1. Run using Docker:
```bash
docker-compose up --build
```

---

## 🛑 How To Stop

To stop the simulator from the terminal:

```bash
CTRL+C
```

---

## 📊 Results Summary

After shutdown, a summary is printed including:

- HTTP successes (per action)
- HTTP failures (per action)
- Per-customer total success/failure (indexed by `user_id`)

---

## 👤 Lead Developer

- **Alanas Liveris** (`s5525684`)