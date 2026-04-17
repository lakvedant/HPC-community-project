#!/usr/bin/env python3
import subprocess
import re
import matplotlib.pyplot as plt
import os
import sys

DATASETS = ["facebook", "email", "twitter"]
MPI_PROCS = [1, 2, 4]

def run_cmd(cmd):
    try:
        # Run standard python since conda might have issues if run inside subprocess
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running: {cmd}")
        print(e.stderr)
        return ""

def main():
    print("====================================")
    print(" HPC LOUVAIN AUTOMATED BENCHMARKING ")
    print("====================================\n")
    
    # 1. Compile the code
    print("-> Compiling C executable...")
    # Conda's mpicc might be needed. If standard make fails, we rely on user's terminal environment.
    run_cmd("make clean && make")
    
    results = {
        "facebook": {"serial": 0, "parallel": {}},
        "email": {"serial": 0, "parallel": {}},
        "twitter": {"serial": 0, "parallel": {}}
    }

    for dataset in DATASETS:
        print(f"\n--- Testing Dataset: {dataset.upper()} ---")
        
        # 2. Fetch data if missing
        txt_file = f"{dataset}.txt"
        clean_file = f"{dataset}_clean.txt"
        
        if not os.path.exists(txt_file):
            print(f"  Fetching {dataset} dataset...")
            run_cmd(f"{sys.executable} scripts/fetch_data.py {dataset}")
            
        if not os.path.exists(clean_file):
            print(f"  Normalizing node IDs for {dataset}...")
            run_cmd(f"{sys.executable} scripts/normalize.py {txt_file} {clean_file}")
            
        serial_time = None
        
        # 3. Parameter Sweep
        for np in MPI_PROCS:
            print(f"  Running {dataset} with MPI processes: {np} ...")
            cmd = f"mpirun -np {np} ./louvain {clean_file}"
            out = run_cmd(cmd)
            
            # Parse output
            # Example: "Serial Runtime: 0.010s"
            if not serial_time:
                s_match = re.search(r'Serial Runtime:\s*([0-9\.]+)s', out)
                if s_match:
                    serial_time = float(s_match.group(1))
                    results[dataset]["serial"] = serial_time
            
            p_match = re.search(r'Parallel Runtime:\s*([0-9\.]+)s', out)
            if p_match:
                p_time = float(p_match.group(1))
                results[dataset]["parallel"][np] = p_time
                print(f"    -> Serial: {serial_time}s | Parallel({np}): {p_time}s")
            else:
                print("    -> Error: Could not parse runtime.")
                results[dataset]["parallel"][np] = 0

    # 4. Generate Visualizations
    print("\nGenerating benchmark visualizations...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Scalability (Line graph)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    for i, dataset in enumerate(DATASETS):
        runtimes = [results[dataset]["parallel"].get(np, 0) for np in MPI_PROCS]
        ax1.plot(MPI_PROCS, runtimes, marker='o', linewidth=2, color=colors[i], label=f"{dataset} (Parallel)")
        # Plot dotted line for serial baseline
        s_time = results[dataset]["serial"]
        ax1.axhline(y=s_time, color=colors[i], linestyle='--', alpha=0.5, label=f"{dataset} (Serial)")

    ax1.set_xticks(MPI_PROCS)
    ax1.set_xlabel("Number of MPI Processes (-np)")
    ax1.set_ylabel("Execution Time (seconds)")
    ax1.set_yscale('log') # Use log scale because dataset sizes vary vastly
    ax1.set_title("MPI Scalability & Parallel Overhead Analysis")
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
    ax1.grid(True, which="both", ls="--", alpha=0.2)

    # Plot 2: Speedup Comparison (Bar chart)
    # Compare Serial vs Parallel (np=4)
    bar_width = 0.35
    index = range(len(DATASETS))
    
    serial_times = [results[d]["serial"] for d in DATASETS]
    parallel_times = [results[d]["parallel"].get(4, 0) for d in DATASETS]
    
    ax2.bar(index, serial_times, bar_width, label='Serial', color='#3F2965')
    ax2.bar([i + bar_width for i in index], parallel_times, bar_width, label='Parallel (np=4)', color='#FFC107')
    
    ax2.set_xlabel('Datasets')
    ax2.set_ylabel('Execution Time (seconds)')
    ax2.set_yscale('log')
    ax2.set_title('Serial vs Parallel (np=4) Performance')
    ax2.set_xticks([i + bar_width/2 for i in index])
    ax2.set_xticklabels([d.capitalize() for d in DATASETS])
    ax2.legend()
    ax2.grid(True, axis='y', ls="--", alpha=0.2)

    plt.tight_layout()
    output_img = "benchmark_results.png"
    plt.savefig(output_img, dpi=200)
    print(f"\nAll tests finished successfully! Visualization saved to: {output_img}")

if __name__ == "__main__":
    main()
