from generate_experiment_data import get_experiments_results, get_usefull_iterations, get_all_iterations
from simulation_charts import generate_plots


exp_name = "experimento_full_2024-11-09_02-00-07"
mitigation_strategies = ["betweenness", "closeness", "pressure", "node_degree"]
reinforcement_percents = [3,6,10,50,100]

print("Calculando iteraciones a usar")
usefull_iterations = get_usefull_iterations(exp_name, mitigation_strategies, reinforcement_percents)
# all_iterations = get_all_iterations(exp_name)
print(f"Iteraciones a usar: {len(usefull_iterations)}")
print("Generando datos")
exp_results = get_experiments_results(exp_name, mitigation_strategies, reinforcement_percents, usefull_iterations)

print("Generando plots")
generate_plots(exp_name, exp_results, mitigation_strategies, reinforcement_percents)
