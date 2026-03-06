import re
import os
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Combine OPC and cusp data into a single file.")
parser.add_argument("opc_file", help="Path to the OPC file")
parser.add_argument("cusp_file", help="Path to the cusp file")
args = parser.parse_args()

# Paths to input files
opc_file_path = args.opc_file
cusp_file_path = args.cusp_file

# Determine the output file path (same directory as input files)
output_dir = os.path.dirname(opc_file_path)
output_file_path = os.path.join(output_dir, "cusp_opc.txt")

# Function to extract the Tooth Name from the Filename
def extract_tooth_name(filename):
    match = re.search(r"9000_(\d+)", filename)
    if match:
        return match.group(1)
    return None

# Read OPC file and create a dictionary
opc_dict = {}
with open(opc_file_path, 'r') as opc_file:
    next(opc_file)  # Skip header line
    for line in opc_file:
        filename, opc_value = line.strip().split(',')
        tooth_name = extract_tooth_name(filename)
        if tooth_name:
            opc_dict[tooth_name] = opc_value

# Open output file for writing
with open(output_file_path, 'w') as output_file:
    # Write header
    output_file.write("Tooth Name\tRADIANS\tDEGREES\tNOTES\tREAL CUSPS\tFAILS INHIB?\tOPC Value\n")

    # Read the cusp file and write combined data to the output file
    with open(cusp_file_path, 'r') as cusp_file:
        next(cusp_file)  # Skip header line
        for line in cusp_file:
            parts = line.strip().split('\t')
            tooth_name = parts[0]
            if tooth_name in opc_dict:
                opc_value = opc_dict[tooth_name]
                radians = parts[1] if len(parts) > 1 else ""
                degrees = parts[2] if len(parts) > 2 else ""
                notes = parts[3] if len(parts) > 3 else ""
                real_cusps = parts[4] if len(parts) > 4 else ""
                fails_inhib = parts[5] if len(parts) > 5 else ""
                output_file.write(f"{tooth_name}\t{radians}\t{degrees}\t{notes}\t{real_cusps}\t{fails_inhib}\t{opc_value}\n")

print(f"File successfully created: {output_file_path}")
