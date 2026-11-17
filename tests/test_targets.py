import pytest
import numpy as np
import json
from ssi.targets import merge_classes, chart_rule

def test_merge_classes():
    # Prompt fixtures: 
    # [7,20,13,3] -> [27,16]
    res1 = merge_classes(["B1", "B2", "B3", "B4"], [7, 20, 13, 3])
    assert res1["counts_after"] == [27, 16]
    
    # [18,4,4,0] -> NO_VALID_TARGET
    res2 = merge_classes(["B1", "B2", "B3", "B4"], [18, 4, 4, 0])
    assert res2["status"] == "NO_VALID_TARGET"
    
    # [16,4,4,0] -> [24] (which is also NO_VALID_TARGET due to length 1)
    res3 = merge_classes(["B1", "B2", "B3", "B4"], [16, 4, 4, 0])
    assert res3["status"] == "NO_VALID_TARGET"
    assert res3["counts_after"] == [24]
    
    # [30,30,30,30] -> unchanged
    res4 = merge_classes(["B1", "B2", "B3", "B4"], [30, 30, 30, 30])
    assert res4["status"] == "SUCCESS"
    assert res4["counts_after"] == [30, 30, 30, 30]

def test_chart_rule():
    # 39.0 inches -> ties 38 and 40. up->40, down->38.
    # 39.0 inches is 39 * 2.54 = 99.06 cm
    chest_cm = 99.06
    assert chart_rule(chest_cm, tie_mode='up') == 40
    assert chart_rule(chest_cm, tie_mode='down') == 38
    
    # 38.0 inches is exactly 38.
    assert chart_rule(38.0 * 2.54, tie_mode='up') == 38
    assert chart_rule(38.0 * 2.54, tie_mode='down') == 38
    
    # 38.5 inches -> dist 0.5 to 38, 1.5 to 40. Nearest is 38.
    assert chart_rule(38.5 * 2.54, tie_mode='up') == 38
    assert chart_rule(38.5 * 2.54, tie_mode='down') == 38
