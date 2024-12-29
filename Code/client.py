import cv2
import socket
import struct
import pickle

# Server address and port
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5002

# Initialize socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Video capture
cap = cv2.VideoCapture(0)  # Use 0 for webcam, or provide a video file path

try:
    while True:
        while True:
            ret, frame = cap.read()
            cv2.imshow('Client', frame)
            
            if not ret:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Serialize the image
        data = pickle.dumps(frame)

        # Send message length first
        message_size = struct.pack("L", len(data))  # L is for unsigned long
        client_socket.sendall(message_size + data)
        
        # Receive response from server
        response_length = struct.unpack("L", client_socket.recv(8))[
            0]  # 8 bytes for size
        response_data = b""
        while len(response_data) < response_length:
            response_data += client_socket.recv(4096)

        # Deserialize the dictionary
        response_dict = pickle.loads(response_data)
        print(f"Server response (dictionary): {response_dict}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    cap.release()
    client_socket.close()
