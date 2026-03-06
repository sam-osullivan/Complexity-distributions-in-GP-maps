#!/usr/bin/env python3
# tooth_entropy.py — Shannon entropy of cusp value distribution
# Usage: python3 tooth_entropy.py <input_file> <output_file>
#
# Reads:  <input_file>             (compiled file with ID, Cusps, OPC columns)
# Writes: <output_file>            (one line: cusp entropy with 3 decimals)
# Also writes: cusp_distribution.txt  (list of cusp values and their frequencies)

import os
import sys
import numpy as np
from collections import Counter

def shannon_entropy(frequencies):
    """
    Calculate Shannon entropy from frequency counts.
    
    Parameters:
    -----------
    frequencies : array-like
        Frequency counts for each unique pattern
        
    Returns:
    --------
    float
        Shannon entropy in bits
    """
    frequencies = np.array(frequencies)
    frequencies = frequencies[frequencies > 0]  # Remove zero frequencies
    
    if len(frequencies) == 0:
        return 0.0
    
    total = np.sum(frequencies)
    probabilities = frequencies / total
    entropy = -np.sum(probabilities * np.log2(probabilities))
    
    print(f"Total unique cusp values: {len(frequencies)}")
    print(f"Total data points: {total}")
    print(f"S = {round(entropy, 3)}")
    
    return entropy

def calculate_cusp_entropy(input_file: str, output_file: str) -> None:
    """
    Calculate entropy of the distribution of cusp values.
    """
    if not os.path.isfile(input_file):
        print(f"Error: input file not found: {input_file}")
        sys.exit(1)
    
    # Count occurrences of each unique cusp value
    cusp_counts = Counter()
    processed_rows = 0
    invalid_rows = 0
    invalid_ids = []  # Track invalid row IDs
    
    print(f"Reading cusp data from: {input_file}")
    
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            print("Error: Input file appears empty or has no data rows")
            sys.exit(1)
        
        # Parse header
        header = lines[0].strip()
        print(f"Header: {header}")
        
        # Find column indices
        header_parts = header.split()
        try:
            id_col = header_parts.index('ID')
            cusps_col = header_parts.index('Cusps')
        except ValueError as e:
            print(f"Error: Could not find required columns (ID, Cusps) in header: {e}")
            sys.exit(1)
        
        # Process data rows
        for i, line in enumerate(lines[1:], 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('\t')  # Try tab-separated first
            if len(parts) < 3:
                parts = line.split()  # Fallback to space-separated
            
            if len(parts) < 3:
                print(f"Warning: Line {i+1} has insufficient columns: {line}")
                invalid_rows += 1
                continue
            
            try:
                id_val = int(parts[id_col])
                cusps_val = int(parts[cusps_col])
                
                # Count this cusp value
                cusp_counts[cusps_val] += 1
                processed_rows += 1
                
                # Progress indicator
                if processed_rows % 10000 == 0:
                    print(f"Processed {processed_rows} rows...")
                    
            except ValueError as e:
                print(f"Warning: Could not parse line {i+1}: {line} - {e}")
                invalid_rows += 1
                # Try to extract ID for tracking
                try:
                    invalid_ids.append(parts[0])
                except:
                    invalid_ids.append(f"line_{i+1}")
                continue
    
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Save invalid IDs to file
    invalid_ids_file = os.path.join(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', 'invalid_cusp_ids.txt')
    with open(invalid_ids_file, 'w') as f:
        for id_val in invalid_ids:
            f.write(f"{id_val}\n")
    
    print(f"Saved {len(invalid_ids)} invalid row IDs to: {invalid_ids_file}")
    
    if not cusp_counts:
        print("Error: No valid cusp data found!")
        sys.exit(1)
    
    print(f"\nDataset summary:")
    print(f"Valid rows processed: {processed_rows}")
    print(f"Invalid rows skipped: {invalid_rows}")
    print(f"Unique cusp values found: {len(cusp_counts)}")
    
    # Show cusp distribution
    sorted_cusps = sorted(cusp_counts.items())
    
    print(f"\nCusp value distribution:")
    for cusp_val, count in sorted_cusps:
        print(f"  {cusp_val} cusps: {count} samples")
    
    # Save cusp distribution to file
    cusp_dist_file = os.path.join(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', 'cusp_distribution.txt')
    with open(cusp_dist_file, 'w') as f:
        f.write("Cusp_Value\tFrequency\n")
        for cusp_val, count in sorted_cusps:
            f.write(f"{cusp_val}\t{count}\n")
    
    print(f"Cusp distribution saved to: {cusp_dist_file}")
    
    # Calculate entropy of the cusp distribution
    frequencies = list(cusp_counts.values())
    entropy_val = shannon_entropy(frequencies)
    
    # Write result to output file
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    with open(output_file, "w") as out:
        out.write(f"{entropy_val:.3f}\n")
    
    print(f"\nCusp entropy saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 tooth_entropy.py <input_file> <output_file>")
        print("Example: python3 tooth_entropy.py ./1000_compiledOPCandcusp.txt ./entropy/cusp_entropy.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    calculate_cusp_entropy(input_file, output_file)
