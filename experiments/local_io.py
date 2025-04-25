"""
local_io.py - Measures time for local file I/O operations on a Raspberry Pi
"""

import os
import time
import argparse
import csv
from datetime import datetime


def read_file(filepath):
    """
    Read a file from local disk and return its contents
    """
    start_time = time.perf_counter()

    with open(filepath, "rb") as f:
        data = f.read()

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    return data, elapsed_time


def run_experiment(filepath, iterations=10):
    """
    Run the local I/O experiment multiple times
    """
    results = []
    file_size = os.path.getsize(filepath)

    print(f"Running local I/O experiment with file: {filepath}")
    print(f"File size: {file_size} bytes")

    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}...")
        _, elapsed = read_file(filepath)
        results.append(elapsed)
        print(f"Time: {elapsed:.6f} seconds")

    avg_time = sum(results) / len(results)
    print(f"Average time: {avg_time:.6f} seconds")

    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"../results/local_io_{timestamp}.csv"

    os.makedirs("results", exist_ok=True)

    with open(result_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Iteration", "Time (s)", "File Size (bytes)"])
        for i, time_value in enumerate(results):
            writer.writerow([i + 1, f"{time_value:.6f}", file_size])
        writer.writerow(["Average", f"{avg_time:.6f}", ""])

    print(f"Results saved to {result_file}")
    return results, avg_time


if __name__ == "__main__":
    filepath = "../data/10mb-examplefile-com.txt"
    iterations = 1
    run_experiment(filepath, iterations)
