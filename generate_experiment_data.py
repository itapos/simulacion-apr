import os
import pickle
import pandas as pd


def filter_leak_keys(d):
    return {k: v for k, v in d.items() if not k.startswith("Leak_")}


def get_experiments_results(exp_name: str):
    mitigation_strategies = ["betweenness", "closeness", "pressure", "node_degree"]
    reinforcement_percents = [3, 6, 10]

    results = {}
    path = f"results/{exp_name}"

    # =========================================================================================================
    # ============================================= No earthquake =============================================
    # =========================================================================================================
    folder = "no_earthquake"

    # Cargar los resultados de la simulación
    pickle_route = f"{path}/{folder}/metrics.pickle"
    with open(pickle_route, "rb") as f:
        sim_metrics = pickle.load(f)

    # wn pickle route
    wn_pickle_route = f"{path}/{folder}/simulation_data/wn_realization_1.pickle"

    # # Simple values
    # num_damages = sim_metrics.get("num_damages", None)
    # num_major_damages = sim_metrics.get("num_major_damages", None)
    # num_moderate_damages = sim_metrics.get("num_moderate_damages", None)
    # pga = sim_metrics.get("pga", None)
    # min_system_pressure = sim_metrics.get("min_system_pressure", None)
    # mean_system_pressure = sim_metrics.get("mean_system_pressure", None)
    # min_system_junctions_pressure = sim_metrics.get(
    #     "min_system_junctions_pressure", None
    # )
    # mean_system_wsa = sim_metrics.get("mean_system_wsa", None)
    # realization_id = sim_metrics.get("realization_id", None)
    # mitigation_strategy = sim_metrics.get("mitigation_strategy", None)
    # mitigation_reinforcement_percent = sim_metrics.get(
    #     "mitigation_reinforcement_percent", None
    # )
    # realization_time = sim_metrics.get("realization_time", None)

    # # Series of list of data
    # mitigation_reinforced_pipes = sim_metrics.get("mitigation_reinforced_pipes", None)

    # # Series of Data frames
    # pressure = sim_metrics.get("pressure", None)
    # wsa = sim_metrics.get("wsa", None)

    # Cleaned Data frames
    raw_betweenness_centrality = sim_metrics.get("betweenness_centrality", None)
    filtered_raw_betweenness_centrality = raw_betweenness_centrality.apply(
        filter_leak_keys
    )
    betweenness_centrality = pd.DataFrame(
        filtered_raw_betweenness_centrality.tolist()
    ).T

    raw_closeness_centrality = sim_metrics.get("closeness_centrality", None)
    filtered_raw_closeness_centrality = raw_closeness_centrality.apply(filter_leak_keys)
    closeness_centrality = pd.DataFrame(filtered_raw_closeness_centrality.tolist()).T

    raw_mean_node_pressure = sim_metrics.get("mean_node_pressure", None)
    filtered_raw_mean_node_pressure = raw_mean_node_pressure.apply(filter_leak_keys)
    mean_node_pressure = pd.DataFrame(filtered_raw_mean_node_pressure.tolist()).T

    mean_t_pressure = pd.DataFrame(sim_metrics.get("mean_t_pressure", None).tolist()).T

    todini = pd.DataFrame(sim_metrics.get("todini", None).tolist()).T

    mean_t_wsa = pd.DataFrame(sim_metrics.get("mean_t_wsa", None).tolist()).T

    mean_t_flowrate = pd.DataFrame(sim_metrics.get("mean_t_flowrate", None).tolist()).T

    mean_t_demand = pd.DataFrame(sim_metrics.get("mean_t_demand", None).tolist()).T

    mean_t_tank_levels = pd.DataFrame(
        sim_metrics.get("mean_t_tank_levels", None).tolist()
    ).T

    # No tiene sentido usarlos
    # node_degree = sim_metrics.get("node_degree", None)
    # bridges = sim_metrics.get("bridges", None)

    # ################### Datos promedio del experimento ####################
    # Por nodo
    experiment_betweenness_centrality = betweenness_centrality.mean(axis=1)
    experiment_closeness_centrality = closeness_centrality.mean(axis=1)
    experiment_mean_node_pressure = mean_node_pressure.mean(axis=1)

    # Por Tiempo
    experiment_mean_t_pressure = mean_t_pressure.mean(axis=1)
    experiment_todini = todini.mean(axis=1)
    experiment_mean_t_wsa = mean_t_wsa.mean(axis=1)
    experiment_mean_t_flowrate = mean_t_flowrate.mean(axis=1)
    experiment_mean_t_demand = mean_t_demand.mean(axis=1)
    experiment_mean_t_tank_levels = mean_t_tank_levels.mean(axis=1)
    ########################################################################

    experiment_results = {
        "wn_pickle_route": wn_pickle_route,
        "betweenness_centrality": experiment_betweenness_centrality,
        "closeness_centrality": experiment_closeness_centrality,
        "mean_node_pressure": experiment_mean_node_pressure,
        "mean_t_pressure": experiment_mean_t_pressure,
        "todini": experiment_todini,
        "mean_t_wsa": experiment_mean_t_wsa,
        "mean_t_flowrate": experiment_mean_t_flowrate,
        "mean_t_demand": experiment_mean_t_demand,
        "mean_t_tank_levels": experiment_mean_t_tank_levels,
    }

    results[folder] = experiment_results

    # =========================================================================================================
    # =========================================== Simple  Eartquake ===========================================
    # =========================================================================================================
    folder = "base_earthquake"

    # Cargar los resultados de la simulación
    pickle_route = f"{path}/{folder}/metrics.pickle"
    with open(pickle_route, "rb") as f:
        sim_metrics = pickle.load(f)

    # # Simple values
    # num_damages = sim_metrics.get("num_damages", None)
    # num_major_damages = sim_metrics.get("num_major_damages", None)
    # num_moderate_damages = sim_metrics.get("num_moderate_damages", None)
    # pga = sim_metrics.get("pga", None)
    # min_system_pressure = sim_metrics.get("min_system_pressure", None)
    # mean_system_pressure = sim_metrics.get("mean_system_pressure", None)
    # min_system_junctions_pressure = sim_metrics.get(
    #     "min_system_junctions_pressure", None
    # )
    # mean_system_wsa = sim_metrics.get("mean_system_wsa", None)
    # realization_id = sim_metrics.get("realization_id", None)
    # mitigation_strategy = sim_metrics.get("mitigation_strategy", None)
    # mitigation_reinforcement_percent = sim_metrics.get(
    #     "mitigation_reinforcement_percent", None
    # )
    # realization_time = sim_metrics.get("realization_time", None)

    # # Series of list of data
    # mitigation_reinforced_pipes = sim_metrics.get("mitigation_reinforced_pipes", None)

    # # Series of Data frames
    # pressure = sim_metrics.get("pressure", None)
    # wsa = sim_metrics.get("wsa", None)

    # Cleaned Data frames
    raw_betweenness_centrality = sim_metrics.get("betweenness_centrality", None)
    filtered_raw_betweenness_centrality = raw_betweenness_centrality.apply(
        filter_leak_keys
    )
    betweenness_centrality = pd.DataFrame(
        filtered_raw_betweenness_centrality.tolist()
    ).T

    raw_closeness_centrality = sim_metrics.get("closeness_centrality", None)
    filtered_raw_closeness_centrality = raw_closeness_centrality.apply(filter_leak_keys)
    closeness_centrality = pd.DataFrame(filtered_raw_closeness_centrality.tolist()).T

    raw_mean_node_pressure = sim_metrics.get("mean_node_pressure", None)
    filtered_raw_mean_node_pressure = raw_mean_node_pressure.apply(filter_leak_keys)
    mean_node_pressure = pd.DataFrame(filtered_raw_mean_node_pressure.tolist()).T

    mean_t_pressure = pd.DataFrame(sim_metrics.get("mean_t_pressure", None).tolist()).T

    todini = pd.DataFrame(sim_metrics.get("todini", None).tolist()).T

    mean_t_wsa = pd.DataFrame(sim_metrics.get("mean_t_wsa", None).tolist()).T

    mean_t_flowrate = pd.DataFrame(sim_metrics.get("mean_t_flowrate", None).tolist()).T

    mean_t_demand = pd.DataFrame(sim_metrics.get("mean_t_demand", None).tolist()).T

    mean_t_tank_levels = pd.DataFrame(
        sim_metrics.get("mean_t_tank_levels", None).tolist()
    ).T

    # No tiene sentido usarlos
    # node_degree = sim_metrics.get("node_degree", None)
    # bridges = sim_metrics.get("bridges", None)

    # ################### Datos promedio del experimento ####################
    # Por nodo
    experiment_betweenness_centrality = betweenness_centrality.mean(axis=1)
    experiment_closeness_centrality = closeness_centrality.mean(axis=1)
    experiment_mean_node_pressure = mean_node_pressure.mean(axis=1)

    # Por Tiempo
    experiment_mean_t_pressure = mean_t_pressure.mean(axis=1)
    experiment_todini = todini.mean(axis=1)
    experiment_mean_t_wsa = mean_t_wsa.mean(axis=1)
    experiment_mean_t_flowrate = mean_t_flowrate.mean(axis=1)
    experiment_mean_t_demand = mean_t_demand.mean(axis=1)
    experiment_mean_t_tank_levels = mean_t_tank_levels.mean(axis=1)
    # #######################################################################

    experiment_results = {
        "betweenness_centrality": experiment_betweenness_centrality,
        "closeness_centrality": experiment_closeness_centrality,
        "mean_node_pressure": experiment_mean_node_pressure,
        "mean_t_pressure": experiment_mean_t_pressure,
        "todini": experiment_todini,
        "mean_t_wsa": experiment_mean_t_wsa,
        "mean_t_flowrate": experiment_mean_t_flowrate,
        "mean_t_demand": experiment_mean_t_demand,
        "mean_t_tank_levels": experiment_mean_t_tank_levels,
    }

    results[folder] = experiment_results

    # =========================================================================================================
    # ========================================= Mitigated  Eartquakes =========================================
    # =========================================================================================================
    for mitigation_strategy_name in mitigation_strategies:
        for reinforcement_percent in reinforcement_percents:
            folder = f"{mitigation_strategy_name}_at_{reinforcement_percent}"

            # Cargar los resultados de la simulación
            pickle_route = f"{path}/{folder}/results.pickle"
            with open(pickle_route, "rb") as f:
                sim_metrics = pickle.load(f)

            # # Simple values
            # num_damages = sim_metrics.get("num_damages", None)
            # num_major_damages = sim_metrics.get("num_major_damages", None)
            # num_moderate_damages = sim_metrics.get("num_moderate_damages", None)
            # pga = sim_metrics.get("pga", None)
            # min_system_pressure = sim_metrics.get("min_system_pressure", None)
            # mean_system_pressure = sim_metrics.get("mean_system_pressure", None)
            # min_system_junctions_pressure = sim_metrics.get(
            #     "min_system_junctions_pressure", None
            # )
            # mean_system_wsa = sim_metrics.get("mean_system_wsa", None)
            # realization_id = sim_metrics.get("realization_id", None)
            # mitigation_strategy = sim_metrics.get("mitigation_strategy", None)
            # mitigation_reinforcement_percent = sim_metrics.get(
            #     "mitigation_reinforcement_percent", None
            # )
            # realization_time = sim_metrics.get("realization_time", None)

            # # Series of list of data
            # mitigation_reinforced_pipes = sim_metrics.get(
            #     "mitigation_reinforced_pipes", None
            # )

            # # Series of Data frames
            # pressure = sim_metrics.get("pressure", None)
            # wsa = sim_metrics.get("wsa", None)

            # Cleaned Data frames
            raw_betweenness_centrality = sim_metrics.get("betweenness_centrality", None)
            filtered_raw_betweenness_centrality = raw_betweenness_centrality.apply(
                filter_leak_keys
            )
            betweenness_centrality = pd.DataFrame(
                filtered_raw_betweenness_centrality.tolist()
            ).T

            raw_closeness_centrality = sim_metrics.get("closeness_centrality", None)
            filtered_raw_closeness_centrality = raw_closeness_centrality.apply(
                filter_leak_keys
            )
            closeness_centrality = pd.DataFrame(
                filtered_raw_closeness_centrality.tolist()
            ).T

            raw_mean_node_pressure = sim_metrics.get("mean_node_pressure", None)
            filtered_raw_mean_node_pressure = raw_mean_node_pressure.apply(
                filter_leak_keys
            )
            mean_node_pressure = pd.DataFrame(
                filtered_raw_mean_node_pressure.tolist()
            ).T

            mean_t_pressure = pd.DataFrame(
                sim_metrics.get("mean_t_pressure", None).tolist()
            ).T

            todini = pd.DataFrame(sim_metrics.get("todini", None).tolist()).T

            mean_t_wsa = pd.DataFrame(sim_metrics.get("mean_t_wsa", None).tolist()).T

            mean_t_flowrate = pd.DataFrame(
                sim_metrics.get("mean_t_flowrate", None).tolist()
            ).T

            mean_t_demand = pd.DataFrame(
                sim_metrics.get("mean_t_demand", None).tolist()
            ).T

            mean_t_tank_levels = pd.DataFrame(
                sim_metrics.get("mean_t_tank_levels", None).tolist()
            ).T

            # No tiene sentido usarlos
            # node_degree = sim_metrics.get("node_degree", None)
            # bridges = sim_metrics.get("bridges", None)

            # ################### Datos promedio del experimento ####################
            # Por nodo
            experiment_betweenness_centrality = betweenness_centrality.mean(axis=1)
            experiment_closeness_centrality = closeness_centrality.mean(axis=1)
            experiment_mean_node_pressure = mean_node_pressure.mean(axis=1)

            # Por Tiempo
            experiment_mean_t_pressure = mean_t_pressure.mean(axis=1)
            experiment_todini = todini.mean(axis=1)
            experiment_mean_t_wsa = mean_t_wsa.mean(axis=1)
            experiment_mean_t_flowrate = mean_t_flowrate.mean(axis=1)
            experiment_mean_t_demand = mean_t_demand.mean(axis=1)
            experiment_mean_t_tank_levels = mean_t_tank_levels.mean(axis=1)
            ########################################################################

            experiment_results = {
                "betweenness_centrality": experiment_betweenness_centrality,
                "closeness_centrality": experiment_closeness_centrality,
                "mean_node_pressure": experiment_mean_node_pressure,
                "mean_t_pressure": experiment_mean_t_pressure,
                "todini": experiment_todini,
                "mean_t_wsa": experiment_mean_t_wsa,
                "mean_t_flowrate": experiment_mean_t_flowrate,
                "mean_t_demand": experiment_mean_t_demand,
                "mean_t_tank_levels": experiment_mean_t_tank_levels,
            }

            results[folder] = experiment_results
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
        "betweenness_at_3": "C. Interposición al 3%",
        "betweenness_at_6": "C. Interposición al 6%",
        "betweenness_at_10": "C. Interposición al 10%",
        "closeness_at_3": "C. Cercanía al 3%",
        "closeness_at_6": "C. Cercanía al 6%",
        "closeness_at_10": "C. Cercanía al 10%",
        "pressure_at_3": "Presión al 3%",
        "pressure_at_6": "Presión al 6%",
        "pressure_at_10": "Presión al 10%",
        "node_degree_at_3": "Grado nodal al 3%",
        "node_degree_at_6": "Grado nodal al 6%",
        "node_degree_at_10": "Grado nodal al 10%",
    }
    return verbose_name[exp_name]
