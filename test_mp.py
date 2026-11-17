import cv2
import mediapipe as mp
import numpy as np

def test_mp():
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True, model_complexity=2, enable_segmentation=True)
    
    # Read first photo
    img_path = r"C:\Users\kapil\.gemini\antigravity\scratch\ssi_project\data\photos_raw\Q7. Upload the photo (File responses)\P003.jpg"
    image = cv2.imread(img_path)
    if image is None:
        print("Failed to read image")
        return
        
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    
    if results.pose_landmarks:
        print("Landmarks found!")
        print("Mask max:", np.max(results.segmentation_mask))
    else:
        print("No landmarks found.")

if __name__ == "__main__":
    test_mp()

