from openapi_client.models import (
    Household,
    Emissions,
    EmissionsValues,
)

from constants.utils import PeriodEnum
from constants.machines.space_heating import SPACE_HEATING_INFO
from constants.machines.water_heating import WATER_HEATING_INFO
from constants.machines.cooktop import COOKTOP_INFO
from params import OPERATIONAL_LIFETIME
from savings.emissions.get_machine_emissions import (
    get_appliance_emissions,
    get_other_appliance_emissions,
    get_vehicle_emissions,
)


def calculate_emissions(
    current_household: Household, electrified_household: Household
) -> Emissions:
    """Calculate emissions for current and electrified households over various periods."""

    periods = [PeriodEnum.WEEKLY, PeriodEnum.YEARLY, PeriodEnum.OPERATIONAL_LIFETIME]

    emissions_before = {
        period: _get_emissions_for_period(current_household, period)
        for period in periods
    }
    emissions_after = {
        period: _get_emissions_for_period(electrified_household, period)
        for period in periods
    }

    return Emissions(
        perWeek=_calculate_emissions_values(
            emissions_before[PeriodEnum.WEEKLY], emissions_after[PeriodEnum.WEEKLY]
        ),
        perYear=_calculate_emissions_values(
            emissions_before[PeriodEnum.YEARLY], emissions_after[PeriodEnum.YEARLY]
        ),
        overLifetime=_calculate_emissions_values(
            emissions_before[PeriodEnum.OPERATIONAL_LIFETIME],
            emissions_after[PeriodEnum.OPERATIONAL_LIFETIME],
        ),
        operationalLifetime=OPERATIONAL_LIFETIME,
    )


def _get_emissions_for_period(household: Household, period: PeriodEnum) -> dict:
    """Calculate emissions for a given household and period."""
    return {
        "space_heating": get_appliance_emissions(
            household.space_heating, SPACE_HEATING_INFO, period
        ),
        "water_heating": get_appliance_emissions(
            household.water_heating, WATER_HEATING_INFO, period
        ),
        "cooktop": get_appliance_emissions(household.cooktop, COOKTOP_INFO, period),
        "vehicles": get_vehicle_emissions(household.vehicles, period),
        "other": get_other_appliance_emissions(period),
    }


def _calculate_totals(emissions: dict) -> float:
    """Sum all emissions."""
    return sum(emissions.values())


def _calculate_emissions_values(before: dict, after: dict) -> EmissionsValues:
    """Calculate emissions values for before and after scenarios."""
    before_total = _calculate_totals(before)
    after_total = _calculate_totals(after)
    return EmissionsValues(
        before=round(before_total, 2),
        after=round(after_total, 2),
        difference=round(after_total - before_total, 2),
    )
