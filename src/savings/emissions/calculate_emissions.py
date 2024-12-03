from openapi_client.models import (
    Household,
    Emissions,
    EmissionsValues,
)

from constants.utils import PeriodEnum
from constants.machines.space_heating import SPACE_HEATING_INFO
from constants.machines.water_heating import WATER_HEATING_INFO
from constants.machines.cooktop import COOKTOP_INFO
from openapi_client.models.location_enum import LocationEnum
from params import OPERATIONAL_LIFETIME
from savings.emissions.get_machine_emissions import (
    get_appliance_emissions,
    get_other_appliance_emissions,
    get_vehicle_emissions,
)


def calculate_emissions(
    current_household: Household, electrified_household: Household
) -> Emissions:

    # Weekly
    weekly_before = _get_total_emissions(
        current_household, PeriodEnum.WEEKLY, current_household.location
    )
    weekly_after = _get_total_emissions(
        electrified_household, PeriodEnum.WEEKLY, electrified_household.location
    )

    # Yearly
    yearly_before = _get_total_emissions(
        current_household, PeriodEnum.YEARLY, current_household.location
    )
    yearly_after = _get_total_emissions(
        electrified_household, PeriodEnum.YEARLY, electrified_household.location
    )

    # Operational lifetime
    lifetime_before = _get_total_emissions(
        current_household, PeriodEnum.OPERATIONAL_LIFETIME, current_household.location
    )
    lifetime_after = _get_total_emissions(
        electrified_household,
        PeriodEnum.OPERATIONAL_LIFETIME,
        electrified_household.location,
    )

    return Emissions(
        perWeek=EmissionsValues(
            before=round(weekly_before, 2),
            after=round(weekly_after, 2),
            difference=round(weekly_after - weekly_before, 2),
        ),
        perYear=EmissionsValues(
            before=round(yearly_before, 2),
            after=round(yearly_after, 2),
            difference=round(yearly_after - yearly_before, 2),
        ),
        overLifetime=EmissionsValues(
            before=round(lifetime_before, 2),
            after=round(lifetime_after, 2),
            difference=round(lifetime_after - lifetime_before, 2),
        ),
        operationalLifetime=OPERATIONAL_LIFETIME,
    )


def _get_total_emissions(
    household: Household,
    period: PeriodEnum,
    location: LocationEnum,
):
    appliance_emissions = _get_total_appliance_emissions(household, period, location)
    vehicle_emissions = get_vehicle_emissions(household.vehicles, period)
    other_emissions = get_other_appliance_emissions(household.occupancy, period)
    return appliance_emissions + vehicle_emissions + other_emissions


def _get_total_appliance_emissions(
    household: Household, period: PeriodEnum, location: LocationEnum
):
    return (
        get_appliance_emissions(
            household.space_heating,
            SPACE_HEATING_INFO,
            location,
            household.occupancy,
            period,
        )
        + get_appliance_emissions(
            household.water_heating,
            WATER_HEATING_INFO,
            location,
            household.occupancy,
            period,
        )
        + get_appliance_emissions(
            household.cooktop,
            COOKTOP_INFO,
            location,
            household.occupancy,
            period,
        )
    )
