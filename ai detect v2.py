import cv2
from ultralytics import YOLO
import serial
import pygame
import smtplib
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Initialize YOLO model
model = YOLO("yolo11n.pt")

def detect_objects(frame):
    results = model(frame)
    objects = []

    for result in results:
        if result.boxes:
            for box in result.boxes:
                label = model.names[int(box.cls)]
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                objects.append((label, (x1, y1, x2, y2)))

                # Draw the bounding box and label on the frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    return frame, objects

def capture_webcam_image():
    save_folder = r'C:\Users\annam\Downloads\p\images'
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam")
        return None, None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    time.sleep(1)
    
    for _ in range(5):  # Retry mechanism
        ret, frame = cap.read()
        if ret:
            snapshot_filename = os.path.join(save_folder, 'motion_detected_image.jpg')
            cv2.imwrite(snapshot_filename, frame)
            cap.release()
            return snapshot_filename, frame
        print("Retrying to capture image...")
        time.sleep(0.5)

    print("Failed to capture image after multiple attempts")
    cap.release()
    return None, None

def send_email(snapshot_filename):
    email = "2005techreview@gmail.com"
    receiver_email = "storagejohn4.5.6@gmail.com"
    subject = "WARNING!!!!!!!"
    message = "MOTION DETECTED!!!!"

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        with open(snapshot_filename, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename=motion_detected_image.jpg')
            msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, "culnexqnwhwtviam")
        server.sendmail(email, receiver_email, msg.as_string())
        server.quit()

        print("Email has been sent")
    except Exception as e:
        print(f"Error sending email: {e}")

pygame.mixer.init()
ser = serial.Serial('COM7', 9600)
sound_file_path = r'C:\Users\annam\Downloads\p\1.mp3'
print("Waiting for messages from Arduino...")

last_msg_time = 0
msg_cooldown = 10

cap = cv2.VideoCapture(2)
if not cap.isOpened():
    print("Cannot open webcam")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break
    frame, objects = detect_objects(frame)

    if ser.in_waiting:
        message = ser.readline().decode('utf-8').strip()
        print(f"Received message: {message}")

        if message == "Play Sound":
            current_time = time.time()
            if current_time - last_msg_time >= msg_cooldown:
                snapshot_filename, frame = capture_webcam_image()
                if snapshot_filename and frame is not None:
                    frame, objects = detect_objects(frame)
                    if any(label == "person" for label, _ in objects):
                        ser.write("person".encode('utf-8'))
                        send_email(snapshot_filename)
                        last_msg_time = current_time
        

    if frame is not None and frame.shape[0] > 0 and frame.shape[1] > 0:
        cv2.imshow("Frame", frame)
    else:
        print("Invalid frame dimensions")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()