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
        print("Usage: python script.py input_dir output_dir min_patch_size")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    min_patch_size = int(sys.argv[3])

    # Check if the input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate over all .ply files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.ply'):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + '_opc.txt'
            output_path = os.path.join(output_dir, output_filename)
            calculate_opc(input_path, output_path, min_patch_size)
