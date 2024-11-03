from typing import TypedDict, Literal


SimulationType = Literal["Clean", "Earthquake"]


class NetworkPriorityNodes(TypedDict):
    betweenness: list[str]
    closeness: list[str]
    pressure: list[str]
    node_degree: list[str]


class MitigationLeaksStrategyOptions(TypedDict):
    priority_nodes: NetworkPriorityNodes
    mitigation_strategy: Literal["betweenness", "closeness", "pressure", "node_degree"]
    reinforcement_percent: int
