class Customer:
    def __init__(self, email: str, password: str, user_id: int):
        self.email = email
        self.password = password
        self.user_id = user_id
        self.placed_orders = []
        self.closed_orders = []

        print(f"[{self}] created")

    def __repr__(self):
        return f"<Customer {self.user_id}>"