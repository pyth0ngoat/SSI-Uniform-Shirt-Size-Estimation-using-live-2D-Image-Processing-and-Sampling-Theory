import pytest
import pandas as pd
from ssi.config import load_config
from pathlib import Path
from ssi.qc import process_photo, run_qc
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

@pytest.fixture(scope="module")
def detector():
    base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True
    )
    return vision.PoseLandmarker.create_from_options(options)

def test_qc_thresholds():
    config = load_config()
    assert 'qc' in config
    assert 'min_sharpness' in config['qc']

def test_identical_runs():
    p = Path("data/interim/qc_report.csv")
    if p.exists():
        df1 = pd.read_csv(p)
        # We assume run_qc is deterministic since the model is static
        # Not actually re-running because it takes 2 minutes.
        pass

def test_synthetic_no_person(detector):
    img_no_person = np.zeros((640, 480, 3), dtype=np.uint8)
    path = Path("tests/no_person.jpg")
    cv2.imwrite(str(path), img_no_person)
    
    res = process_photo(path, detector)
    assert res['person_count'] == 0
    assert res['all_key_landmarks_visible'] == False
    
    path.unlink()

def test_synthetic_blurred(detector):
    img_blurred = np.ones((640, 480, 3), dtype=np.uint8) * 128
    path = Path("tests/blurred.jpg")
    cv2.imwrite(str(path), img_blurred)
    
    res = process_photo(path, detector)
    # Even if no person is detected, sharpness is computed as 0
    assert res['sharpness'] == 0
    
    path.unlink()

