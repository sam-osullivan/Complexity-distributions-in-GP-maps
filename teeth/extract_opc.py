import os
import sys

def extract_opc_values(input_dir, output_file):
    try:
        with open(output_file, 'w') as outfile:
            outfile.write("Filename,OPC Value\n")
            for filename in os.listdir(input_dir):
                if filename.endswith('.txt'):
                    file_path = os.path.join(input_dir, filename)
                    with open(file_path, 'r') as infile:
                        opc_value = infile.read().strip()
                        outfile.write(f"{filename},{opc_value}\n")
        print(f"OPC values extracted and saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py input_dir")
        sys.exit(1)

    input_dir = sys.argv[1]

    # Check if the input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    # Define the output file path
    output_file = os.path.join(input_dir, 'opc_list.txt')

    # Extract OPC values and write to the output file
    extract_opc_values(input_dir, output_file)
