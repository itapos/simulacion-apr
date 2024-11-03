from generate_experiment_data import get_experiments_results
from simulation_charts import generate_plots


exp_name = "experimento_full_2024-11-03_02-57-09"

print("Generando datos")
exp_results = get_experiments_results(exp_name)

print("Generando plots")
generate_plots(exp_name, exp_results)
