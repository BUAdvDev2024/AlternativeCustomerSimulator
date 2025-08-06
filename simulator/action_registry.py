class ActionRegistry:
    def __init__(self):
        self._registry = {}

    def register_all(self, action_definitions: dict):
        """
        Registers all actions defined in action_definitions.
        """
        for action_name, payload in action_definitions.items():
            self.register(action_name, payload.get("config"), payload.get("behaviour"))

    def register(self, name: str, config: dict, behaviour_instance):
        self._registry[name] = {
            "config": config,
            "behaviour": behaviour_instance
        }

        print(f"[ActionRegistry] registered action : '{name}'")

    def get(self, action_name: str):
        if action_name not in self._registry:
            raise KeyError(f"Action '{action_name}' not found in registry.")
        return self._registry[action_name]