import time
from datetime import datetime
import os
import numpy as np
import pandas as pd

from utils.general_utils import format_time, generate_excels
from utils.main_simulation_functions import simulate_network_parallel

# =================================== INITIAL PARAMS ===================================
max_workers = 8
iterations_per_pga = 20  # Run x iterations for each PGA
inp_file = "networks/Melocoton.inp"
total_duration = 48 * 3600  # seconds
minimum_pressure = 5  # m.c.a
required_pressure = 15  # m.c.a
leak_start_time = 5 * 3600  # seconds
# Optional (Only for mitigation)
# mitigation_strategy can be any of "betweenness"|"closeness"|"pressure"|"node_degree"
mitigation_strategy = ""
reinforcement_percent = 3

# PGA range for the experiment
pga_range = np.arange(0.15, 0.36, 0.01)  # PGA values from 0.15 to 0.35 in steps of 0.01
# ======================================================================================

if __name__ == "__main__":
    start_time = time.time()
    start_datetime = datetime.now()
    start_datetime_str = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    start_datetime_str_for_file_paths = start_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    print(f"Starting at {start_datetime_str}")

    # Create the results folder with the start datetime
    mitigation_sufix = (
        f"_{mitigation_strategy}_at_{reinforcement_percent}"
        if mitigation_strategy != ""
        else ""
    )
    experiment_folder = f"results/experimento_pga_{start_datetime_str_for_file_paths}{mitigation_sufix}"
    os.makedirs(experiment_folder, exist_ok=True)

    all_experiments_results = []

    # Loop over each PGA value in the specified range
    for pga_value in pga_range:
        pga_value=round(pga_value,2)
        output_folder = f"{experiment_folder}/pga_{pga_value:.2f}"
        os.makedirs(output_folder, exist_ok=True)
        print(f"Running experiment for PGA: {pga_value:.2f}")

        # Run the specified number of iterations for each PGA value
        results = simulate_network_parallel(
            inp_file=inp_file,
            leak_start_time=leak_start_time,
            required_pressure=required_pressure,
            num_realizations=iterations_per_pga,
            pga_values=[pga_value] * iterations_per_pga,  # Same PGA for all iterations
            max_workers=max_workers,
            total_duration=total_duration,
            minimum_pressure=minimum_pressure,
            output_folder=output_folder,
            mitigation_strategy=mitigation_strategy,
            reinforcement_percent=reinforcement_percent,
        )

        # Analyze results for this PGA
        num_iterations_with_negative_pressure = 0
        min_pressure_all_iterations = float("inf")

        for _, row in results.iterrows():
            if "error" in row and pd.notna(row["error"]):
                continue  # Skip erroneous iterations

            # Find the minimum pressure across all nodes in this iteration
            min_pressure = row["min_system_pressure"]
            min_pressure_all_iterations = min(min_pressure_all_iterations, min_pressure)

            # Check if there's any negative pressure in this iteration
            if min_pressure < 0:
                num_iterations_with_negative_pressure += 1

        # Save experiment results for this PGA
        experiment_result = {
            "pga": pga_value,
            "num_iterations": iterations_per_pga,
            "min_pressure": min_pressure_all_iterations,
            "negative_pressure_count": num_iterations_with_negative_pressure,
        }
        all_experiments_results.append(experiment_result)

    # Optionally, save all results to a CSV file for further analysis
    output_filename = os.path.join(experiment_folder, "pga_experiment_results.csv")
    pd.DataFrame(all_experiments_results).to_csv(output_filename, index=False)

    # # Generate Excels (if needed)
    # print("Generating Excel files")
    # generate_excels(experiment_folder, pd.DataFrame(all_experiments_results),"")

    end_time = time.time()
    end_datetime = datetime.now()
    end_datetime_str = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    print("======================")
    print(f"Completed in {format_time(start_time, end_time)}")
    print(f"Completed at {end_datetime_str}")
    print("======================")
