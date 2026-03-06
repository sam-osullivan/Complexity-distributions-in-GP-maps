#!/usr/bin/env python3
import numpy as np
import os
import sys
from pathlib import Path

def main():
    # Check if input file is provided as command-line argument
    if len(sys.argv) < 2:
        print("Usage: python3 mean_opc_scaled_and_simple.py <input_file>")
        print("Example: python3 mean_opc_scaled_and_simple.py RandOPCandCusp.txt")
        return
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return

    # Read OPC values and Cusp values from the input file
    complexities = []
    cusp_values = set()
    
    with open(input_file, 'r') as f:
        header = f.readline()  # Skip header
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                try:
                    cusp = int(parts[1])
                    opc = float(parts[2])
                    cusp_values.add(cusp)
                    complexities.append(opc)
                except ValueError:
                    print(f"Warning: Could not parse values in line: {line.strip()}")

    if not complexities:
        print(f"Error: No valid OPC values found in {input_file}")
        return

    complexities = np.array(complexities)
    print(f"Found {len(complexities)} OPC values")

    # Calculate simple mean
    simple_mean = np.mean(complexities)
    print(f"Simple mean: {simple_mean}")

    # Count unique cusp patterns
    N_unique = len(cusp_values)
    print(f"Found {N_unique} unique Cusp values")

    if N_unique == 0:
        print("Error: No unique Cusp values found")
        return

    # Calculate scaled mean using the formula
    min_complexity = np.min(complexities)
    max_complexity = np.max(complexities)

    print(f"Min OPC: {min_complexity}")
    print(f"Max OPC: {max_complexity}")

    if max_complexity == min_complexity:
        print("Warning: All OPC values are the same, scaled mean will be 0")
        scaled_mean = 0.0
    else:
        log2_N_unique = np.log2(N_unique)
        scaled_complexities = log2_N_unique * (complexities - min_complexity) / (max_complexity - min_complexity)
        scaled_mean = np.mean(scaled_complexities)

    print(f"Scaled mean: {scaled_mean}")

    # Save simple mean in current directory
    simple_mean_file = Path("simple_mean.txt")
    with open(simple_mean_file, 'w') as f:
        f.write(str(simple_mean))
    print(f"Saved simple mean to {simple_mean_file.resolve()}")

    # Save scaled mean in current directory
    scaled_mean_file = Path("scaled_mean.txt")
    with open(scaled_mean_file, 'w') as f:
        f.write(str(scaled_mean))
    print(f"Saved scaled mean to {scaled_mean_file.resolve()}")

    print("Done!")

if __name__ == "__main__":
    main()
