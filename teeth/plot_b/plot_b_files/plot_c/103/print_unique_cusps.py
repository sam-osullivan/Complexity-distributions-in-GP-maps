#!/usr/bin/env python3
import os
import sys

def main():
    # Check if input file is provided
    if len(sys.argv) < 2:
        print("Usage: python3 print_unique_cusps.py <input_file>")
        print("Example: python3 print_unique_cusps.py RandOPCandCusp.txt")
        return

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return

    cusp_values = set()

    with open(input_file, 'r') as f:
        header = f.readline()  # Skip header
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    cusp = int(parts[1])
                    cusp_values.add(cusp)
                except ValueError:
                    print(f"Warning: Could not parse cusp value in line: {line.strip()}")

    N_unique = len(cusp_values)
    print(f"N_unique = {N_unique}")

    if N_unique == 0:
        print("Warning: No unique Cusp values found")

if __name__ == "__main__":
    main()
