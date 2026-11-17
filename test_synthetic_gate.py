import json
import pandas as pd
from ssi.gate import gate

def run_tests():
    # Test 1: EXPLORATORY synthetic
    with open("data/processed/class_map_SYNTH.json", "w") as f:
        json.dump({"status": "OK", "counts_before": [20, 21], "counts_after": [27, 14]}, f)
    pd.DataFrame({'a': range(41)}).to_csv("data/processed/analysis_synth.csv", index=False)
    
    s, r = gate("SYNTH")
    print(f"Synthetic Gate: {s} - {r}")
    assert s == "EXPLORATORY"
    print("Tests passed!")

if __name__ == '__main__':
    run_tests()

