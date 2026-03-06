import os
import sys
import numpy as np
import math
from collections import defaultdict

# Function to read .off file and extract vertices and faces
def read_off_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    if lines[0].strip() not in ['OFF', 'COFF']:
        raise ValueError("The file is not in OFF or COFF format.")

    header = lines[1].strip().split()
    num_vertices = int(header[0])
    num_faces = int(header[1])

    vertices = []
    for i in range(2, 2 + num_vertices):
        vertex_data = list(map(float, lines[i].strip().split()))
        vertices.append([round(coord, 6) for coord in vertex_data[:3]])  # Round to 6 decimal places

    faces = []
    for i in range(2 + num_vertices, 2 + num_faces):
        faces.append(list(map(int, lines[i].strip().split()[1:])))

    return vertices, faces

# Function to find cusps (local maxima)
def find_cusps(vertices, faces):
    vertex_heights = [-v[2] for v in vertices]  # Using negative z-coordinate as height
    adjacency_list = defaultdict(set)

    for face in faces:
        for i in range(len(face)):
            adjacency_list[face[i]].add(face[(i + 1) % len(face)])
            adjacency_list[face[i]].add(face[(i - 1) % len(face)])

    cusps = []
    epsilon = 0.0001

    # Find the leftmost and rightmost x coordinates
    x_coords = [v[0] for v in vertices]
    leftmost_x = min(x_coords)
    rightmost_x = max(x_coords)

    for i, height in enumerate(vertex_heights):
        # Skip the leftmost and rightmost points
        if vertices[i][0] == leftmost_x or vertices[i][0] == rightmost_x:
            continue

        is_maxima = True
        for neighbor in adjacency_list[i]:
            if abs(vertex_heights[neighbor] - height) < epsilon:
                continue
            elif vertex_heights[neighbor] > height:
                is_maxima = False
                break

        if is_maxima and len(adjacency_list[i]) > 2:
            # Check if the maximum z-distance between neighboring vertices is greater than 0.5
            neighbor_indices = adjacency_list[i]
            max_z_distance = 0
            for neighbor_index in neighbor_indices:
                neighbor = vertices[neighbor_index]
                z_distance = abs(height - (-neighbor[2]))
                if z_distance > max_z_distance:
                    max_z_distance = z_distance
            if max_z_distance > 0.5:
                cusps.append(vertices[i])

    return cusps

# Function to read local maxima from file
def read_local_maxima(infile):
    data = []
    with open(infile, 'r') as in_file:
        header = in_file.readline().strip().split()
        if header != ["X", "Y", "Z"]:
            raise ValueError("Error: Cannot recognize input file format.")
        for line in in_file:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            data.append([float(parts[0]), float(parts[1]), float(parts[2])])
    return data

# Function to get individual cusps
def get_individual_cusps(data):
    if not data:
        return None, []

    # Calculate and print Euclidean distances for debugging
    distances = [math.sqrt(data[i][0]**2 + data[i][1]**2 + data[i][2]**2) for i in range(len(data))]
    for i, dist in enumerate(distances):
        print(f"Cusp {i} coordinates: {data[i]}, Euclidean distance: {dist}")

    # Determine cusp A as the cusp with the smallest Euclidean distance to the origin
    cuspA = min(range(len(data)), key=lambda i: distances[i])

    # Print the identified cuspA for debugging
    print(f"Identified cuspA: {data[cuspA]}, Euclidean distance: {distances[cuspA]}")

    return cuspA, data

# Function to compute angle
def get_angle(cuspA, data):
    if cuspA is None or cuspA < 0 or cuspA >= len(data):
        print("Invalid cuspA index:", cuspA)
        return None, None  # Invalid cuspA index

    p2 = data[cuspA]
    x2 = p2[0]

    # Find p1: cusp with x coordinate just below x2
    p1_candidates = [point for point in data if point[0] < x2]
    if not p1_candidates:
        print("No cusp with x coordinate below x2 for cuspA:", cuspA)
        return None, None  # No cusp with x coordinate below x2
    p1 = max(p1_candidates, key=lambda point: point[0])

    # Find p3: cusp with x coordinate just above x2
    p3_candidates = [point for point in data if point[0] > x2]
    if not p3_candidates:
        print("No cusp with x coordinate above x2 for cuspA:", cuspA)
        return None, None  # No cusp with x coordinate above x2
    p3 = min(p3_candidates, key=lambda point: point[0])

    print(f"p1: {p1}, p2: {p2}, p3: {p3}")

    v1 = [p1[0] - p2[0], p1[2] - p2[2]]
    v2 = [p3[0] - p2[0], p3[2] - p2[2]]

    # Compute norms of the vectors
    n1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    n2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

    print(f"v1: {v1}, n1: {n1}, v2: {v2}, n2: {n2}")

    # Handle zero norm cases
    if n1 == 0 or n2 == 0:
        print("Zero norm vector for cuspA:", cuspA)
        return None, None

    # Normalize the vectors
    v1 = [v1[0] / n1, v1[1] / n1]
    v2 = [v2[0] / n2, v2[1] / n2]

    # Compute dot product
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]

    # Ensure the dot product is within the valid range for acos
    dot_product = max(min(dot_product, 1.0), -1.0)

    # Calculate angle
    angle = math.acos(dot_product)
    return round(angle, 3), round(angle / (2 * math.pi) * 360, 3)

# Function to determine real cusps based on proximity
def determine_real_cusps(cusps, threshold=0.1):
    if not cusps:
        return 0

    real_cusps = []
    cusps.sort(key=lambda x: x[0])  # Sort cusps by X coordinate

    current_group = [cusps[0]]
    for cusp in cusps[1:]:
        if abs(cusp[0] - current_group[-1][0]) <= threshold:
            current_group.append(cusp)
        else:
            real_cusps.append(current_group)
            current_group = [cusp]
    real_cusps.append(current_group)

    return len(real_cusps)

# Main function to process the .off files in a directory and generate the output file
def process_off_files(directory):
    # Create a subdirectory for results
    results_dir = os.path.join(directory, "z_batch_results")
    os.makedirs(results_dir, exist_ok=True)

    # Open output files
    full_batch_out = open(os.path.join(results_dir, "z_full_batch_out.txt"), 'w')
    angles_out = open(os.path.join(results_dir, "angles.txt"), 'w')
    fails_out = open(os.path.join(results_dir, "fails.txt"), 'w')
    cusp_files = {}

    # Write headers
    full_batch_out.write("ID\tRADIANS\tDEGREES\tNOTES\tREAL CUSPS\tFAILS INHIB?\n")
    angles_out.write("ID\tRADIANS\tDEGREES\tNOTES\tREAL CUSPS\tFAILS INHIB?\n")
    fails_out.write("ID\tRADIANS\tDEGREES\tNOTES\tREAL CUSPS\tFAILS INHIB?\n")

    for filename in os.listdir(directory):
        if filename.endswith(".off"):
            print(filename)
            file_path = os.path.join(directory, filename)
            vertices, faces = read_off_file(file_path)
            cusps = find_cusps(vertices, faces)

            local_maxima = cusps

            cuspA, cusps = get_individual_cusps(local_maxima)

            # Check if all other cusps have a higher Z value than cusp A
            passes_inhibitory_cascade = True
            tolerance = 0.1
            if len(cusps) > 1:
                for i in range(len(cusps)):
                    if i != cuspA and cusps[i][2] < cusps[cuspA][2] - tolerance:
                        print(f"Fails Inhibitory Cascade: cusp {i} with Z value {cusps[i][2]} is lower than cuspA")
                        passes_inhibitory_cascade = False
                        break

            # Compute angle
            angle, degrees = get_angle(cuspA, cusps)
            if angle is None:
                print(f"No angle calculated for file {filename}, cuspA {cuspA}")
                angle_radians = ""
                angle_degrees = ""
            else:
                angle_radians = angle
                angle_degrees = degrees

            # Determine the number of real cusps
            num_real_cusps = determine_real_cusps(local_maxima)

            # Determine the tooth ID
            base_name = os.path.splitext(filename)[0]
            if '9_' in base_name:
                tooth_id = base_name.split('9_', 1)[1]
            else:
                tooth_id = base_name  # fallback to whole name

            fails_inhib = "FAILS" if not passes_inhibitory_cascade else ""
            notes = "" #Placeholder for the NOTES field
            output_line = f"{tooth_id}\t{angle_radians}\t{angle_degrees}\t{notes}\t{num_real_cusps}\t{fails_inhib}\n"
            full_batch_out.write(output_line)

            # Write to specific cusp file
            cusp_file_name = os.path.join(results_dir, f"{num_real_cusps}_cusp.txt")
            if cusp_file_name not in cusp_files:
                cusp_files[cusp_file_name] = open(cusp_file_name, 'w')
                cusp_files[cusp_file_name].write("ID\tRADIANS\tDEGREES\tNOTES\tREAL CUSPS\tFAILS INHIB?\n")
            cusp_files[cusp_file_name].write(output_line)

            # Write to angles file if angle is calculated
            if angle_radians != "":
                angles_out.write(output_line)

            # Write to fails file if it fails inhibitory cascade
            if fails_inhib == "FAILS":
                fails_out.write(output_line)

    # Close all files
    full_batch_out.close()
    angles_out.close()
    fails_out.close()
    for file in cusp_files.values():
        file.close()

    print("Finished. Output data stored in:", results_dir)

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 git5Z_batch_mut.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    process_off_files(directory)
