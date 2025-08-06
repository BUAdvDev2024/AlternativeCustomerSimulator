import importlib.util
import os
from util import yaml_loader

REQUIRED_BEHAVIOUR_FUNCS = [
    "get_endpoint",
    "get_method",
    "get_header",
    "get_body",
    "process_response"
]

def load_module_from_file(filepath: str):
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if not spec or not spec.loader:
        raise ImportError(f"Failed to load module from {filepath}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "Behaviour"):
        raise AttributeError(f"Module '{filepath}' must define a Behaviour class.")

    return module

def validate_behaviour_instance(behaviour_instance, action_name: str):
    missing = [f for f in REQUIRED_BEHAVIOUR_FUNCS if not hasattr(behaviour_instance, f)]
    if missing:
        raise AttributeError(f"Action '{action_name}' missing required function(s): {missing}")

def load_actions_config(config_path: str) -> dict:
    """
    Loads the action config YAML and returns a dictionary mapping action names to (config, behaviour_module)
    """
    action_config = yaml_loader.load_yaml(config_path)
    actions = action_config.get("actions", [])

    loaded = {}

    for action in actions:
        name = action.get("name")
        behaviour_path = action.get("behaviour")

        if not name or not behaviour_path:
            raise ValueError(f"Action entry must have 'name' and 'behaviour' fields: {action}")

        module = load_module_from_file(behaviour_path)
        behaviour_instance = module.Behaviour()

        validate_behaviour_instance(behaviour_instance, name)

        loaded[name] = {
            "config": action,
            "behaviour": behaviour_instance
        }

    return loaded