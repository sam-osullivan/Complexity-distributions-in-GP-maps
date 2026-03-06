#!/usr/bin/env python3
"""
calculate_mean_opc.py - Calculate mean OPC value from compiled data

Usage: python3 calculate_mean_opc.py <input_file> <output_file>

Arguments:
    input_file  - Path to compiled data file (ID, Cusps, OPC columns)
    output_file - Path for output file (will contain mean OPC value)

Example:
    python3 calculate_mean_opc.py ./1000_compiledOPCandcusp.txt ./mean_opc.txt
"""

import os
import sys
import numpy as np

def calculate_mean_opc(input_file: str, output_file: str) -> None:
    """
    Calculate mean OPC value from compiled data file.
    """
    if not os.path.isfile(input_file):
        print(f"Error: input file not found: {input_file}")
        sys.exit(1)
    
    print(f"Reading OPC data from: {input_file}")
    
    opc_values = []
    processed_rows = 0
    invalid_rows = 0
    
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            print("Error: Input file appears empty or has no data rows")
            sys.exit(1)
        
        # Parse header
        header = lines[0].strip()
        print(f"Header: {header}")
        
        # Find OPC column index
        header_parts = header.split()
        try:
            opc_col = header_parts.index('OPC')
        except ValueError as e:
            print(f"Error: Could not find OPC column in header: {e}")
            sys.exit(1)
        
        print(f"OPC column found at index: {opc_col}")
        
        # Process data rows
        for i, line in enumerate(lines[1:], 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('\t')  # Try tab-separated first
            if len(parts) < 3:
                parts = line.split()  # Fallback to space-separated
            
            if len(parts) <= opc_col:
                print(f"Warning: Line {i+1} has insufficient columns: {line}")
                invalid_rows += 1
                continue
            
            try:
                opc_val = float(parts[opc_col])
                opc_values.append(opc_val)
                processed_rows += 1
                
                # Progress indicator
                if processed_rows % 10000 == 0:
                    print(f"Processed {processed_rows} rows...")
                    
            except ValueError as e:
                print(f"Warning: Could not parse OPC value on line {i+1}: {line} - {e}")
                invalid_rows += 1
                continue
    
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    if not opc_values:
        print("Error: No valid OPC values found!")
        sys.exit(1)
    
    # Calculate statistics
    opc_array = np.array(opc_values)
    mean_opc = np.mean(opc_array)
    std_opc = np.std(opc_array)
    min_opc = np.min(opc_array)
    max_opc = np.max(opc_array)
    
    print(f"\nOPC Statistics:")
    print(f"Valid rows processed: {processed_rows}")
    print(f"Invalid rows skipped: {invalid_rows}")
    print(f"Mean OPC: {mean_opc:.6f}")
    print(f"Standard deviation: {std_opc:.6f}")
    print(f"Range: {min_opc:.6f} to {max_opc:.6f}")
    
    # Write result to output file
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    with open(output_file, "w") as out:
        out.write(f"{mean_opc:.6f}\n")
    
    print(f"\nMean OPC saved to: {output_file}")

def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("Calculate Mean OPC Script")
    print("-" * 25)
    
    calculate_mean_opc(input_file, output_file)
    
    print("\nScript completed successfully!")

if __name__ == "__main__":
    main()
