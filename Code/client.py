import cv2
import socket
import struct
import pickle

import threading
import time
import copy


class Gaze_Capture_Client:
    def __init__(self, fps=11, cap=cv2.VideoCapture(0), server_ip='127.0.0.1', server_port=5002):
        # Initialize socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, server_port))
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.worker_thread = None
        self.cap = cap
        self.fps = fps
        # Shared resource

    def worker(self, stop_event, results_dict, cap, time_between_frames):
        while not stop_event.is_set():
            # Simulate a time-consuming operation
            time.sleep(time_between_frames)
            ret, frame = cap.read()
            cv2.imshow('Client', frame)
            # Serialize the image
            data = pickle.dumps(frame)

            # Send message length first
            # L is for unsigned long
            message_size = struct.pack("L", len(data))
            self.client_socket.sendall(message_size + data)

            # Receive response from server
            response_length = struct.unpack("L", self.client_socket.recv(8))[
                0]  # 8 bytes for size
            response_data = b""
            while len(response_data) < response_length:
                response_data += self.client_socket.recv(4096)
            response_dict = pickle.loads(response_data)
            print(f"Server response (dictionary): {response_dict}")
            if (response_dict["status"] != "error"):
                gaze_distance = response_dict["score"]
                with self.lock:  # Ensure thread-safe access
                    if results_dict["number_of_samples"] == 0:
                        results_dict["number_of_samples"] = 1
                        results_dict["average_score"] = gaze_distance
                        
                    old_average_score = results_dict["average_score"]
                    
                    results_dict["average_score"] = ((
                        old_average_score*results_dict["number_of_samples"]) + gaze_distance)/(results_dict["number_of_samples"]+1)
                    
                    results_dict["number_of_samples"] = results_dict["number_of_samples"] + 1

    def start_capture(self):
        self.results_dict = {}
        self.results_dict["average_score"] = 0
        self.results_dict["number_of_samples"] = 1

        # Worker function that runs in parallel

        time_between_frames = 1/self.fps

        # Start the worker thread
        self.worker_thread = threading.Thread(target=self.worker, args=(
            self.stop_event, self.results_dict, self.cap, time_between_frames,))
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def stop_capture(self):
        self.stop_event.set()
        self.worker_thread.join()
        with self.lock:
            print(self.results_dict)
        return copy.deepcopy(self.results_dict)

    def __del__(self):
        self.cap.release()
        self.client_socket.close()


if __name__ == "__main__":
    gz_client = Gaze_Capture_Client()
    gz_client.start_capture()
    time.sleep(10)  # Simulate a time-consuming operation
    print(gz_client.stop_capture())
    del gz_client  # for a secure release of resources
