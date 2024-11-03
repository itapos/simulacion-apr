import wntr
from wntr.network import WaterNetworkModel
import pandas as pd
import networkx as nx
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import os
import pickle

from .types import MitigationLeaksStrategyOptions, SimulationType
from .charts_utils import generate_charts
from .leaks_utils import generate_leaks
from .general_utils import (
    generate_pga_series,
    generate_fragility_curve,
    format_time,
)


def simulate_wrapper(
    inp_file: str,
    simulation_type: SimulationType,
    mitigation_leaks_strategy_options: MitigationLeaksStrategyOptions | None,
    leak_start_time: int,
    required_pressure: int,
    realization_id: int,
    total_duration: int,
    minimum_pressure: float,
    pga_value: float,
    output_folder: str,
):
    try:
        start_time = time.time()
        # Reconstruct the network within each worker process
        wn = WaterNetworkModel(inp_file)
        wn.options.hydraulic.demand_model = "PDD"
        wn.options.time.duration = total_duration
        wn.options.hydraulic.minimum_pressure = minimum_pressure
        wn.options.hydraulic.required_pressure = required_pressure

        if simulation_type == "Earthquake":
            pga = generate_pga_series(pga_value, wn)
            FC = generate_fragility_curve()
            failure_probability = FC.cdf_probability(pga)
            damage_states = FC.sample_damage_state(failure_probability)
            actual_time = time.time()
            formated_time = format_time(start_time, actual_time)
            print(
                f"Iteration {realization_id}: adding leaks for pga: {pga_value} ({formated_time})"
            )

            wn, reinforced_pipes = generate_leaks(
                wn=wn,
                damage_states=damage_states,
                leak_start_time=leak_start_time,
                mitigation_leaks_strategy_options=mitigation_leaks_strategy_options,
            )

        # Simulate the network
        actual_time = time.time()
        print(
            f"Iteration {realization_id}: simulating ({format_time(start_time, actual_time)})"
        )
        sim = wntr.sim.WNTRSimulator(wn)
        simulation_results = sim.run_sim()

        # Guardar wn y simulation_results
        simulation_data_folder = os.path.join(output_folder, "simulation_data")
        os.makedirs(simulation_data_folder, exist_ok=True)
        wn_filename = os.path.join(
            simulation_data_folder, f"wn_realization_{realization_id}.pickle"
        )
        sim_results_filename = os.path.join(
            simulation_data_folder, f"simulation_results_{realization_id}.pickle"
        )

        with open(wn_filename, "wb") as f:
            pickle.dump(wn, f)

        with open(sim_results_filename, "wb") as f:
            pickle.dump(simulation_results, f)

        # Calculate metrics
        actual_time = time.time()
        print(
            f"Iteration {realization_id}: calculating metrics ({format_time(start_time, actual_time)})"
        )
        metrics = {}
        if simulation_type == "Earthquake":
            damages_count = damage_states.value_counts()
            major_damages = damages_count.get("Mayor", 0)
            moderated_damages = damages_count.get("Moderado", 0)

            metrics["num_damages"] = major_damages + moderated_damages
            metrics["num_major_damages"] = major_damages
            metrics["num_moderate_damages"] = moderated_damages
            metrics["pga"] = pga_value

        G = wn.get_graph()

        # ===== Topologic =====
        # Betweenness centrality
        bc = nx.betweenness_centrality(G, normalized=True, weight="length")
        metrics["betweenness_centrality"] = bc

        # Closeness centrality
        cc = nx.closeness_centrality(G, distance="length")
        metrics["closeness_centrality"] = cc

        # Node degree
        node_degree = G.degree()
        metrics["node_degree"] = node_degree

        # Bridges
        bridges = list(wntr.metrics.bridges(G))
        metrics["bridges"] = bridges

        # ===== Hydraulic =====
        # Avg pressure
        pressure = simulation_results.node["pressure"]
        mean_node_pressure = pressure.mean()
        mean_t_pressure = pressure.mean(axis=1)
        mean_system_pressure = pressure.mean().mean()
        metrics["pressure"] = pressure
        metrics["mean_node_pressure"] = mean_node_pressure
        metrics["min_system_pressure"] = pressure.min().min()
        metrics["mean_t_pressure"] = mean_t_pressure
        metrics["mean_system_pressure"] = mean_system_pressure
        junctions = wn.junction_name_list
        junctions_pressure = pressure[junctions]
        metrics["min_system_junctions_pressure"] = junctions_pressure.min().min()

        # Todini
        head = simulation_results.node["head"]
        pressure = simulation_results.node["pressure"]
        demand = simulation_results.node["demand"]
        pump_flowrate = simulation_results.link["flowrate"].loc[:, wn.pump_name_list]
        todini: pd.Series = wntr.metrics.todini_index(
            head, pressure, demand, pump_flowrate, wn, required_pressure
        )
        metrics["todini"] = todini

        # WSA
        demand_nodes = wn.junction_name_list
        demand_nodes_index = [
            node
            for node in demand_nodes
            if wn.get_node(node).demand_timeseries_list[0].base_value > 0
        ]
        demand = simulation_results.node["demand"]

        filtered_demand = demand[demand_nodes_index]
        filtered_expected_demand = wntr.metrics.expected_demand(wn)[demand_nodes_index]

        wsa: pd.DataFrame = wntr.metrics.water_service_availability(
            filtered_expected_demand, filtered_demand
        )
        mean_t_wsa = wsa.mean(axis=1)
        mean_system_wsa = mean_t_wsa.mean()
        metrics["wsa"] = wsa
        metrics["mean_t_wsa"] = mean_t_wsa
        metrics["mean_system_wsa"] = mean_system_wsa

        # Others
        flowrate = simulation_results.link["flowrate"]
        mean_t_flowrate = flowrate.mean(axis=1)
        metrics["mean_t_flowrate"] = mean_t_flowrate

        demand = simulation_results.node["demand"]
        mean_t_demand = demand.mean(axis=1)
        metrics["mean_t_demand"] = mean_t_demand

        head = simulation_results.node["head"]
        tank_names = wn.tank_name_list
        tank_levels = head[tank_names]
        mean_t_tank_levels = tank_levels.mean(axis=1)
        metrics["mean_t_tank_levels"] = mean_t_tank_levels

        metrics["realization_id"] = realization_id
        # Add mitigation data
        if simulation_type == "Earthquake" and mitigation_leaks_strategy_options is not None:
            mitigation_strategy = mitigation_leaks_strategy_options[
                "mitigation_strategy"
            ]
            reinforcement_percent = mitigation_leaks_strategy_options[
                "reinforcement_percent"
            ]

            metrics["mitigation_strategy"] = mitigation_strategy
            metrics["mitigation_reinforcement_percent"] = reinforcement_percent
            metrics["mitigation_reinforced_pipes"] = reinforced_pipes

        # Generate Charts
        charts_data_folder = os.path.join(output_folder, "charts")
        os.makedirs(charts_data_folder, exist_ok=True)

        print(
            f"Iteration {realization_id}: generating Charts ({format_time(start_time, actual_time)})"
        )
        generate_charts(
            simulation_type,
            inp_file,
            charts_data_folder,
            realization_id,
            wn,
            FC if simulation_type == "Earthquake" else None,
            damage_states if simulation_type == "Earthquake" else None,
            pga_value,
            mean_t_wsa,
            todini,
            pressure,
        )

        actual_time = time.time()
        print(
            f"Iteration {realization_id}: Done ({format_time(start_time, actual_time)})"
        )
        metrics["realization_time"] = format_time(start_time, actual_time)
        return metrics
    except Exception as e:
        print(f"Error in realization {realization_id}: {e}")
        return {"realization_id": realization_id, "error": str(e)}


def simulate_network_parallel(
    simulation_type: SimulationType,
    inp_file: str,
    mitigation_leaks_strategy_options: MitigationLeaksStrategyOptions | None,
    leak_start_time: int,
    required_pressure: int,
    num_realizations: int,
    pga_values: list[float],
    max_workers: int,
    total_duration: int,
    minimum_pressure: float,
    output_folder: str,
) -> pd.DataFrame:
    results_list = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                simulate_wrapper,
                inp_file,
                simulation_type,
                mitigation_leaks_strategy_options,
                leak_start_time,
                required_pressure,
                i + 1,
                total_duration,
                minimum_pressure,
                pga_values[i] if simulation_type == "Earthquake" else 0,
                output_folder,
            )
            for i in range(num_realizations)
        ]

        # Use `as_completed` to get results as they complete
        for future in as_completed(futures):
            result = future.result()
            results_list.append(result)

    # Convert results into a DataFrame
    results_df = pd.DataFrame(results_list)
    return results_df
