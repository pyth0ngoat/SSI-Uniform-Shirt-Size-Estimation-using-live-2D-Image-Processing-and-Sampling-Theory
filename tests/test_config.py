from ssi.config import load_config, set_seed
import numpy as np
import random

def test_load_config():
    config = load_config()
    assert "seed" in config
    assert config["seed"] == 20260929
    assert "categories" in config

def test_set_seed():
    set_seed(42)
    a = random.random()
    b = np.random.rand()
    
    set_seed(42)
    a_new = random.random()
    b_new = np.random.rand()
    
    assert a == a_new
    assert b == b_new

