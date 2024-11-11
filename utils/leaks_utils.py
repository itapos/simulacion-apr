import pandas as pd
import numpy as np
import wntr
from wntr.network import WaterNetworkModel
from decimal import Decimal, ROUND_HALF_UP
import networkx as nx
import pickle
from scipy.stats import lognorm

from utils.types import NetworkPriorityNodes, MitigationLeaksStrategyOptions

def get_damage_states(pga_values:list[float], inp_file:str):
    wn = WaterNetworkModel(inp_file)
    FC = wntr.scenario.FragilityCurve()
    FC.add_state("Moderado", 1, {"Default": lognorm(0.163, scale=1.2 * 0.379)})
    FC.add_state("Mayor", 2, {"Default": lognorm(0.225, scale=1.2 * 0.385)})

    pga_and_damage_states_list=[]
    for pga_value in pga_values:
        pga = pd.Series(pga_value, index=wn.pipe_name_list)
        failure_probability = FC.cdf_probability(pga)
        damage_states = FC.sample_damage_state(failure_probability)
        pga_and_damage_states_list.append((pga_value,damage_states))
    
    return pga_and_damage_states_list

def get_network_priority_nodes(
    wn_filepath: str, mean_node_pressure: pd.Series
) -> NetworkPriorityNodes:
    with open(wn_filepath, "rb") as f:
        wn = pickle.load(f)

    return {
        "betweenness": order_pipes_by_betweenness(wn),
        "closeness": order_pipes_by_closeness(wn),
        "pressure": order_pipes_by_pressure(wn, mean_node_pressure),
        "node_degree": order_pipes_by_node_degree(wn),
    }


def order_pipes_by_betweenness(wn: WaterNetworkModel) -> list[str]:
    import networkx as nx
    
    # Obtener el grafo de la red
    G = wn.to_graph()
    
    # Calcular la betweenness centrality de los nodos
    bc = nx.betweenness_centrality(G, normalized=True, weight="length")
    
    # Calcular la betweenness centrality promedio para cada tubería
    pipe_centrality = {}
    for pipe_name, pipe in wn.links():
        if pipe.link_type == "Pipe":  # Asegurarse de considerar solo tuberías
            start_node = pipe.start_node.name
            end_node = pipe.end_node.name
            # Promedio de la centralidad de los nodos de inicio y fin
            pipe_centrality[pipe_name] = (bc[start_node] + bc[end_node]) / 2

    # Ordenar las tuberías por su centralidad promedio (de mayor a menor)
    sorted_pipes = sorted(pipe_centrality.items(), key=lambda x: x[1], reverse=True)
    
    # Retornar solo los nombres de las tuberías ordenadas
    sorted_pipe_names = [pipe_name for pipe_name, _ in sorted_pipes]
    return sorted_pipe_names


def order_pipes_by_closeness(wn: WaterNetworkModel) -> list[str]:
    import networkx as nx
    
    # Obtener el grafo de la red
    G = wn.to_graph()
    
    # Calcular la closeness centrality de los nodos
    cc = nx.closeness_centrality(G, distance="length")
    
    # Calcular la closeness centrality promedio para cada tubería
    pipe_centrality = {}
    for pipe_name, pipe in wn.links():
        if pipe.link_type == "Pipe":  # Asegurarse de considerar solo tuberías
            start_node = pipe.start_node.name
            end_node = pipe.end_node.name
            # Promedio de la centralidad de los nodos de inicio y fin
            pipe_centrality[pipe_name] = (cc[start_node] + cc[end_node]) / 2

    # Ordenar las tuberías por su centralidad promedio (de mayor a menor)
    sorted_pipes = sorted(pipe_centrality.items(), key=lambda x: x[1], reverse=True)
    
    # Retornar solo los nombres de las tuberías ordenadas
    sorted_pipe_names = [pipe_name for pipe_name, _ in sorted_pipes]
    return sorted_pipe_names


def order_pipes_by_node_degree(wn: WaterNetworkModel) -> list[str]:
    # Crear un diccionario para almacenar el grado de cada nodo
    node_degree = {}
    nodes = wn.node_name_list
    for node_name in nodes:
        links = wn.get_links_for_node(node_name)  # Obtener las tuberías conectadas al nodo
        degree = len(links)  # El grado del nodo es el número de conexiones
        node_degree[node_name] = degree

    # Calcular el promedio del grado de los nodos conectados a cada tubería
    pipe_centrality = {}
    for pipe_name, pipe in wn.links():
        if pipe.link_type == "Pipe":  # Considerar solo tuberías
            start_node = pipe.start_node.name
            end_node = pipe.end_node.name
            # Promedio del grado de los nodos de inicio y fin
            pipe_centrality[pipe_name] = (node_degree[start_node] + node_degree[end_node]) / 2

    # Ordenar las tuberías por el promedio de los grados de sus nodos (de mayor a menor)
    sorted_pipes = sorted(pipe_centrality.items(), key=lambda x: x[1], reverse=True)

    # Retornar solo los nombres de las tuberías ordenadas
    sorted_pipe_names = [pipe_name for pipe_name, _ in sorted_pipes]
    return sorted_pipe_names

def order_pipes_by_pressure(
    wn: WaterNetworkModel, mean_node_pressure: pd.Series
) -> list[str]:
    avg_pressure = {}
    pipes = wn.pipe_name_list
    for pipe_name in pipes:
        pipe = wn.get_link(pipe_name)
        start_node = pipe.start_node.name
        end_node = pipe.end_node.name
        # Use the mean pressure directly from the Series for each node
        avg_pressure[pipe_name] = (
            mean_node_pressure[start_node] + mean_node_pressure[end_node]
        ) / 2

    # Sort pipes based on computed average pressure
    sorted_pipes = sorted(avg_pressure.items(), key=lambda x: x[1], reverse=True)
    sorted_pipe_names = [pipe_name for pipe_name, _ in sorted_pipes]
    return sorted_pipe_names


def get_reinforced_pipes(
    mitigation_leaks_strategy_options: MitigationLeaksStrategyOptions,
):
    mitigation_strategy = mitigation_leaks_strategy_options["mitigation_strategy"]
    reinforcement_percent = mitigation_leaks_strategy_options["reinforcement_percent"]
    priority_nodes = mitigation_leaks_strategy_options["priority_nodes"]

    if mitigation_strategy == "betweenness":
        ordered_pipes = priority_nodes["betweenness"]
    elif mitigation_strategy == "closeness":
        ordered_pipes = priority_nodes["closeness"]
    elif mitigation_strategy == "pressure":
        ordered_pipes = priority_nodes["pressure"]
    elif mitigation_strategy == "node_degree":
        ordered_pipes = priority_nodes["node_degree"]
    else:
        raise ValueError(f"Invalid mitigation_strategy '{mitigation_strategy}'")

    to_select = len(ordered_pipes) * reinforcement_percent / 100

    # Decimal is used because of the way python rounds numbers. E.g., round(2.5)=2
    int_to_select = int(Decimal(to_select).quantize(0, ROUND_HALF_UP))

    if int_to_select == 0:
        return []
    return ordered_pipes[:int_to_select]


def should_calculate_reinforced_pipes(
    mitigation_leaks_strategy_options: MitigationLeaksStrategyOptions | None,
):
    if mitigation_leaks_strategy_options is None:
        return False

    mitigation_strategy = mitigation_leaks_strategy_options["mitigation_strategy"]
    reinforcement_percent = mitigation_leaks_strategy_options["reinforcement_percent"]

    valid_mitigation_strategy = (
        isinstance(mitigation_strategy, str) and mitigation_strategy != ""
    )
    valid_reinforcement_percent = (
        isinstance(reinforcement_percent, int) and reinforcement_percent >= 0
    )

    if valid_mitigation_strategy and valid_reinforcement_percent:
        return True
    elif valid_mitigation_strategy and not valid_reinforcement_percent:
        raise ValueError(
            f"Invalid reinforcement_percent '{reinforcement_percent}' for mitigation_strategy '{mitigation_strategy}'"
        )
    return False


def generate_leaks(
    wn: WaterNetworkModel,
    damage_states: pd.Series,
    leak_start_time: int,
    mitigation_leaks_strategy_options: MitigationLeaksStrategyOptions | None,
) -> tuple[WaterNetworkModel, list[str]]:
    reinforced_pipes = []
    should_reinforce = should_calculate_reinforced_pipes(
        mitigation_leaks_strategy_options
    )
    if should_reinforce:
        reinforced_pipes = get_reinforced_pipes(mitigation_leaks_strategy_options)

    for pipe_name, damage_state in damage_states.items():
        pipe_diameter = wn.get_link(pipe_name).diameter
        if damage_state is not None:
            if damage_state == "Mayor":
                leak_diameter = 0.1 * pipe_diameter
                leak_diameter = min(leak_diameter, 0.0050)
                if pipe_name in reinforced_pipes:
                    leak_diameter = leak_diameter * 0.1
                leak_area = np.pi * (leak_diameter / 2) ** 2
            elif damage_state == "Moderado":
                leak_diameter = 0.05 * pipe_diameter
                leak_diameter = min(leak_diameter, 0.0025)
                if pipe_name in reinforced_pipes:
                    leak_diameter = leak_diameter * 0.1
                leak_area = np.pi * (leak_diameter / 2) ** 2
            else:
                leak_area = 0

            # Add leak to the network
            wn = wntr.morph.split_pipe(
                wn, pipe_name, f"{pipe_name}_A", f"Leak_{pipe_name}"
            )
            leak_node = wn.get_node(f"Leak_{pipe_name}")
            leak_node.add_leak(wn, area=leak_area, start_time=leak_start_time)

    return wn, reinforced_pipes
