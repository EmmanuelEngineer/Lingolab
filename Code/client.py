import cv2
import socket
import struct
import pickle

import threading
import time


FPS = 11

# Server address and port
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5002

# Initialize socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Shared resource


def worker(stop_event, results_dict):
    average_score = 0
    number_of_samples = 0
    while not stop_event.is_set():
        time.sleep(time_between_frames)  # Simulate a time-consuming operation
        ret, frame = cap.read()
        cv2.imshow('Client', frame)
        # Serialize the image
        data = pickle.dumps(frame)

        # Send message length first
        # L is for unsigned long
        message_size = struct.pack("L", len(data))
        client_socket.sendall(message_size + data)

        # Receive response from server
        response_length = struct.unpack("L", client_socket.recv(8))[
            0]  # 8 bytes for size
        response_data = b""
        while len(response_data) < response_length:
            response_data += client_socket.recv(4096)
        response_dict = pickle.loads(response_data)
        print(f"Server response (dictionary): {response_dict}")
        if (response_dict["status"] != "error"):
            gaze_distance = response_dict["score"]
            with lock:  # Ensure thread-safe access
                old_average_score = results_dict["average_score"]
                results_dict["average_score"] = ((
                    old_average_score*number_of_samples) + gaze_distance)/results_dict["number_of_samples"]
                results_dict["number_of_samples"] = results_dict["number_of_samples"] + 1


if __name__ == "__main__":
    lock = threading.Lock()
    stop_event = threading.Event()
    """ with lock:
        global average_score
        global number_of_samples
        global run """
    # average_score, number_of_samples = 0, 0
    results_dict = {}
    results_dict["average_score"] = 0
    results_dict["number_of_samples"] = 0

    # Worker function that runs in parallel

    time_between_frames = 1/FPS
    cap = cv2.VideoCapture(0)  # Use 0 for webcam, or provide a video file path
    

    # Start the worker thread
    worker_thread = threading.Thread(target=worker, args=(
        stop_event, results_dict, ))

    # Video capture

    try:
        worker_thread.daemon = True
        worker_thread.start()

        time.sleep(10)  # Simulate a time-consuming operation
        stop_event.set()
        worker_thread.join()
        with lock:
            print(results_dict)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        client_socket.close()



