import time
from datetime import datetime
import os
import pandas as pd
from utils.leaks_utils import get_network_priority_nodes
from utils.general_utils import format_time, generate_excels, generate_pga_value
from utils.main_simulation_functions import simulate_network_parallel
from utils.types import MitigationLeaksStrategyOptions
import pickle

# =================================== INITIAL PARAMS ===================================
max_workers = 8
num_realizations_per_iteration = 500
inp_file = "networks/Melocoton.inp"
total_duration = 24 * 3600  # seconds
minimum_pressure = 5  # m.c.a
required_pressure = 15  # m.c.a
leak_start_time = 5 * 3600  # seconds
# Optional (Only for mitigation)
# mitigation_strategy can be any of "betweenness"|"closeness"|"pressure"|"node_degree"
mitigation_strategies = ["betweenness", "closeness", "pressure", "node_degree"]
reinforcement_percentages = [3, 6, 10]

# ======================================================================================

if __name__ == "__main__":
    start_time = time.time()
    start_datetime = datetime.now()
    start_datetime_str = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    start_datetime_str_for_file_paths = start_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    print(f"Starting at {start_datetime_str}")

    # Create the results folder with the start datetime
    experiment_folder = f"results/experimento_full_{start_datetime_str_for_file_paths}"
    os.makedirs(experiment_folder, exist_ok=True)

    all_experiments_results = []

    # Generar los valores de PGA para todas las simulaciones
    pga_values = [generate_pga_value() for _ in range(num_realizations_per_iteration)]

    print("\n===============================")
    print("Starting no earthquake experiment")
    # Run no earthquake experiment
    no_earthquake_output_folder = f"{experiment_folder}/no_earthquake"
    no_earthquake_results = simulate_network_parallel(
        simulation_type="Clean",
        inp_file=inp_file,
        mitigation_leaks_strategy_options=None,
        leak_start_time=leak_start_time,
        required_pressure=required_pressure,
        num_realizations=1,
        pga_values=[],
        max_workers=max_workers,
        total_duration=total_duration,
        minimum_pressure=minimum_pressure,
        output_folder=no_earthquake_output_folder,
    )

    # Pickle the results
    base_earthquake_results_filename = os.path.join(
        no_earthquake_output_folder, "metrics.pickle"
    )

    with open(base_earthquake_results_filename, "wb") as f:
        pickle.dump(no_earthquake_results, f)

    # Analyze no_earthquake_results
    num_iterations_with_negative_pressure = 0
    min_pressure_all_iterations = float("inf")

    for _, row in no_earthquake_results.iterrows():
        if "error" in row and pd.notna(row["error"]):
            continue  # Skip erroneous iterations

        # Find the minimum pressure across all nodes in this iteration
        min_pressure = row["min_system_junctions_pressure"]
        min_pressure_all_iterations = min(min_pressure_all_iterations, min_pressure)

        # Check if there's any negative pressure in this iteration
        if min_pressure < 0:
            num_iterations_with_negative_pressure += 1

    no_earthquake_experiment_result = {
        "mitigation_strategy": "No_earthquake",
        "reinforcement_percent": 0,
        "num_iterations": num_realizations_per_iteration,
        "min_pressure": min_pressure_all_iterations,
        "negative_pressure_count": num_iterations_with_negative_pressure,
    }
    all_experiments_results.append(no_earthquake_experiment_result)

    # Generate Excels
    print("Generating Excel files")
    generate_excels(no_earthquake_output_folder, no_earthquake_results, "")

    # Calculate priority nodes
    print("Generating priority_nodes dict")
    no_earthquake_network_filepath = os.path.join(
        no_earthquake_output_folder, "simulation_data", "wn_realization_1.pickle"
    )

    # Calculate average pressures for each node in the no earthquake experiment
    mean_node_pressure = no_earthquake_results["mean_node_pressure"][0]

    # Generate the priority nodes dictionary
    priority_nodes = get_network_priority_nodes(
        no_earthquake_network_filepath, mean_node_pressure
    )

    # Save priority_Nodes
    print("Saving priority_nodes dict")
    priority_nodes_filename = os.path.join(experiment_folder, "priority_nodes.pickle")
    with open(priority_nodes_filename, "wb") as f:
        pickle.dump(priority_nodes, f)

    print("\n===============================")
    print("Starting earthquake with no mitigation experiment")
    # Run base earthquake experiment
    base_earthquake_output_folder = f"{experiment_folder}/base_earthquake"
    base_earthquake_results = simulate_network_parallel(
        simulation_type="Earthquake",
        inp_file=inp_file,
        mitigation_leaks_strategy_options=None,
        leak_start_time=leak_start_time,
        required_pressure=required_pressure,
        num_realizations=num_realizations_per_iteration,
        pga_values=pga_values,
        max_workers=max_workers,
        total_duration=total_duration,
        minimum_pressure=minimum_pressure,
        output_folder=base_earthquake_output_folder,
    )

    # Pickle the results
    base_earthquake_results_filename = os.path.join(
        base_earthquake_output_folder, "metrics.pickle"
    )
    with open(base_earthquake_results_filename, "wb") as f:
        pickle.dump(base_earthquake_results, f)

    # Analyze base_earthquake_results
    num_iterations_with_negative_pressure = 0
    min_pressure_all_iterations = float("inf")

    for _, row in base_earthquake_results.iterrows():
        if "error" in row and pd.notna(row["error"]):
            continue  # Skip erroneous iterations

        # Find the minimum pressure across all nodes in this iteration
        min_pressure = row["min_system_junctions_pressure"]
        min_pressure_all_iterations = min(min_pressure_all_iterations, min_pressure)

        # Check if there's any negative pressure in this iteration
        if min_pressure < 0:
            num_iterations_with_negative_pressure += 1

    base_earthquake_experiment_result = {
        "mitigation_strategy": "Earthquake_no_mitigation",
        "reinforcement_percent": 0,
        "num_iterations": num_realizations_per_iteration,
        "min_pressure": min_pressure_all_iterations,
        "negative_pressure_count": num_iterations_with_negative_pressure,
    }
    all_experiments_results.append(base_earthquake_experiment_result)

    # Generate Excels
    print("Generating Excel files")
    generate_excels(base_earthquake_output_folder, base_earthquake_results, "")

    print("\n===============================")
    print("Starting earthquake with mitigation experiments")
    # Loop over each strategy and reinforcement percent
    for mitigation_strategy in mitigation_strategies:
        for reinforcement_percent in reinforcement_percentages:
            experiment_name = (
                f"{mitigation_strategy}_at_{reinforcement_percent}"
                if mitigation_strategy != ""
                else ""
            )
            output_folder = f"{experiment_folder}/{experiment_name}"
            os.makedirs(output_folder, exist_ok=True)
            print(
                f"\nRunning experiment for mitigation strategy '{mitigation_strategy}' "
                f"and {reinforcement_percent} % reinforcement."
            )

            mitigation_leaks_strategy_options: MitigationLeaksStrategyOptions = {
                "mitigation_strategy": mitigation_strategy,
                "reinforcement_percent": reinforcement_percent,
                "priority_nodes": priority_nodes,
            }

            # Run the specified number of iterations for each PGA value
            results = simulate_network_parallel(
                simulation_type="Earthquake",
                inp_file=inp_file,
                mitigation_leaks_strategy_options=mitigation_leaks_strategy_options,
                leak_start_time=leak_start_time,
                required_pressure=required_pressure,
                num_realizations=num_realizations_per_iteration,
                pga_values=pga_values,
                max_workers=max_workers,
                total_duration=total_duration,
                minimum_pressure=minimum_pressure,
                output_folder=output_folder,
            )

            # Pickle the results
            results_filename = os.path.join(
                output_folder, f"results.pickle"
            )
            with open(results_filename, "wb") as f:
                pickle.dump(results, f)

            # Analyze results for this PGA
            num_iterations_with_negative_pressure = 0
            min_pressure_all_iterations = float("inf")

            for _, row in results.iterrows():
                if "error" in row and pd.notna(row["error"]):
                    continue  # Skip erroneous iterations

                # Find the minimum pressure across all nodes in this iteration
                min_pressure = row["min_system_junctions_pressure"]
                min_pressure_all_iterations = min(
                    min_pressure_all_iterations, min_pressure
                )

                # Check if there's any negative pressure in this iteration
                if min_pressure < 0:
                    num_iterations_with_negative_pressure += 1

            # Save experiment results for this PGA
            experiment_result = {
                "mitigation_strategy": mitigation_strategy,
                "reinforcement_percent": reinforcement_percent,
                "num_iterations": num_realizations_per_iteration,
                "min_pressure": min_pressure_all_iterations,
                "negative_pressure_count": num_iterations_with_negative_pressure,
            }
            all_experiments_results.append(experiment_result)

            # Generate Excels
            print("Generating Excel files")
            generate_excels(output_folder, results, f"_{experiment_name}")

    # Save all results to a CSV file for further analysis
    output_filename = os.path.join(experiment_folder, "experiment_results.csv")
    pd.DataFrame(all_experiments_results).to_csv(output_filename, index=False)

    end_time = time.time()
    end_datetime = datetime.now()
    end_datetime_str = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    print("======================")
    print(f"Completed in {format_time(start_time, end_time)}")
    print(f"Completed at {end_datetime_str}")
    print("======================")
