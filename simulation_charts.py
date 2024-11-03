import wntr
import pickle
import matplotlib.pyplot as plt
from wntr.network import WaterNetworkModel
from generate_experiment_data import get_exp_verbose_name
import os


def generate_plots(exp_name:str, exp_results: dict):
    mitigation_strategies = ["betweenness", "closeness", "pressure", "node_degree"]
    wn_no_earthquake_route = exp_results["no_earthquake"]["wn_pickle_route"]
    
    plots_folder = os.path.join("results", exp_name, "plots")
    os.makedirs(plots_folder, exist_ok=True)

    with open(wn_no_earthquake_route, "rb") as f:
        wn_no_earthquake = pickle.load(f)

    for experiment in mitigation_strategies:
        print(f"Generating plots for {experiment}")
        # betweenness_centrality
        betweenness_centrality_data = {
            "no_earthquake": exp_results["no_earthquake"]["betweenness_centrality"],
            "base_earthquake": exp_results["base_earthquake"]["betweenness_centrality"],
            f"{experiment}_at_3": exp_results[f"{experiment}_at_3"][
                "betweenness_centrality"
            ],
            f"{experiment}_at_6": exp_results[f"{experiment}_at_6"][
                "betweenness_centrality"
            ],
            f"{experiment}_at_10": exp_results[f"{experiment}_at_10"][
                "betweenness_centrality"
            ],
        }
        plot_experiment_betweenness_centrality(
            plots_folder, experiment, wn_no_earthquake, betweenness_centrality_data
        )

        # closeness_centrality
        closeness_centrality_data = {
            "no_earthquake": exp_results["no_earthquake"]["closeness_centrality"],
            "base_earthquake": exp_results["base_earthquake"]["closeness_centrality"],
            f"{experiment}_at_3": exp_results[f"{experiment}_at_3"][
                "closeness_centrality"
            ],
            f"{experiment}_at_6": exp_results[f"{experiment}_at_6"][
                "closeness_centrality"
            ],
            f"{experiment}_at_10": exp_results[f"{experiment}_at_10"][
                "closeness_centrality"
            ],
        }
        plot_experiment_closeness_centrality(
            plots_folder, experiment, wn_no_earthquake, closeness_centrality_data
        )

        # mean_node_pressure
        mean_node_pressure_data = {
            "no_earthquake": exp_results["no_earthquake"]["mean_node_pressure"],
            "base_earthquake": exp_results["base_earthquake"]["mean_node_pressure"],
            f"{experiment}_at_3": exp_results[f"{experiment}_at_3"][
                "mean_node_pressure"
            ],
            f"{experiment}_at_6": exp_results[f"{experiment}_at_6"][
                "mean_node_pressure"
            ],
            f"{experiment}_at_10": exp_results[f"{experiment}_at_10"][
                "mean_node_pressure"
            ],
        }
        plot_experiment_mean_node_pressure(
            plots_folder, experiment, wn_no_earthquake, mean_node_pressure_data
        )

        # mean_t_pressure
        mean_t_pressure_data = {
            "no_earthquake": exp_results["no_earthquake"]["mean_t_pressure"],
            "base_earthquake": exp_results["base_earthquake"]["mean_t_pressure"],
            f"{experiment}_at_3": exp_results[f"{experiment}_at_3"]["mean_t_pressure"],
            f"{experiment}_at_6": exp_results[f"{experiment}_at_6"]["mean_t_pressure"],
            f"{experiment}_at_10": exp_results[f"{experiment}_at_10"]["mean_t_pressure"],
        }
        plot_experiment_mean_t_pressure(plots_folder, experiment, mean_t_pressure_data)

        # todini
        todini_data = {
            "no_earthquake": exp_results["no_earthquake"]["todini"],
            "base_earthquake": exp_results["base_earthquake"]["todini"],
            f"{experiment}_at_3": exp_results[f"{experiment}_at_3"]["todini"],
            f"{experiment}_at_6": exp_results[f"{experiment}_at_6"]["todini"],
            f"{experiment}_at_10": exp_results[f"{experiment}_at_10"]["todini"],
        }
        plot_experiment_todini(plots_folder, experiment, todini_data)

        # mean_t_wsa
        mean_t_wsa_data = {
            "no_earthquake": exp_results["no_earthquake"]["mean_t_wsa"],
            "base_earthquake": exp_results["base_earthquake"]["mean_t_wsa"],
            f"{experiment}_at_3": exp_results[f"{experiment}_at_3"]["mean_t_wsa"],
            f"{experiment}_at_6": exp_results[f"{experiment}_at_6"]["mean_t_wsa"],
            f"{experiment}_at_10": exp_results[f"{experiment}_at_10"]["mean_t_wsa"],
        }
        plot_experiment_mean_t_wsa(plots_folder, experiment, mean_t_wsa_data)

        # mean_t_flowrate
        mean_t_flowrate_data = {
            "no_earthquake": exp_results["no_earthquake"]["mean_t_flowrate"],
            "base_earthquake": exp_results["base_earthquake"]["mean_t_flowrate"],
            f"{experiment}_at_3": exp_results[f"{experiment}_at_3"]["mean_t_flowrate"],
            f"{experiment}_at_6": exp_results[f"{experiment}_at_6"]["mean_t_flowrate"],
            f"{experiment}_at_10": exp_results[f"{experiment}_at_10"]["mean_t_flowrate"],
        }
        plot_experiment_mean_t_flowrate(plots_folder, experiment, mean_t_flowrate_data)

        # mean_t_demand
        mean_t_demand_data = {
            "no_earthquake": exp_results["no_earthquake"]["mean_t_demand"],
            "base_earthquake": exp_results["base_earthquake"]["mean_t_demand"],
            f"{experiment}_at_3": exp_results[f"{experiment}_at_3"]["mean_t_demand"],
            f"{experiment}_at_6": exp_results[f"{experiment}_at_6"]["mean_t_demand"],
            f"{experiment}_at_10": exp_results[f"{experiment}_at_10"]["mean_t_demand"],
        }
        plot_experiment_mean_t_demand(plots_folder, experiment, mean_t_demand_data)

        # mean_t_tank_levels
        mean_t_tank_levels_data = {
            "no_earthquake": exp_results["no_earthquake"]["mean_t_tank_levels"],
            "base_earthquake": exp_results["base_earthquake"]["mean_t_tank_levels"],
            f"{experiment}_at_3": exp_results[f"{experiment}_at_3"][
                "mean_t_tank_levels"
            ],
            f"{experiment}_at_6": exp_results[f"{experiment}_at_6"][
                "mean_t_tank_levels"
            ],
            f"{experiment}_at_10": exp_results[f"{experiment}_at_10"][
                "mean_t_tank_levels"
            ],
        }
        plot_experiment_mean_t_tank_levels(
            plots_folder, experiment, mean_t_tank_levels_data
        )


# =============================================================================
def plot_experiment_betweenness_centrality(
    base_path: str,
    exp_name: str,
    wn: WaterNetworkModel,
    data: dict,
):
    experiment_folder = os.path.join(base_path, exp_name)
    os.makedirs(experiment_folder, exist_ok=True)

    title_fontsize, text_fontsize, fig_size, node_size = 12, 10, (6, 8), 12

    for key, serie in data.items():
        label = get_exp_verbose_name(key)
        fig, ax = plt.subplots(figsize=fig_size)
        fig.suptitle("Centralidad de interposición", fontsize=title_fontsize)
        plt.figtext(
            0.5,
            0.94,
            f"Experimento: {label}",
            ha="center",
            fontsize=text_fontsize,
            style="italic",
        )
        wntr.graphics.plot_network(
            wn,
            ax=ax,
            node_size=node_size,
            node_attribute=serie,
            node_colorbar_label="[-]",
        )

        fig.savefig(
            f"{experiment_folder}/{key}_betweenness_centrality.png",
            format="png",
            dpi=300,
        )
        plt.close(fig)


def plot_experiment_closeness_centrality(
    base_path: str,
    exp_name: str,
    wn: WaterNetworkModel,
    data: dict,
):
    experiment_folder = os.path.join(base_path, exp_name)
    os.makedirs(experiment_folder, exist_ok=True)

    title_fontsize, text_fontsize, fig_size, node_size = 12, 10, (6, 8), 12

    for key, serie in data.items():
        label = get_exp_verbose_name(key)
        fig, ax = plt.subplots(figsize=fig_size)
        fig.suptitle("Centralidad de cercanía", fontsize=title_fontsize)
        plt.figtext(
            0.5,
            0.94,
            f"Experimento: {label}",
            ha="center",
            fontsize=text_fontsize,
            style="italic",
        )
        wntr.graphics.plot_network(
            wn,
            ax=ax,
            node_size=node_size,
            node_attribute=serie,
            node_colorbar_label="[-]",
        )

        fig.savefig(
            f"{experiment_folder}/{key}_closeness_centrality.png",
            format="png",
            dpi=300,
        )
        plt.close(fig)


def plot_experiment_mean_node_pressure(
    base_path: str,
    exp_name: str,
    wn: WaterNetworkModel,
    data: dict,
):
    experiment_folder = os.path.join(base_path, exp_name)
    os.makedirs(experiment_folder, exist_ok=True)

    title_fontsize, text_fontsize, fig_size, node_size = 12, 10, (6, 8), 12

    for key, serie in data.items():
        label = get_exp_verbose_name(key)
        fig, ax = plt.subplots(figsize=fig_size)
        fig.suptitle("Presión de nodo promedio", fontsize=title_fontsize)
        plt.figtext(
            0.5,
            0.94,
            f"Experimento: {label}",
            ha="center",
            fontsize=text_fontsize,
            style="italic",
        )
        wntr.graphics.plot_network(
            wn,
            ax=ax,
            node_size=node_size,
            node_attribute=serie,
            node_colorbar_label="[-]",
        )

        fig.savefig(
            f"{experiment_folder}/{key}mean_node_pressure.png", format="png", dpi=300
        )
        plt.close(fig)


def plot_experiment_mean_t_pressure(
    base_path: str,
    exp_name: str,
    data: dict,
):
    experiment_folder = os.path.join(base_path, exp_name)
    os.makedirs(experiment_folder, exist_ok=True)

    suptitle_fontsize, title_fontsize, fig_size = 12, 10, (7, 4)
    fig, ax = plt.subplots(figsize=fig_size)
    for key, serie in data.items():
        label = get_exp_verbose_name(key)
        ax.plot(serie.index / 3600, serie.values, label=label)
    fig.suptitle(
        "Presión de la red promedio", fontsize=suptitle_fontsize
    )  # fontweight='bold'
    ax.set_title(f"Experimento: {exp_name}", fontsize=title_fontsize, style="italic")
    ax.set_xlabel("Tiempo [h]")
    ax.set_ylabel("Presión [m³/s]")
    # ax.set_ylim([0, 1.19])
    ax.set_xlim([0, 24])
    ax.grid(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), fontsize=10, ncol=3)

    # plt.show()
    fig.tight_layout()
    fig.savefig(f"{experiment_folder}/mean_t_pressure.png", format="png", dpi=300)
    plt.close(fig)


def plot_experiment_todini(
    base_path: str,
    exp_name: str,
    data: dict,
):
    experiment_folder = os.path.join(base_path, exp_name)
    os.makedirs(experiment_folder, exist_ok=True)

    suptitle_fontsize, title_fontsize, fig_size = 12, 10, (7, 4)
    fig, ax = plt.subplots(figsize=fig_size)
    for key, serie in data.items():
        label = get_exp_verbose_name(key)
        ax.plot(serie.index / 3600, serie.values, label=label)
    fig.suptitle(
        "Índice de Todini promedio", fontsize=suptitle_fontsize
    )  # fontweight='bold'
    ax.set_title(f"Experimento: {exp_name}", fontsize=title_fontsize, style="italic")
    ax.set_xlabel("Tiempo [h]")
    ax.set_ylabel("Índice de Todini [-]")
    # ax.set_ylim([0, 1.19])
    ax.set_xlim([0, 24])
    ax.grid(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), fontsize=10, ncol=3)

    # plt.show()
    fig.tight_layout()
    fig.savefig(f"{experiment_folder}/todini.png", format="png", dpi=300)
    plt.close(fig)


def plot_experiment_mean_t_wsa(
    base_path: str,
    exp_name: str,
    data: dict,
):
    experiment_folder = os.path.join(base_path, exp_name)
    os.makedirs(experiment_folder, exist_ok=True)

    suptitle_fontsize, title_fontsize, fig_size = 12, 10, (7, 4)
    fig, ax = plt.subplots(figsize=fig_size)
    for key, serie in data.items():
        label = get_exp_verbose_name(key)
        ax.plot(serie.index / 3600, serie.values, label=label)
    fig.suptitle("WSA red promedio", fontsize=suptitle_fontsize)  # fontweight='bold'
    ax.set_title(f"Experimento: {exp_name}", fontsize=title_fontsize, style="italic")
    ax.set_xlabel("Tiempo [h]")
    ax.set_ylabel("Fracción de demanda cubierta (WSA) [-]")
    ax.set_ylim([0, 1.19])
    ax.set_xlim([0, 24])
    ax.grid(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), fontsize=10, ncol=3)

    # plt.show()
    fig.tight_layout()
    fig.savefig(f"{experiment_folder}/mean_t_wsa.png", format="png", dpi=300)
    plt.close(fig)


def plot_experiment_mean_t_flowrate(
    base_path: str,
    exp_name: str,
    data: dict,
):
    experiment_folder = os.path.join(base_path, exp_name)
    os.makedirs(experiment_folder, exist_ok=True)

    suptitle_fontsize, title_fontsize, fig_size = 12, 10, (7, 4)
    fig, ax = plt.subplots(figsize=fig_size)
    for key, serie in data.items():
        label = get_exp_verbose_name(key)
        ax.plot(serie.index / 3600, serie.values, label=label)
    fig.suptitle("Caudal promedio", fontsize=suptitle_fontsize)  # fontweight='bold'
    ax.set_title(f"Experimento: {exp_name}", fontsize=title_fontsize, style="italic")
    ax.set_xlabel("Tiempo [h]")
    ax.set_ylabel("Caudal [m³/s]")
    # ax.set_ylim([0, 1.19])
    ax.set_xlim([0, 24])
    ax.grid(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), fontsize=10, ncol=3)

    # plt.show()
    fig.tight_layout()
    fig.savefig(f"{experiment_folder}/mean_t_flowrate.png", format="png", dpi=300)
    plt.close(fig)


def plot_experiment_mean_t_demand(
    base_path: str,
    exp_name: str,
    data: dict,
):
    experiment_folder = os.path.join(base_path, exp_name)
    os.makedirs(experiment_folder, exist_ok=True)

    suptitle_fontsize, title_fontsize, fig_size = 12, 10, (7, 4)
    fig, ax = plt.subplots(figsize=fig_size)
    for key, serie in data.items():
        label = get_exp_verbose_name(key)
        ax.plot(serie.index / 3600, serie.values, label=label)
    fig.suptitle("Demanda promedio", fontsize=suptitle_fontsize)  # fontweight='bold'
    ax.set_title(f"Experimento: {exp_name}", fontsize=title_fontsize, style="italic")
    ax.set_xlabel("Tiempo [h]")
    ax.set_ylabel("Demanda [m³/s]")
    # ax.set_ylim([0, 1.19])
    ax.set_xlim([0, 24])
    ax.grid(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), fontsize=10, ncol=3)

    # plt.show()
    fig.tight_layout()
    fig.savefig(f"{experiment_folder}/mean_t_demand.png", format="png", dpi=300)
    plt.close(fig)


def plot_experiment_mean_t_tank_levels(
    base_path: str,
    exp_name: str,
    data: dict,
):
    experiment_folder = os.path.join(base_path, exp_name)
    os.makedirs(experiment_folder, exist_ok=True)

    suptitle_fontsize, title_fontsize, fig_size = 12, 10, (7, 4)
    fig, ax = plt.subplots(figsize=fig_size)
    for key, serie in data.items():
        label = get_exp_verbose_name(key)
        ax.plot(serie.index / 3600, serie.values, label=label)
    fig.suptitle("Nivel del estanque", fontsize=suptitle_fontsize)  # fontweight='bold'
    ax.set_title(f"Experimento: {exp_name}", fontsize=title_fontsize, style="italic")
    ax.set_xlabel("Tiempo [h]")
    ax.set_ylabel("Nivel [m]")
    # ax.set_ylim([0, 1.19])
    ax.set_xlim([0, 24])
    ax.grid(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), fontsize=10, ncol=3)

    # plt.show()
    fig.tight_layout()
    fig.savefig(f"{experiment_folder}/mean_t_tank_levels.png", format="png", dpi=300)
    plt.close(fig)
