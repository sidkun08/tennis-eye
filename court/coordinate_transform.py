import cv2
import numpy as np

def get_transformed_coords(img_coords, real_world_coords, bounce_coords):
    img_coords = np.array([img_coords], dtype=np.float32).reshape(-1, 2)
    real_world_coords = np.array([real_world_coords], dtype=np.float32).reshape(-1, 2)
    bounce_coords = np.array([bounce_coords], dtype=np.float32).reshape(-1, 1, 2)
    transformation_function, _ = cv2.findHomography(img_coords, real_world_coords, cv2.RANSAC, 5.0)
    transformed_coords = cv2.perspectiveTransform(bounce_coords, transformation_function)
    return transformed_coords.reshape(-1, 2)