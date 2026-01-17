import cv2
import mediapipe as mp
import numpy as np
import time
import os

# --- MediaPipe Setup ---
# Download the model asset bundle if it doesn't exist
model_path = 'face_landmarker.task'
if not os.path.exists(model_path):
    print(f"Downloading {model_path}...")
    import urllib.request
    url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    urllib.request.urlretrieve(url, model_path)
    print(f"{model_path} downloaded successfully.")
else:
    print(f"{model_path} already exists.")

# Global variable to store detection results
latest_face_landmarker_result = None

# Callback function to get the detection results asynchronously
def face_landmarker_callback(result, output_image, timestamp_ms):
    global latest_face_landmarker_result
    latest_face_landmarker_result = result

# Create FaceLandmarker object
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    num_faces=1,  # Detect a single face
    result_callback=face_landmarker_callback
)
face_landmarker = vision.FaceLandmarker.create_from_options(options)

# --- Motor Control Parameters ---
# These can be adjusted based on your motor characteristics
MAX_MOTOR_STEP = 100  # Maximum motor step size
DEAD_ZONE = 0.05  # Don't move motor if error is less than this (5% of frame)
SMOOTHING_FACTOR = 0.3  # For smoothing motor commands (0-1, lower = smoother)

# Store previous motor commands for smoothing
prev_motor_x = 0
prev_motor_y = 0

def calculate_motor_movement(face_x, face_y, frame_width, frame_height):
    """
    Calculate motor movement commands based on face position.
    
    Args:
        face_x: Normalized face x position (0-1)
        face_y: Normalized face y position (0-1)
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
    
    Returns:
        (motor_x, motor_y): Motor movement commands (-MAX_MOTOR_STEP to +MAX_MOTOR_STEP)
    """
    global prev_motor_x, prev_motor_y
    
    # Calculate error from center (0.5, 0.5 in normalized coordinates)
    error_x = face_x - 0.5  # -0.5 to +0.5
    error_y = face_y - 0.5  # -0.5 to +0.5
    
    # Apply dead zone - don't move if error is too small
    if abs(error_x) < DEAD_ZONE:
        error_x = 0
    if abs(error_y) < DEAD_ZONE:
        error_y = 0
    
    # Scale error to motor step range (-MAX_MOTOR_STEP to +MAX_MOTOR_STEP)
    # Multiply by 2 to use full range (error is -0.5 to +0.5, so *2 gives -1 to +1)
    motor_x = error_x * 2 * MAX_MOTOR_STEP
    motor_y = error_y * 2 * MAX_MOTOR_STEP
    
    # Apply smoothing to prevent jittery movements
    motor_x = prev_motor_x * (1 - SMOOTHING_FACTOR) + motor_x * SMOOTHING_FACTOR
    motor_y = prev_motor_y * (1 - SMOOTHING_FACTOR) + motor_y * SMOOTHING_FACTOR
    
    # Round to integer steps
    motor_x = int(round(motor_x))
    motor_y = int(round(motor_y))
    
    # Update previous values
    prev_motor_x = motor_x
    prev_motor_y = motor_y
    
    return motor_x, motor_y

# --- Video Capture and Processing Loop ---
cap = cv2.VideoCapture(0)  # Use MacBook's camera

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit(1)

print("Camera stream opened. Press 'q' to quit.")

# Set camera properties for better performance
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

frame_count = 0
fps_start_time = time.time()

# Main processing loop
while True:
    success, frame = cap.read()
    if not success:
        print("Error: Failed to grab frame.")
        break
    
    # Convert the frame to RGB as MediaPipe expects RGB
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    
    # Send image to the asynchronous detector
    timestamp_ms = int(time.time() * 1000)
    face_landmarker.detect_async(mp_image, timestamp_ms)
    
    # Prepare image for display
    display_image = frame.copy()
    h, w, _ = frame.shape
    
    # Draw center crosshair
    cv2.line(display_image, (w//2, 0), (w//2, h), (128, 128, 128), 1)
    cv2.line(display_image, (0, h//2), (w, h//2), (128, 128, 128), 1)
    
    # Process detection results if available
    if latest_face_landmarker_result and latest_face_landmarker_result.face_landmarks:
        for face_landmarks in latest_face_landmarker_result.face_landmarks:
            # Use nose tip (landmark 4) as tracking point
            if len(face_landmarks) > 4:
                nose = face_landmarks[4]
                
                # Convert normalized coordinates to pixel coordinates
                cx = int(nose.x * w)
                cy = int(nose.y * h)
                
                # Draw tracking point
                cv2.circle(display_image, (cx, cy), 10, (0, 255, 0), 2)
                
                # Calculate motor movement
                motor_x, motor_y = calculate_motor_movement(nose.x, nose.y, w, h)
                
                # Calculate error for display
                error_x = (nose.x - 0.5) * 100  # Convert to percentage
                error_y = (nose.y - 0.5) * 100
                
                # Draw line from center to face
                cv2.line(display_image, (w//2, h//2), (cx, cy), (0, 255, 255), 2)
                
                # Display information on image
                info_text = [
                    f"Face Position: ({nose.x:.2f}, {nose.y:.2f})",
                    f"Error: X={error_x:.1f}%, Y={error_y:.1f}%",
                    f"Motor Command: X={motor_x:+4d}, Y={motor_y:+4d} steps",
                ]
                
                for i, text in enumerate(info_text):
                    cv2.putText(display_image, text, (10, 30 + i * 25),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
                
                # Print motor command to console
                print(f"Frame {frame_count}: Motor X={motor_x:+4d}, Motor Y={motor_y:+4d} steps | Error X={error_x:+.1f}%, Y={error_y:+.1f}%")
    else:
        # No face detected
        cv2.putText(display_image, "No face detected", (10, 30),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
    
    # Calculate and display FPS
    frame_count += 1
    if frame_count % 30 == 0:
        fps = 30 / (time.time() - fps_start_time)
        fps_start_time = time.time()
        print(f"FPS: {fps:.1f}")
    
    # Display the frame
    cv2.imshow('Face Tracking with Motor Control', display_image)
    
    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("\nFace landmark detection stream stopped.")

# Release resources
cap.release()
cv2.destroyAllWindows()
face_landmarker.close()
