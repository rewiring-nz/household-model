import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from colours import COLOURS


def plot_savings(df: pd.DataFrame) -> None:
    plot_emissions_savings_pct(
        df,
        col='emissions_savings_without_vehicles_pct',
        xlabel="% of household's emissions saved (without vehicles)",
        filepath='../plots/emissions_savings_without_vehicles_histogram_pct.png',
    )
    plot_emissions_savings_pct(
        df,
        col='emissions_savings_with_vehicles_pct',
        xlabel="% of household's emissions saved (with all vehicles switched to EVs)",
        filepath='../plots/emissions_savings_with_vehicles_histogram_pct.png',
    )
    plot_cumulative_emissions_savings(
        df,
        col='total_emissions_savings_without_vehicles_lifetime',
        filepath='../plots/emissions_savings_without_vehicles_cumulative_pct.png',
    )
    plot_cumulative_emissions_savings(
        df,
        col='total_emissions_savings_with_vehicles_lifetime',
        filepath='../plots/emissions_savings_with_vehicles_cumulative_pct.png',
    )


def plot_emissions_savings_pct(
    df: pd.DataFrame, col: str, xlabel: str, filepath: str
) -> None:
    fig = plt.figure(figsize=(9, 4))
    bins = np.arange(
        0, 105, 5
    )  # change to remove everything under 0% once we figure out the wood stuff
    ax = df[col].hist(bins=bins, color=COLOURS['red']['300'])
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Number of households')
    ax.set_xlim((0, 100))
    ax.set_xticks(bins)
    plt.tight_layout()
    plt.savefig(
        filepath,
        dpi=150,
        transparent=True,
    )
    plt.show()


def calc_cumsum(savings: pd.Series) -> pd.DataFrame:
    """Calculate the cumulative sum and percentages of savings

    Args:
        savings (pd.Series): should have no NAs
        col (str): name of emissions savings column to calculate on

    Returns:
        pd.DataFrame: df with cumsum and household pct
    """
    whole_cohort_savings = savings.sum()
    cumulative_emissions_savings = savings.cumsum().reset_index(drop=True)
    cumsum_pct = (
        100 * cumulative_emissions_savings / whole_cohort_savings
    ).reset_index()
    cumsum_pct['households_pct'] = 100 * cumsum_pct['index'] / len(cumsum_pct)
    return cumsum_pct


def get_min_pct_households_for_pct_savings_over_90(df: pd.DataFrame) -> float:
    n_total_switched = len(df)
    whole_cohort_savings = df.sum()

    # Get % of emissions saved per % of households electrified
    pct_households_to_pct_savings = {}
    for pct in range(0, 100, 1):
        n_segment = int(pct / 100 * n_total_switched)
        savings = df[n_segment]
        pct_savings = round(100 * savings / whole_cohort_savings, 2)
        pct_households_to_pct_savings[pct] = pct_savings

    # Get the lowest percentage of households where 90% of emissions are saved
    pct_households_to_pct_savings_over_90 = {
        k: v for k, v in pct_households_to_pct_savings.items() if v > 90
    }
    min_pct_households_for_pct_savings_over_90 = min(
        [k for k, v in pct_households_to_pct_savings_over_90.items()]
    )
    return min_pct_households_for_pct_savings_over_90


def plot_cumulative_emissions_savings(df: pd.DataFrame, filepath: str) -> None:
    import pdb

    without_vehicles = (
        df['total_emissions_savings_without_vehicles_lifetime']
        .dropna()
        .sort_values(ascending=False)
    )
    pdb.set_trace()
    cumsum_pct_without_vehicles = calc_cumsum(without_vehicles)
    intercept_without_vehicles = get_min_pct_households_for_pct_savings_over_90(
        cumsum_pct_without_vehicles
    )
    pdb.set_trace()
    with_vehicles = (
        df['total_emissions_savings_with_vehicles_lifetime']
        .dropna()
        .sort_values(ascending=False)
    )
    pdb.set_trace()
    cumsum_pct_with_vehicles = calc_cumsum(with_vehicles)
    pdb.set_trace()
    intercept_with_vehicles = get_min_pct_households_for_pct_savings_over_90(
        cumsum_pct_with_vehicles
    )
    pdb.set_trace()
    # Plot
    fig = plt.figure(figsize=(6, 4))

    # With vehicles
    plt.plot(
        cumsum_pct_with_vehicles['households_pct'],
        cumsum_pct_with_vehicles['total_emissions_savings_with_vehicles_lifetime'],
        lw=3,
        c=COLOURS['blue']['500'],
        label='With vehicles',
    )
    pdb.set_trace()
    plt.plot(
        [intercept_with_vehicles, intercept_with_vehicles],
        [0, 90],
        color='k',
        alpha=0.5,
        linestyle='dashed',
        linewidth=2,
    )
    plt.plot(
        [0, intercept_with_vehicles],
        [90, 90],
        color='k',
        alpha=0.5,
        linestyle='dashed',
        linewidth=2,
    )

    # Without vehicles
    plt.plot(
        cumsum_pct_without_vehicles['households_pct'],
        cumsum_pct_without_vehicles[
            'total_emissions_savings_without_vehicles_lifetime'
        ],
        lw=3,
        c=COLOURS['red']['500'],
        label='Without vehicles',
    )
    plt.plot(
        [intercept_without_vehicles, intercept_without_vehicles],
        [0, 90],
        color='k',
        alpha=0.5,
        linestyle='dashed',
        linewidth=2,
    )
    plt.plot(
        [0, intercept_without_vehicles],
        [90, 90],
        color='k',
        alpha=0.5,
        linestyle='dashed',
        linewidth=2,
    )

    plt.xlabel('% of households')
    plt.ylabel('Cumulative emissions saved (% of total)')
    ax = plt.gca()
    ax.set_xlim((0, 100))
    ax.set_ylim((0, 101))
    ax.set_xticks(range(0, 101, 10))
    ax.set_yticks(range(0, 100, 10))
    plt.legend()

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, transparent=True)
    plt.show()
