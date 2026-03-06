import os
import sys
import warnings
from topomesh import TopoMesh

def calculate_opc(input_path, output_path, min_patch_size):
    try:
        # Load the .ply file
        mesh = TopoMesh(input_path)
        # Calculate OPC
        mesh.GenerateOPCR(min_patch_size)
        # Save the OPC result to the output path
        with open(output_path, 'w') as f:
            f.write(str(mesh.OPCR))
        print(f"OPC calculation completed. Result saved to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py input_file output_file min_patch_size")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    min_patch_size = int(sys.argv[3])

    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    # Calculate OPC for the single input file
    calculate_opc(input_file, output_file, min_patch_size)
