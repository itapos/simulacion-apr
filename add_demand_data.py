import pandas as pd
import pickle

def reorder_new_data(data: list[dict[str, pd.Series]], realization_id: pd.Series) -> pd.DataFrame:
    # Create a DataFrame from the new data
    new_data_df = pd.DataFrame(data)
    
    # Reorder new data based on realization_id
    reordered_data = new_data_df.loc[realization_id.reset_index(drop=True) - 1].reset_index(drop=True)
    
    return reordered_data

def calculate_mean_t_leak_demand_and_total_demand(iterations:int, folder:str):
    folder = f"{folder}/simulation_data"
    data=[]
    
    for i in range(1,iterations+1):
        wn_pickle_route = f"{folder}/wn_realization_{i}.pickle"
        results_pickle_route = f"{folder}/simulation_results_{i}.pickle"
        with open(results_pickle_route, "rb") as f:
            results= pickle.load(f)
        with open(wn_pickle_route, "rb") as f:
            wn= pickle.load(f)
            
        demand = results.node['demand'].loc[:,wn.junction_name_list]
        
        leak_demand = results.node['leak_demand'].loc[:,wn.junction_name_list]
    
        total_demand = demand + leak_demand    
    
        mean_t_demand = demand.sum(axis=1)
        mean_t_leak_demand = leak_demand.sum(axis=1)
        mean_t_total_demand = total_demand.sum(axis=1)

        iteration_data = {
            "mean_t_demand": mean_t_demand,
            "mean_t_leak_demand": mean_t_leak_demand,
            "mean_t_total_demand": mean_t_total_demand,
        }
        data.append(iteration_data)
    
    return data

def add_mean_t_leak_demand_and_total_demand(exp_name: str, mitigation_strategies:list[str], reinforcement_percents:list[int], iterations:int):
    path = f"results/{exp_name}"
    # =========================================================================================================
    # ============================================= No earthquake =============================================
    # =========================================================================================================
    print("Iterating no earthquake")
    folder = f"{path}/no_earthquake"
    
    results_pickle_route = f"{folder}/metrics.pickle"
    old_results_pickle_route = f"{folder}/old_metrics.pickle"
    with open(results_pickle_route, "rb") as f:
        metrics: pd.DataFrame = pickle.load(f)
    
    new_data = calculate_mean_t_leak_demand_and_total_demand(1, folder)
    reordered_new_data = reorder_new_data(new_data, metrics['realization_id'])

    new_metrics = pd.merge(
        metrics.drop(columns=['mean_t_demand']),  # Drop 'mean_t_demand' from metrics
        reordered_new_data,                       # Merge with reordered_new_data
        left_index=True,                          # Merge based on the index
        right_index=True
    )
    
    with open(old_results_pickle_route, "wb") as f:
        pickle.dump(metrics, f)

    with open(results_pickle_route, "wb") as f:
        pickle.dump(new_metrics, f)

    # =========================================================================================================
    # =========================================== Simple  Eartquake ===========================================
    # =========================================================================================================
    print("Iterating base earthquake")
    folder = f"{path}/base_earthquake"
    
    results_pickle_route = f"{folder}/metrics.pickle"
    old_results_pickle_route = f"{folder}/old_metrics.pickle"
    with open(results_pickle_route, "rb") as f:
        metrics: pd.DataFrame = pickle.load(f)
    
    new_data = calculate_mean_t_leak_demand_and_total_demand(iterations, folder)
    reordered_new_data = reorder_new_data(new_data, metrics['realization_id'])

    new_metrics = pd.merge(
        metrics.drop(columns=['mean_t_demand']),  # Drop 'mean_t_demand' from metrics
        reordered_new_data,                       # Merge with reordered_new_data
        left_index=True,                          # Merge based on the index
        right_index=True
    )
    
    with open(old_results_pickle_route, "wb") as f:
        pickle.dump(metrics, f)

    with open(results_pickle_route, "wb") as f:
        pickle.dump(new_metrics, f)
    
    # =========================================================================================================
    # ========================================= Mitigated  Eartquakes =========================================
    # =========================================================================================================
    for mitigation_strategy_name in mitigation_strategies:
        for reinforcement_percent in reinforcement_percents:
            print(f"Iterating {mitigation_strategy_name} at {reinforcement_percent}")
            folder = f"{path}/{mitigation_strategy_name}_at_{reinforcement_percent}"

            # Cargar los resultados de la simulación
            results_pickle_route = f"{folder}/results.pickle"
            old_results_pickle_route = f"{folder}/old_results.pickle"
            with open(results_pickle_route, "rb") as f:
                metrics: pd.DataFrame = pickle.load(f)
            
            new_data = calculate_mean_t_leak_demand_and_total_demand(iterations, folder)
            reordered_new_data = reorder_new_data(new_data, metrics['realization_id'])

            new_metrics = pd.merge(
                metrics.drop(columns=['mean_t_demand']),  # Drop 'mean_t_demand' from metrics
                reordered_new_data,                       # Merge with reordered_new_data
                left_index=True,                          # Merge based on the index
                right_index=True
            )
            
            with open(old_results_pickle_route, "wb") as f:
                pickle.dump(metrics, f)

            with open(results_pickle_route, "wb") as f:
                pickle.dump(new_metrics, f)

# ================================================================================================
exp_name = "experimento_full_2024-11-09_02-00-07"
mitigation_strategies = ["betweenness", "closeness", "pressure", "node_degree"]
reinforcement_percents = [3,6,10,50,100]
iterations = 500

add_mean_t_leak_demand_and_total_demand(exp_name, mitigation_strategies, reinforcement_percents, iterations)