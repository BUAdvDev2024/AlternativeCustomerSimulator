import yaml

def load_yaml(path: str) -> dict:
    """
    Loads a YAML file as a dictionary using provided file path.
    """
    with open(path, 'r') as f:
        return yaml.safe_load(f)