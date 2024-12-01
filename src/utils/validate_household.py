from openapi_client.models import Household, Solar, Battery


def validate_household(household: Household):
    ensure_no_battery_without_solar(household.solar, household.battery)


def ensure_no_battery_without_solar(solar: Solar, battery: Battery):
    has_or_wants_solar = solar.has_solar or solar.install_solar
    has_or_wants_battery = battery.has_battery or battery.install_battery
    if not has_or_wants_solar and has_or_wants_battery:
        raise ValueError("Can't have battery without solar")
