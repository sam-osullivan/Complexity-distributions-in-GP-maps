import numpy as np
import os
import sys

# Function to convert sequences of numerical values into binary strings
def sol_str(q, file1):
    bin_str = []
    for j in range(1, len(q)):
        if q[j] <= q[j-1]:
            bin_str.append(0)
            file1.write(str(0))
        else:
            bin_str.append(1)
            file1.write(str(1))
    file1.write("\n")
    return bin_str

def main(input_dir, output_dir):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over all solution files in the input directory
    for solution_filename in os.listdir(input_dir):
        if solution_filename.startswith("solution") and solution_filename.endswith(".txt"):
            solution_file_path = os.path.join(input_dir, solution_filename)
            binary_file_path = os.path.join(output_dir, f"binary{solution_filename.split('solution')[1]}")

            try:
                # Reading the solution file
                with open(solution_file_path, "r") as fn:
                    arr = fn.read()
                    arrlist = arr.split("\n")
                    # Remove lines containing null characters
                    arrlist = [x for x in arrlist if '\x00' not in x]
                    arrlist = [float(x) for x in arrlist if x.strip()]  # Convert to float and remove empty strings

                # Open the binary file for writing
                with open(binary_file_path, "w") as file1:
                    sol_str(arrlist, file1)
            except ValueError as e:
                print(f"Error processing file {solution_file_path}: {e}")

    print('Done.')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python 2_binarize.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    main(input_dir, output_dir)
