import pytest
import numpy as np
import cv2
from ssi.features import extract_features

class MockLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MockResult:
    def __init__(self, lm, mask):
        self.pose_landmarks = [lm]
        class MaskMock:
            def __init__(self, mask):
                self.mask = mask
            def numpy_view(self):
                return self.mask
        self.segmentation_masks = [MaskMock(mask)]

class MockDetector:
    def __init__(self, lm, mask):
        self.result = MockResult(lm, mask)
    def detect(self, mp_image):
        return self.result

def test_features_scale_invariant():
    w, h = 100, 200
    lm = {i: MockLandmark(0.5, 0.5) for i in range(33)}
    lm[11] = MockLandmark(0.4, 0.2)
    lm[12] = MockLandmark(0.6, 0.2)
    lm[13] = MockLandmark(0.3, 0.35)
    lm[14] = MockLandmark(0.7, 0.35)
    lm[15] = MockLandmark(0.2, 0.5)
    lm[16] = MockLandmark(0.8, 0.5)
    lm[23] = MockLandmark(0.45, 0.5)
    lm[24] = MockLandmark(0.55, 0.5)
    lm[27] = MockLandmark(0.45, 0.8)
    lm[28] = MockLandmark(0.55, 0.8)
    
    mask = np.zeros((h, w, 1))
    mask[20:180, 30:70] = 1.0 # head to ankle
    
    detector = MockDetector(lm, mask)
    img_rgb = np.zeros((h, w, 3), dtype=np.uint8)
    
    feats_1 = extract_features(img_rgb, detector)
    
    w2, h2 = int(w*0.5), int(h*0.5)
    mask2 = np.zeros((h2, w2, 1))
    mask2[10:90, 15:35] = 1.0
    
    detector2 = MockDetector(lm, mask2)
    img_rgb2 = np.zeros((h2, w2, 3), dtype=np.uint8)
    
    feats_2 = extract_features(img_rgb2, detector2)
    
    for k in feats_1:
        if not np.isnan(feats_1[k]) and k not in ['shoulder_tilt_deg', 'torso_lean_deg']:
            diff = abs(feats_1[k] - feats_2[k])
            # If values are extremely small, avoid division by zero
            if abs(feats_1[k]) > 1e-4:
                assert diff / abs(feats_1[k]) < 0.05

