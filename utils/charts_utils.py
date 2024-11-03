from wntr.network import WaterNetworkModel
import pandas as pd
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import wntr
from wntr.scenario import FragilityCurve
from .types import SimulationType


def generate_charts(
    simulation_type: SimulationType,
    inp_file: str,
    base_path: str,
    realization_id: int,
    wn: WaterNetworkModel,
    FC: FragilityCurve | None,
    damage_states: pd.Series | None,
    pga_value: float,
    mean_t_wsa: pd.Series,
    todini: pd.Series,
    pressure: pd.DataFrame,
):
    if simulation_type == "Earthquake":
        if FC is None:
            raise ValueError("FC is None.")
        if damage_states is None:
            raise ValueError("damage_states is None.")

        generate_damage_chart(
            inp_file,
            base_path,
            realization_id,
            damage_states,
            pga_value,
            FC,
        )

    generate_wsa_chart(
        base_path,
        realization_id,
        mean_t_wsa,
    )

    generate_todini_chart(
        base_path,
        realization_id,
        todini,
    )

    generate_pressure_chart(
        base_path,
        realization_id,
        wn,
        pressure,
    )


def generate_damage_chart(
    inp_file: str,
    base_path: str,
    realization_id: int,
    damage_states: pd.Series,
    pga_value: float,
    FC: FragilityCurve,
):
    wn = WaterNetworkModel(inp_file)
    priority_map = FC.get_priority_map()
    damage_value = damage_states.map(priority_map)

    colors = ["grey", "royalblue", "darkorange"]
    cmap = ListedColormap(colors)

    fig, ax = plt.subplots(figsize=(5, 8))
    wntr.graphics.plot_network(
        wn,
        ax=ax,
        link_attribute=damage_value,
        node_size=0,
        link_cmap=cmap,  # Colormap que definiste
        link_range=[0, 2],
        link_width=2,
        link_colorbar_label="Estado daño:\n\n0=Ninguno\n1=Moderado\n2=Mayor\n",
        title=f"Estado de daño de la red \npga = {round(pga_value,2)} [g]",
    )

    fig.savefig(
        f"{base_path}/earthquake_damage_{realization_id}.png",
        format="png",
        dpi=300,
    )
    plt.close(fig)


def generate_wsa_chart(
    base_path: str,
    realization_id: int,
    mean_t_wsa: pd.Series,
):
    fig, ax = plt.subplots()
    plt.plot(mean_t_wsa.index / 3600, mean_t_wsa)
    plt.title("WSA red promedio")
    plt.xlabel("Tiempo [h]")
    plt.ylabel("Fracción de demanda cubierta (WSA) [-]")
    plt.grid(True)
    ax.set_xlim([0, 24])
    ax.set_ylim([0, 1.19])

    fig.savefig(f"{base_path}/mean_t_wsa_{realization_id}.png", format="png", dpi=300)
    plt.close(fig)


def generate_todini_chart(
    base_path: str,
    realization_id: int,
    todini: pd.Series,
):
    fig, ax = plt.subplots()
    plt.plot(todini.index / 3600, todini)
    plt.title("Todini")
    plt.xlabel("Tiempo [h]")
    plt.ylabel("Índice de Todini [-]")
    plt.grid(True)
    ax.set_xlim([0, 24])

    fig.savefig(f"{base_path}/todini_{realization_id}.png", format="png", dpi=300)
    plt.close(fig)


def generate_pressure_chart(
    base_path: str,
    realization_id: int,
    wn: WaterNetworkModel,
    pressure: pd.DataFrame,
):
    junctions = wn.junction_name_list
    pressure = pressure[junctions]

    min_pressure = pressure.iloc[-1].min()
    max_pressure = pressure.iloc[-1].max()

    fig, ax = plt.subplots(figsize=(10, 15))
    wntr.graphics.plot_network(
        wn,
        ax=ax,
        title=f"Presión de la red \nPmin = {round(min_pressure,2)} [m.c.a] \nPmax = {round(max_pressure,2)} [m.c.a]",
        node_attribute="pressure",
        node_colorbar_label="[m.c.a]",
        node_range=[-10, 80],
    )

    fig.savefig(f"{base_path}/pressure_{realization_id}.png", format="png", dpi=300)
    plt.close(fig)
