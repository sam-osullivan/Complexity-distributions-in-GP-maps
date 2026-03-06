#!/usr/bin/env python3
"""
create_complexity_quintiles.py

Splits a complexity table into 5 quintiles based on complexity_entropy values.
G1 = lowest complexity (bottom 20%)
G5 = highest complexity (top 20%)

Usage:
    python3 create_complexity_quintiles.py \
        --input /path/to/table.txt \
        --output-dir /path/to/output \
        --samples-per-group 2000
"""

import pandas as pd
import numpy as np
import os
import argparse
from pathlib import Path

def setup_arguments():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description='Create complexity quintile groups from table data')
    
    parser.add_argument('--input', type=str, required=True,
                       help='Path to input table file (TSV format)')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='Base output directory (subdirectories G1-G5 will be created)')
    parser.add_argument('--samples-per-group', type=int, default=2000,
                       help='Number of samples per quintile group (default: 2000)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for sampling (default: 42)')
    
    return parser

def main():
    # Parse arguments
    parser = setup_arguments()
    args = parser.parse_args()
    
    input_file = args.input
    output_dir = Path(args.output_dir)
    samples_per_group = args.samples_per_group
    
    # Set random seed for reproducible sampling
    np.random.seed(args.seed)
    
    print(f"Loading data from: {input_file}")
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    try:
        # Read the data
        df = pd.read_csv(input_file, sep='\t')
        print(f"✓ Loaded {len(df)} rows")
        
        # Check required columns
        required_cols = ['file_number', 'complexity_entropy']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"Error: Missing required columns: {missing_cols}")
            print(f"Available columns: {list(df.columns)}")
            return
        
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    # Sort by complexity (ascending)
    df_sorted = df.sort_values('complexity_entropy').reset_index(drop=True)
    total_rows = len(df_sorted)
    
    print(f"✓ Data sorted by complexity_entropy")
    print(f"   Complexity range: {df_sorted['complexity_entropy'].min():.2f} to {df_sorted['complexity_entropy'].max():.2f}")
    
    # Calculate quintile boundaries (20% each)
    quintile_size = total_rows // 5
    
    # Define quintiles
    quintiles = []
    for i in range(5):
        start_idx = i * quintile_size
        if i == 4:  # Last quintile gets any remaining rows
            end_idx = total_rows
        else:
            end_idx = (i + 1) * quintile_size
        
        quintile_data = df_sorted.iloc[start_idx:end_idx]
        group_name = f"G{i+1}"
        
        # Sample the requested number of rows from this quintile
        if len(quintile_data) >= samples_per_group:
            sampled_data = quintile_data.sample(n=samples_per_group, random_state=args.seed + i)
        else:
            print(f"Warning: {group_name} has only {len(quintile_data)} rows, using all available")
            sampled_data = quintile_data
        
        quintiles.append((group_name, sampled_data))
        
        print(f"   {group_name}: complexity {quintile_data['complexity_entropy'].min():.2f} - {quintile_data['complexity_entropy'].max():.2f}, "
              f"sampled {len(sampled_data)} rows")
    
    # Create output directories and save files
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for group_name, group_data in quintiles:
        # Create subdirectory
        group_dir = output_dir / group_name
        group_dir.mkdir(exist_ok=True)
        
        # Prepare output data (file_number and complexity_entropy only)
        output_data = group_data[['file_number', 'complexity_entropy']].copy()
        
        # Save to file
        output_file = group_dir / f"{group_name}_files.txt"
        output_data.to_csv(output_file, sep='\t', index=False)
        
        print(f"✅ Saved {group_name}: {len(output_data)} rows to {output_file}")
        
        # Print sample statistics
        complexity_mean = group_data['complexity_entropy'].mean()
        complexity_std = group_data['complexity_entropy'].std()
        print(f"   {group_name} stats: mean={complexity_mean:.2f}, std={complexity_std:.2f}")
    
    print(f"\n🎯 Summary:")
    print(f"   Created 5 quintile groups in: {output_dir}")
    print(f"   G1 = lowest complexity (bottom 20%)")
    print(f"   G5 = highest complexity (top 20%)")
    print(f"   Each group sampled to {samples_per_group} files (or all available)")
    
    # Overall statistics
    print(f"\n📊 Overall complexity distribution:")
    print(f"   Total samples: {total_rows}")
    print(f"   Min complexity: {df_sorted['complexity_entropy'].min():.2f}")
    print(f"   Max complexity: {df_sorted['complexity_entropy'].max():.2f}")
    print(f"   Mean complexity: {df_sorted['complexity_entropy'].mean():.2f}")
    print(f"   Median complexity: {df_sorted['complexity_entropy'].median():.2f}")

if __name__ == "__main__":
    main()
