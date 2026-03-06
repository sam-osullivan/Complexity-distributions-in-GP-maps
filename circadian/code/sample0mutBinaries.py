#!/usr/bin/env python3
import glob
import os
import shutil
import random

# Set fixed seed for reproducibility
random.seed(42)

# Input and output directories
input_dir = '/mnt/users/osullivans/circ/oct24/t0to50/binary_out'
output_dir = '/mnt/users/osullivans/circ/oct24/t0to50/0_mut_binary'

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Dictionary to store unique binary strings and their source files
unique_binaries = {}

# Read all txt files
txt_files = glob.glob(os.path.join(input_dir, '*.txt'))
print(f"Processing {len(txt_files)} files...")

for file_path in txt_files:
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if content and content not in unique_binaries:
                unique_binaries[content] = file_path
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

print(f"Found {len(unique_binaries)} unique binary strings")

# Randomly sample one file for each unique binary string and copy
for i, (binary_string, source_file) in enumerate(unique_binaries.items()):
    filename = os.path.basename(source_file)
    dest_path = os.path.join(output_dir, filename)
    shutil.copy2(source_file, dest_path)

print(f"Copied {len(unique_binaries)} unique binary files to {output_dir}")
