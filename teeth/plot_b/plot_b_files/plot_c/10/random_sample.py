#!/usr/bin/env python3
import sys
import random

def main():
    # Check if arguments are provided
    if len(sys.argv) < 4:
        print("Usage: python3 random_sample.py <input_file> <output_file> <num_rows>")
        print("Example: python3 random_sample.py RandOPCandCusp.txt 103OPCandCusp.txt 1000")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    num_rows = int(sys.argv[3])
    
    # Read the input file
    with open(input_file, 'r') as f:
        header = f.readline()
        data_lines = f.readlines()
    
    print(f"Total rows in input file: {len(data_lines)}")
    
    # Check if we have enough rows
    if num_rows > len(data_lines):
        print(f"Warning: Requested {num_rows} rows but only {len(data_lines)} available.")
        print(f"Using all {len(data_lines)} rows.")
        num_rows = len(data_lines)
    
    # Randomly sample the specified number of rows
    sampled_lines = random.sample(data_lines, num_rows)
    
    # Write to output file
    with open(output_file, 'w') as f:
        f.write(header)  # Write the header first
        f.writelines(sampled_lines)
    
    print(f"Randomly selected {num_rows} rows and saved to {output_file}")
    print("Done!")

if __name__ == "__main__":
    main()
