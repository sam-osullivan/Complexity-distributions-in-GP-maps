#!/usr/bin/env python3
"""
make_0mut_table.py

Creates a 0_mut compiled table by filtering compiled_rand.txt to only include
rows where the file_number corresponds to files present in the 0_mut_binary directory.
"""

import os
import pandas as pd
import glob
import re

def main():
    # Define paths
    compiled_rand_file = "/mnt/users/osullivans/circ/oct24/t0to50/tables/t0to50_table.txt"
    mut_binary_dir = "/mnt/users/osullivans/circ/oct24/t0to50/0_mut_binary"
    output_file = "/mnt/users/osullivans/circ/oct24/t0to50/compiled_0mut.txt"
    
    # Check if compiled_rand.txt exists
    if not os.path.exists(compiled_rand_file):
        print(f"Error: {compiled_rand_file} not found. Please run the rand compilation script first.")
        return
    
    # Read the compiled_rand.txt file
    print("Reading compiled_rand.txt...")
    df_rand = pd.read_csv(compiled_rand_file, sep='\t')
    print(f"Loaded {len(df_rand)} rows from compiled_rand.txt")
    
    # Get all binary files in 0_mut_binary directory
    mut_binary_files = glob.glob(os.path.join(mut_binary_dir, "binary*.txt"))
    print(f"Found {len(mut_binary_files)} files in 0_mut_binary directory")
    
    # Extract file numbers from 0_mut binary filenames
    mut_file_numbers = set()
    for file_path in mut_binary_files:
        filename = os.path.basename(file_path)
        match = re.search(r'binary(\d+)\.txt', filename)
        if match:
            file_number = int(match.group(1))
            mut_file_numbers.add(file_number)
        else:
            print(f"Warning: Could not extract file number from {filename}")
    
    print(f"Extracted {len(mut_file_numbers)} unique file numbers from 0_mut_binary")
    
    # Filter compiled_rand.txt to only include rows with file_numbers in 0_mut set
    df_0mut = df_rand[df_rand['file_number'].isin(mut_file_numbers)]
    
    print(f"Filtered to {len(df_0mut)} rows matching 0_mut file numbers")
    
    # Check if we got all expected rows
    missing_count = len(mut_file_numbers) - len(df_0mut)
    if missing_count > 0:
        print(f"Warning: {missing_count} file numbers from 0_mut_binary not found in compiled_rand.txt")
        
        # Show which ones are missing
        found_numbers = set(df_0mut['file_number'].values)
        missing_numbers = mut_file_numbers - found_numbers
        if len(missing_numbers) <= 10:
            print(f"Missing file numbers: {sorted(missing_numbers)}")
        else:
            print(f"Missing file numbers (first 10): {sorted(list(missing_numbers))[:10]}")
    
    # Sort by file_number for consistent output
    df_0mut = df_0mut.sort_values('file_number')
    
    # Write output file
    df_0mut.to_csv(output_file, sep='\t', index=False)
    print(f"Output written to: {output_file}")
    
    # Print statistics
    print(f"\nStatistics:")
    print(f"Original rand data: {len(df_rand)} rows")
    print(f"0_mut binary files: {len(mut_file_numbers)} files")
    print(f"Final 0_mut data: {len(df_0mut)} rows")
    
    # Show sample of output data
    print(f"\nSample 0_mut data (first 5 rows):")
    print(df_0mut.head().to_string(index=False))
    
    # Print complexity statistics
    if len(df_0mut) > 0:
        print(f"\nComplexity statistics:")
        print(f"Mean complexity (0_mut): {df_0mut['complexity_entropy'].mean():.2f}")
        print(f"Mean complexity (rand): {df_rand['complexity_entropy'].mean():.2f}")
        print(f"Min complexity (0_mut): {df_0mut['complexity_entropy'].min():.2f}")
        print(f"Max complexity (0_mut): {df_0mut['complexity_entropy'].max():.2f}")

if __name__ == "__main__":
    main()
