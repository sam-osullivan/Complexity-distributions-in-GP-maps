1. To solve ODE system for set of input parameters:
python3 run_solutions.py \
    --input-dir /mnt/users/osullivans/circ/oct24/t0to50/parameters \
    --tf 50 \
    --num_chunks 50 \
    --n_steps 49999 \

2. Binarize output curves
python3 2bin.py </solutions_out> </binary_out>

3. Calculate Lempel-Ziv Complexity
python3 lz.py </binary_out> </lz_values>

4. Store results in a table
python3 make_any_table.py \
--params-dir <parameters_directory>
--binary-dir <binaries_directory>
--lz-dir <lz_values_directory>
--output <output_table.txt>

6. sample P-distribution and compile into a table:
python3 sample0mutbinaries.py
&
python3 make_0mut_table.py

7. Mutate parameters
python3 mutate_params.py --input <input_folder> --output <output_folder> -seed 42
