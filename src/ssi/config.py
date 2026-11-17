import yaml
from pathlib import Path
import random
import numpy as np

def load_config():
    """Loads the project configuration from config.yaml."""
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def set_seed(seed):
    """Sets the global random seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)

