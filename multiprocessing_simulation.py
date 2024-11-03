import time
from datetime import datetime
import pickle
import os

from utils.general_utils import format_time, generate_pga_value, generate_excels
from utils.main_simulation_functions import simulate_network_parallel

# =================================== INITIAL PARAMS ===================================
max_workers = 8
num_realizations = 4
inp_file = "networks/Melocoton.inp"
total_duration = 24 * 3600  # seconds
minimum_pressure = 5  # m.c.a
required_pressure = 15  # m.c.a
leak_start_time = 5 * 3600  # seconds
# Optional (Only for mitigation)
# mitigation_strategy can be any of "betweenness"|"closeness"|"pressure"|"node_degree"
mitigation_strategy = "pressure"
reinforcement_percent = 10
# ======================================================================================

if __name__ == "__main__":
    start_time = time.time()
    start_datetime = datetime.now()
    start_datetime_str = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    start_datetime_str_for_file_paths = start_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    print(f"Starting at {start_datetime_str}")

    # Crear la carpeta de resultados con la fecha y hora de inicio
    experiment_sufix = (
        f"_{mitigation_strategy}_at_{reinforcement_percent}"
        if mitigation_strategy != ""
        else "_base"
    )
    output_folder = f"results/{start_datetime_str_for_file_paths}{experiment_sufix}"
    os.makedirs(output_folder, exist_ok=True)

    # Generar los valores de PGA para todas las simulaciones
    pga_values = [generate_pga_value() for _ in range(num_realizations)]

    results = simulate_network_parallel(
        inp_file=inp_file,
        leak_start_time=leak_start_time,
        required_pressure=required_pressure,
        num_realizations=num_realizations,
        pga_values=pga_values,
        max_workers=max_workers,
        total_duration=total_duration,
        minimum_pressure=minimum_pressure,
        output_folder=output_folder,
        mitigation_strategy=mitigation_strategy,
        reinforcement_percent=reinforcement_percent,
    )

    # Pickle the results
    results_filename = os.path.join(
        output_folder, f"results_{start_datetime_str_for_file_paths}.pickle"
    )
    with open(results_filename, "wb") as f:
        pickle.dump(results, f)

    # Generate Excels
    print("Generating Excel files")
    generate_excels(output_folder, results, experiment_sufix)

    end_time = time.time()
    end_datetime = datetime.now()
    end_datetime_str = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    print("======================")
    print(f"Completed in {format_time(start_time, end_time)}")
    print(f"Completed at {end_datetime_str}")
    print("======================")
