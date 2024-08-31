from savings.emissions.get_machine_emissions import (
    get_appliance_emissions,
    get_other_appliance_emissions,
)
from openapi_client.models import (
    Household,
    Emissions,
    EmissionsValues,
)
from constants.utils import PeriodEnum
from constants.machines.space_heating import (
    SPACE_HEATING_INFO,
)
from constants.machines.water_heating import WATER_HEATING_INFO
from constants.machines.cooktop import COOKTOP_INFO
from params import OPERATIONAL_LIFETIME


def calculate_emissions(
    current_household: Household, electrified_household: Household
) -> Emissions:

    # Weekly
    space_heating_emissions_weekly_before = get_appliance_emissions(
        current_household.space_heating, SPACE_HEATING_INFO, PeriodEnum.WEEKLY
    )
    space_heating_emissions_weekly_after = get_appliance_emissions(
        electrified_household.space_heating, SPACE_HEATING_INFO, PeriodEnum.WEEKLY
    )
    water_heating_emissions_weekly_before = get_appliance_emissions(
        current_household.water_heating, WATER_HEATING_INFO, PeriodEnum.WEEKLY
    )
    water_heating_emissions_weekly_after = get_appliance_emissions(
        electrified_household.water_heating, WATER_HEATING_INFO, PeriodEnum.WEEKLY
    )
    cooktop_emissions_weekly_before = get_appliance_emissions(
        current_household.cooktop, COOKTOP_INFO, PeriodEnum.WEEKLY
    )
    cooktop_emissions_weekly_after = get_appliance_emissions(
        electrified_household.cooktop, COOKTOP_INFO, PeriodEnum.WEEKLY
    )
    # TODO: vehicle emissions
    other_emissions_weekly_before = get_other_appliance_emissions(PeriodEnum.WEEKLY)
    other_emissions_weekly_after = get_other_appliance_emissions(PeriodEnum.WEEKLY)

    # We use the function to get emissions over longer periods, rather than relying on straight multiplication for emissions over operational lifetime, since macroeconomic factors can change things.

    # Yearly
    space_heating_emissions_yearly_before = get_appliance_emissions(
        current_household.space_heating, SPACE_HEATING_INFO, PeriodEnum.YEARLY
    )
    space_heating_emissions_yearly_after = get_appliance_emissions(
        electrified_household.space_heating, SPACE_HEATING_INFO, PeriodEnum.YEARLY
    )
    water_heating_emissions_yearly_before = get_appliance_emissions(
        current_household.water_heating, WATER_HEATING_INFO, PeriodEnum.YEARLY
    )
    water_heating_emissions_yearly_after = get_appliance_emissions(
        electrified_household.water_heating, WATER_HEATING_INFO, PeriodEnum.YEARLY
    )
    cooktop_emissions_yearly_before = get_appliance_emissions(
        current_household.cooktop, COOKTOP_INFO, PeriodEnum.YEARLY
    )
    cooktop_emissions_yearly_after = get_appliance_emissions(
        electrified_household.cooktop, COOKTOP_INFO, PeriodEnum.YEARLY
    )
    other_emissions_yearly_before = get_other_appliance_emissions(PeriodEnum.YEARLY)
    other_emissions_yearly_after = get_other_appliance_emissions(PeriodEnum.YEARLY)

    # Operational lifetime
    space_heating_emissions_lifetime_before = get_appliance_emissions(
        current_household.space_heating,
        SPACE_HEATING_INFO,
        PeriodEnum.OPERATIONAL_LIFETIME,
    )
    space_heating_emissions_lifetime_after = get_appliance_emissions(
        electrified_household.space_heating,
        SPACE_HEATING_INFO,
        PeriodEnum.OPERATIONAL_LIFETIME,
    )
    water_heating_emissions_lifetime_before = get_appliance_emissions(
        current_household.water_heating,
        WATER_HEATING_INFO,
        PeriodEnum.OPERATIONAL_LIFETIME,
    )
    water_heating_emissions_lifetime_after = get_appliance_emissions(
        electrified_household.water_heating,
        WATER_HEATING_INFO,
        PeriodEnum.OPERATIONAL_LIFETIME,
    )
    cooktop_emissions_lifetime_before = get_appliance_emissions(
        current_household.cooktop, COOKTOP_INFO, PeriodEnum.OPERATIONAL_LIFETIME
    )
    cooktop_emissions_lifetime_after = get_appliance_emissions(
        electrified_household.cooktop, COOKTOP_INFO, PeriodEnum.OPERATIONAL_LIFETIME
    )
    other_emissions_lifetime_before = get_other_appliance_emissions(
        PeriodEnum.OPERATIONAL_LIFETIME
    )
    other_emissions_lifetime_after = get_other_appliance_emissions(
        PeriodEnum.OPERATIONAL_LIFETIME
    )

    # Total emissions before
    weekly_before = (
        space_heating_emissions_weekly_before
        + water_heating_emissions_weekly_before
        + cooktop_emissions_weekly_before
        + other_emissions_weekly_before
    )
    yearly_before = (
        space_heating_emissions_yearly_before
        + water_heating_emissions_yearly_before
        + cooktop_emissions_yearly_before
        + other_emissions_yearly_before
    )
    lifetime_before = (
        space_heating_emissions_lifetime_before
        + water_heating_emissions_lifetime_before
        + cooktop_emissions_lifetime_before
        + other_emissions_lifetime_before
    )

    # Total emissions after
    weekly_after = (
        space_heating_emissions_weekly_after
        + water_heating_emissions_weekly_after
        + cooktop_emissions_weekly_after
        + other_emissions_weekly_after
    )
    yearly_after = (
        space_heating_emissions_yearly_after
        + water_heating_emissions_yearly_after
        + cooktop_emissions_yearly_after
        + other_emissions_yearly_after
    )
    lifetime_after = (
        space_heating_emissions_lifetime_after
        + water_heating_emissions_lifetime_after
        + cooktop_emissions_lifetime_after
        + other_emissions_lifetime_after
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
