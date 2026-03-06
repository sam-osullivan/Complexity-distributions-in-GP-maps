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
python3 make_rand_table.py
