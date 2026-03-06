#!/usr/bin/env python3
"""
sequential_mutations.py

Sequentially mutates parameter files through multiple generations.
Creates 2param, 3param, 4param, ... up to 10param directories.

Usage:
    python3 sequential_mutations.py --base-dir /path/to/plot_b --max-generation 10
"""

import os
import subprocess
import argparse
from pathlib import Path

def setup_arguments():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description='Run sequential mutations through multiple generations')
    
    parser.add_argument('--base-dir', type=str, required=True,
                       help='Base directory containing G1-G5 subdirectories')
    parser.add_argument('--max-generation', type=int, default=10,
                       help='Maximum generation number (default: 10)')
    parser.add_argument('--start-generation', type=int, default=2,
                       help='Starting generation number (default: 2)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show commands without executing them')
    
    return parser

def run_mutation(base_dir, group, input_gen, output_gen, seed, dry_run=False):
    """Run mutation for a specific group and generation"""
    
    input_dir = base_dir / group / f"{input_gen}param"
    output_dir = base_dir / group / f"{output_gen}param"
    
    # Check if input directory exists
    if not input_dir.exists():
        print(f"❌ Warning: {input_dir} does not exist, skipping...")
        return False
    
    # Build command
    cmd = [
        'python3', 'mutate_params.py',
        '--input', str(input_dir),
        '--output', str(output_dir),
        '--seed', str(seed),
        '--overwrite'
    ]
    
    if dry_run:
        print(f"🔍 Would run: {' '.join(cmd)}")
        return True
    
    try:
        print(f"🔄 {group}: {input_gen}param → {output_gen}param (seed: {seed})")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
        
        if result.returncode == 0:
            print(f"✅ {group} generation {output_gen} completed successfully")
            return True
        else:
            print(f"❌ Error in {group} generation {output_gen}:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception running {group} generation {output_gen}: {e}")
        return False

def main():
    # Parse arguments
    parser = setup_arguments()
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    max_gen = args.max_generation
    start_gen = args.start_generation
    
    print(f"Sequential mutations: {start_gen}param through {max_gen}param")
    print(f"Base directory: {base_dir}")
    print(f"Dry run: {args.dry_run}")
    
    # Validate base directory
    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_dir}")
        return
    
    # Define groups and seed patterns
    groups = ['G1', 'G2', 'G3', 'G4', 'G5']
    
    # Check that all groups have the starting generation
    missing_groups = []
    for group in groups:
        start_dir = base_dir / group / f"{start_gen-1}param"
        if not start_dir.exists():
            missing_groups.append(f"{group}/{start_gen-1}param")
    
    if missing_groups:
        print(f"Error: Missing starting directories: {missing_groups}")
        return
    
    # Run sequential mutations
    total_success = 0
    total_attempts = 0
    
    for generation in range(start_gen, max_gen + 1):
        input_gen = generation - 1
        output_gen = generation
        
        print(f"\n{'='*60}")
        print(f"GENERATION {output_gen}: Mutating {input_gen}param → {output_gen}param")
        print(f"{'='*60}")
        
        gen_success = 0
        
        for i, group in enumerate(groups, 1):
            # Generate seed: generation * 1000 + group_number * 100 + base
            seed = generation * 1000 + i * 100 + 1
            
            success = run_mutation(base_dir, group, input_gen, output_gen, seed, args.dry_run)
            total_attempts += 1
            
            if success:
                gen_success += 1
                total_success += 1
        
        print(f"\nGeneration {output_gen} summary: {gen_success}/{len(groups)} groups successful")
        
        if gen_success == 0:
            print(f"❌ No successful mutations in generation {output_gen}, stopping...")
            break
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Total successful mutations: {total_success}/{total_attempts}")
    print(f"Generations processed: {start_gen} through {max_gen}")
    
    if not args.dry_run:
        print(f"\nDirectory structure created:")
        for group in groups:
            group_dir = base_dir / group
            param_dirs = sorted([d.name for d in group_dir.iterdir() 
                               if d.is_dir() and d.name.endswith('param')])
            print(f"  {group}: {', '.join(param_dirs)}")

if __name__ == "__main__":
    main()
