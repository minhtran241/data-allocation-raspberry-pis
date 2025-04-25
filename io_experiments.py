#!/usr/bin/env python3
"""
io_experiments.py - Compare and visualize results from local and remote I/O experiments
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import glob


def load_results(local_results_file, remote_results_file):
    """
    Load experiment results from CSV files
    """
    local_df = pd.read_csv(local_results_file)
    remote_df = pd.read_csv(remote_results_file)

    # Filter out average row
    local_df = local_df[local_df["Iteration"] != "Average"]
    remote_df = remote_df[remote_df["Iteration"] != "Average"]

    # Convert columns to numeric
    local_df["Iteration"] = pd.to_numeric(local_df["Iteration"])
    local_df["Time (s)"] = pd.to_numeric(local_df["Time (s)"])

    remote_df["Iteration"] = pd.to_numeric(remote_df["Iteration"])
    remote_df["Time (s)"] = pd.to_numeric(remote_df["Time (s)"])

    return local_df, remote_df


def compare_results(local_df, remote_df):
    """
    Compare and summarize experiment results
    """
    local_avg = local_df["Time (s)"].mean()
    remote_avg = remote_df["Time (s)"].mean()

    print(f"Local I/O average time: {local_avg:.6f} seconds")
    print(f"Remote I/O average time: {remote_avg:.6f} seconds")
    print(f"Difference: {remote_avg - local_avg:.6f} seconds")
    print(f"Remote is {remote_avg / local_avg:.2f}x slower than local")

    return local_avg, remote_avg


def visualize_results(local_df, remote_df, output_file=None):
    """
    Create visualization of experiment results
    """
    plt.figure(figsize=(12, 8))

    # Line plot
    plt.subplot(2, 1, 1)
    plt.plot(local_df["Iteration"], local_df["Time (s)"], "b-", label="Local I/O")
    plt.plot(remote_df["Iteration"], remote_df["Time (s)"], "r-", label="Remote I/O")
    plt.xlabel("Iteration")
    plt.ylabel("Time (seconds)")
    plt.title("Comparison of Local vs Remote I/O Performance")
    plt.legend()
    plt.grid(True)

    # Box plot
    plt.subplot(2, 1, 2)
    data = [local_df["Time (s)"], remote_df["Time (s)"]]
    plt.boxplot(data, labels=["Local I/O", "Remote I/O"])
    plt.ylabel("Time (seconds)")
    plt.title("Distribution of I/O Times")
    plt.grid(True)

    plt.tight_layout()

    if output_file:
        plt.savefig(output_file)
        print(f"Visualization saved to {output_file}")
    else:
        plt.show()


def find_latest_results():
    """
    Find the latest local and remote results files
    """
    local_files = glob.glob("results/local_io_*.csv")
    remote_files = glob.glob("results/remote_io_*.csv")

    latest_local = max(local_files, key=os.path.getctime) if local_files else None
    latest_remote = max(remote_files, key=os.path.getctime) if remote_files else None

    return latest_local, latest_remote


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare local and remote I/O experiment results"
    )
    parser.add_argument("--local", help="Path to local I/O results CSV file")
    parser.add_argument("--remote", help="Path to remote I/O results CSV file")
    parser.add_argument("--output", help="Path to save visualization")

    args = parser.parse_args()

    # If files not specified, try to find the latest results
    if not args.local or not args.remote:
        latest_local, latest_remote = find_latest_results()

        if not args.local:
            args.local = latest_local

        if not args.remote:
            args.remote = latest_remote

    if not args.local or not args.remote:
        print(
            "Error: Could not find results files. Please specify them with --local and --remote."
        )
        exit(1)

    print(f"Comparing results from:")
    print(f"Local: {args.local}")
    print(f"Remote: {args.remote}")

    local_df, remote_df = load_results(args.local, args.remote)
    compare_results(local_df, remote_df)
    visualize_results(local_df, remote_df, args.output)
