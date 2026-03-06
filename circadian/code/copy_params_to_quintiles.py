#!/usr/bin/env python3
"""
copy_params_to_quintiles.py

Copies parameter files to quintile subdirectories based on file numbers listed in G1-G5 directories.
Creates ./0param subdirectories and copies parametersXXXX.txt files there.

Usage:
    python3 copy_params_to_quintiles.py \
        --params-dir /path/to/parameters \
        --quintiles-dir /path/to/quintiles \
        --param-pattern "parameters{}.txt"
"""

import pandas as pd
import os
import shutil
import argparse
from pathlib import Path
import glob

def setup_arguments():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description='Copy parameter files to quintile subdirectories')
    
    parser.add_argument('--params-dir', type=str, required=True,
                       help='Directory containing parameter files (parametersXXXX.txt)')
    parser.add_argument('--quintiles-dir', type=str, required=True,
                       help='Directory containing G1-G5 subdirectories with file lists')
    parser.add_argument('--param-pattern', type=str, default='parameters{}.txt',
                       help='Pattern for parameter filenames with {} for number (default: parameters{}.txt)')
    parser.add_argument('--list-pattern', type=str, default='*_files.txt',
                       help='Pattern for quintile list files (default: *_files.txt)')
    
    return parser

def read_file_numbers_from_quintile(quintile_dir, list_pattern):
    """Read file numbers from a quintile directory's list file"""
    quintile_path = Path(quintile_dir)
    
    # Find the list file (e.g., G1_files.txt)
    list_files = list(quintile_path.glob(list_pattern))
    
    if not list_files:
        print(f"Warning: No list file found in {quintile_dir} matching pattern {list_pattern}")
        return set()
    
    if len(list_files) > 1:
        print(f"Warning: Multiple list files found in {quintile_dir}, using {list_files[0]}")
    
    list_file = list_files[0]
    
    try:
        # Read the TSV file
        df = pd.read_csv(list_file, sep='\t')
        
        if 'file_number' not in df.columns:
            print(f"Error: 'file_number' column not found in {list_file}")
            return set()
        
        file_numbers = set(df['file_number'].astype(int))
        print(f"✓ Read {len(file_numbers)} file numbers from {list_file.name}")
        return file_numbers
        
    except Exception as e:
        print(f"Error reading {list_file}: {e}")
        return set()

def main():
    # Parse arguments
    parser = setup_arguments()
    args = parser.parse_args()
    
    params_dir = Path(args.params_dir)
    quintiles_dir = Path(args.quintiles_dir)
    param_pattern = args.param_pattern
    list_pattern = args.list_pattern
    
    print(f"Parameter files directory: {params_dir}")
    print(f"Quintiles directory: {quintiles_dir}")
    print(f"Parameter file pattern: {param_pattern}")
    
    # Validate directories
    if not params_dir.exists():
        print(f"Error: Parameters directory not found: {params_dir}")
        return
    
    if not quintiles_dir.exists():
        print(f"Error: Quintiles directory not found: {quintiles_dir}")
        return
    
    # Find quintile subdirectories (G1, G2, G3, G4, G5)
    quintile_dirs = []
    for i in range(1, 6):
        group_dir = quintiles_dir / f"G{i}"
        if group_dir.exists() and group_dir.is_dir():
            quintile_dirs.append(group_dir)
        else:
            print(f"Warning: Quintile directory G{i} not found")
    
    if not quintile_dirs:
        print("Error: No quintile directories (G1-G5) found")
        return
    
    print(f"✓ Found {len(quintile_dirs)} quintile directories")
    
    # Build mapping: file_number -> quintile_directory
    file_to_quintile = {}
    
    for quintile_dir in quintile_dirs:
        file_numbers = read_file_numbers_from_quintile(quintile_dir, list_pattern)
        
        for file_num in file_numbers:
            if file_num in file_to_quintile:
                print(f"Warning: File {file_num} appears in multiple quintiles")
            file_to_quintile[file_num] = quintile_dir
    
    print(f"✓ Built mapping for {len(file_to_quintile)} unique file numbers")
    
    # Find all parameter files
    param_glob = params_dir / param_pattern.replace('{}', '*')
    param_files = list(params_dir.glob(param_pattern.replace('{}', '*')))
    
    print(f"✓ Found {len(param_files)} parameter files in {params_dir}")
    
    if not param_files:
        print(f"Warning: No parameter files found matching pattern {param_pattern} in {params_dir}")
        return
    
    # Copy files to appropriate quintile subdirectories
    copied_count = 0
    not_found_count = 0
    error_count = 0
    
    for param_file in param_files:
        # Extract file number from filename
        try:
            # Extract number from filename like "parameters1234.txt"
            stem = param_file.stem  # removes .txt
            if stem.startswith('parameters'):
                file_num_str = stem[len('parameters'):]
                file_num = int(file_num_str)
            else:
                print(f"Warning: Cannot parse file number from {param_file.name}")
                continue
            
        except ValueError:
            print(f"Warning: Cannot extract valid number from {param_file.name}")
            continue
        
        # Check if this file number is in our mapping
        if file_num not in file_to_quintile:
            not_found_count += 1
            continue
        
        # Get target quintile directory
        target_quintile = file_to_quintile[file_num]
        
        # Create 0param subdirectory
        param_subdir = target_quintile / "0param"
        param_subdir.mkdir(exist_ok=True)
        
        # Copy parameter file
        target_file = param_subdir / param_file.name
        
        try:
            shutil.copy2(param_file, target_file)
            copied_count += 1
            
            if copied_count % 100 == 0:
                print(f"   Copied {copied_count} files...")
                
        except Exception as e:
            print(f"Error copying {param_file} to {target_file}: {e}")
            error_count += 1
    
    # Summary
    print(f"\n📊 Copy Summary:")
    print(f"   Successfully copied: {copied_count} parameter files")
    print(f"   Not found in quintiles: {not_found_count} files")
    print(f"   Copy errors: {error_count} files")
    print(f"   Total processed: {len(param_files)} parameter files")
    
    # Show directory structure created
    print(f"\n📁 Directory structure created:")
    for quintile_dir in quintile_dirs:
        param_subdir = quintile_dir / "0param"
        if param_subdir.exists():
            file_count = len(list(param_subdir.glob('parameters*.txt')))
            print(f"   {quintile_dir.name}/0param/ - {file_count} parameter files")

if __name__ == "__main__":
    main()
