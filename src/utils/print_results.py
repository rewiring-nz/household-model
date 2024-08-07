import sys

sys.path.append('../src')

import pandas as pd
from params import OPERATIONAL_LIFETIME


def print_results(df: pd.DataFrame) -> None:
    print(f"\n\n\nResults:")

    print(f"\n\n\n\N{factory} Emissions savings:")

    print(f"\nEmissions")
    print(f"\n- Without vehicles")
    print(f"\n  - over {OPERATIONAL_LIFETIME} year operational lifetime (kg CO2e)")
    print(
        f"    - Mean: {round(df['total_emissions_without_vehicles_lifetime'].mean())}"
    )
    print(
        f"    - Median: {round(df['total_emissions_without_vehicles_lifetime'].median())}"
    )
    print(f"\n- With vehicles")
    print(f"\n  - over {OPERATIONAL_LIFETIME} year operational lifetime (kg CO2e)")
    print(f"    - Mean: {round(df['total_emissions_with_vehicles_lifetime'].mean())}")
    print(
        f"    - Median: {round(df['total_emissions_with_vehicles_lifetime'].median())}"
    )

    print(f"\nSavings")

    print(f"\n- Without switching vehicles")
    print(f"\n  - per year (kg CO2e)")
    print(
        f"    - Mean: {round(df['total_emissions_savings_without_vehicles_year'].mean())}"
    )
    print(
        f"    - Median: {round(df['total_emissions_savings_without_vehicles_year'].median())}"
    )
    print(f"\n  - over {OPERATIONAL_LIFETIME} year operational lifetime (kg CO2e)")
    print(
        f"    - Mean: {round(df['total_emissions_savings_without_vehicles_lifetime'].mean())}"
    )
    print(
        f"    - Median: {round(df['total_emissions_savings_without_vehicles_lifetime'].median())}"
    )
    print(f"\n  - As percentage")
    print(
        f"    - Mean: {round(df['emissions_savings_without_vehicles_pct'].mean(), 1)}%"
    )
    print(
        f"    - Median: {round(df['emissions_savings_without_vehicles_pct'].median(), 1)}%"
    )
    total_emissions_saved = round(
        df['total_emissions_savings_without_vehicles_lifetime'].sum(), 1
    )
    total_emissions_saved_pct = round(
        (
            100
            * total_emissions_saved
            / df['total_emissions_without_vehicles_lifetime'].sum()
        ),
        1,
    )
    print(
        f"\n  - Total saved across whole cohort for lifetime: {total_emissions_saved:,} kg CO2e ({total_emissions_saved_pct}%)"
    )

    print(f"\n- With all vehicles switched")
    print(f"\n  - per year (kg CO2e)")
    print(
        f"    - Mean: {round(df['total_emissions_savings_with_vehicles_year'].mean())}"
    )
    print(
        f"    - Median: {round(df['total_emissions_savings_with_vehicles_year'].median())}"
    )
    print(f"\n  - over {OPERATIONAL_LIFETIME} year operational lifetime (kg CO2e)")
    print(
        f"    - Mean: {round(df['total_emissions_savings_with_vehicles_lifetime'].mean())}"
    )
    print(
        f"    - Median: {round(df['total_emissions_savings_with_vehicles_lifetime'].median())}"
    )
    print(f"\n  - As percentage")
    print(f"    - Mean: {round(df['emissions_savings_with_vehicles_pct'].mean(), 1)}%")
    print(
        f"    - Median: {round(df['emissions_savings_with_vehicles_pct'].median(), 1)}%"
    )
    total_emissions_saved = round(
        df['total_emissions_savings_with_vehicles_lifetime'].sum(), 1
    )
    total_emissions_saved_pct = round(
        (
            100
            * total_emissions_saved
            / df['total_emissions_with_vehicles_lifetime'].sum()
        ),
        1,
    )
    print(
        f"\n  - Total saved across whole cohort for lifetime: {total_emissions_saved:,} kg CO2e ({total_emissions_saved_pct}%)"
    )

    print(f"\n\n\n\N{House with Garden} Opex savings:")

    print('\nCosts')
    print(f"\n- Without vehicles")
    print(f"\n  - per year")
    print(
        f"    - Mean: {round((df['total_opex_lifetime_without_vehicles']/OPERATIONAL_LIFETIME).mean())}"
    )
    print(
        f"    - Median: {round((df['total_opex_lifetime_without_vehicles']/OPERATIONAL_LIFETIME).median())}"
    )
    print(f"\n- With vehicles")
    print(f"\n  - per year")
    print(
        f"    - Mean: {round((df['total_opex_lifetime_with_vehicles']/OPERATIONAL_LIFETIME).mean())}"
    )
    print(
        f"    - Median: {round((df['total_opex_lifetime_with_vehicles']/OPERATIONAL_LIFETIME).median())}"
    )

    print('\nSavings')

    print(f"\n- Without switching vehicles")
    print(f"\n  - per year")
    total_opex_savings_lifetime_without_vehicles_mean = df[
        'total_opex_savings_lifetime_without_vehicles'
    ].mean()
    total_opex_savings_lifetime_without_vehicles_median = df[
        'total_opex_savings_lifetime_without_vehicles'
    ].median()
    print(
        f"    - Mean: ${round(total_opex_savings_lifetime_without_vehicles_mean/OPERATIONAL_LIFETIME):,}"
    )
    print(
        f"    - Median: ${round(total_opex_savings_lifetime_without_vehicles_median/OPERATIONAL_LIFETIME):,}"
    )
    print(f"\n  - over {OPERATIONAL_LIFETIME} year operational lifetime")
    print(f"    - Mean: ${round(total_opex_savings_lifetime_without_vehicles_mean):,}")
    print(
        f"    - Median: ${round(total_opex_savings_lifetime_without_vehicles_median):,}"
    )
    print(f"\n  - As percentage")
    print(f"    - Mean: {round(df['opex_savings_without_vehicles_pct'].mean(), 1)}%")
    print(
        f"    - Median: {round(df['opex_savings_without_vehicles_pct'].median(), 1)}%"
    )
    total_opex_saved = round(
        df['total_opex_savings_lifetime_without_vehicles'].sum(), 1
    )
    total_opex_saved_pct = round(
        (100 * total_opex_saved / df['total_opex_lifetime_without_vehicles'].sum()),
        1,
    )
    print(
        f"\n  - Total saved across whole cohort for lifetime: ${total_opex_saved:,} ({total_opex_saved_pct}%)"
    )
    print(f"\n- With all vehicles switched")
    print(f"\n  - per year")
    total_opex_savings_lifetime_with_vehicles_mean = df[
        'total_opex_savings_lifetime_with_vehicles'
    ].mean()
    total_opex_savings_lifetime_with_vehicles_median = df[
        'total_opex_savings_lifetime_with_vehicles'
    ].median()
    print(
        f"    - Mean: ${round(total_opex_savings_lifetime_with_vehicles_mean/OPERATIONAL_LIFETIME):,}"
    )
    print(
        f"    - Median: ${round(total_opex_savings_lifetime_with_vehicles_median/OPERATIONAL_LIFETIME):,}"
    )
    print(f"\n  - over {OPERATIONAL_LIFETIME} year operational lifetime")
    print(f"    - Mean: ${round(total_opex_savings_lifetime_with_vehicles_mean):,}")
    print(f"    - Median: ${round(total_opex_savings_lifetime_with_vehicles_median):,}")
    print(f"\n  - As percentage")
    print(f"    - Mean: {round(df['opex_savings_with_vehicles_pct'].mean(), 1)}%")
    print(f"    - Median: {round(df['opex_savings_with_vehicles_pct'].median(), 1)}%")
    total_opex_saved = round(df['total_opex_savings_lifetime_with_vehicles'].sum(), 1)
    total_opex_saved_pct = round(
        (100 * total_opex_saved / df['total_opex_lifetime_with_vehicles'].sum()),
        1,
    )
    print(
        f"\n  - Total saved across whole cohort for lifetime: ${total_opex_saved:,} ({total_opex_saved_pct}%)"
    )

    print(f"\n\n\n\N{Money with Wings} Upfront costs:")

    print(f"\n- With all vehicles switched (vehicle costs not included)")
    total_upfront_cost_mean = df['total_upfront_cost'].mean()
    total_upfront_cost_median = df['total_upfront_cost'].median()
    print(
        f"    - Mean: ${round(total_upfront_cost_mean):,} (${round(total_upfront_cost_mean/OPERATIONAL_LIFETIME)} per year)"
    )
    print(
        f"    - Median: ${round(total_upfront_cost_median):,} (${round(total_upfront_cost_median/OPERATIONAL_LIFETIME)} per year)"
    )

    print('\n\n')


if __name__ == "__main__":
    file_path_enriched = '../data/survey_results_enriched.csv'
    df_enriched = pd.read_csv(file_path_enriched)
    print_results(df_enriched)
