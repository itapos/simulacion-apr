import numpy as np
import pandas as pd
from scipy.stats import lognorm
from scipy.stats import truncnorm
from wntr.scenario import FragilityCurve
from datetime import timedelta
from wntr.network import WaterNetworkModel
import wntr
import os


def generate_pga_value() -> float:
    """
    Generates a PGA value between 0.2 and 0.4 using a truncated normal distribution
    and returns it as a float.
    """
    mu = 0.28  # mean
    sigma = 0.06  # standard deviation
    lower, upper = 0.2, 0.4  # limits

    # Calculate 'a' and 'b' parameters for truncnorm
    a, b = (lower - mu) / sigma, (upper - mu) / sigma

    # Generate value
    pga_value = truncnorm.rvs(a, b, loc=mu, scale=sigma)
    rounded_pga_value = np.round(pga_value, 7)

    return rounded_pga_value


def generate_pga_series(pga_value: float, wn: WaterNetworkModel) -> pd.Series:
    """
    Takes a PGA value and returns it as a pd.Series indexed by pipe names.
    """
    # Create a pd.Series assigning the PGA value to each pipe
    pga_series = pd.Series(pga_value, index=wn.pipe_name_list)

    return pga_series


def generate_fragility_curve() -> FragilityCurve:
    FC = wntr.scenario.FragilityCurve()
    FC.add_state("Moderado", 1, {"Default": lognorm(0.163, scale=1.2 * 0.379)})
    FC.add_state("Mayor", 2, {"Default": lognorm(0.225, scale=1.2 * 0.385)})

    return FC


def format_time(start_seconds, end_seconds):
    total_seconds = end_seconds - start_seconds

    td = timedelta(seconds=total_seconds)

    # Extract hours, minutes, and seconds from timedelta
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format with 2 decimals in seconds
    formatted_time = f"{hours}:{minutes:02}:{seconds + td.microseconds / 1e6:05.2f}"

    return formatted_time


def generate_excels(output_folder: str, results: pd.DataFrame, sufix: str):
    metrics_dict = {
        "mean_t_pressure": {},
        "mean_t_wsa": {},
        "todini": {},
        "mean_t_flowrate": {},
        "mean_t_demand": {},
        "mean_t_tank_levels": {},
    }
    for _, row in results.iterrows():
        realization_id = row["realization_id"]

        if "error" in row and pd.notna(row["error"]):
            print(f"Skipping realization {realization_id} due to error.")
            continue

        mean_t_pressure = row["mean_t_pressure"]
        mean_t_wsa = row["mean_t_wsa"]
        todini = row["todini"]
        mean_t_flowrate = row["mean_t_flowrate"]
        mean_t_demand = row["mean_t_demand"]
        mean_t_tank_levels = row["mean_t_tank_levels"]

        metrics_dict["mean_t_pressure"][realization_id] = mean_t_pressure
        metrics_dict["mean_t_wsa"][realization_id] = mean_t_wsa
        metrics_dict["todini"][realization_id] = todini
        metrics_dict["mean_t_flowrate"][realization_id] = mean_t_flowrate
        metrics_dict["mean_t_demand"][realization_id] = mean_t_demand
        metrics_dict["mean_t_tank_levels"][realization_id] = mean_t_tank_levels

    # Crear DataFrames para cada métrica
    df_average_pressure = pd.DataFrame(metrics_dict["mean_t_pressure"])
    df_wsa = pd.DataFrame(metrics_dict["mean_t_wsa"])
    df_todini = pd.DataFrame(metrics_dict["todini"])
    df_average_flowrate = pd.DataFrame(metrics_dict["mean_t_flowrate"])
    df_average_demand = pd.DataFrame(metrics_dict["mean_t_demand"])
    df_average_tank_levels = pd.DataFrame(metrics_dict["mean_t_tank_levels"])

    df_average_pressure.to_excel(
        os.path.join(output_folder, f"Average_Pressure{sufix}.xlsx")
    )
    df_wsa.to_excel(os.path.join(output_folder, f"WSA{sufix}.xlsx"))
    df_todini.to_excel(os.path.join(output_folder, f"Todini{sufix}.xlsx"))
    df_average_flowrate.to_excel(
        os.path.join(output_folder, f"Average_Flowrate{sufix}.xlsx")
    )
    df_average_demand.to_excel(
        os.path.join(output_folder, f"Average_Demand{sufix}.xlsx")
    )
    df_average_tank_levels.to_excel(
        os.path.join(output_folder, f"Average_Tank_Levels{sufix}.xlsx")
    )
