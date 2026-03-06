#!/usr/bin/env python3
"""
Script to assemble compiled_rand.txt from separate data files.

Combines data from:
- params_out/: genotype data (indices_temp values)
- binaries_out/: phenotype binary strings
- LZ_values/: complexity entropy values
"""

import os
import glob
import re
from pathlib import Path


def extract_genotype_from_params(file_path):
    """Extract indices_temp list from parameters file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Look for indices_temp line
        match = re.search(r'indices_temp = \[(.*?)\]', content)
        if match:
            # Extract the numbers and convert to list
            numbers_str = match.group(1)
            # Split by comma and clean up whitespace
            numbers = [int(x.strip()) for x in numbers_str.split(',')]
            return numbers
        else:
            print(f"Warning: indices_temp not found in {file_path}")
            return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def extract_phenotype_from_binary(file_path):
    """Extract binary string from binary file."""
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def extract_complexity_from_lz(file_path):
    """Extract complexity value from LZ file."""
    try:
        with open(file_path, 'r') as f:
            return float(f.read().strip())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def main():
    # Define directories
    params_dir = "/mnt/users/osullivans/circ/oct24/t0to50/parameters"
    binary_dir = "/mnt/users/osullivans/circ/oct24/t0to50/binary_out"
    lz_dir = "/mnt/users/osullivans/circ/oct24/t0to50/lz_values"

    output_file = "/mnt/users/osullivans/circ/oct24/t0to50/tables/t0to50_table.txt"

    # Get all parameter files
    param_files = glob.glob(os.path.join(params_dir, "parameters*.txt"))
    print(f"Found {len(param_files)} parameter files")

    # Prepare output data
    output_data = []

    # Process each parameter file
    for param_file in sorted(param_files):
        # Extract file number from filename
        filename = os.path.basename(param_file)
        file_number_match = re.search(r'parameters(\d+)\.txt', filename)

        if not file_number_match:
            print(f"Warning: Could not extract file number from {filename}")
            continue

        file_number = int(file_number_match.group(1))

        # Construct corresponding file paths
        binary_file = os.path.join(binary_dir, f"binary{file_number}.txt")
        lz_file = os.path.join(lz_dir, f"k{file_number}.txt")

        # Check if all files exist
        if not all([os.path.exists(f) for f in [param_file, binary_file, lz_file]]):
            missing = [f for f in [param_file, binary_file, lz_file] if not os.path.exists(f)]
            print(f"Warning: Missing files for {file_number}: {missing}")
            continue

        # Extract data from each file
        genotype_raw = extract_genotype_from_params(param_file)
        phenotype_binary = extract_phenotype_from_binary(binary_file)
        complexity_entropy = extract_complexity_from_lz(lz_file)

        # Check if all extractions were successful
        if genotype_raw is None or phenotype_binary is None or complexity_entropy is None:
            print(f"Warning: Failed to extract data for file number {file_number}")
            continue

        # Convert genotype list to comma-separated string
        genotype_str = ','.join(map(str, genotype_raw))

        # Add to output data
        output_data.append([file_number, genotype_str, phenotype_binary, complexity_entropy])

    print(f"Successfully processed {len(output_data)} files")

    # Write output file
    with open(output_file, 'w') as f:
        # Write header
        f.write("file_number\tgenotype_raw\tphenotype_binary\tcomplexity_entropy\n")
        # Write data rows
        for row in output_data:
            f.write(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\n")

    print(f"Output written to: {output_file}")

    # Print some sample data for verification
    print("\nSample data (first 5 rows):")
    print("file_number\tgenotype_raw\tphenotype_binary\tcomplexity_entropy")
    for i, row in enumerate(output_data[:5]):
        print(f"{row[0]}\t{row[1][:20]}...\t{row[2]}\t{row[3]}")


if __name__ == "__main__":
    main()
