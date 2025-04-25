"""
remote_io_client.py - Client component for remote file I/O experiment on Raspberry Pi
"""

import os
import time
import socketio
import csv
from datetime import datetime
from config.settings import SERVER_PORT, DEFAULT_ITERATIONS

# Server settings (another Raspberry Pi in same network)
SERVER_HOST = "192.168.1.3"


def run_experiment(server_url, filepath, iterations=10):
    """
    Run the remote I/O experiment multiple times
    """
    results = []

    print(f"Running remote I/O experiment with file: {filepath}")
    print(f"Connecting to server: {server_url}")

    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}...")
        elapsed = measure_remote_io(server_url, filepath)
        results.append(elapsed)
        print(f"Time: {elapsed:.6f} seconds")
        time.sleep(0.5)  # Short delay between iterations

    avg_time = sum(results) / len(results)
    print(f"Average time: {avg_time:.6f} seconds")

    # Get the file size (assuming file exists locally too for comparison)
    file_size = os.path.getsize(filepath) if os.path.exists(filepath) else "unknown"

    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"results/remote_io_{timestamp}.csv"

    os.makedirs("results", exist_ok=True)

    with open(result_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Iteration", "Time (s)", "File Size (bytes)"])
        for i, time_value in enumerate(results):
            writer.writerow([i + 1, f"{time_value:.6f}", file_size])
        writer.writerow(["Average", f"{avg_time:.6f}", ""])

    print(f"Results saved to {result_file}")
    return results, avg_time


def measure_remote_io(server_url, filepath):
    """
    Measure the time taken for a remote file I/O operation via Socket.IO
    """
    sio = socketio.Client()

    # Variables to store received data and completion status
    received_data = None
    operation_completed = False
    start_time = 0  # Initialize in outer scope
    end_time = 0  # Initialize in outer scope

    @sio.event
    def connect():
        nonlocal start_time
        start_time = time.perf_counter()
        # Request the file immediately after connecting
        sio.emit("read_file_request", {"filepath": filepath})

    @sio.event
    def connect_error(data):
        print(f"Connection error: {data}")
        sio.disconnect()

    @sio.event
    def disconnect():
        print("Disconnected from server")

    @sio.on("read_file_response")
    def on_read_file_response(data):
        nonlocal received_data, operation_completed, end_time
        received_data = data
        end_time = time.perf_counter()
        operation_completed = True

        if "error" in data:
            print(f"Error: {data['error']}")
        else:
            file_size = data.get("file_size", 0)
            print(f"Received file: {data.get('filepath')}, size: {file_size} bytes")

        # Close the connection
        sio.disconnect()

    # Connect to the server
    try:
        connection_start_time = (
            time.perf_counter()
        )  # Record time before connection attempt
        sio.connect(server_url)

        # Wait for the operation to complete (with timeout)
        timeout = 30  # seconds
        wait_time = 0
        while not operation_completed and wait_time < timeout:
            time.sleep(0.1)
            wait_time += 0.1

        if not operation_completed:
            print("Operation timed out")
            sio.disconnect()
            return float("inf")

        # Calculate elapsed time
        elapsed_time = end_time - start_time

        # Alternative calculation including connection overhead
        total_elapsed = end_time - connection_start_time
        print(
            f"Total time (including connection overhead): {total_elapsed:.6f} seconds"
        )

        return elapsed_time

    except Exception as e:
        print(f"Error during remote I/O: {e}")
        return float("inf")
    finally:
        if sio.connected:
            sio.disconnect()


if __name__ == "__main__":
    server_url = f"http://{SERVER_HOST}:{SERVER_PORT}"
    filepath = "../../data/10mb-examplefile-com.txt"
    run_experiment(server_url, filepath, DEFAULT_ITERATIONS)
