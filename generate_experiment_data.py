import os
import pickle
import pandas as pd


def filter_leak_keys(d):
    return {k: v for k, v in d.items() if not k.startswith("Leak_")}

def get_df_gte_threshold(data:pd.DataFrame, threshold:float):
    new_df = (data.T >= threshold).sum()
    return new_df / len(data.T)

def load_and_process_simulation_results(pickle_route: str, usefull_iterations:set):
    # Cargar los resultados de la simulación desde el archivo pickle
    with open(pickle_route, "rb") as f:
        sim_metrics = pickle.load(f)
    
    # Extraer las métricas necesarias desde sim_metrics
    pressure = sim_metrics.get("pressure", None)
    raw_betweenness_centrality = sim_metrics.get("betweenness_centrality", None)
    raw_closeness_centrality = sim_metrics.get("closeness_centrality", None)
    raw_mean_node_pressure = sim_metrics.get("mean_node_pressure", None)
    mean_t_pressure = sim_metrics.get("mean_t_pressure", None)
    todini = sim_metrics.get("todini", None)
    mean_t_wsa = sim_metrics.get("mean_t_wsa", None)
    mean_t_flowrate = sim_metrics.get("mean_t_flowrate", None)
    mean_t_demand = sim_metrics.get("mean_t_demand", None)
    mean_t_leak_demand = sim_metrics.get("mean_t_leak_demand", None)
    mean_t_total_demand = sim_metrics.get("mean_t_total_demand", None)
    mean_t_tank_levels = sim_metrics.get("mean_t_tank_levels", None)
    num_damages = sim_metrics.get("num_damages", [0])
    
    # Inicializar diccionarios para recopilar datos válidos de cada métrica
    valid_pressures = {}
    valid_betweenness_centrality = {}
    valid_closeness_centrality = {}
    valid_mean_node_pressure = {}
    valid_mean_t_pressure = {}
    valid_todini = {}
    valid_mean_t_wsa = {}
    valid_mean_t_flowrate = {}
    valid_mean_t_demand = {}
    valid_mean_t_leak_demand = {}
    valid_mean_t_total_demand = {}
    valid_mean_t_tank_levels = {}
    valid_num_damages={}
    valid_t_required_satisfied_node_pressure = {}
    valid_t_min_satisfied_node_pressure = {}

    # Filtrar simulaciones
    for i in usefull_iterations:
        # Almacenar datos válidos en los diccionarios
        valid_pressures[i] = pressure[i]
        valid_betweenness_centrality[i] = raw_betweenness_centrality[i]
        valid_closeness_centrality[i] = raw_closeness_centrality[i]
        valid_mean_node_pressure[i] = raw_mean_node_pressure[i]
        valid_mean_t_pressure[i] = mean_t_pressure[i]
        valid_todini[i] = todini[i]
        valid_mean_t_wsa[i] = mean_t_wsa[i]
        valid_mean_t_flowrate[i] = mean_t_flowrate[i]
        valid_mean_t_demand[i] = mean_t_demand[i]
        valid_mean_t_leak_demand[i] = mean_t_leak_demand[i]
        valid_mean_t_total_demand[i] = mean_t_total_demand[i]
        valid_mean_t_tank_levels[i] = mean_t_tank_levels[i]
        valid_num_damages[i] = num_damages[i]
        valid_t_required_satisfied_node_pressure[i] = get_df_gte_threshold(pressure[i], 15)
        valid_t_min_satisfied_node_pressure[i] = get_df_gte_threshold(pressure[i], 5)

    # Convertir datos válidos a Series/DataFrames y aplicar las transformaciones necesarias
    pressure = pd.Series(valid_pressures)
    betweenness_centrality = pd.DataFrame(pd.Series(valid_betweenness_centrality).apply(filter_leak_keys).tolist()).T
    closeness_centrality = pd.DataFrame(pd.Series(valid_closeness_centrality).apply(filter_leak_keys).tolist()).T
    mean_node_pressure = pd.DataFrame(pd.Series(valid_mean_node_pressure).apply(filter_leak_keys).tolist()).T
    mean_t_pressure = pd.DataFrame(valid_mean_t_pressure.values()).T
    todini = pd.DataFrame(valid_todini.values()).T
    mean_t_wsa = pd.DataFrame(valid_mean_t_wsa.values()).T
    mean_t_flowrate = pd.DataFrame(valid_mean_t_flowrate.values()).T
    mean_t_demand = pd.DataFrame(valid_mean_t_demand.values()).T
    mean_t_leak_demand = pd.DataFrame(valid_mean_t_leak_demand.values()).T
    mean_t_total_demand = pd.DataFrame(valid_mean_t_total_demand.values()).T
    mean_t_tank_levels = pd.DataFrame(valid_mean_t_tank_levels.values()).T
    num_damages=pd.Series(valid_num_damages)
    t_required_satisfied_node_pressure = pd.DataFrame(valid_t_required_satisfied_node_pressure).T
    t_min_satisfied_node_pressure = pd.DataFrame(valid_t_min_satisfied_node_pressure).T

    # Calcular valores promedio en las simulaciones válidas
    experiment_results = {
        # Por nodo
        "betweenness_centrality": betweenness_centrality.mean(axis=1),
        "closeness_centrality": closeness_centrality.mean(axis=1),
        "mean_node_pressure": mean_node_pressure.mean(axis=1),
        # Por tiempo
        "mean_t_pressure": mean_t_pressure.mean(axis=1),
        "todini": todini.mean(axis=1),
        "mean_t_wsa": mean_t_wsa.mean(axis=1),
        "mean_t_flowrate": mean_t_flowrate.mean(axis=1),
        "mean_t_demand": mean_t_demand.mean(axis=1),
        "mean_t_leak_demand": mean_t_leak_demand.mean(axis=1),
        "mean_t_total_demand": mean_t_total_demand.mean(axis=1),
        "mean_t_tank_levels": mean_t_tank_levels.mean(axis=1),
        "t_required_satisfied_node_pressure": t_required_satisfied_node_pressure.mean(),
        "t_min_satisfied_node_pressure": t_min_satisfied_node_pressure.mean(),
        # Otro
        "num_damages":num_damages,
        "min_num_damages":num_damages.min(),
        "max_num_damages":num_damages.max(),
        "mean_num_damages":num_damages.mean(),
    }
    
    return experiment_results

def get_all_iterations(exp_name: str):
    path = f"results/{exp_name}"
    
    # =========================================================================================================
    # =========================================== Simple  Eartquake ===========================================
    # =========================================================================================================
    folder = "base_earthquake"

    # Cargar los resultados de la simulación
    pickle_route = f"{path}/{folder}/metrics.pickle"
    all_iterations_index = get_all_iterations_index(pickle_route)
    return all_iterations_index

def get_usefull_iterations(exp_name: str, mitigation_strategies:list[str], reinforcement_percents:list[int]):
    negative_pressure_iterations = set()
    path = f"results/{exp_name}"
    
    # =========================================================================================================
    # =========================================== Simple  Eartquake ===========================================
    # =========================================================================================================
    folder = "base_earthquake"

    # Cargar los resultados de la simulación
    pickle_route = f"{path}/{folder}/metrics.pickle"

    update_negative_pressure_iterations(pickle_route,negative_pressure_iterations)
    all_iterations_index = get_all_iterations_index(pickle_route)

    # =========================================================================================================
    # ========================================= Mitigated  Eartquakes =========================================
    # =========================================================================================================
    for mitigation_strategy_name in mitigation_strategies:
        for reinforcement_percent in reinforcement_percents:
            folder = f"{mitigation_strategy_name}_at_{reinforcement_percent}"

            # Cargar los resultados de la simulación
            pickle_route = f"{path}/{folder}/results.pickle"
            update_negative_pressure_iterations(pickle_route,negative_pressure_iterations)
    
    return all_iterations_index - negative_pressure_iterations

def get_all_iterations_index(pickle_route: str):
    all_iterations = set()
    with open(pickle_route, "rb") as f:
        sim_metrics = pickle.load(f)
    pressure = sim_metrics.get("pressure", None)

    for i in pressure.index:
        all_iterations.add(i)
    return all_iterations

def update_negative_pressure_iterations(pickle_route: str, negative_pressure_iterations:set[int]):
    # Cargar los resultados de la simulación desde el archivo pickle
    with open(pickle_route, "rb") as f:
        sim_metrics = pickle.load(f)
    pressure = sim_metrics.get("pressure", None)

    for i in pressure.index:
        pressure_df = pd.DataFrame(pressure[i])
        if (pressure_df < 0).any().any():
            negative_pressure_iterations.add(i)
    

def get_experiments_results(exp_name: str, mitigation_strategies:list[str], reinforcement_percents:list[int], usefull_iterations:set):
    results = {}
    path = f"results/{exp_name}"

    # =========================================================================================================
    # ============================================= No earthquake =============================================
    # =========================================================================================================
    folder = "no_earthquake"

    # Cargar los resultados de la simulación
    pickle_route = f"{path}/{folder}/metrics.pickle"
    
    # wn pickle route
    wn_pickle_route = f"{path}/{folder}/simulation_data/wn_realization_1.pickle"

    experiment_results = load_and_process_simulation_results(pickle_route, [0])
    experiment_results["wn_pickle_route"] = wn_pickle_route

    results[folder] = experiment_results
    print(f"{folder} \n\tmin_num_damages: {experiment_results['min_num_damages']}")
    print(f"\tmax_num_damages: {experiment_results['max_num_damages']}")
    print(f"\tmean_num_damages: {experiment_results['mean_num_damages']}")

    # =========================================================================================================
    # =========================================== Simple  Eartquake ===========================================
    # =========================================================================================================
    folder = "base_earthquake"

    # Cargar los resultados de la simulación
    pickle_route = f"{path}/{folder}/metrics.pickle"

    experiment_results = load_and_process_simulation_results(pickle_route, usefull_iterations)

    results[folder] = experiment_results
    print(f"{folder} \n\tmin_num_damages: {experiment_results['min_num_damages']}")
    print(f"\tmax_num_damages: {experiment_results['max_num_damages']}")
    print(f"\tmean_num_damages: {experiment_results['mean_num_damages']}")

    # =========================================================================================================
    # ========================================= Mitigated  Eartquakes =========================================
    # =========================================================================================================
    for mitigation_strategy_name in mitigation_strategies:
        for reinforcement_percent in reinforcement_percents:
            folder = f"{mitigation_strategy_name}_at_{reinforcement_percent}"

            # Cargar los resultados de la simulación
            pickle_route = f"{path}/{folder}/results.pickle"
            
            experiment_results = load_and_process_simulation_results(pickle_route, usefull_iterations)

            results[folder] = experiment_results
            print(f"{folder} \n\tmin_num_damages: {experiment_results['min_num_damages']}")
            print(f"\tmax_num_damages: {experiment_results['max_num_damages']}")
            print(f"\tmean_num_damages: {experiment_results['mean_num_damages']}")

    # Save results
    plots_folder = os.path.join("results", exp_name, "plots")
    os.makedirs(plots_folder, exist_ok=True)

    with open(f"{plots_folder}/data.pickle", "wb") as f:
        pickle.dump(results, f)

    return results


def get_exp_verbose_name(exp_name: str):
    verbose_name = {
        "no_earthquake": "Sin sismo",
        "base_earthquake": "Sismo base",
        "betweenness": "C. Interposición",
        "betweenness_at_3": "C. Interposición al 3%",
        "betweenness_at_6": "C. Interposición al 6%",
        "betweenness_at_10": "C. Interposición al 10%",
        "betweenness_at_50": "C. Interposición al 50%",
        "betweenness_at_100": "C. Interposición al 100%",
        "closeness": "C. Cercanía",
        "closeness_at_3": "C. Cercanía al 3%",
        "closeness_at_6": "C. Cercanía al 6%",
        "closeness_at_10": "C. Cercanía al 10%",
        "closeness_at_50": "C. Cercanía al 50%",
        "closeness_at_100": "C. Cercanía al 100%",
        "pressure": "Presión",
        "pressure_at_3": "Presión al 3%",
        "pressure_at_6": "Presión al 6%",
        "pressure_at_10": "Presión al 10%",
        "pressure_at_50": "Presión al 50%",
        "pressure_at_100": "Presión al 100%",
        "node_degree": "Grado nodal",
        "node_degree_at_3": "Grado nodal al 3%",
        "node_degree_at_6": "Grado nodal al 6%",
        "node_degree_at_10": "Grado nodal al 10%",
        "node_degree_at_50": "Grado nodal al 50%",
        "node_degree_at_100": "Grado nodal al 100%",
    }
    return verbose_name[exp_name]

